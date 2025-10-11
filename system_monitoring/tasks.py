import random

import httpx
from celery import shared_task
from django.conf import settings
from django.utils import timezone

from .metrics_parsers import parse_percent, parse_uptime
from .models import Machine, MetricsSample


def floor_to_15mins(dt):
    minute = dt.minute - (dt.minute % 15)  # 0/15/30/45
    return dt.replace(minute=minute, second=0, microsecond=0)


@shared_task  # для автодискавер в celery
def collect_metrics(machine_id):
    now = timezone.now()
    timeslot = floor_to_15mins(now)

    machine = Machine.objects.filter(pk=machine_id, is_active=True).first()
    if not machine:
        return "Machine not found"

    timeout = httpx.Timeout(
        timeout=settings.REQUEST_READ_TIMEOUT,
        connect=settings.REQUEST_CONNECT_TIMEOUT,
        read=settings.REQUEST_READ_TIMEOUT,
        write=settings.REQUEST_READ_TIMEOUT,
        pool=settings.REQUEST_CONNECT_TIMEOUT,
    )
    with httpx.Client(timeout=timeout) as client:
        response = client.get(machine.url)
    response.raise_for_status()  # проверяем код ответа, если 400-599 ошибка

    data = response.json()
    cpu = int(float(data["cpu"]))
    mem = parse_percent(data["mem"])
    disk = parse_percent(data["disk"])
    uptime = parse_uptime(str(data["uptime"]))
    MetricsSample.objects.create(  # INSERT
        machine=machine,  # id
        collected_at=now,
        timeslot_start=timeslot,
        cpu_pct=cpu,
        mem_pct=mem,
        disk_pct=disk,
        uptime_sec=uptime,
    )
    return "Metrics collected succesfully"


@shared_task
def schedule_collecting():
    machines = list(Machine.objects.filter(is_active=True))
    for machine in machines:
        delay = random.randint(0, machine.jitter_sec)
        collect_metrics.apply_async(  # метод celery для поставки в очередь
            kwargs={"machine_id": machine.pk}, countdown=delay
        )
    return f"scheduled {len(machines)} polls"
