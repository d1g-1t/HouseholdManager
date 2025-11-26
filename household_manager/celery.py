import os

from celery import Celery
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "household_manager.settings")

app = Celery("household_manager")

app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

app.conf.task_routes = {
    "apps.receipts.tasks.*": {"queue": "ocr"},
    "apps.ml_categorizer.tasks.*": {"queue": "ml"},
    "apps.notifications.tasks.*": {"queue": "notifications"},
}

app.conf.beat_schedule = {
    "retrain-ml-model-daily": {
        "task": "apps.ml_categorizer.tasks.retrain_categorization_model",
        "schedule": crontab(hour=3, minute=0),
        "options": {"queue": "ml"},
    },
    "send-daily-budget-summary": {
        "task": "apps.notifications.tasks.send_daily_budget_summary",
        "schedule": crontab(hour=20, minute=0),
        "options": {"queue": "notifications"},
    },
    "send-monthly-report": {
        "task": "apps.analytics.tasks.generate_monthly_reports",
        "schedule": crontab(day_of_month=1, hour=9, minute=0),
        "options": {"queue": "default"},
    },
    "cleanup-old-receipts": {
        "task": "apps.receipts.tasks.cleanup_old_receipt_images",
        "schedule": crontab(hour=2, minute=0, day_of_week=0),
        "options": {"queue": "default"},
    },
}


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f"Request: {self.request!r}")
