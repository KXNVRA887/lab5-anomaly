"""Упражнения 1-7 к ЛР № 5 (вариант А; для Б см. переключатель VARIANT)."""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "anomaly-basic"))
from main import (calc_mean, calc_median, calc_std, filter_anomalies,  # noqa: E402
                  generate_pressure_series)

N = int(sys.argv[1]) if len(sys.argv) > 1 and sys.argv[1].isdigit() else 10
series, T_MIN, T_MAX = generate_pressure_series(N)
SPIKE, DIP = 8, 3  # индексы: 9-й и 4-й час


def bounds(data, k):
    m = calc_mean(data)
    s = calc_std(data, m)
    return round(m - k * s, 2), round(m + k * s, 2)


def hours_out(data, low, high):
    return [h for h, v in enumerate(data, start=1) if not low <= v <= high]


def header(t):
    print("\n" + "=" * 70 + f"\n{t}\n" + "=" * 70)


# --- Упражнение 1 ---------------------------------------------------------
header("Упражнение 1. Чувствительность порога k")
print(f"{'k':<6}{'Границы отсечения':<24}Часы выбросов")
for k in (1.5, 2.0, 3.0):
    lo, hi = bounds(series, k)
    print(f"{k:<6}[{lo:.2f}; {hi:.2f}]".ljust(30) + str(hours_out(series, lo, hi)))
print("Малое k -> ложные срабатывания; большое k -> пропуск реальных сбоев.")

# --- Упражнение 2 ---------------------------------------------------------
header("Упражнение 2. Эффект маскирования (шпилька = 1000.0)")
masked = series[:]
masked[SPIKE] = 1000.0
m0 = calc_mean(series)
s0 = calc_std(series, m0)
m1 = calc_mean(masked)
s1 = calc_std(masked, m1)
lo, hi = bounds(masked, 2.0)
print(f"sigma: {s0:.2f} -> {s1:.2f}; коридор 2*sigma: [{lo:.2f}; {hi:.2f}]")
found = hours_out(masked, lo, hi)
print(f"Найденные часы: {found}; провал {DIP + 1}-го часа ({masked[DIP]}) "
      f"{'найден' if DIP + 1 in found else 'СПРЯТАН в тени шпильки'}")


# --- Упражнение 3 ---------------------------------------------------------
def two_pass(data, k=2.0):
    lo1, hi1 = bounds(data, k)
    cleaned1, _ = filter_anomalies(data, lo1, hi1)
    lo2, hi2 = bounds(cleaned1, k)  # пересчёт на очищенном ряде
    return (lo1, hi1), (lo2, hi2), hours_out(data, lo1, hi1), hours_out(data, lo2, hi2)


header("Упражнение 3. Двухпроходная очистка (ряд с 1000.0)")
b1, b2, h1, h2 = two_pass(masked)
print(f"Проход 1: [{b1[0]:.2f}; {b1[1]:.2f}] -> часы {h1}")
print(f"Проход 2: [{b2[0]:.2f}; {b2[1]:.2f}] -> часы {h2}")
print("Второй проход", "обнаружил" if DIP + 1 in h2 else "не обнаружил", "замаскированный провал.")

# --- Упражнение 4 ---------------------------------------------------------
header("Упражнение 4. remove() внутри цикла for")
bad = series[:]
bad[3] = bad[4] = 110.0
low_bound = T_MIN
print("До:", bad)
for val in bad:  # ОШИБКА: изменяем список во время обхода
    if val < low_bound:
        bad.remove(val)
print("После remove в цикле:", bad, "<- второй 110.0 остался!")
good, anomalies = filter_anomalies(series[:3] + [110.0, 110.0] + series[5:], low_bound, T_MAX)
print("Через новый список:", good, "| выбросы:", anomalies)


# --- Упражнение 5 ---------------------------------------------------------
def replace_outliers_with_neighbor_avg(data, low, high):
    """Заменяет выброс полусуммой соседей; крайние точки - медианой ряда."""
    med = calc_median(data)
    result = data[:]
    for i, v in enumerate(data):
        if low <= v <= high:
            continue
        if i == 0 or i == len(data) - 1:
            result[i] = med
        else:
            result[i] = (data[i - 1] + data[i + 1]) / 2
    return result


header("Упражнение 5. Импутация полусуммой соседей")
print("Ряд:", replace_outliers_with_neighbor_avg(series, T_MIN, T_MAX))

# --- Упражнение 6 ---------------------------------------------------------
header("Упражнение 6. Доля брака")
lo, hi = bounds(series, 2.0)
_, anomalies = filter_anomalies(series, lo, hi)
rate = len(anomalies) / len(series) * 100
verdict = ("Канал исправен" if rate <= 10
           else "Требуется калибровка датчика" if rate <= 25 else "Авария телеметрии")
print(f"anomaly_rate = {len(anomalies)} / {len(series)} * 100 = {rate:.2f}% -> {verdict}")

# --- Упражнение 7 ---------------------------------------------------------
header("Упражнение 7. Константный ряд (залипание датчика)")
const = [170.0] * 12
cm = calc_mean(const)
cs = calc_std(const, cm)
o = sorted(const)
q1, q3 = calc_median(o[:6]), calc_median(o[6:])
print(f"mean = {cm:.2f}, sigma = {cs:.2f}, Q1 = {q1:.2f}, Q3 = {q3:.2f}, IQR = {q3 - q1:.2f}")
print("z без защиты: деление на 0 ->", end=" ")
try:
    print(abs(const[0] - cm) / cs)
except ZeroDivisionError as e:
    print("ZeroDivisionError:", e)
print("z с защитой  :", abs(const[0] - cm) / cs if cs > 0 else 0.0)
