"""
mem0_quickstart.py
A 30-second smoke-test using Mem0 OSS.

Docs reference:
  https://docs.mem0.ai/open-source/python-quickstart
"""

import asyncio
from mem0 import Memory        # sync version is fine for a quick demo

async def main() -> None:
    # 1. instantiate
    m = Memory()   # works entirely in-process, zero external deps

    # 2. add a memory for a user
    m.add(
        "I like to drink coffee in the morning and go for a walk.",
        user_id="alice"
    )
    print("[+] Added memory for alice")

    # 3. retrieve it back semantically
    related = m.search(
        "Should I drink coffee or tea?",
        user_id="alice"
    )
    print("\n[+] Search results:")
    for row in related["results"]:
        print(" •", row["memory"])

if __name__ == "__main__":
    asyncio.run(main())
