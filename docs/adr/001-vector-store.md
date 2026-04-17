# ADR 001: Vector Store Selection

**Context:** We need a vector database to store embeddings and perform similarity searches. We evaluated Pinecone, Weaviate, Qdrant, and pgvector.

**Decision:** We selected pgvector (PostgreSQL extension).

**Consequences:** Using pgvector allows us to keep relational metadata and vector embeddings in the same database, simplifying our architecture and ensuring transactional consistency, avoiding the complexity of syncing data between Postgres and a separate standalone vector database like Pinecone or Qdrant.