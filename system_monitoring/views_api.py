# system_monitoring/views_api.py

import json
import time
from datetime import datetime, timedelta

from django.http import JsonResponse, StreamingHttpResponse
from django.utils import timezone

from .models import Incident


def apply_active(qs, active_flag):
    active_filter_value = (active_flag or "").lower()
    if active_filter_value == "true":
        return qs.filter(active=True)
    elif active_filter_value == "false":
        return qs.filter(active=False)
    return qs


def serialize(qs):
    items = []
    for i in qs:
        items.append(
            {
                "id": i.id,
                "machine": str(i.machine),
                "machine_id": i.machine_id,
                "type": i.type,
                "active": i.active,
                "started_at": i.started_at.isoformat(),
                "resolved_at": i.resolved_at.isoformat()
                if i.resolved_at
                else None,
                "first_timeslot": i.first_timeslot.isoformat(),
                "last_timeslot": i.last_timeslot.isoformat(),
                "details": i.details,
            }
        )
    return items


def parse_since(since_param):
    if not since_param:
        return timezone.now() - timedelta(seconds=1)
    try:
        since_param = since_param.replace("Z", "+00:00")
        return datetime.fromisoformat(since_param)
    except Exception:
        return timezone.now() - timedelta(seconds=1)


def changed_since_list(since, active_flag):
    base = apply_active(
        Incident.objects.all().select_related("machine"), active_flag
    )

    l1 = list(base.filter(created_at__gt=since))
    l2 = list(base.filter(last_timeslot__gt=since))
    l3 = list(base.filter(resolved_at__gt=since))

    by_id = {}
    for it in l1 + l2 + l3:
        by_id[it.pk] = it

    items = list(by_id.values())
    items.sort(key=lambda x: x.created_at, reverse=True)
    return items


def incidents_list(request):
    active = (request.GET.get("active") or "true").lower()
    try:
        limit = int(request.GET.get("limit") or "100")
    except ValueError:
        limit = 100
    try:
        offset = int(request.GET.get("offset") or "0")
    except ValueError:
        offset = 0

    qs = Incident.objects.select_related("machine").order_by("-started_at")
    qs = apply_active(qs, active)

    total = qs.count()
    page = qs[offset : offset + limit]
    data = serialize(page)

    return JsonResponse(
        {
            "total": total,
            "items": data,
            "server_time": timezone.now().isoformat(),
        }
    )


def stream_incident_updates(since, active_flag):
    deadline = time.time() + 120.0
    last_seen = since

    while time.time() < deadline:
        changed = changed_since_list(last_seen, active_flag)
        if changed:
            max_created = max(it.created_at for it in changed)
            max_last_ts = max(
                (it.last_timeslot for it in changed), default=max_created
            )
            max_resolved = max(
                (it.resolved_at for it in changed if it.resolved_at),
                default=max_created,
            )
            last_seen = max(max_created, max_last_ts, max_resolved)

            payload = {
                "items": serialize(changed),
                "ts": timezone.now().isoformat(),
            }
            body = json.dumps(payload).encode("utf-8")
            yield b"event: incidents\n"
            yield b"data: " + body + b"\n\n"
        else:
            yield b": ping\n\n"

        time.sleep(2.0)


def incidents_stream(request):
    active = (request.GET.get("active") or "true").lower()
    since = parse_since(request.GET.get("since"))

    response = StreamingHttpResponse(
        stream_incident_updates(since, active),
        content_type="text/event-stream",
    )
    response["Cache-Control"] = "no-cache"
    response["X-Accel-Buffering"] = "no"
    return response
