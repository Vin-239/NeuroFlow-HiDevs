# ADR 002: Chunking Strategy

**Context:** Raw text must be chunked before embedding. Options include fixed-size chunking, sentence-boundary chunking, and semantic chunking.

**Decision:** We will use semantic chunking by default, with a fallback to fixed-size chunking.

**Consequences:** Semantic chunking respects topic boundaries, leading to better context retrieval. We will switch to fixed-size chunking (e.g., 500 tokens with 50 token overlap) only under conditions where processing speed must be strictly prioritized over context quality, or if the semantic chunker fails on abnormally formatted text.