from abc import ABC, abstractmethod
from typing import AsyncGenerator, Union, List
from dataclasses import dataclass

@dataclass
class ChatMessage:
    role: str  # "system" | "user" | "assistant"
    content: Union[str, list]  # str for text, list for multi-modal

@dataclass
class GenerationResult:
    content: str
    model: str
    input_tokens: int
    output_tokens: int
    latency_ms: float
    cost_usd: float
    finish_reason: str

class BaseLLMProvider(ABC):
    @abstractmethod
    async def complete(self, messages: List[ChatMessage], **kwargs) -> GenerationResult: ...
    
    @abstractmethod
    async def stream(self, messages: List[ChatMessage], **kwargs) -> AsyncGenerator[str, None]: ...
    
    @abstractmethod
    async def embed(self, texts: List[str]) -> List[List[float]]: ...
    
    @property
    @abstractmethod
    def cost_per_input_token(self) -> float: ...
    
    @property
    @abstractmethod
    def cost_per_output_token(self) -> float: ...
    
    @property
    @abstractmethod
    def context_window(self) -> int: ...