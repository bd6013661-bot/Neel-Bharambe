"""Adversarial tests for the proof checker.

A checker that accepts every proof its own generator produces has demonstrated
nothing.  The tests that matter are the ones below, which take a valid proof and
corrupt it in each of the ways a broken — or dishonest — search would, then
insist the checker notices.

The corruptions mirror real failure modes:

* ``skip a subtree``           -- the classic bug in a hand-rolled search: an
                                  extension is silently never explored.
* ``bogus permutation``        -- a canonicity witness that does not shrink the code.
* ``non-permutation``          -- a witness that is not a bijection at all.
* ``prune a legal extension``  -- claiming a graph violates the property when it does not.
* ``truncated proof``          -- the search died halfway and the tail is missing.
* ``inflated tallies``         -- the summary line disagrees with the body.
* ``wrong claim``              -- the header claims a stronger result than the body supports.
"""

import io
import re

import pytest

from orbitcert import RamseyProperty, TriangleFree, check_stream, enumerate_graphs
from orbitcert.proof import ProofSyntaxError, parse_string


def make_proof(prop, order):
    buf = io.StringIO()
    result = enumerate_graphs(prop, order, proof=buf, collect=True)
    return buf.getvalue(), result


@pytest.fixture(scope="module")
def r33():
    return make_proof(RamseyProperty(3, 3), 6)


@pytest.fixture(scope="module")
def r34():
    return make_proof(RamseyProperty(3, 4), 9)


def test_valid_proof_is_accepted(r33):
    proof, result = r33
    assert result.nonexistence
    res = check_stream(io.StringIO(proof))
    assert res.ok, res.error
    assert "R(3,3) <= 6" in res.claim


def test_valid_proof_accepted_for_r34(r34):
    proof, _ = r34
    res = check_stream(io.StringIO(proof))
    assert res.ok, res.error
    assert "R(3,4) <= 9" in res.claim


def test_checker_reports_the_claim_it_verified(r33):
    proof, _ = r33
    res = check_stream(io.StringIO(proof))
    assert res.problem == "ramsey"
    assert res.params == {"s": "3", "t": "3"}
    assert res.order == 6
    assert res.witnesses > 0
    assert res.nodes > 0


# --------------------------------------------------------------------------
# Corruptions. Each must be rejected.
# --------------------------------------------------------------------------

def test_deleting_a_witness_leaves_a_hole(r33):
    """Dropping an X record means a satisfying extension is unaccounted for."""
    proof, _ = r33
    lines = proof.splitlines(keepends=True)
    idx = next(i for i, l in enumerate(lines) if l.startswith("X "))
    tampered = "".join(lines[:idx] + lines[idx + 1:])
    res = check_stream(io.StringIO(tampered))
    assert not res.ok
    assert "hole" in res.error or "witness" in res.error or "declares" in res.error


def test_deleting_a_descent_leaves_a_hole(r33):
    """Skipping a subtree is the exact bug this system exists to catch."""
    proof, _ = r33
    lines = proof.splitlines(keepends=True)
    # Excise a whole childless subtree -- "D <mask>", its "empty" assertion, and
    # the matching "U" -- so the record nesting stays balanced and the only thing
    # broken is the claim that every extension was accounted for.
    idx = next(i for i, l in enumerate(lines)
               if l.startswith("D ")
               and i + 2 < len(lines)
               and lines[i + 1].startswith("empty ")
               and lines[i + 2] == "U\n")
    tampered = "".join(lines[:idx] + lines[idx + 3:])
    res = check_stream(io.StringIO(tampered))
    assert not res.ok
    assert "hole" in res.error or "declares" in res.error


def test_corrupting_a_permutation_is_caught(r33):
    """A witness that does not actually shrink the code must be rejected."""
    proof, _ = r33
    lines = proof.splitlines(keepends=True)
    idx = next(i for i, l in enumerate(lines) if l.startswith("X "))
    parts = lines[idx].split()
    identity = " ".join(str(i) for i in range(len(parts) - 2))
    lines[idx] = f"X {parts[1]} {identity}\n"
    res = check_stream(io.StringIO("".join(lines)))
    assert not res.ok
    assert "smaller" in res.error or "permutation" in res.error


def test_non_bijective_witness_is_caught(r33):
    proof, _ = r33
    lines = proof.splitlines(keepends=True)
    idx = next(i for i, l in enumerate(lines) if l.startswith("X "))
    parts = lines[idx].split()
    zeros = " ".join("0" for _ in range(len(parts) - 2))
    lines[idx] = f"X {parts[1]} {zeros}\n"
    res = check_stream(io.StringIO("".join(lines)))
    assert not res.ok
    assert "permutation" in res.error


def test_witness_of_wrong_length_is_caught(r33):
    proof, _ = r33
    lines = proof.splitlines(keepends=True)
    idx = next(i for i, l in enumerate(lines) if l.startswith("X "))
    parts = lines[idx].split()
    lines[idx] = f"X {parts[1]} 0 1\n"
    res = check_stream(io.StringIO("".join(lines)))
    assert not res.ok
    assert "permutation" in res.error


def test_truncated_proof_is_rejected(r33):
    proof, _ = r33
    lines = proof.splitlines(keepends=True)
    tampered = "".join(lines[:len(lines) // 2])
    res = check_stream(io.StringIO(tampered))
    assert not res.ok
    assert "qed" in res.error or "unclosed" in res.error


def test_missing_qed_is_rejected(r33):
    proof, _ = r33
    tampered = "".join(l for l in proof.splitlines(keepends=True) if not l.startswith("qed"))
    res = check_stream(io.StringIO(tampered))
    assert not res.ok
    assert "qed" in res.error or "unclosed" in res.error


def test_inflated_node_tally_is_rejected(r33):
    proof, _ = r33
    tampered = re.sub(r"qed (\d+) (\d+)",
                      lambda m: f"qed {int(m.group(1)) + 1} {m.group(2)}", proof)
    res = check_stream(io.StringIO(tampered))
    assert not res.ok
    assert "declares" in res.error


def test_inflated_witness_tally_is_rejected(r33):
    proof, _ = r33
    tampered = re.sub(r"qed (\d+) (\d+)",
                      lambda m: f"qed {m.group(1)} {int(m.group(2)) + 1}", proof)
    res = check_stream(io.StringIO(tampered))
    assert not res.ok
    assert "declares" in res.error


def test_witness_for_a_property_violating_mask_is_rejected(r33):
    """You cannot dress up a property rejection as a canonicity rejection."""
    proof, _ = r33
    lines = proof.splitlines(keepends=True)
    idx = next(i for i, l in enumerate(lines) if l.startswith("X "))
    # mask 0b11111 at the root's first level is a K3 for the (3,3) problem once
    # enough vertices exist; use an all-ones mask which is maximally likely to
    # violate. The checker must complain about the property, not the permutation.
    parts = lines[idx].split()
    nperm = len(parts) - 2
    lines[idx] = f"X {(1 << (nperm - 1)) - 1:x} " + " ".join(str(i) for i in range(nperm)) + "\n"
    res = check_stream(io.StringIO("".join(lines)))
    assert not res.ok


def test_ascending_above_the_root_is_rejected(r33):
    proof, _ = r33
    lines = proof.splitlines(keepends=True)
    idx = next(i for i, l in enumerate(lines) if l.startswith("root"))
    tampered = "".join(lines[:idx + 1] + ["U\n"] + lines[idx + 1:])
    res = check_stream(io.StringIO(tampered))
    assert not res.ok
    assert "above the root" in res.error


def test_duplicate_mask_is_rejected(r33):
    proof, _ = r33
    lines = proof.splitlines(keepends=True)
    idx = next(i for i, l in enumerate(lines) if l.startswith("X "))
    tampered = "".join(lines[:idx] + [lines[idx], lines[idx]] + lines[idx + 1:])
    res = check_stream(io.StringIO(tampered))
    assert not res.ok
    assert "twice" in res.error or "declares" in res.error


def test_swapping_the_claimed_parameters_is_caught(r33):
    """Relabelling the header to a stronger claim must not survive checking."""
    proof, _ = r33
    tampered = proof.replace("problem ramsey s=3 t=3", "problem ramsey s=3 t=4")
    res = check_stream(io.StringIO(tampered))
    assert not res.ok


# --------------------------------------------------------------------------
# Malformed input handling: the checker must reject, never crash.
# --------------------------------------------------------------------------

@pytest.mark.parametrize("text", [
    "",
    "not-a-proof 1\n",
    "orbitcert-proof 99\n",
    "orbitcert-proof 1\nD 0\n",
    "orbitcert-proof 1\nproblem ramsey s=3 t=3\norder 6\nD 0\n",
    "orbitcert-proof 1\nproblem nonsense\norder 3\nroot 0\nqed 1 0\n",
    "orbitcert-proof 1\nproblem ramsey s=3 t=3\norder 6\nroot 0\nbogus\n",
    "orbitcert-proof 1\nproblem ramsey s=3 t=3\norder 0\nroot 0\nqed 1 0\n",
])
def test_malformed_proofs_are_rejected_without_crashing(text):
    res = check_stream(io.StringIO(text))
    assert not res.ok
    assert res.error


def test_parse_reports_line_numbers():
    with pytest.raises(ProofSyntaxError, match="line 2"):
        parse_string("orbitcert-proof 1\nfrobnicate\n")


def test_checker_builds_its_own_property_from_the_header(r33):
    """The claim is fixed by the proof, not supplied by the caller."""
    proof, _ = r33
    res = check_stream(io.StringIO(proof))
    assert res.ok
    # A proof for (3,3) must not be readable as a proof about (4,4).
    tampered = proof.replace("s=3 t=3", "s=4 t=4")
    assert not check_stream(io.StringIO(tampered)).ok
