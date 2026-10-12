"""Scripted model + tools. The model follows the protocol in PROTOCOL exactly."""
PROTOCOL = 'Each step returns {"action": "search"|"final_answer", "input": str}.'
MAX_STEPS = 12


class StepBudgetExceeded(RuntimeError):
    pass


def model_step(question: str, history: list) -> dict:
    if len(history) >= MAX_STEPS:
        raise StepBudgetExceeded(f"agent took {len(history)} steps without finishing")
    if not history:
        return {"action": "search", "input": question}
    return {"action": "final_answer", "input": f"Answer: {history[-1]['observation']}"}


def search(q: str) -> str:
    return {"capital of Nigeria": "Abuja", "capital of Ghana": "Accra"}[q]
