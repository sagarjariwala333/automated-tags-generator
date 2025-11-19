from typing import List, Dict
from tool.tag_critic_models import TagEvaluation, RevisionModel, IterationLog, TagCriticResponse
from tool.tag_critic_utils import normalize_tag

def evaluate_tags_rubric(
    recommended_tags: List[str],
    context: str = "",
    threshold: float = 70.0,
    max_iterations: int = 3,
    llm=None,
    tag_critic_eval_prompt=None,
    tag_critic_revise_prompt=None
) -> TagCriticResponse:
    """
    Evaluate and refine tags using a rubric evaluator loop.
    - Scores tags for relevance, clarity, quality, specificity, coverage, distinctiveness, and overall score (0-100).
    - Attempts to refine failing tags up to max_iterations.
    - Eliminates tags that still don't pass threshold.
    Returns a TagCriticResponse Pydantic model.
    """
    tags_current = []
    seen = set()
    for t in recommended_tags:
        if not t:
            continue
        norm = normalize_tag(t)
        if norm in seen:
            continue
        seen.add(norm)
        tags_current.append(t.strip())

    iteration_logs: List[IterationLog] = []
    last_evaluations: List[TagEvaluation] = []

    for iteration in range(1, max_iterations + 1):
        tags_str = ", ".join(tags_current)
        eval_prompt = tag_critic_eval_prompt.format(context=context, tags_str=", ".join(tags_current))

        # Use structured output for evaluation
        structured_llm = llm.with_structured_output(List[TagEvaluation])
        evaluations = structured_llm.invoke(eval_prompt)
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

        revise_prompt = tag_critic_revise_prompt.format(
            context=context,
            failing_tags="\n".join([f"{f.tag} (score: {f.score})" for f in failing])
        )
        # Use structured output for revisions
        structured_llm_revise = llm.with_structured_output(List[RevisionModel])
        revisions = structured_llm_revise.invoke(revise_prompt)

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
            norm = normalize_tag(t)
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
