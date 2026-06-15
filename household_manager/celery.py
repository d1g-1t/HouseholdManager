import os
from importlib import import_module

from celery import Celery
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "household_manager.settings")

app = Celery("household_manager")

app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

_task_routes: dict[str, dict[str, str]] = {}
_beat_schedule: dict[str, dict[str, object]] = {}

_route_defs = {
    "apps.receipts.tasks": {"queue": "ocr"},
    "apps.ml_categorizer.tasks": {"queue": "ml"},
    "apps.notifications.tasks": {"queue": "notifications"},
}

for module_path, route in _route_defs.items():
    try:
        import_module(module_path)
        _task_routes[f"{module_path}.*"] = route
    except ImportError:
        pass

_beat_defs = [
    ("retrain-ml-model-daily", "apps.ml_categorizer.tasks.retrain_categorization_model", crontab(hour=3, minute=0), {"queue": "ml"}),
    ("send-daily-budget-summary", "apps.notifications.tasks.send_daily_budget_summary", crontab(hour=20, minute=0), {"queue": "notifications"}),
    ("send-monthly-report", "apps.analytics.tasks.generate_monthly_reports", crontab(day_of_month=1, hour=9, minute=0), {"queue": "default"}),
    ("cleanup-old-receipts", "apps.receipts.tasks.cleanup_old_receipt_images", crontab(hour=2, minute=0, day_of_week=0), {"queue": "default"}),
]

for name, task_path, schedule, options in _beat_defs:
    try:
        import_module(".".join(task_path.split(".")[:-1]))
        _beat_schedule[name] = {"task": task_path, "schedule": schedule, "options": options}
    except ImportError:
        pass

app.conf.task_routes = _task_routes
app.conf.beat_schedule = _beat_schedule


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f"Request: {self.request!r}")
