"""Navigation helper for a robot agent: which way to turn toward a waypoint."""
import numpy as np


def turn_direction(heading, to_target) -> str:
    z = np.cross(np.asarray(heading, float), np.asarray(to_target, float))
    if abs(z) < 1e-9:
        return "straight"
    return "left" if z > 0 else "right"


def turn_all(pairs) -> list[str]:
    h = np.asarray([p[0] for p in pairs], float)
    t = np.asarray([p[1] for p in pairs], float)
    z = np.cross(h, t)
    return ["straight" if abs(v) < 1e-9 else ("left" if v > 0 else "right") for v in z]
