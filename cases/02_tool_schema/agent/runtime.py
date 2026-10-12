"""Deterministic stand-ins for the model and the tool. The 'model' fills arguments
exactly as the schema declares them, like a strict function-calling model would."""

_TEMPS = {"Lagos": 31, "Abuja": 29, "Kano": 34}


def scripted_model(question: str, tools: list) -> dict:
    fn = tools[0]["function"]
    city = question.rsplit(" in ", 1)[-1].rstrip("?")
    args = {}
    for name, spec in fn["parameters"]["properties"].items():
        if spec["type"] == "string":
            args[name] = city
        elif spec["type"] == "integer":
            args[name] = len(city)  # a strict model coerces to the declared type
    return {"name": fn["name"], "arguments": args}


def get_weather(city: str) -> dict:
    if not isinstance(city, str):
        raise TypeError(f"city must be str, got {type(city).__name__}")
    return {"city": city, "temp_c": _TEMPS[city]}


def execute(call: dict) -> dict:
    if call["name"] != "get_weather":
        raise ValueError(f"unknown tool {call['name']}")
    return get_weather(**call["arguments"])
