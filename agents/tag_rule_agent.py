import re
from typing import List, Dict, Any, Tuple

def is_valid_tag(tag: str, seen: set) -> Tuple[bool, str]:
    if not (3 <= len(tag) <= 30):
        return False, "length"
    if not re.fullmatch(r"[a-z0-9\-]+", tag):
        return False, "invalid_chars"
    if tag in seen:
        return False, "duplicate"
    if tag in {"project", "app", "code"}:
        return False, "generic"
    if tag in {"awesome", "cool"}:
        return False, "subjective"
    if tag.strip() != tag:
        return False, "whitespace"
    if '--' in tag or tag.startswith('-') or tag.endswith('-'):
        return False, "bad_hyphen"
    return True, ""

def rule_based_tag_filter(tags: List[str]) -> Dict[str, Any]:
    filtered = []
    eliminated = []
    seen = set()
    for tag in tags:
        tag_norm = tag.lower().replace(' ', '-')
        valid, reason = is_valid_tag(tag_norm, seen)
        if valid:
            filtered.append(tag_norm)
            seen.add(tag_norm)
        else:
            eliminated.append({"tag": tag, "reason": reason})
    # Remove near-duplicates (edit distance 1 or 2)
    def is_near_duplicate(t, others):
        for o in others:
            if t == o:
                continue
            if abs(len(t) - len(o)) > 2:
                continue
            # Simple Levenshtein distance (max 2)
            d = sum(1 for a, b in zip(t, o) if a != b) + abs(len(t) - len(o))
            if d <= 2:
                return True
        return False
    final = []
    for tag in filtered:
        if is_near_duplicate(tag, final):
            eliminated.append({"tag": tag, "reason": "near_duplicate"})
        else:
            final.append(tag)
    if len(final) > 20:
        eliminated += [{"tag": t, "reason": "max_20"} for t in final[20:]]
        final = final[:20]
    return {
        "valid_tags": final,
        "eliminated": eliminated,
        "agent": "tag_rule_agent"
    }
