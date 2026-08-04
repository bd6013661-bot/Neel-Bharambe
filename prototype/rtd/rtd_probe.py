import itertools, sys, time
from pysat.formula import IDPool
from pysat.solvers import Cadical153

def search(n, m, vcd, tdmin, timeout_note=""):
    """Exists a concept class D of m distinct concepts on n points with
       VCdim(D) <= vcd  and  TDmin(D) >= tdmin ?"""
    pool = IDPool()
    X = lambda r, i: pool.id(('x', r, i))
    cls = []

    # --- rows strictly increasing lexicographically (breaks row symmetry + distinctness)
    # use standard lex-less encoding with equality prefix vars
    for r in range(m - 1):
        E = lambda i: pool.id(('e', r, i))   # prefix equality up to i-1
        cls.append([E(0)])
        for i in range(n):
            # if prefix equal, then x[r][i] <= x[r+1][i]
            cls.append([-E(i), -X(r, i), X(r + 1, i)])
            if i + 1 <= n - 1:
                # E(i+1) <-> E(i) & (x[r][i] == x[r+1][i])   (only need ->)
                cls.append([-E(i + 1), E(i)])
                cls.append([-E(i + 1), -X(r, i), X(r + 1, i)])
                cls.append([-E(i + 1), X(r, i), -X(r + 1, i)])
                cls.append([E(i + 1), -E(i), X(r, i), X(r + 1, i)])
                cls.append([E(i + 1), -E(i), -X(r, i), -X(r + 1, i)])
        # strict: not all equal
        cls.append([-E(n - 1), -X(r, n - 1), -X(r + 1, n - 1)])
        cls.append([-E(n - 1), X(r, n - 1), X(r + 1, n - 1)])

    # --- VC dim <= vcd : no (vcd+1)-subset is shattered
    k = vcd + 1
    for S in itertools.combinations(range(n), k):
        missvars = []
        for p in itertools.product([0, 1], repeat=k):
            mv = pool.id(('miss', S, p))
            missvars.append(mv)
            for r in range(m):
                # miss -> row r does not match p on S
                cl = [-mv]
                for i, b in zip(S, p):
                    cl.append(-X(r, i) if b else X(r, i))
                cls.append(cl)
        cls.append(missvars)

    # --- TDmin >= tdmin : for every row r and every (tdmin-1)-subset T,
    #     some other row agrees with r on T
    t = tdmin - 1
    for r in range(m):
        for T in itertools.combinations(range(n), t):
            ag = []
            for r2 in range(m):
                if r2 == r:
                    continue
                a = pool.id(('a', r, r2, T))
                ag.append(a)
                for i in T:
                    cls.append([-a, -X(r, i), X(r2, i)])
                    cls.append([-a, X(r, i), -X(r2, i)])
            cls.append(ag)

    t0 = time.time()
    with Cadical153(bootstrap_with=cls) as s:
        sat = s.solve()
        el = time.time() - t0
        if sat:
            mod = set(l for l in s.get_model() if l > 0)
            rows = [''.join('1' if X(r, i) in mod else '0' for i in range(n)) for r in range(m)]
            return True, el, rows, len(cls)
        return False, el, None, len(cls)

if __name__ == '__main__':
    print("=== sanity: VCD<=2, TDmin>=3 (known ratio 3/2 regime) ===")
    for n in range(4, 9):
        maxm = 1 + n + n * (n - 1) // 2
        found = None
        for m in range(4, maxm + 1):
            sat, el, rows, nc = search(n, m, 2, 3)
            if sat:
                found = (m, rows, el, nc)
                break
        if found:
            print(f"n={n}: smallest m with VCD<=2,TDmin>=3 is {found[0]}  ({found[2]:.2f}s, {found[3]} clauses)")
            for row in found[1]:
                print("   ", row)
            break
        else:
            print(f"n={n}: none up to m={maxm}")
