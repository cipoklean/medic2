import sys

from agent.agent import answer

EXPECTED = {"What's the weather in Lagos?": "It is 31°C in Lagos",
            "What's the weather in Kano?": "It is 34°C in Kano"}
fails = 0
for q, want in EXPECTED.items():
    try:
        got = answer(q)
    except Exception as e:
        print(f"FAIL {q!r}: {type(e).__name__}: {e}"); fails += 1; continue
    print(("PASS" if got == want else f"FAIL got {got!r} want {want!r}"), q)
    fails += got != want
sys.exit(1 if fails else 0)
