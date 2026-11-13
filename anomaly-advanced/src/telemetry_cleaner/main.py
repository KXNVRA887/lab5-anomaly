"""Консольный интерфейс сравнения детекторов Z-score и IQR (вариант Б)."""
import sys

from telemetry_cleaner import config, detectors


def main() -> None:
    print("ИНТЕЛЛЕКТУАЛЬНЫЙ МОДУЛЬ ОЧИСТКИ ТЕЛЕМЕТРИИ СКВАЖИНЫ (ВАРИАНТ Б)")
    print("=" * 76)
    raw = (sys.argv[1] if len(sys.argv) > 1 else input("Введите ваш номер по журналу N: ")).strip()
    student_n = int(raw) if raw.isdigit() and int(raw) > 0 else 5
    print(f"N = {student_n}")

    series = detectors.build_series_16h(student_n)
    mean_v = detectors.calc_mean(series)
    med_v = detectors.calc_median(series)
    std_v = detectors.calc_std(series, mean_v)
    q1, q3, iqr = detectors.calc_quartiles_iqr(series)
    z_low, z_high = detectors.get_zscore_bounds(series, config.Z_K)
    iqr_low, iqr_high = detectors.get_iqr_bounds(series, config.IQR_FACTOR)

    print(f"\nИсходный ряд (16 ч): {series}")
    print("-" * 76)
    print(f"Среднее: {mean_v:.2f} | Медиана: {med_v:.2f} | СКО (sigma): {std_v:.2f} атм")
    print(f"Квартили: Q1 = {q1:.2f} | Q3 = {q3:.2f} | IQR = {iqr:.2f} атм")
    print(f"Коридор Z-score ({config.Z_K}*sigma): [{z_low:.2f}; {z_high:.2f}] атм")
    print(f"Коридор Тьюки ({config.IQR_FACTOR}*IQR): [{iqr_low:.2f}; {iqr_high:.2f}] атм")

    cleaned_iqr = detectors.filter_by_bounds(series, iqr_low, iqr_high)
    imputed_iqr = detectors.impute_with_median(series, iqr_low, iqr_high)

    print("\nСРАВНИТЕЛЬНАЯ ТАБЛИЦА ДЕТЕКЦИИ И ИМПУТАЦИИ ПО ЧАСАМ")
    print("-" * 76)
    print(f"{'Час':<5}{'P факт':>10}{'Z-оценка':>10}{'Метод Z-score':>16}{'Метод 1.5*IQR':>16}{'Ряд с заменой':>16}")
    print("-" * 76)
    z_outliers: list[int] = []
    iqr_outliers: list[int] = []
    for idx, val in enumerate(series):
        hour = idx + 1
        z_val = abs(val - mean_v) / std_v if std_v > 0 else 0.0
        is_z = val < z_low or val > z_high
        is_iqr = val < iqr_low or val > iqr_high
        if is_z:
            z_outliers.append(hour)
        if is_iqr:
            iqr_outliers.append(hour)
        print(f"{hour:<5}{val:>10.2f}{z_val:>10.2f}{'ВЫБРОС' if is_z else 'Норма':>16}"
              f"{'ВЫБРОС!' if is_iqr else 'Норма':>16}{imputed_iqr[idx]:>16.2f}")

    cln_mean = detectors.calc_mean(cleaned_iqr)
    cln_std = detectors.calc_std(cleaned_iqr, cln_mean)
    print("-" * 76)
    print(f"Выбросы по Z-score (часы): {z_outliers}")
    print(f"Выбросы по 1.5*IQR (часы): {iqr_outliers}")
    print(f"Очищенный ряд ({len(cleaned_iqr)} точек): {cleaned_iqr}")
    print(f"После очистки (IQR): среднее = {cln_mean:.2f} атм, СКО {std_v:.2f} -> {cln_std:.2f} атм")


if __name__ == "__main__":
    main()
