"""Smooth LineArt path conversion."""

from __future__ import annotations

from graphassist.schema.lineart import PathCommand


def catmull_rom_to_commands(points: list[list[float]], *, closed: bool = False) -> list[PathCommand]:
    """Convert points to cubic Bezier commands using Catmull-Rom interpolation."""
    if len(points) < 2:
        raise ValueError("at least 2 points are required")

    commands = [PathCommand(command="M", values=[points[0][0], points[0][1]])]
    count = len(points)
    segment_count = count if closed else count - 1
    for index in range(segment_count):
        p0 = points[index - 1] if index > 0 else (points[-1] if closed else points[0])
        p1 = points[index]
        p2 = points[(index + 1) % count]
        p3 = points[(index + 2) % count] if (index + 2 < count or closed) else p2
        c1 = [p1[0] + (p2[0] - p0[0]) / 6.0, p1[1] + (p2[1] - p0[1]) / 6.0]
        c2 = [p2[0] - (p3[0] - p1[0]) / 6.0, p2[1] - (p3[1] - p1[1]) / 6.0]
        commands.append(PathCommand(command="C", values=[c1[0], c1[1], c2[0], c2[1], p2[0], p2[1]]))
    if closed:
        commands.append(PathCommand(command="Z"))
    return commands
