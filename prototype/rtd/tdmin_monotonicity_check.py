"""Verify the claim: removing a concept can RAISE TDmin.

TD(c; C) = min |T| such that no other c' in C agrees with c on all of T.
TDmin(C)  = min over c in C of TD(c; C).
"""
from itertools import combinations

def TD(c, C, n):
    others = [d for d in C if d != c]
    for size in range(0, n + 1):
        for T in combinations(range(n), size):
            if not any(all(d[i] == c[i] for i in T) for d in others):
                return size
    return None

def TDmin(C, n):
    return min(TD(c, C, n) for c in C)

n = 3
C  = ['000', '100', '010', '110', '001']
Cp = ['000', '100', '010', '110']          # C with 001 deleted

print("C  =", C)
for c in C:  print(f"   TD({c}) = {TD(c, C, n)}")
print("TDmin(C)  =", TDmin(C, n))
print()
print("C' = C \\ {001} =", Cp)
for c in Cp: print(f"   TD({c}) = {TD(c, Cp, n)}")
print("TDmin(C') =", TDmin(Cp, n))
print()
print("REMOVING A CONCEPT RAISED TDmin:", TDmin(Cp, n) > TDmin(C, n))

# And the other direction: does adding concepts ever raise TDmin from 0-ish to high?
# Exhaustive: over all classes on 3 points, find max |TDmin(C') - TDmin(C)| for C' = C minus one.
best_up = best_down = 0
allc = [format(i, '03b') for i in range(8)]
for size in range(2, 9):
    for C in combinations(allc, size):
        C = list(C)
        t = TDmin(C, n)
        for c in C:
            Cp = [d for d in C if d != c]
            if len(Cp) < 2: continue
            tp = TDmin(Cp, n)
            best_up = max(best_up, tp - t)
            best_down = max(best_down, t - tp)
print(f"\nover all classes on 3 points, removing one concept:")
print(f"  max increase in TDmin = {best_up}")
print(f"  max decrease in TDmin = {best_down}")
print("  -> non-monotone in BOTH directions:", best_up > 0 and best_down > 0)
