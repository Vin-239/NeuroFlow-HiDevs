import redis.asyncio as aioredis
from opentelemetry import trace
from config import settings
from .base import ChatMessage, GenerationResult
from .openai_provider import OpenAIProvider
from .anthropic_provider import AnthropicProvider
from .router import ModelRouter, RoutingCriteria

tracer = trace.get_tracer(__name__)

class NeuroFlowClient:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(NeuroFlowClient, cls).__new__(cls)
            cls._instance.router = ModelRouter()
            cls._instance.redis = aioredis.from_url(f"redis://:{settings.REDIS_PASSWORD}@{settings.REDIS_HOST}:{settings.REDIS_PORT}/0")
        return cls._instance

    def _get_provider(self, model_name: str):
        if "gpt" in model_name:
            return OpenAIProvider(model=model_name)
        elif "claude" in model_name:
            return AnthropicProvider(model=model_name)
        return OpenAIProvider() # Default fallback

    async def _track_metrics(self, result: GenerationResult):
        pipe = self.redis.pipeline()
        pipe.incr(f"metrics:model:{result.model}:calls")
        pipe.incrbyfloat(f"metrics:model:{result.model}:cost_usd", result.cost_usd)
        await pipe.execute()

    async def chat(self, messages: list[ChatMessage], criteria: RoutingCriteria) -> GenerationResult:
        model_name = await self.router.select_model(criteria)
        
        # FallbackChain implementation
        fallback_chain = [model_name]
        if "gpt" in model_name: fallback_chain.append("claude-3-haiku-20240307")
        else: fallback_chain.append("gpt-4o-mini")

        for attempt_model in fallback_chain:
            try:
                provider = self._get_provider(attempt_model)
                with tracer.start_as_current_span("llm_generation") as span:
                    result = await provider.complete(messages)
                    
                    span.set_attribute("model", attempt_model)
                    span.set_attribute("input_tokens", result.input_tokens)
                    span.set_attribute("output_tokens", result.output_tokens)
                    span.set_attribute("cost_usd", result.cost_usd)
                    span.set_attribute("latency_ms", result.latency_ms)
                    
                    await self._track_metrics(result)
                    return result
            except Exception as e:
                if attempt_model == fallback_chain[-1]:
                    raise e # Last resort failed

    async def embed(self, texts: list[str]) -> list[list[float]]:
        # Always route embeddings to OpenAI for this setup
        provider = OpenAIProvider()
        with tracer.start_as_current_span("llm_embedding") as span:
            return await provider.embed(texts)