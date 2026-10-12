from agent.runtime import make_client

client = make_client()


def summarize(text: str) -> str:
    msg = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=200,
        temperature=0.2,
        messages=[{"role": "user", "content": text}],
    )
    return msg.content[0].text
