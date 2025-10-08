#!/usr/bin/env python3
"""Test script for Phase 2 AI providers: DeepSeek, Ollama, Gemini, LM Studio"""

import asyncio
import os
from app.providers.deepseek_provider import DeepSeekProvider
from app.providers.ollama_provider import OllamaProvider
from app.providers.gemini_provider import GeminiProvider
from app.providers.lm_studio_provider import LMStudioProvider

async def test_gemini():
    api_key = os.getenv("GOOGLE_AI_API_KEY", "")
    if not api_key:
        print("⚠️  GOOGLE_AI_API_KEY not set - skipping Gemini test")
        return

    provider = GeminiProvider(api_key)

    try:
        print("🔍 Testing Gemini health check...")
        health = await provider.health_check()
        print(f"   Health: {'✅ OK' if health else '❌ FAIL'}")

        if health:
            print("🎤 Testing Gemini chat...")
            from app.providers.base import ChatMessage
            messages = [ChatMessage(role="user", content="Hello, say hi in exactly 4 words")]
            response = ""
            async for chunk in provider.chat(messages, stream=True):
                response += chunk
                print(f"   Response chunk: {chunk!r}")
            print(f"   Full response: {response}")

    except Exception as e:
        print(f"❌ Gemini test failed: {e}")

async def test_lm_studio():
    base_url = os.getenv("LM_STUDIO_URL", "http://localhost:1234")
    provider = LMStudioProvider(base_url)

    try:
        print("🔍 Testing LM Studio health check...")
        health = await provider.health_check()
        print(f"   Health: {'✅ OK' if health else '❌ FAIL (ensure LM Studio server is running)'}")

        if health:
            print("🎤 Testing LM Studio chat...")
            from app.providers.base import ChatMessage
            messages = [ChatMessage(role="user", content="Respond with exactly one word")]
            response = ""
            async for chunk in provider.chat(messages, stream=True):
                response += chunk
                print(f"   Response chunk: {chunk!r}")
            print(f"   Full response: {response}")

    except Exception as e:
        print(f"❌ LM Studio test failed: {e}")

async def test_deepseek():
    api_key = os.getenv("DEEPSEEK_API_KEY", "")
    if not api_key:
        print("⚠️  DEEPSEEK_API_KEY not set - skipping DeepSeek test")
        return

    provider = DeepSeekProvider(api_key)

    try:
        print("🔍 Testing DeepSeek health check...")
        health = await provider.health_check()
        print(f"   Health: {'✅ OK' if health else '❌ FAIL'}")

        if health:
            print("🎤 Testing DeepSeek chat...")
            from app.providers.base import ChatMessage
            messages = [ChatMessage(role="user", content="Say hello in exactly 5 words")]
            response = ""
            async for chunk in provider.chat(messages, stream=True):
                response += chunk
                print(f"   Response chunk: {chunk!r}")
            print(f"   Full response: {response}")

    except Exception as e:
        print(f"❌ DeepSeek test failed: {e}")

async def test_ollama():
    base_url = os.getenv("OLLAMA_URL", "http://localhost:11434")
    provider = OllamaProvider(base_url)

    try:
        print("🔍 Testing Ollama health check...")
        health = await provider.health_check()
        print(f"   Health: {'✅ OK' if health else '❌ FAIL (ensure Ollama is running)'}")

        if health:
            print("🎤 Testing Ollama chat...")
            from app.providers.base import ChatMessage
            messages = [ChatMessage(role="user", content="Say hello in exactly 3 words")]
            response = ""
            async for chunk in provider.chat(messages, stream=True):
                response += chunk
                print(f"   Response chunk: {chunk!r}")
            print(f"   Full response: {response}")

    except Exception as e:
        print(f"❌ Ollama test failed: {e}")

async def main():
    print("🚀 Testing All Phase 2 Provider Implementations\n")

    await test_gemini()
    print()
    await test_lm_studio()
    print()
    await test_deepseek()
    print()
    await test_ollama()

    print("\n✅ All provider tests complete!")

if __name__ == "__main__":
    asyncio.run(main())