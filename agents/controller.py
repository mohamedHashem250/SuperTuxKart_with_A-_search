"""Very simple waypoint follower. Not an optimal vehicle controller."""
import math
import numpy as np


def steering_to_target(kart, target, gain=1.7):
    position = np.asarray(kart.location, dtype=float)
    front = np.asarray(kart.front, dtype=float)
    # API describes `front` as a point ahead of the kart's location.
    heading = front[[0, 2]] - position[[0, 2]]
    if np.linalg.norm(heading) < 1e-5:
        return 0.0, 0.0
    heading /= np.linalg.norm(heading)
    direction = np.asarray(target, dtype=float)[[0, 2]] - position[[0, 2]]
    if np.linalg.norm(direction) < 1e-5:
        return 0.0, 0.0
    direction /= np.linalg.norm(direction)
    # Positive angle: target to our right in STK (X right, Z forward).
    angle = math.atan2(heading[1]*direction[0] - heading[0]*direction[1],
                       float(np.dot(heading, direction)))
    return float(np.clip(gain*angle, -1.0, 1.0)), angle


def driving_command(kart, target):
    steer, angle = steering_to_target(kart, target)
    speed = float(kart.speed)
    sharp_turn = abs(angle) > 0.65
    brake = bool(sharp_turn and speed > 12.0)
    acceleration = 0.0 if brake else (0.45 if sharp_turn else 0.85)
    return {'steer': steer, 'acceleration': acceleration, 'brake': brake}
