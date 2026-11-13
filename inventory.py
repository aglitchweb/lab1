"""Лабораторная работа №1. Автоматическая инвентаризация компьютера."""

import json
import platform
import socket
from datetime import datetime

import psutil


def get_system_info():
    """Возвращает общую информацию об операционной системе."""
    return {
        "hostname": socket.gethostname(),
        "os": platform.system(),
        "os_version": platform.version(),
        "architecture": platform.machine(),
        "boot_time": datetime.fromtimestamp(psutil.boot_time()).strftime(
            "%Y-%m-%d %H:%M"
        ),
    }


def get_cpu_info():
    """Возвращает сведения о процессоре."""
    freq = psutil.cpu_freq()
    return {
        "model": platform.processor(),
        "physical_cores": psutil.cpu_count(logical=False),
        "logical_cores": psutil.cpu_count(logical=True),
        "max_freq_mhz": round(freq.max) if freq and freq.max else None,
        "load_percent": psutil.cpu_percent(interval=1),
    }


def get_memory_info():
    """Возвращает сведения об оперативной памяти."""
    mem = psutil.virtual_memory()
    return {
        "total_gb": round(mem.total / 1024**3, 1),
        "used_percent": mem.percent,
        "available_gb": round(mem.available / 1024**3, 2),
    }


def get_disk_info():
    """Возвращает сведения о доступных разделах дисков."""
    disks = []
    for part in psutil.disk_partitions():
        try:
            usage = psutil.disk_usage(part.mountpoint)
        except (PermissionError, OSError):
            # Некоторые системные или съёмные разделы могут быть недоступны.
            continue

        disks.append(
            {
                "device": part.device,
                "mountpoint": part.mountpoint,
                "fs": part.fstype,
                "total_gb": round(usage.total / 1024**3, 1),
                "used_percent": usage.percent,
            }
        )
    return disks


def get_network_info():
    interfaces = []
    for name, addrs in psutil.net_if_addrs().items():
        ipv4 = next(
            (addr for addr in addrs if addr.family == socket.AF_INET),
            None,
        )
        if ipv4 is None:
            continue
        mac = next(
            (addr.address for addr in addrs if addr.family == psutil.AF_LINK),
            None,
        )
        interfaces.append(
            {
                "name": name,
                "ipv4": ipv4.address,
                "netmask": ipv4.netmask,
                "mac": mac,
            }
        )

    return interfaces


def analyze(passport):
    recommendations = []
    memory = passport["memory"]
    cpu = passport["cpu"]
    total_ram = memory["total_gb"]
    physical_cores = cpu["physical_cores"] or 0
    if total_ram < 8:
        recommendations.append(
            "Недостаточно памяти для виртуальных машин и Docker."
        )
    if total_ram >= 16 and physical_cores >= 6:
        recommendations.append(
            "Компьютер подходит для одновременной работы нескольких VM."
        )
    for disk in passport["disks"]:
        if disk["used_percent"] > 85:
            disk_name = disk["mountpoint"] or disk["device"]
            recommendations.append(
                f"Освободить место на диске {disk_name}: заполнено "
                f"{disk['used_percent']}%."
            )
    if physical_cores < 4:
        recommendations.append(
            "Процессор может стать узким местом (bottleneck)."
        )
    if memory["used_percent"] >= 85:
        recommendations.append(
            "Высокая текущая загрузка RAM: проверьте процессы, "
            "потребляющие оперативную память."
        )
    if not recommendations:
        recommendations.append(
            "По заданным правилам критических рекомендаций не обнаружено."
        )
    return recommendations


def main():
    passport = {
        "collected_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "system": get_system_info(),
        "cpu": get_cpu_info(),
        "memory": get_memory_info(),
        "disks": get_disk_info(),
        "network": get_network_info(),
    }

    passport["recommendations"] = analyze(passport)

    filename = f"passport_{passport['system']['hostname']}.json"
    with open(filename, "w", encoding="utf-8") as file:
        json.dump(passport, file, indent=2, ensure_ascii=False)

    print(json.dumps(passport, indent=2, ensure_ascii=False))
    print(f"\nПаспорт сохранён в файл {filename}")


if __name__ == "__main__":
    main()
