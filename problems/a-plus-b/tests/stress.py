import json
import random

rng = random.Random(20260930)
values = [-10**18, -10**18 + 1, -2**31, -1, 0, 1, 2**31 - 1, 10**18 - 1, 10**18]
cases = [f"{a} {b}\n" for a in values for b in values]
cases += [f"{rng.randint(-10**18, 10**18)} {rng.randint(-10**18, 10**18)}\n" for _ in range(50)]
print(json.dumps(cases))
