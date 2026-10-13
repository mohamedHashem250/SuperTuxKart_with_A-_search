"""Connect the generic A* search with the current race observations."""
import math
from planning.astar import astar
from planning.track_graph import TrackGraph, distance_xz
from agents.controller import driving_command


class AStarRacingAgent:
    def __init__(self, track, replan_interval=12, horizon=12):
        self.graph = TrackGraph(track)
        self.replan_interval = replan_interval
        self.horizon = horizon
        self.path = []
        self.last_plan_step = -10**9
        self.plan_cost = math.nan
        self.expanded = 0

    @staticmethod
    def get_hazards(items):
        """First version only: known banana and bubblegum pickups/traps."""
        hazards = []
        for item in items:
            kind = getattr(item.type, 'name', str(item.type))
            if kind in ('BANANA', 'BUBBLEGUM'):
                hazards.append((item.location, max(1.0, float(item.size))))
        return hazards

    def choose_action(self, kart, world, step):
        position = kart.location
        segment = int(kart.node)
        if not (0 <= segment < self.graph.n):
            segment = self.graph.nearest_segment(position)
        lane = self.graph.closest_lane(segment, position)
        start = (segment, lane)

        if step - self.last_plan_step >= self.replan_interval or not self.path:
            goal = self.graph.goal_segment_ahead(segment, steps=self.horizon)
            hazards = self.get_hazards(world.items)
            result = astar(
                start=start,
                is_goal=lambda n: n[0] == goal,
                successors=lambda n: self.graph.neighbors(n, hazards),
                heuristic=lambda n: self.graph.heuristic(n, goal),
            )
            self.last_plan_step = step
            if result is not None:
                self.path = result.path
                self.plan_cost = result.cost
                self.expanded = result.expanded
            else:
                # Safe fallback if graph disconnected: drive toward next center.
                self.path = [(goal, 1)]
                self.plan_cost = math.nan
                self.expanded = 0

        # Select a sufficiently distant waypoint, not the kart's current node.
        lookahead = max(5.0, min(13.0, 4.0 + float(kart.speed) * 0.35))
        target_node = self.path[-1]
        for node in self.path[1:]:
            if distance_xz(self.graph.position(node), position) >= lookahead:
                target_node = node
                break
        target = self.graph.position(target_node)
        command = driving_command(kart, target)
        return command, {'segment': segment, 'goal': self.path[-1][0],
                         'target': target_node, 'expanded': self.expanded,
                         'path_cost': self.plan_cost, 'path': list(self.path)}
