from django.contrib import admin

from .models import Machine, MetricsSample


@admin.register(Machine)
class MachineAdmin(admin.ModelAdmin):
    list_display = ("name", "url", "is_active", "jitter_sec", "updated_at")
    list_filter = ("is_active",)
    search_fields = ("name", "url")


@admin.register(MetricsSample)
class MetricsSampleAdmin(admin.ModelAdmin):
    list_display = (
        "machine",
        "collected_at",
        "timeslot_start",
        "cpu_pct",
        "mem_pct",
        "disk_pct",
        "uptime_sec",
    )
    list_filter = ("machine",)
    search_fields = ("machine__name",)
