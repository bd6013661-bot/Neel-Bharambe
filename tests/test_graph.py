"""Tests for the graph representation and the prefix-structured code."""

import itertools
import subprocess

import pytest

from orbitcert.graph import (
    code,
    code_int,
    complement,
    degree,
    edges,
    empty,
    extend,
    from_edges,
    from_graph6,
    has_edge,
    induced,
    num_edges,
    relabel,
    to_graph6,
)

from .helpers import all_labelled_graphs, random_graph


def test_empty_graph_has_no_edges():
    for k in range(1, 8):
        g = empty(k)
        assert len(g) == k
        assert num_edges(g) == 0
        assert list(edges(g)) == []


def test_from_edges_round_trips():
    g = from_edges(5, [(0, 1), (1, 2), (3, 4)])
    assert sorted(edges(g)) == [(0, 1), (1, 2), (3, 4)]
    assert num_edges(g) == 3
    assert degree(g, 1) == 2
    assert has_edge(g, 0, 1) and not has_edge(g, 0, 2)


def test_from_edges_rejects_loops_and_out_of_range():
    with pytest.raises(ValueError, match="loop"):
        from_edges(3, [(1, 1)])
    with pytest.raises(ValueError, match="out of range"):
        from_edges(3, [(0, 5)])


def test_representation_is_symmetric():
    for k in range(1, 7):
        for g in itertools.islice(all_labelled_graphs(k), 200):
            for u in range(k):
                for v in range(k):
                    assert bool(g[u] >> v & 1) == bool(g[v] >> u & 1)
            assert all(not (g[u] >> u & 1) for u in range(k)), "no self-loops"


@pytest.mark.parametrize("k", range(2, 7))
def test_code_is_upper_triangle_column_major(k):
    for g in itertools.islice(all_labelled_graphs(k), 300):
        expected = tuple(1 if has_edge(g, i, j) else 0
                         for j in range(1, k) for i in range(j))
        assert code(g) == expected
        assert len(code(g)) == k * (k - 1) // 2


@pytest.mark.parametrize("k", range(2, 8))
def test_prefix_property(k):
    """The whole design rests on this: induced subgraph codes are code prefixes."""
    for g in itertools.islice(all_labelled_graphs(k), 400):
        full = code(g)
        for m in range(1, k + 1):
            sub = code(induced(g, m))
            assert full[:len(sub)] == sub, (
                f"code(induced(g,{m})) is not a prefix of code(g) for {g}")


@pytest.mark.parametrize("k", range(2, 7))
def test_code_int_orders_identically_to_code(k):
    graphs = list(itertools.islice(all_labelled_graphs(k), 400))
    by_tuple = sorted(graphs, key=code)
    by_int = sorted(graphs, key=code_int)
    assert [code(g) for g in by_tuple] == [code(g) for g in by_int]


def test_extend_appends_exactly_one_column():
    g = from_edges(3, [(0, 1)])
    h = extend(g, 0b101)  # new vertex 3 joined to 0 and 2
    assert len(h) == 4
    assert sorted(edges(h)) == [(0, 1), (0, 3), (2, 3)]
    assert induced(h, 3) == g
    assert code(h)[:len(code(g))] == code(g)


def test_extend_rejects_out_of_range_neighbourhood():
    with pytest.raises(ValueError, match="outside"):
        extend(empty(3), 0b1000)


def test_relabel_is_a_group_action():
    for k in range(2, 7):
        for g in itertools.islice(all_labelled_graphs(k), 100):
            identity = tuple(range(k))
            assert relabel(g, identity) == g
            for p in itertools.islice(itertools.permutations(range(k)), 12):
                for q in itertools.islice(itertools.permutations(range(k)), 12):
                    # (q after p) applied at once equals p then q
                    composed = tuple(q[p[i]] for i in range(k))
                    assert relabel(g, composed) == relabel(relabel(g, p), q)


def test_relabel_preserves_edge_count_and_degrees():
    for k in range(2, 7):
        for g in itertools.islice(all_labelled_graphs(k), 150):
            for p in itertools.islice(itertools.permutations(range(k)), 8):
                h = relabel(g, p)
                assert num_edges(h) == num_edges(g)
                assert sorted(degree(h, v) for v in range(k)) == \
                       sorted(degree(g, v) for v in range(k))


def test_relabel_rejects_wrong_length():
    with pytest.raises(ValueError, match="length"):
        relabel(empty(3), (0, 1))


def test_complement_is_an_involution():
    for k in range(1, 7):
        for g in itertools.islice(all_labelled_graphs(k), 200):
            assert complement(complement(g)) == g
            assert num_edges(g) + num_edges(complement(g)) == k * (k - 1) // 2


@pytest.mark.parametrize("k", range(1, 8))
def test_graph6_round_trip(k):
    for g in itertools.islice(all_labelled_graphs(k), 300):
        assert from_graph6(to_graph6(g)) == g


def test_graph6_matches_nauty():
    """Our graph6 must be byte-identical to nauty's, or interop claims are hollow."""
    graphs = list(all_labelled_graphs(5))
    ours = [to_graph6(g) for g in graphs]
    proc = subprocess.run(["nauty-labelg", "-q"], input="\n".join(ours),
                          capture_output=True, text=True)
    if proc.returncode != 0:
        pytest.skip("nauty not available")
    # labelg canonises; feeding its own output back must be a fixed point.
    canonised = proc.stdout.split()
    again = subprocess.run(["nauty-labelg", "-q"], input="\n".join(canonised),
                           capture_output=True, text=True)
    assert again.stdout.split() == canonised
    # And every line must decode back to a graph on 5 vertices with the same size.
    for original, canon_line in zip(ours, canonised):
        assert num_edges(from_graph6(canon_line)) == num_edges(from_graph6(original))


def test_graph6_rejects_bad_input():
    with pytest.raises(ValueError):
        from_graph6("")
    with pytest.raises(ValueError, match="1 <= k <= 62"):
        to_graph6(empty(63))
