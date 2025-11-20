from typing import List, Dict
from tool.tag_critic_models import TagEvaluation, RevisionModel, IterationLog, TagCriticResponse, TagEvaluationList, RevisionModelList
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
    print(f"[Rubric] Initial tags: {tags_current}")

    iteration_logs: List[IterationLog] = []
    last_evaluations: List[TagEvaluation] = []

    for iteration in range(1, max_iterations + 1):
        tags_str = "\n".join(f"- {tag}" for tag in tags_current)
        print(f"[Rubric] Iteration {iteration} - Tags: {tags_str}")
        eval_prompt = tag_critic_eval_prompt.format(context=context, tags_str=tags_str)
        print(f"[Rubric] Iteration {iteration} - Prompt: {eval_prompt}")

        # Use structured output for evaluation
        structured_llm = llm.with_structured_output(TagEvaluationList)
        evaluations_response = structured_llm.invoke(eval_prompt)
        evaluations = evaluations_response.evaluations
        print(f"[Rubric] Iteration {iteration} - Evaluations: {evaluations}")
        last_evaluations = evaluations

        failing = [e for e in evaluations if e.score < threshold]
        passing = [e for e in evaluations if e.score >= threshold]
        print(f"[Rubric] Iteration {iteration} - Failing: {failing}")
        print(f"[Rubric] Iteration {iteration} - Passing: {passing}")

        iteration_logs.append(IterationLog(
            iteration=iteration,
            evaluations=evaluations,
            failing_count=len(failing),
            passing_count=len(passing)
        ))

        if not failing:
            print(f"[Rubric] Iteration {iteration} - All tags passed threshold.")
            break

        revise_prompt = tag_critic_revise_prompt.format(
            context=context,
            failing_tags="\n".join([f"{f.tag} (score: {f.score})" for f in failing])
        )
        print(f"[Rubric] Iteration {iteration} - Revise Prompt: {revise_prompt}")
        # Use structured output for revisions
        structured_llm_revise = llm.with_structured_output(RevisionModelList)
        revisions_response = structured_llm_revise.invoke(revise_prompt)
        revisions = revisions_response.revisions
        print(f"[Rubric] Iteration {iteration} - Revisions: {revisions}")

        rev_map: Dict[str, str] = {}
        for r in revisions:
            orig = r.original
            revised = r.revised or None
            if revised and revised.strip():
                if orig:
                    rev_map[orig.strip()] = revised.strip()
                else:
                    rev_map[f"_ins_{len(rev_map)}"] = revised.strip()
        print(f"[Rubric] Iteration {iteration} - Rev map: {rev_map}")

        new_tags = []
        for t in tags_current:
            if t in rev_map:
                new_tags.append(rev_map[t])
            else:
                new_tags.append(t)

        for k, v in rev_map.items():
            if k.startswith("_ins_"):
                new_tags.append(v)
        print(f"[Rubric] Iteration {iteration} - New tags: {new_tags}")

        normalized = []
        seen2 = set()
        for t in new_tags:
            if not t or not isinstance(t, str):
                continue
            norm = normalize_tag(t)
            if norm not in seen2:
                seen2.add(norm)
                normalized.append(t.strip())
        print(f"[Rubric] Iteration {iteration} - Normalized tags: {normalized}")

        tags_current = normalized

    final_tags = []
    if last_evaluations:
        # Filter passing tags, then sort by score (descending)
        passing = [e for e in last_evaluations if e.score >= threshold]
        sorted_passing = sorted(passing, key=lambda x: x.score, reverse=True)
        final_tags = [e.tag for e in sorted_passing[:10]]
    else:
        final_tags = tags_current[:10]

    # if last_evaluations:
    #     for e in last_evaluations:
    #         if e.score >= threshold:
    #             final_tags.append(e.tag)
    # else:
    #     final_tags = tags_current
    print(f"[Rubric] Final tags: {final_tags}")

    result_model = TagCriticResponse(
        original_tags=recommended_tags,
        final_tags=final_tags,
        threshold=threshold,
        iterations=len(iteration_logs),
        iteration_logs=iteration_logs,
        last_evaluations=last_evaluations,
        agent="tag_critic_agent"
    )
    print(f"[Rubric] Result model: {result_model}")
    return result_model
