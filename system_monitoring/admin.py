from django.contrib import admin

from .models import Incident, Machine, MetricsSample, MonitorUser


@admin.register(Machine)
class MachineAdmin(admin.ModelAdmin):
    list_display = ("name", "url", "jitter_sec", "updated_at")
    list_filter = ()
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


@admin.register(Incident)
class IncidentAdmin(admin.ModelAdmin):
    list_display = (
        "machine",
        "type",
        "active",
        "started_at",
        "resolved_at",
        "first_timeslot",
        "last_timeslot",
        "details",
    )
    list_filter = ("type", "active", "machine")
    search_fields = ("machine__name", "details")


@admin.register(MonitorUser)
class MonitorUserAdmin(admin.ModelAdmin):
    list_display = ("username", "created_at")
    search_fields = ("username",)
