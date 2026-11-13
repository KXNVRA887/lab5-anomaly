"""Расчёт квартилей, границ Z-score / IQR, фильтрация и импутация."""
from telemetry_cleaner import config


def build_series_16h(student_n: int) -> list[float]:
    base = 180.0 + 2.5 * student_n
    step = float(student_n % 4) + 1.5
    return [round(base + k * step, 2) for k in config.OFFSETS_16H]


def calc_mean(series: list[float]) -> float:
    if not series:
        raise ValueError("Пустой числовой ряд")
    total = 0.0
    for x in series:
        total += x
    return total / len(series)


def calc_median(series: list[float]) -> float:
    n = len(series)
    if n == 0:
        raise ValueError("Пустой числовой ряд")
    ordered = sorted(series)
    mid = n // 2
    if n % 2 == 1:
        return ordered[mid]
    return (ordered[mid - 1] + ordered[mid]) / 2.0


def calc_std(series: list[float], mean_val: float) -> float:
    if not series:
        raise ValueError("Пустой числовой ряд")
    sq_sum = 0.0
    for x in series:
        sq_sum += (x - mean_val) ** 2
    return (sq_sum / len(series)) ** 0.5


def calc_quartiles_iqr(series: list[float]) -> tuple[float, float, float]:
    """Q1, Q3, IQR методом Тьюки (медианы младшей и старшей половин)."""
    n = len(series)
    if n < 4:
        raise ValueError("Для расчёта квартилей нужно минимум 4 элемента")
    ordered = sorted(series)
    mid = n // 2
    lower_half = ordered[:mid]
    upper_half = ordered[mid:] if n % 2 == 0 else ordered[mid + 1:]
    q1 = calc_median(lower_half)
    q3 = calc_median(upper_half)
    return q1, q3, round(q3 - q1, 2)


def get_zscore_bounds(series, k: float = config.Z_K) -> tuple[float, float]:
    m = calc_mean(series)
    s = calc_std(series, m)
    return round(m - k * s, 2), round(m + k * s, 2)


def get_iqr_bounds(series, factor: float = config.IQR_FACTOR) -> tuple[float, float]:
    q1, q3, iqr = calc_quartiles_iqr(series)
    return round(q1 - factor * iqr, 2), round(q3 + factor * iqr, 2)


def filter_by_bounds(series, low, high) -> list[float]:
    return [x for x in series if low <= x <= high]


def impute_with_median(series, low, high) -> list[float]:
    med = round(calc_median(series), 2)
    return [x if low <= x <= high else med for x in series]
