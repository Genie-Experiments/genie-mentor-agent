# local_persist_check.py
#
# 1.  python local_persist_check.py --add
# 2.  close the terminal, reopen, run python local_persist_check.py
#     → should print Found!

import sys, uuid
from mem0 import Memory

mem  = Memory()
USER = "demo_local"
TAG  = f"persist-{uuid.uuid4().hex[:6]}"
TEXT = f"Persistence test {TAG}"

if "--add" in sys.argv:
    mem.add(TEXT, user_id=USER)
    print("[+] Added:", TEXT)
else:
    hits = mem.search(TAG, user_id=USER)
    print("Found!" if hits else "Not found", hits)
