"""Tests for the canonicity engine, checked against brute force over all k!."""

import itertools
import math
import random

import pytest

from orbitcert.canon import (
    automorphisms,
    canonical_form,
    find_smaller,
    is_canonical,
    verify_witness,
)
from orbitcert.graph import code, from_edges, relabel

from .helpers import (
    A000088,
    all_labelled_graphs,
    brute_canonical_code,
    brute_is_canonical,
    random_graph,
)


def _sample(k: int, cap: int, seed: int):
    """Every labelled graph on k vertices when that is affordable, else a random sample.

    Brute-force oracles cost k! per graph, so exhaustive comparison stops paying
    for itself around k = 6. Below the cap the coverage is total; above it the
    sample is fixed by a seed so failures reproduce.
    """
    total = 1 << (k * (k - 1) // 2)
    if total <= cap:
        return list(all_labelled_graphs(k))
    rng = random.Random(seed)
    return [random_graph(k, p=rng.choice([0.2, 0.35, 0.5, 0.65, 0.8]), rng=rng)
            for _ in range(cap)]


@pytest.mark.parametrize("k", range(1, 7))
def test_is_canonical_agrees_with_brute_force(k):
    for g in _sample(k, 1200, seed=11 + k):
        assert is_canonical(g) == brute_is_canonical(g), g


@pytest.mark.parametrize("k", range(1, 7))
def test_canonical_count_matches_oeis_a000088(k):
    """One canonical representative per isomorphism class, so counts are A000088."""
    n = sum(1 for g in all_labelled_graphs(k) if is_canonical(g))
    assert n == A000088[k]


@pytest.mark.parametrize("k", range(2, 7))
def test_every_witness_is_valid(k):
    for g in _sample(k, 1200, seed=31 + k):
        w = find_smaller(g)
        if w is None:
            assert brute_is_canonical(g), g
        else:
            assert verify_witness(g, w), (g, w)
            assert code(relabel(g, w)) < code(g)


@pytest.mark.parametrize("k", range(1, 7))
def test_canonical_form_is_the_brute_force_minimum(k):
    for g in _sample(k, 1200, seed=51 + k):
        assert code(canonical_form(g)) == brute_canonical_code(g), g


@pytest.mark.parametrize("k", range(2, 7))
def test_canonical_form_is_isomorphism_invariant(k):
    rng = random.Random(20260803 + k)
    for _ in range(120):
        g = random_graph(k, rng=rng)
        p = list(range(k))
        rng.shuffle(p)
        assert canonical_form(g) == canonical_form(relabel(g, tuple(p)))


@pytest.mark.parametrize("k", range(1, 7))
def test_canonical_form_is_idempotent(k):
    for g in itertools.islice(all_labelled_graphs(k), 400):
        c = canonical_form(g)
        assert canonical_form(c) == c
        assert is_canonical(c)


@pytest.mark.parametrize("k", range(1, 6))
def test_orbit_stabiliser(k):
    """|Aut(G)| * |orbit of G| == k!, a sharp check on the automorphism search."""
    for g in _sample(k, 1200, seed=71 + k):
        aut = len(automorphisms(g))
        orbit = len({code(relabel(g, p)) for p in itertools.permutations(range(k))})
        assert aut * orbit == math.factorial(k), (g, aut, orbit)


@pytest.mark.parametrize("k", range(1, 6))
def test_automorphisms_really_are_automorphisms(k):
    for g in itertools.islice(all_labelled_graphs(k), 300):
        for p in automorphisms(g):
            assert relabel(g, p) == g


def test_automorphism_group_of_known_graphs():
    # C5 has automorphism group D5 of order 10.
    c5 = from_edges(5, [(0, 1), (1, 2), (2, 3), (3, 4), (4, 0)])
    assert len(automorphisms(c5)) == 10
    # K4 has automorphism group S4 of order 24.
    k4 = from_edges(4, list(itertools.combinations(range(4), 2)))
    assert len(automorphisms(k4)) == 24
    # The path on 4 vertices has only the identity and the flip.
    p4 = from_edges(4, [(0, 1), (1, 2), (2, 3)])
    assert len(automorphisms(p4)) == 2


def test_verify_witness_rejects_non_permutations():
    g = from_edges(3, [(1, 2)])
    assert not verify_witness(g, (0, 0, 1))     # not a bijection
    assert not verify_witness(g, (0, 1))        # wrong length
    assert not verify_witness(g, (0, 1, 2))     # identity never shrinks the code


def test_verify_witness_rejects_a_non_shrinking_permutation():
    """A permutation that maps a canonical graph elsewhere must not be accepted."""
    g = from_edges(4, [(2, 3)])
    assert is_canonical(g)
    for p in itertools.permutations(range(4)):
        assert not verify_witness(g, p)


def test_node_limit_errs_only_towards_keeping_graphs():
    """A truncated search may miss a witness; it must never invent one."""
    rng = random.Random(99)
    for k in range(4, 8):
        for _ in range(150):
            g = random_graph(k, rng=rng)
            w = find_smaller(g, node_limit=3)
            if w is not None:
                # Whatever it found under a tight budget must still be valid.
                assert verify_witness(g, w)


def test_single_vertex_and_empty_are_canonical():
    assert is_canonical((0,))
    assert find_smaller((0,)) is None
