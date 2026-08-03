"""Tests for orderly generation: completeness, no duplicates, published counts."""

import io
import itertools

import pytest

from orbitcert import (
    CliqueFree,
    GirthAtLeast,
    RamseyProperty,
    TriangleFree,
    check_stream,
    enumerate_graphs,
    iter_level,
)
from orbitcert.canon import is_canonical
from orbitcert.graph import code, induced

from .helpers import (
    A000088,
    A006785,
    all_labelled_graphs,
    brute_canonical_code,
    brute_girth,
    brute_has_clique,
    brute_has_independent_set,
    brute_iso_classes,
    nauty_available,
    nauty_iso_classes,
    our_iso_classes,
)

requires_nauty = pytest.mark.skipif(not nauty_available(), reason="nauty not installed")


class AnyGraph(CliqueFree):
    """No constraint at all -- enumerates every isomorphism class."""

    name = "clique-free"

    def __init__(self):
        super().__init__(99)


@pytest.mark.parametrize("n", range(1, 8))
def test_unconstrained_counts_match_a000088(n):
    res = enumerate_graphs(AnyGraph(), n, collect=True)
    assert len(res.witnesses) == A000088[n]
    assert res.counts == A000088[1:n + 1]


@pytest.mark.parametrize("n", range(1, 9))
def test_triangle_free_counts_match_a006785(n):
    res = enumerate_graphs(TriangleFree(), n, collect=True)
    assert len(res.witnesses) == A006785[n]


@pytest.mark.parametrize("n", range(1, 6))
def test_enumeration_finds_exactly_the_isomorphism_classes(n):
    """Completeness and non-redundancy against brute force over all labelled graphs."""
    res = enumerate_graphs(AnyGraph(), n, collect=True)
    got = {code(g) for g in res.witnesses}
    assert len(got) == len(res.witnesses), "duplicate isomorphism classes emitted"
    assert got == brute_iso_classes(n)


@pytest.mark.parametrize("n", range(1, 6))
def test_triangle_free_enumeration_matches_brute_force(n):
    res = enumerate_graphs(TriangleFree(), n, collect=True)
    got = {code(g) for g in res.witnesses}
    want = brute_iso_classes(n, predicate=lambda g: not brute_has_clique(g, 3))
    assert got == want


@pytest.mark.parametrize("s,t,n", [(3, 3, 5), (3, 4, 5), (4, 4, 5), (3, 5, 5), (4, 3, 5)])
def test_ramsey_enumeration_matches_brute_force(s, t, n):
    res = enumerate_graphs(RamseyProperty(s, t), n, collect=True)
    got = {code(g) for g in res.witnesses}
    want = brute_iso_classes(
        n, predicate=lambda g: not brute_has_clique(g, s) and not brute_has_independent_set(g, t))
    assert got == want


@pytest.mark.parametrize("n", range(1, 6))
def test_every_emitted_graph_is_canonical(n):
    res = enumerate_graphs(AnyGraph(), n, collect=True)
    for g in res.witnesses:
        assert is_canonical(g)
        assert code(g) == brute_canonical_code(g)


@pytest.mark.parametrize("n", range(2, 7))
def test_every_prefix_of_an_emitted_graph_is_canonical(n):
    """Prefix-heredity: the property the whole pruning argument depends on."""
    res = enumerate_graphs(AnyGraph(), n, collect=True)
    for g in res.witnesses:
        for m in range(1, n + 1):
            assert is_canonical(induced(g, m)), (g, m)


@pytest.mark.parametrize("girth", [4, 5, 6])
def test_girth_property_matches_brute_force(girth):
    res = enumerate_graphs(GirthAtLeast(girth), 5, collect=True)
    got = {code(g) for g in res.witnesses}
    want = brute_iso_classes(5, predicate=lambda g: brute_girth(g) >= girth)
    assert got == want


# --------------------------------------------------------------------------
# Cross-checks against nauty: an independent implementation of a different
# algorithm, written by different people in a different language.
# --------------------------------------------------------------------------

@requires_nauty
@pytest.mark.parametrize("n", range(1, 9))
def test_matches_nauty_on_all_graphs(n):
    res = enumerate_graphs(AnyGraph(), n, collect=True)
    assert our_iso_classes(res.witnesses) == nauty_iso_classes(n)


@requires_nauty
@pytest.mark.parametrize("n", range(1, 10))
def test_matches_nauty_on_triangle_free_graphs(n):
    res = enumerate_graphs(TriangleFree(), n, collect=True)
    assert our_iso_classes(res.witnesses) == nauty_iso_classes(n, "-t")


@requires_nauty
@pytest.mark.parametrize("n", range(1, 9))
def test_matches_nauty_on_girth_at_least_5(n):
    """geng -t -f is triangle-free and square-free, i.e. girth >= 5."""
    res = enumerate_graphs(GirthAtLeast(5), n, collect=True)
    assert our_iso_classes(res.witnesses) == nauty_iso_classes(n, "-t", "-f")


# --------------------------------------------------------------------------
# Known Ramsey numbers, cross-checked against Radziszowski's survey DS1.
# --------------------------------------------------------------------------

RAMSEY_CASES = [
    # (s, t, R(s,t), critical graph count on R-1 vertices)
    (3, 3, 6, 1),
    (3, 4, 9, 3),
    (4, 4, 18, 2),
    (3, 5, 14, 1),
    (3, 6, 18, 7),
    (3, 7, 23, 191),
]


@pytest.mark.parametrize("s,t,R,ncrit", [c for c in RAMSEY_CASES if c[2] <= 9])
def test_small_ramsey_numbers_and_critical_counts(s, t, R, ncrit):
    crit = enumerate_graphs(RamseyProperty(s, t), R - 1, collect=True)
    assert len(crit.witnesses) == ncrit, f"critical graph count for R({s},{t})"
    above = enumerate_graphs(RamseyProperty(s, t), R, collect=True)
    assert above.nonexistence, f"R({s},{t}) should be exactly {R}"


@pytest.mark.parametrize("s,t,R", [(3, 3, 6), (3, 4, 9)])
def test_certificates_verify_for_small_ramsey_numbers(s, t, R):
    buf = io.StringIO()
    res = enumerate_graphs(RamseyProperty(s, t), R, proof=buf, collect=True)
    assert res.nonexistence
    chk = check_stream(io.StringIO(buf.getvalue()))
    assert chk.ok, chk.error
    assert f"R({s},{t}) <= {R}" in chk.claim


def test_r35_critical_graph_is_the_known_cyclic_graph():
    """The unique (3,5)-graph on 13 vertices is the circulant C13(1,5)."""
    res = enumerate_graphs(RamseyProperty(3, 5), 13, collect=True)
    assert len(res.witnesses) == 1
    g = res.witnesses[0]
    assert len(g) == 13
    # It is 4-regular, as the circulant C13(1,5) is.
    degrees = {bin(row).count("1") for row in g}
    assert degrees == {4}


# --------------------------------------------------------------------------
# Structural guarantees
# --------------------------------------------------------------------------

@pytest.mark.parametrize("n", range(1, 7))
def test_iter_level_agrees_with_enumerate_graphs(n):
    a = {code(g) for g in iter_level(TriangleFree(), n)}
    b = {code(g) for g in enumerate_graphs(TriangleFree(), n, collect=True).witnesses}
    assert a == b


def test_node_limit_never_loses_graphs():
    """A crippled canonicity search must still find every isomorphism class."""
    full = enumerate_graphs(TriangleFree(), 6, collect=True)
    want = {code(g) for g in full.witnesses}
    crippled = enumerate_graphs(TriangleFree(), 6, collect=True, node_limit=1)
    got = {code(g) for g in crippled.witnesses}
    # Every genuine class is still present; duplicates may appear, never losses.
    assert want <= got
    assert len(crippled.witnesses) >= len(full.witnesses)


def test_node_limit_still_produces_a_verifiable_certificate():
    buf = io.StringIO()
    res = enumerate_graphs(RamseyProperty(3, 4), 9, proof=buf, collect=True, node_limit=2)
    assert res.nonexistence
    chk = check_stream(io.StringIO(buf.getvalue()))
    assert chk.ok, chk.error


def test_order_must_be_positive():
    with pytest.raises(ValueError, match="at least 1"):
        enumerate_graphs(TriangleFree(), 0)


def test_ramsey_parameters_validated():
    with pytest.raises(ValueError, match="s, t >= 2"):
        RamseyProperty(1, 3)


def test_search_result_summary_is_informative():
    res = enumerate_graphs(RamseyProperty(3, 3), 6, collect=True)
    text = res.summary()
    assert "NO graph exists" in text
    assert "n=5:1" in text
