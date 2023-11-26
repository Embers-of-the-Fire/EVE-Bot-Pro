__all__ = [
    "skill_time_factor",
]

# [0, int(250 * math.sqrt(32) ** x) for x in range(5)]
skill_time_factor = [0, 250, 1414, 8000, 45254, 256000]
