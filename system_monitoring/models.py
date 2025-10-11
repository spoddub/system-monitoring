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
