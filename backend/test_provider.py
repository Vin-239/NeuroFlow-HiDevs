import asyncio
import os
import sys

# Add backend to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from providers.base import ChatMessage
from providers.openai_provider import OpenAIProvider
from providers.anthropic_provider import AnthropicProvider

async def main():
    print("--- Testing OpenAI ---")
    openai_prov = OpenAIProvider()
    print("Testing Embedding...")
    emb = await openai_prov.embed(["hello world"])
    print(f"Embedding generated: length {len(emb[0])}")
    
    print("Testing Stream...")
    msgs = [ChatMessage(role="user", content="Say exactly one word: Hello")]
    async for token in openai_prov.stream(msgs):
        print(token, end="", flush=True)
    print("\n")

    # Note: Anthropic needs an API key to work. Ensure it is in your .env if testing.
    # print("--- Testing Anthropic ---")
    # anthropic_prov = AnthropicProvider()
    # async for token in anthropic_prov.stream(msgs):
    #     print(token, end="", flush=True)

if __name__ == "__main__":
    asyncio.run(main())