# ADR 003: Evaluation Framework

**Context:** We must evaluate generations for faithfulness, relevance, precision, and recall. Human annotation is too slow for every query.

**Decision:** We will use an automated LLM-as-judge evaluation framework instead of human-only annotation.

**Consequences:** This allows for asynchronous, scalable scoring of every generation. Failure modes include the judge LLM being biased or hallucinating scores. We will detect these failures by maintaining a small, static "golden dataset" of human-annotated pairs and periodically testing the LLM-as-judge against it to measure alignment drift.