def to_int_if_whole(x: float) -> float | int:
    if x.is_integer():
        return int(x)
    return x
