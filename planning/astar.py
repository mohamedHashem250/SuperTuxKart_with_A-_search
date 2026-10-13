"""A* graph search inspired by the *interface* taught in CS 188 Project 1.

Original implementation written for this SuperTuxKart project; no Berkeley
solution code is included.
"""
from dataclasses import dataclass
import heapq
from itertools import count
from math import inf
from typing import Any, Callable, Iterable, Optional


@dataclass
class SearchResult:
    path: list
    cost: float
    expanded: int


def astar(
    start: Any,
    is_goal: Callable[[Any], bool],
    successors: Callable[[Any], Iterable[tuple[Any, float]]],
    heuristic: Callable[[Any], float],
    max_expansions: int = 10000,
) -> Optional[SearchResult]:
    """Return minimum-cost state path under an admissible, consistent heuristic.

    successor yields (next_state, nonnegative_edge_cost).
    The frontier is ordered by f(n) = g(n) + h(n).
    """
    frontier = []
    serial = count()
    heapq.heappush(frontier, (float(heuristic(start)), next(serial), 0.0, start))
    best_cost = {start: 0.0}
    previous = {}
    expanded = 0

    while frontier:
        _, _, g, state = heapq.heappop(frontier)
        if g > best_cost.get(state, inf) + 1e-9:
            continue  # outdated queue entry
        if is_goal(state):
            path = [state]
            while state in previous:
                state = previous[state]
                path.append(state)
            path.reverse()
            return SearchResult(path=path, cost=g, expanded=expanded)

        if expanded >= max_expansions:
            return None
        expanded += 1

        for next_state, edge_cost in successors(state):
            if edge_cost < 0:
                raise ValueError('A* requires nonnegative edge costs')
            candidate = g + float(edge_cost)
            if candidate + 1e-9 < best_cost.get(next_state, inf):
                best_cost[next_state] = candidate
                previous[next_state] = state
                f_score = candidate + float(heuristic(next_state))
                heapq.heappush(frontier, (f_score, next(serial), candidate, next_state))

    return None  # no path found
