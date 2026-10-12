"""A weather agent. It publishes a tool schema to its model, then executes the
model's tool calls against the real tool."""
from agent.runtime import execute, scripted_model

WEATHER_TOOL = {
    "type": "function",
    "function": {
        "name": "get_weather",
        "description": "Current temperature for a city",
        "parameters": {
            "type": "object",
            "properties": {"location": {"type": "integer", "description": "City name"}},
            "required": ["location"],
        },
    },
}


def answer(question: str) -> str:
    call = scripted_model(question, [WEATHER_TOOL])
    result = execute(call)
    return f"It is {result['temp_c']}°C in {result['city']}"
