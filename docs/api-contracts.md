# API Contracts

## 1. POST /ingest
* **HTTP Method/Path:** `POST /ingest`
* **Request schema:** `{"file_url": "string", "metadata": "object"}`
* **Response schema:** `{"status": "string", "document_id": "string"}`
* **Error codes:** 400 (Invalid format), 500 (Processing failed)
* **Authentication:** Bearer Token
* **Rate limit:** 20 requests/minute

## 2. POST /query
* **HTTP Method/Path:** `POST /query`
* **Request schema:** `{"query": "string", "filters": "object"}`
* **Response schema:** `{"query_id": "string", "status": "string"}`
* **Error codes:** 400 (Invalid query), 429 (Too many requests)
* **Authentication:** Bearer Token
* **Rate limit:** 50 requests/minute

## 3. GET /query/{query_id}/stream
* **HTTP Method/Path:** `GET /query/{query_id}/stream`
* **Request schema:** None (Path parameter)
* **Response schema:** `{"chunk": "string", "is_final": "boolean"}` (Stream)
* **Error codes:** 404 (Query not found)
* **Authentication:** Bearer Token
* **Rate limit:** 50 requests/minute

## 4. GET /evaluations
* **HTTP Method/Path:** `GET /evaluations`
* **Request schema:** `{"page": "integer", "limit": "integer"}` (Query params)
* **Response schema:** `{"data": ["object"], "total": "integer"}`
* **Error codes:** 401 (Unauthorized)
* **Authentication:** Bearer Token
* **Rate limit:** 100 requests/minute

## 5. GET /evaluations/aggregate
* **HTTP Method/Path:** `GET /evaluations/aggregate`
* **Request schema:** `{"time_window": "string"}` (Query param)
* **Response schema:** `{"metrics": {"faithfulness": "number", "relevance": "number"}}`
* **Error codes:** 500 (Aggregation failed)
* **Authentication:** Bearer Token
* **Rate limit:** 100 requests/minute

## 6. POST /pipelines
* **HTTP Method/Path:** `POST /pipelines`
* **Request schema:** `{"name": "string", "config": "object"}`
* **Response schema:** `{"pipeline_id": "string", "status": "created"}`
* **Error codes:** 400 (Invalid config)
* **Authentication:** Bearer Token (Admin)
* **Rate limit:** 10 requests/minute

## 7. GET /pipelines/{id}/runs
* **HTTP Method/Path:** `GET /pipelines/{id}/runs`
* **Request schema:** None (Path parameter)
* **Response schema:** `{"runs": ["object"]}`
* **Error codes:** 404 (Pipeline not found)
* **Authentication:** Bearer Token (Admin)
* **Rate limit:** 50 requests/minute

## 8. POST /finetune/jobs
* **HTTP Method/Path:** `POST /finetune/jobs`
* **Request schema:** `{"model": "string", "dataset_query": "object"}`
* **Response schema:** `{"job_id": "string", "status": "queued"}`
* **Error codes:** 503 (Resources unavailable)
* **Authentication:** Bearer Token (Admin)
* **Rate limit:** 5 requests/minute

## 9. GET /finetune/jobs/{id}
* **HTTP Method/Path:** `GET /finetune/jobs/{id}`
* **Request schema:** None (Path parameter)
* **Response schema:** `{"job_id": "string", "status": "string", "metrics": "object"}`
* **Error codes:** 404 (Job not found)
* **Authentication:** Bearer Token (Admin)
* **Rate limit:** 50 requests/minute

## 10. GET /health & GET /metrics
* **HTTP Method/Path:** `GET /health` | `GET /metrics`
* **Request schema:** None
* **Response schema:** `{"status": "string", "uptime": "number"}`
* **Error codes:** 500 (Service down)
* **Authentication:** None
* **Rate limit:** Unlimited