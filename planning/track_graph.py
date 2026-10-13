"""Convert the PySuperTuxKart2 drivable centerline into a 3-lane graph.

Search node (segment_index, lane_index), where lanes = left / center / right.
The graph is a *planning approximation*, not a complete collision map.
"""
import math
import numpy as np

LANE_FRACTIONS = (-0.28, 0.0, 0.28)


def distance_xz(a, b):
    """2D ground-plane distance (the game's vertical axis is Y)."""
    a, b = np.asarray(a), np.asarray(b)
    return float(math.hypot(float(a[0] - b[0]), float(a[2] - b[2])))


class TrackGraph:
    def __init__(self, track):
        nodes = np.asarray(track.path_nodes, dtype=float)
        if nodes.ndim != 3 or nodes.shape[1:] != (2, 3):
            raise ValueError(f'Expected track.path_nodes (N, 2, 3), got {nodes.shape}')
        self.segments = nodes
        self.centers = nodes.mean(axis=1)
        self.widths = np.asarray(track.path_width, dtype=float).reshape(-1)
        if len(self.widths) != len(nodes):
            raise ValueError('Track widths length differs from segment count')
        self.next_segments = [[int(v) for v in row] for row in track.successors]
        if len(self.next_segments) != len(nodes):
            raise ValueError('Track successor count differs from segment count')
        self.n = len(nodes)
        self.lanes = len(LANE_FRACTIONS)
        self.points = np.empty((self.n, self.lanes, 3), dtype=float)

        for i in range(self.n):
            start, end = nodes[i]
            heading = np.array([end[0]-start[0], end[2]-start[2]], dtype=float)
            mag = float(np.linalg.norm(heading))
            if mag < 1e-6:
                # For an unusual zero-length segment, use a neighboring center.
                other = self.centers[(i + 1) % self.n]
                heading = np.array([other[0] - self.centers[i, 0],
                                    other[2] - self.centers[i, 2]])
                mag = float(np.linalg.norm(heading))
            if mag < 1e-6:
                heading = np.array([0.0, 1.0])
                mag = 1.0
            heading /= mag
            sideways = np.array([heading[1], -heading[0]])
            # Treat width as total usable width, take conservative offsets.
            for lane, offset in enumerate(LANE_FRACTIONS):
                point = self.centers[i].copy()
                point[0] += sideways[0] * float(self.widths[i]) * offset
                point[2] += sideways[1] * float(self.widths[i]) * offset
                self.points[i, lane] = point

    def position(self, node):
        segment, lane = node
        return self.points[segment, lane]

    def nearest_segment(self, kart_position):
        diffs = self.centers[:, [0, 2]] - np.asarray(kart_position)[[0, 2]]
        return int(np.argmin((diffs ** 2).sum(axis=1)))

    def closest_lane(self, segment, kart_position):
        options = self.points[segment]
        diffs = options[:, [0, 2]] - np.asarray(kart_position)[[0, 2]]
        return int(np.argmin((diffs ** 2).sum(axis=1)))

    def goal_segment_ahead(self, start, steps=12):
        """Follow first official successor to select one short-horizon target."""
        current = int(start)
        for _ in range(steps):
            links = [v for v in self.next_segments[current] if 0 <= v < self.n and v != current]
            if not links:
                break
            current = links[0]
        return current

    def neighbors(self, state, hazards=(), lane_change_penalty=1.5):
        segment, lane = state
        for next_segment in self.next_segments[segment]:
            if not (0 <= next_segment < self.n) or next_segment == segment:
                continue
            for next_lane in (lane - 1, lane, lane + 1):
                if not (0 <= next_lane < self.lanes):
                    continue
                nxt = (next_segment, next_lane)
                point = self.position(nxt)
                base = distance_xz(self.position(state), point)
                # Add a conservative minimum in unusual overlapping segments.
                cost = max(0.01, base) + lane_change_penalty * abs(lane - next_lane)
                for hazard_position, hazard_radius in hazards:
                    gap = distance_xz(point, hazard_position)
                    # Soft risk penalty, not a hard blockade.
                    if gap < hazard_radius + 2.0:
                        cost += 40.0 * (1.0 - gap / (hazard_radius + 2.0))
                yield nxt, cost

    def heuristic(self, state, goal_segment):
        # Nearest goal-lane Euclidean distance is a lower bound on our cost.
        return min(distance_xz(self.position(state), point)
                   for point in self.points[goal_segment])
