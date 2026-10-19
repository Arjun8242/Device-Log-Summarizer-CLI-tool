"""to clean and normalize a sensor readings"""

import math


def sanitize_readings(values: list[object]) -> list[float]:
    """ clean sensor readings and return a list of floats"""

    if not values:
        return []

    cleaned:list[float] = []

    for value in values:
        try:
            number = float(value)
        except (TypeError, ValueError, OverflowError):
            continue

        # filter negative and non finite values
        if not math.isfinite(number) or number<0:
            continue

        cleaned.append(min(number, 500.0))

    return cleaned

