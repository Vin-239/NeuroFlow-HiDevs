import time
from typing import List, AsyncGenerator
from anthropic import AsyncAnthropic, RateLimitError
from config import settings
from .base import BaseLLMProvider, ChatMessage, GenerationResult
import asyncio

PRICING = {
    "claude-3-haiku-20240307": {"input": 0.25, "output": 1.25},
    "claude-3-5-sonnet-20240620": {"input": 3.00, "output": 15.00}
}

class AnthropicProvider(BaseLLMProvider):
    def __init__(self, model: str = "claude-3-haiku-20240307"):
        self.model = model
        self.client = AsyncAnthropic(api_key=settings.LLM_API_KEY)
        self.max_retries = 3

    @property
    def cost_per_input_token(self) -> float:
        return PRICING.get(self.model, PRICING["claude-3-haiku-20240307"])["input"] / 1_000_000

    @property
    def cost_per_output_token(self) -> float:
        return PRICING.get(self.model, PRICING["claude-3-haiku-20240307"])["output"] / 1_000_000

    @property
    def context_window(self) -> int:
        return 200000

    def _extract_system(self, messages: List[ChatMessage]) -> tuple[str, List[dict]]:
        system_prompt = ""
        formatted_msgs = []
        for m in messages:
            if m.role == "system":
                system_prompt += m.content + "\n"
            else:
                formatted_msgs.append({"role": m.role, "content": m.content})
        return system_prompt.strip(), formatted_msgs

    async def _execute_with_retry(self, coro):
        for attempt in range(self.max_retries):
            try:
                return await coro
            except RateLimitError as e:
                if attempt == self.max_retries - 1:
                    raise e
                await asyncio.sleep(2 ** (attempt + 1))

    async def complete(self, messages: List[ChatMessage], **kwargs) -> GenerationResult:
        start_time = time.time()
        system_prompt, formatted_msgs = self._extract_system(messages)
        
        response = await self._execute_with_retry(
            self.client.messages.create(
                model=self.model,
                system=system_prompt,
                messages=formatted_msgs,
                max_tokens=kwargs.get("max_tokens", 1024),
                **{k:v for k,v in kwargs.items() if k != "max_tokens"}
            )
        )
        
        latency = (time.time() - start_time) * 1000
        in_tokens = response.usage.input_tokens
        out_tokens = response.usage.output_tokens
        cost = (in_tokens * self.cost_per_input_token) + (out_tokens * self.cost_per_output_token)

        return GenerationResult(
            content=response.content[0].text,
            model=self.model,
            input_tokens=in_tokens,
            output_tokens=out_tokens,
            latency_ms=latency,
            cost_usd=cost,
            finish_reason=response.stop_reason
        )

    async def stream(self, messages: List[ChatMessage], **kwargs) -> AsyncGenerator[str, None]:
        system_prompt, formatted_msgs = self._extract_system(messages)
        stream = await self._execute_with_retry(
            self.client.messages.create(
                model=self.model,
                system=system_prompt,
                messages=formatted_msgs,
                max_tokens=kwargs.get("max_tokens", 1024),
                stream=True,
                **{k:v for k,v in kwargs.items() if k != "max_tokens"}
            )
        )
        async for event in stream:
            if event.type == "content_block_delta" and hasattr(event.delta, "text"):
                yield event.delta.text

    async def embed(self, texts: List[str]) -> List[List[float]]:
        raise NotImplementedError("Anthropic does not provide native embeddings. Use OpenAI provider.")