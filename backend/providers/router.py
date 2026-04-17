import json
import redis.asyncio as aioredis
from typing import Optional, List, Dict
from dataclasses import dataclass
from config import settings

@dataclass
class RoutingCriteria:
    task_type: str
    max_cost_per_call: Optional[float] = None
    require_vision: bool = False
    require_long_context: bool = False
    latency_budget_ms: Optional[int] = None
    prefer_fine_tuned: bool = False

class ModelRouter:
    def __init__(self):
        self.redis = aioredis.from_url(f"redis://:{settings.REDIS_PASSWORD}@{settings.REDIS_HOST}:{settings.REDIS_PORT}/0")
        # Fallback if Redis is empty
        self.default_models = [
            {"name": "gpt-4o", "provider": "openai", "vision": True, "context": 128000, "input_cost": 2.50, "fine_tuned_for": []},
            {"name": "gpt-4o-mini", "provider": "openai", "vision": True, "context": 128000, "input_cost": 0.15, "fine_tuned_for": ["classification"]},
            {"name": "claude-3-haiku-20240307", "provider": "anthropic", "vision": True, "context": 200000, "input_cost": 0.25, "fine_tuned_for": []}
        ]

    async def _get_available_models(self) -> List[Dict]:
        try:
            data = await self.redis.get("router:models")
            if data:
                return json.loads(data)
            return self.default_models
        except Exception:
            return self.default_models

    async def select_model(self, criteria: RoutingCriteria, estimated_tokens: int = 1000) -> str:
        models = await self._get_available_models()
        valid_models = []

        for m in models:
            if criteria.require_vision and not m.get("vision", False):
                continue
            if criteria.require_long_context and m.get("context", 0) <= 100000:
                continue
            if criteria.task_type == "evaluation" and "fine_tuned_for" in m and m["fine_tuned_for"]:
                # Evaluations must use base capable models, not fine-tuned
                if m.get("input_cost", 0) < 1.0: # simplistic proxy for "capable judge"
                    continue 
                
            if criteria.max_cost_per_call:
                est_cost = (estimated_tokens / 1_000_000) * m.get("input_cost", 100)
                if est_cost > criteria.max_cost_per_call:
                    continue
                    
            valid_models.append(m)

        if not valid_models:
            return "gpt-4o-mini" # Ultimate fallback

        # Fine-tuned preference override
        if criteria.prefer_fine_tuned and criteria.task_type != "evaluation":
            fine_tuned = [m for m in valid_models if criteria.task_type in m.get("fine_tuned_for", [])]
            if fine_tuned:
                return fine_tuned[0]["name"]

        # Default: Sort by input_cost ascending (Cheapest first)
        valid_models.sort(key=lambda x: x.get("input_cost", 999))
        return valid_models[0]["name"]