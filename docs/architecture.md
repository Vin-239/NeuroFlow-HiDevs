# NeuroFlow Architecture

## 1. Ingestion Subsystem
Accepts raw files (PDF, DOCX, images, CSV, web URLs), extracts content per modality, chunks, embeds, and writes to the vector store.

**Data Flow:**
File Upload / URL -> Modality Extraction (Text/Vision/Parser) -> Chunking -> Embedding -> Vector Store

## 2. Retrieval Subsystem
Given a user query, runs embedding similarity search, keyword search, and metadata filtering in parallel, fuses results via Reciprocal Rank Fusion, passes through a cross-encoder reranker, and returns a ranked context window.

**Data Flow:**
User Query -> Parallel Search (Embedding + Keyword + Metadata) -> Reciprocal Rank Fusion (RRF) -> Cross-Encoder Reranker -> Ranked Context Window

## 3. Generation Subsystem
Assembles the context window into a prompt, routes to the appropriate LLM (by cost tier, capability, or domain), streams the response token by token, and logs the complete input/output pair for evaluation.

## 4. Evaluation Subsystem
Asynchronously scores every generation on: faithfulness (are claims grounded in retrieved context?), answer relevance (does it address the question?), context precision (are retrieved chunks actually used?), context recall (were relevant chunks retrieved?). Stores scores in Postgres and computes rolling aggregates.

## 5. Fine-Tuning Subsystem
Extracts high-quality prompt/completion pairs from the evaluation log (where faithfulness > 0.8 AND user rating >= 4), formats them as JSONL training data, submits fine-tuning jobs, tracks experiments in MLflow, and routes future similar queries to the fine-tuned model when it outperforms the base model.