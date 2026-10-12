from agent.runtime import model_step, search


def run(question: str) -> str:
    history = []
    while True:
        step = model_step(question, history)
        if step["action"] == "finish":
            return step["input"]
        observation = search(step["input"]) if step["action"] == "search" else ""
        history.append({"step": step, "observation": observation or history[-1]["observation"]})
