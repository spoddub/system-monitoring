from django.db import models


# удаленная машина
class Machine(models.Model):
    name = models.CharField(max_length=150, unique=True)
    url = models.URLField()
    # вкл выкл машины
    is_active = models.BooleanField(default=True)
    # задержка в сек
    jitter_sec = models.PositiveBigIntegerField(default=120)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]  # order_by

    def __str__(self) -> str:
        return super().__str__()


# чтение изменений
class MetricsSample(models.Model):
    machine = models.ForeignKey(Machine, on_delete=models.CASCADE)

    collected_at = models.DateTimeField()
    timeslot_start = models.DateTimeField()  # начало 15 минут

    cpu_pct = models.PositiveIntegerField(null=True, blank=True)
    mem_pct = models.PositiveIntegerField(null=True, blank=True)
    disk_pct = models.PositiveIntegerField(null=True, blank=True)
    uptime_sec = models.BigIntegerField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-collected_at"]  # - сначала новые

    def __str__(self) -> str:
        return super().__str__()


class Incident(models.Model):
    class Type(models.TextChoices):
        CPU = "cpu", "CPU > 85%"
        MEM = "mem", "Memory > 90% (30m)"
        DISK = "disk", "Disk > 95% (2h)"

    machine = models.ForeignKey(Machine, on_delete=models.CASCADE)
    # значения только из Type
    type = models.CharField(max_length=10, choices=Type.choices)
    active = models.BooleanField(default=True, db_index=True)

    started_at = models.DateTimeField()  # начало инцидента
    resolved_at = models.DateTimeField(null=True, blank=True)

    first_timeslot = models.DateTimeField()  # в каком таймслоте началось
    last_timeslot = models.DateTimeField()  # последний таймслот с инцидентом

    details = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-started_at"]  # сначала новые
        # mysql фильтр для поиска
        indexes = [
            models.Index(fields=["machine", "type", "active"]),
        ]

    def __str__(self) -> str:
        incident_type = Incident.Type(self.type).label
        status = "ACTIVE" if self.active else "SOLVED"
        return f"Incident {incident_type} is {status}"
