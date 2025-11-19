from langchain_google_genai import ChatGoogleGenerativeAI
import os
from dotenv import load_dotenv
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
import json
import re

load_dotenv()

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0.4,
    google_api_key=os.getenv("GOOGLE_API_KEY")
)

class TagEvaluation(BaseModel):
    tag: str
    relevance: float = Field(0.0, ge=0.0, le=1.0)
    clarity: float = Field(0.0, ge=0.0, le=1.0)
    quality: float = Field(0.0, ge=0.0, le=1.0)
    score: float = Field(0.0, ge=0.0, le=1.0)

class RevisionModel(BaseModel):
    original: Optional[str] = None
    revised: str
    reason: Optional[str] = None

class IterationLog(BaseModel):
    iteration: int
    evaluations: List[TagEvaluation]
    failing_count: int
    passing_count: int

class TagCriticResponse(BaseModel):
    original_tags: List[str]
    final_tags: List[str]
    threshold: float
    iterations: int
    iteration_logs: List[IterationLog]
    last_evaluations: List[TagEvaluation]
    agent: str
    error: Optional[str] = None

def _extract_json_block(text: str):
    """Attempt to extract the first JSON block from the provided text."""
    if not text or not isinstance(text, str):
        return None
    indices = [i for i in (text.find('{'), text.find('[')) if i != -1]
    idx = min(indices) if indices else None
    if idx is None:
        return None
    candidate = text[idx:]
    for end in range(len(candidate), 0, -1):
        try:
            return json.loads(candidate[:end])
        except Exception:
            continue
    return None

def _parse_evaluations(response_text: str) -> List[Dict[str, Any]]:
    """
    Parse evaluation JSON. Expected format:
    [
      {"tag":"...", "relevance":0.8, "clarity":0.9, "quality":0.7, "score":0.8},
      ...
    ]
    """
    parsed = _extract_json_block(response_text)
    if not parsed or not isinstance(parsed, list):
        evals = []
        for line in response_text.splitlines():
            parts = [p.strip() for p in re.split(r'[:\-]', line, maxsplit=1) if p.strip()]
            if len(parts) == 2:
                try:
                    score = float(parts[1])
                    evals.append({"tag": parts[0], "score": score})
                except Exception:
                    continue
        return evals
    return parsed

def _parse_revisions(response_text: str) -> List[Dict[str, str]]:
    """
    Parse revisions JSON. Expected format:
    [
      {"original":"old", "revised":"new", "reason":"..."},
      ...
    ]
    """
    parsed = _extract_json_block(response_text)
    if not parsed:
        lines = [ln.strip("- ").strip() for ln in response_text.splitlines() if ln.strip()]
        return [{"original": None, "revised": ln, "reason": ""} for ln in lines]
    if isinstance(parsed, list) and all(isinstance(x, str) for x in parsed):
        return [{"original": None, "revised": x, "reason": ""} for x in parsed]
    out = []
    for item in parsed:
        if not isinstance(item, dict):
            continue
        out.append({
            "original": item.get("original") or item.get("failed") or None,
            "revised": item.get("revised") or item.get("new") or item.get("suggestion") or "",
            "reason": item.get("reason", "")
        })
    return out

def _normalize_tag(tag: str) -> str:
    return tag.strip().lower()

def _to_tag_evaluation(e: Dict[str, Any]) -> TagEvaluation:
    """Convert a raw evaluation dict to a TagEvaluation model with defaults."""
    tag = e.get("tag") or e.get("name") or (str(e.get("tag", "")) if "tag" in e else "")
    try:
        relevance = float(e.get("relevance", e.get("rel", 0.0)))
    except Exception:
        relevance = 0.0
    try:
        clarity = float(e.get("clarity", e.get("cla", 0.0)))
    except Exception:
        clarity = 0.0
    try:
        quality = float(e.get("quality", e.get("qual", 0.0)))
    except Exception:
        quality = 0.0
    if "score" in e and e.get("score") is not None:
        try:
            score = float(e.get("score"))
        except Exception:
            score = round((relevance + clarity + quality) / 3.0, 3)
    else:
        score = round((relevance + clarity + quality) / 3.0, 3)
    score = max(0.0, min(1.0, score))
    return TagEvaluation(
        tag=str(tag).strip(),
        relevance=round(relevance, 3),
        clarity=round(clarity, 3),
        quality=round(quality, 3),
        score=round(score, 3)
    )

def evaluate_tags_rubric(
    recommended_tags: List[str],
    context: str = "",
    threshold: float = 0.7,
    max_iterations: int = 3
) -> TagCriticResponse:
    """
    Evaluate and refine tags using a rubric evaluator loop.

    - Scores tags for relevance, clarity, quality and overall score (0-1).
    - Attempts to refine failing tags up to max_iterations.
    - Eliminates tags that still don't pass threshold.
    Returns a TagCriticResponse Pydantic model.
    """
    tags_current = []
    seen = set()
    for t in recommended_tags:
        if not t:
            continue
        norm = _normalize_tag(t)
        if norm in seen:
            continue
        seen.add(norm)
        tags_current.append(t.strip())

    iteration_logs: List[IterationLog] = []
    last_evaluations: List[TagEvaluation] = []

    for iteration in range(1, max_iterations + 1):
        tags_str = ", ".join(tags_current)
        eval_prompt = (
            f"You are a tag quality evaluator. Given the context and a set of tags, evaluate each tag on "
            f"Relevance, Clarity, and Quality as numbers between 0.0 and 1.0, and provide an overall score (0.0-1.0) "
            f"as the average. Output a JSON array of objects: "
            "[{\"tag\":\"...\",\"relevance\":0.80,\"clarity\":0.70,\"quality\":0.85,\"score\":0.78}, ...]\n\n"
            f"Context:\n{context}\n\n"
            f"Tags:\n{tags_str}\n\n"
            "Return only JSON. Keep three decimal places for scores."
        )

        eval_response = llm.invoke(eval_prompt)
        eval_raw = eval_response.content if hasattr(eval_response, "content") else str(eval_response)
        evaluations_raw = _parse_evaluations(eval_raw)

        evaluations: List[TagEvaluation] = []
        for e in evaluations_raw:
            try:
                evaluations.append(_to_tag_evaluation(e))
            except Exception:
                continue

        last_evaluations = evaluations

        failing = [e for e in evaluations if e.score < threshold]
        passing = [e for e in evaluations if e.score >= threshold]

        iteration_logs.append(IterationLog(
            iteration=iteration,
            evaluations=evaluations,
            failing_count=len(failing),
            passing_count=len(passing)
        ))

        if not failing:
            break

        revise_prompt = (
            "You are a tag improvement assistant. Given the failing tags and critiques, propose improved versions "
            "that address relevance, clarity, and quality. Return JSON array with objects "
            "[{\"original\":\"...\",\"revised\":\"...\",\"reason\":\"...\"}, ...].\n\n"
            f"Context:\n{context}\n\n"
            "Failing tags and their current evaluations:\n"
            + "\n".join([f"{f.tag} (score: {f.score})" for f in failing])
            + "\n\nOnly return JSON."
        )

        revise_response = llm.invoke(revise_prompt)
        revise_raw = revise_response.content if hasattr(revise_response, "content") else str(revise_response)
        revisions_raw = _parse_revisions(revise_raw)

        revisions: List[RevisionModel] = []
        for r in revisions_raw:
            if r.get("revised"):
                revisions.append(RevisionModel(
                    original=r.get("original"),
                    revised=r.get("revised"),
                    reason=r.get("reason")
                ))

        rev_map: Dict[str, str] = {}
        for r in revisions:
            orig = r.original
            revised = r.revised or None
            if revised and revised.strip():
                if orig:
                    rev_map[orig.strip()] = revised.strip()
                else:
                    rev_map[f"_ins_{len(rev_map)}"] = revised.strip()

        new_tags = []
        for t in tags_current:
            if t in rev_map:
                new_tags.append(rev_map[t])
            else:
                new_tags.append(t)

        for k, v in rev_map.items():
            if k.startswith("_ins_"):
                new_tags.append(v)

        normalized = []
        seen2 = set()
        for t in new_tags:
            if not t or not isinstance(t, str):
                continue
            norm = _normalize_tag(t)
            if norm not in seen2:
                seen2.add(norm)
                normalized.append(t.strip())

        tags_current = normalized

    final_tags = []
    if last_evaluations:
        for e in last_evaluations:
            if e.score >= threshold:
                final_tags.append(e.tag)
    else:
        final_tags = tags_current

    result_model = TagCriticResponse(
        original_tags=recommended_tags,
        final_tags=final_tags,
        threshold=threshold,
        iterations=len(iteration_logs),
        iteration_logs=iteration_logs,
        last_evaluations=last_evaluations,
        agent="tag_critic_agent"
    )
    return result_model

def critique_tags(tags: list, context: str = "", threshold: float = 0.7, max_iterations: int = 3) -> dict:
    """Tag Critic Agent - Evaluates tag quality and attempts improvement"""
    try:
        model_result = evaluate_tags_rubric(tags, context=context, threshold=threshold, max_iterations=max_iterations)
        return model_result.dict()
    except Exception as e:
        return {
            "original_tags": tags,
            "final_tags": [],
            "error": str(e),
            "agent": "tag_critic_agent"
        }