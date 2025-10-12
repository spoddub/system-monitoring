import random
from datetime import timedelta

import httpx
from celery import shared_task
from django.conf import settings
from django.db import transaction
from django.utils import timezone

from .metrics_parsers import parse_percent, parse_uptime
from .models import Incident, Machine, MetricsSample


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


# открываем или обновляем
def open_or_update(
    machine, incident_type, first_timeslot, last_timeslot, message
):
    incident = Incident.objects.filter(
        machine=machine, type=incident_type, active=True
    ).first()

    if incident:
        if (  # если есть прогресс или изменилось сообщение
            last_timeslot > incident.last_timeslot
            or message
            and message != incident.details
        ):
            # берем самый аоздний иницидент и перезаписываем чтобы без дубля
            incident.last_timeslot = max(incident.last_timeslot, last_timeslot)
            if message and message != incident.details:
                incident.details = message
            incident.save(update_fields=["last_timeslot", "details"])
        return "updated"

    Incident.objects.create(
        machine=machine,
        type=incident_type,
        active=True,
        started_at=timezone.now(),
        first_timeslot=first_timeslot,
        last_timeslot=last_timeslot,
        details=message or "",
    )

    return "opened"


# закрываем
def close_if_active(machine, incident_type):
    incident = Incident.objects.filter(
        machine=machine, type=incident_type, active=True
    ).first()

    if incident:
        incident.active = False
        incident.resolved_at = timezone.now()
        incident.save(update_fields=["active", "resolved_at"])
        return "closed"
    return "no_change"


# получаем метрики за последние минуты
def get_recent_metrics_window(machine, minutes):
    last_timeslot = (
        MetricsSample.objects.filter(machine=machine)
        .only("timeslot_start", "cpu_pct", "mem_pct", "disk_pct")
        .order_by("-timeslot_start")
        .first()
    )
    if not last_timeslot:
        return [], None

    window_start = last_timeslot.timeslot_start - timedelta(minutes=minutes)
    metrics = list(
        MetricsSample.objects.filter(
            machine=machine,
            timeslot_start__gt=window_start,
            timeslot_start__lte=last_timeslot.timeslot_start,
        )
        .only("timeslot_start", "cpu_pct", "mem_pct", "disk_pct")
        .order_by("timeslot_start")
    )
    return metrics, last_timeslot


@shared_task
def evaluate_incidents():
    now = timezone.now()
    slot = floor_to_15mins(now)

    created = 0
    updated = 0
    resolved = 0

    for m in Machine.objects.filter(is_active=True).only("id"):
        smp = (
            MetricsSample.objects.filter(machine=m, timeslot_start=slot)
            .order_by("-collected_at")
            .first()
        )
        if not smp:
            continue

        cpu_bad = smp.cpu_pct is not None and smp.cpu_pct > 85

        with transaction.atomic():
            active_cpu = (
                Incident.objects.select_for_update()
                .filter(machine=m, type=Incident.Type.CPU, active=True)
                .first()
            )

            if cpu_bad:
                if active_cpu:
                    changed = False
                    if active_cpu.last_timeslot != slot:
                        active_cpu.last_timeslot = slot
                        changed = True
                    details = f"cpu={smp.cpu_pct}% @ {slot.isoformat()}"
                    if active_cpu.details != details:
                        active_cpu.details = details
                        changed = True
                    if changed:
                        active_cpu.save(
                            update_fields=["last_timeslot", "details"]
                        )
                        updated += 1
                else:
                    Incident.objects.create(
                        machine=m,
                        type=Incident.Type.CPU,
                        active=True,
                        started_at=smp.collected_at,
                        resolved_at=None,
                        first_timeslot=slot,
                        last_timeslot=slot,
                        details=f"cpu={smp.cpu_pct}% @ {slot.isoformat()}",
                    )
                    created += 1
            else:
                if active_cpu:
                    active_cpu.active = False
                    active_cpu.resolved_at = smp.collected_at
                    if active_cpu.details is None:
                        active_cpu.details = ""
                    active_cpu.save(
                        update_fields=["active", "resolved_at", "details"]
                    )
                    resolved += 1

    return f"cpu created={created}, updated={updated}, resolved={resolved}"
