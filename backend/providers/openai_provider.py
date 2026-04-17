import time
import asyncio
from typing import List, AsyncGenerator
from openai import AsyncOpenAI, RateLimitError
from config import settings
from .base import BaseLLMProvider, ChatMessage, GenerationResult

PRICING = {
    "gpt-4o": {"input": 2.50, "output": 10.00},
    "gpt-4o-mini": {"input": 0.15, "output": 0.60},
    "text-embedding-3-small": {"input": 0.02, "output": 0.0}
}

class OpenAIProvider(BaseLLMProvider):
    def __init__(self, model: str = "gpt-4o-mini"):
        self.model = model
        self.client = AsyncOpenAI(api_key=settings.LLM_API_KEY)
        self.max_retries = 3

    @property
    def cost_per_input_token(self) -> float:
        return PRICING.get(self.model, PRICING["gpt-4o-mini"])["input"] / 1_000_000

    @property
    def cost_per_output_token(self) -> float:
        return PRICING.get(self.model, PRICING["gpt-4o-mini"])["output"] / 1_000_000

    @property
    def context_window(self) -> int:
        return 128000

    async def _execute_with_retry(self, coro):
        for attempt in range(self.max_retries):
            try:
                return await coro
            except RateLimitError as e:
                if attempt == self.max_retries - 1:
                    raise e
                # Exponential backoff: 2, 4, 8 seconds
                wait_time = 2 ** (attempt + 1)
                await asyncio.sleep(wait_time)

    def _format_messages(self, messages: List[ChatMessage]) -> List[dict]:
        return [{"role": m.role, "content": m.content} for m in messages]

    async def complete(self, messages: List[ChatMessage], **kwargs) -> GenerationResult:
        start_time = time.time()
        formatted_msgs = self._format_messages(messages)
        
        response = await self._execute_with_retry(
            self.client.chat.completions.create(
                model=self.model,
                messages=formatted_msgs,
                **kwargs
            )
        )
        
        latency = (time.time() - start_time) * 1000
        in_tokens = response.usage.prompt_tokens
        out_tokens = response.usage.completion_tokens
        cost = (in_tokens * self.cost_per_input_token) + (out_tokens * self.cost_per_output_token)

        return GenerationResult(
            content=response.choices[0].message.content,
            model=self.model,
            input_tokens=in_tokens,
            output_tokens=out_tokens,
            latency_ms=latency,
            cost_usd=cost,
            finish_reason=response.choices[0].finish_reason
        )

    async def stream(self, messages: List[ChatMessage], **kwargs) -> AsyncGenerator[str, None]:
        formatted_msgs = self._format_messages(messages)
        stream = await self._execute_with_retry(
            self.client.chat.completions.create(
                model=self.model,
                messages=formatted_msgs,
                stream=True,
                **kwargs
            )
        )
        async for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

    async def embed(self, texts: List[str]) -> List[List[float]]:
        # Process in batches of 100
        embeddings = []
        batch_size = 100
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            response = await self._execute_with_retry(
                self.client.embeddings.create(
                    input=batch,
                    model="text-embedding-3-small"
                )
            )
            embeddings.extend([data.embedding for data in response.data])
        return embeddings