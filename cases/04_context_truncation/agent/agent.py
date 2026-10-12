from agent.runtime import CONTEXT_LIMIT, model

SYSTEM = {"role": "system", "content": "You are a support agent."}


class Chat:
    def __init__(self):
        self.messages = [SYSTEM]

    def ask(self, text: str) -> str:
        self.messages.append({"role": "user", "content": text})
        context = self.messages[:CONTEXT_LIMIT]
        reply = model(context)
        self.messages.append({"role": "assistant", "content": reply})
        return reply
