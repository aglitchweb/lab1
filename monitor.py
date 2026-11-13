"""ЛР1. Мониторинг нагрузки с порогами и журналом в CSV."""
import csv
import time
from datetime import datetime
import psutil

INTERVAL = 5
SAMPLES = 12
THRESHOLDS = {"cpu": 70, "ram": 70, "disk": 90}
LOG_FILE = "monitor_log.csv"


def take_sample():
    memory = psutil.virtual_memory()
    cpu_cores = psutil.cpu_percent(percpu=True)
    return {
        "time": datetime.now().strftime("%H:%M:%S"),
        "cpu": psutil.cpu_percent(interval=None),
        "ram": memory.percent,
        "disk": psutil.disk_usage("C:\\").percent,
        # Дополнительные метрики
        "available_ram_gb": round(memory.available / 1024**3, 2),
        "max_cpu_core": max(cpu_cores)
    }


def check_alerts(sample):
    alerts = []
    for metric, limit in THRESHOLDS.items():
        if sample[metric] >= limit:
            alerts.append(f"{metric.upper()} = {sample[metric]}% (порог {limit}%)")
    return alerts


def main():
    # Первый вызов нужен для подготовки измерения CPU
    psutil.cpu_percent(interval=None)
    psutil.cpu_percent(percpu=True)
    # Списки для итоговой статистики
    cpu_values = []
    ram_values = []
    disk_values = []
    with open(LOG_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "time", "cpu", "ram", "disk",
                "available_ram_gb", "max_cpu_core", "alert"
            ]
        )
        writer.writeheader()
        for i in range(SAMPLES):
            time.sleep(INTERVAL)
            s = take_sample()
            alerts = check_alerts(s)
            s["alert"] = "; ".join(alerts)
            writer.writerow(s)
            # Сохраняем значения для статистики
            cpu_values.append(s["cpu"])
            ram_values.append(s["ram"])
            disk_values.append(s["disk"])
            mark = " <-- ВНИМАНИЕ: " + s["alert"] if alerts else ""
            print(
                f"{s['time']}  "
                f"CPU {s['cpu']:5.1f}%  "
                f"RAM {s['ram']:5.1f}%  "
                f"DISK {s['disk']:5.1f}%  "
                f"Свободная RAM {s['available_ram_gb']:.2f} ГБ  "
                f"Макс. загрузка ядра {s['max_cpu_core']:.1f}%"
                f"{mark}"
            )
    # Итоговая статистика
    print("\nИтоги мониторинга:")
    print(
        f"CPU: среднее {sum(cpu_values) / len(cpu_values):.1f}%, "
        f"максимум {max(cpu_values):.1f}%"
    )
    print(
        f"RAM: среднее {sum(ram_values) / len(ram_values):.1f}%, "
        f"максимум {max(ram_values):.1f}%"
    )
    print(
        f"DISK: среднее {sum(disk_values) / len(disk_values):.1f}%, "
        f"максимум {max(disk_values):.1f}%"
    )
    print(f"\nЖурнал сохранён в {LOG_FILE}")


if __name__ == "__main__":
    main()
