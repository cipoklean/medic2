"""Runs a pydantic-ai agent under a token budget and reports what it spent."""
from pydantic_ai import Agent
from pydantic_ai.models.test import TestModel
from pydantic_ai.usage import UsageLimits

agent = Agent(TestModel(), system_prompt="be brief")


def run_with_budget(prompt: str) -> dict:
    result = agent.run_sync(prompt, usage_limits=UsageLimits(request_tokens_limit=1000))
    usage = result.usage()
    return {"output": result.output, "prompt_tokens": usage.request_tokens,
            "completion_tokens": usage.response_tokens}
