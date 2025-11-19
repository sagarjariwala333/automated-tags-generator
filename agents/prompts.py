# Centralized prompt templates for all agents

# The `tag_critic_eval_prompt` variable in the Python code snippet is defining a prompt template for a
# tag quality evaluator agent. This prompt instructs the agent on how to evaluate a set of tags based
# on various criteria such as Relevance, Clarity, Quality, Specificity, Coverage, and Distinctiveness.
# The agent is required to provide scores for each tag in the specified percentage format with three
# digits after the decimal point and calculate an overall score as the average of individual scores.
# tag_critic_eval_prompt = (
#     "You are a tag quality evaluator. Given the context and a set of tags, evaluate each tag on "
#     "Relevance, Clarity, Quality, Specificity, Coverage, and Distinctiveness as numbers between 0.000 and 100.000 (percentage, 3 digits after decimal point), "
#     "and provide an overall score (0.000-100.000) as the average. "
#     "Output a JSON array of objects: "
#     "[{\"tag\":\"...\",\"relevance\":88.123,\"clarity\":90.111,\"quality\":85.000,\"specificity\":92.000,\"coverage\":80.000,\"distinctiveness\":95.000,\"score\":88.872}, ...]\n\n"
#     "Context:\n{context}\n\n"
#     "Tags:\n{tags_str}\n\n"
#     "Return only JSON. All scores must be in percentage (0.000-100.000) with exactly 3 digits after the decimal point."
# )
tag_critic_eval_prompt = (
    "You are a tag quality evaluator. Given the context and a set of tags, evaluate each tag on "
    "Relevance, Clarity, Quality, Specificity, Coverage, and Distinctiveness as numbers between 0.000 and 100.000 "
    "(percentage, 3 digits after decimal point), and provide an overall score (0.000-100.000) as the average. \n\n"
    "Output a JSON array of objects with exactly one object per tag: \n"
    "[\n"
    "  {\n"
    "    \"tag\": \"<tag_name>\",\n"
    "    \"relevance\": 0.000,\n"
    "    \"clarity\": 0.000,\n"
    "    \"quality\": 0.000,\n"
    "    \"specificity\": 0.000,\n"
    "    \"coverage\": 0.000,\n"
    "    \"distinctiveness\": 0.000,\n"
    "    \"score\": 0.000\n"
    "  }\n"
    "]\n\n"
    "Instructions:\n"
    "- Include **one object per tag provided**, do not add extra tags.\n"
    "- All numbers must be in percentage format with exactly 3 digits after the decimal.\n"
    "- Return **only JSON**, nothing else.\n\n"
    "Context:\n{context}\n\n"
    "Tags (comma-separated):\n{tags_str}"
)


tag_critic_revise_prompt = (
    "You are a tag improvement assistant. Given the failing tags and critiques, propose improved versions "
    "that address relevance, clarity, quality, specificity, coverage, and distinctiveness. "
    "Return JSON array with objects "
    "[{\"original\":\"...\",\"revised\":\"...\",\"reason\":\"...\"}, ...].\n\n"
    "Context:\n{context}\n\n"
    "Failing tags and their current evaluations:\n{failing_tags}\n\n"
    "Only return JSON."
)

tag_candidate_prompt = (
    "You are a Tag Candidate Generator Agent. Based on the provided metadata and content, generate relevant tags.\n\n"
    "Metadata:\n{metadata}\n\n"
    "Content Preview:\n{content_preview}\n\n"
    "Generate 15-20 candidate tags that:\n"
    "1. Represent the main topics and technologies\n"
    "2. Include programming languages, frameworks, and tools\n"
    "3. Cover use cases and application domains\n"
    "4. Are specific and relevant\n"
    "5. Follow standard tagging conventions (lowercase, hyphenated)\n\n"
    "Return ONLY a JSON object with this structure:\n"
    "{{\n  'primary_tags': [...],\n  'technology_tags': [...],\n  'domain_tags': [...],\n  'feature_tags': [...],\n  'all_candidates': [...]\n}}"
)

metadata_extractor_prompt = (
    "You are a Metadata Extractor Agent. Analyze the following content and extract structured metadata.\n\n"
    "Content: {content}\n\n"
    "Extract and return the following metadata in JSON format:\n"
    "- title: Main title or topic\n"
    "- keywords: List of 5-10 relevant keywords\n"
    "- category: Primary category (e.g., Technology, Business, Science, etc.)\n"
    "- summary: Brief 2-3 sentence summary\n"
    "- entities: List of important entities (people, organizations, locations)\n"
    "- sentiment: Overall sentiment (positive, negative, neutral)\n"
    "- language: Detected language\n"
    "- word_count: Approximate word count\n\n"
    "Return ONLY valid JSON, no additional text."
)

tag_polisher_prompt = (
    "Polish these tags: {tags}\nCritique: {critique}\n\nReturn JSON: {{'polished_tags': [...]}}"
)

multi_agent_system_prompt = (
    "You are a multi-agent AI system with specialized roles. Process this task through all agents:\n\n"
    "Task: {task}\n\n"
    "Execute the following agents in sequence and provide their outputs:\n\n"
    "1. **Research Agent**: Gather and analyze key information about the task\n"
    "2. **Writer Agent**: Create well-structured, clear content based on the research\n"
    "3. **Reviewer Agent**: Review the content and provide final improvements\n\n"
    "Format your response as:\n\n"
    "=== RESEARCH AGENT ===\n[Your research findings here]\n\n"
    "=== WRITER AGENT ===\n[Your written content here]\n\n"
    "=== REVIEWER AGENT ===\n[Your review and final version here]\n\n"
    "Begin processing now."
)
