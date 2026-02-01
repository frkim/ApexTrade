"""Celery application setup with Redis broker."""

from celery import Celery

from app.config import settings

celery_app = Celery(
    "apextrade",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=[
        "app.tasks.backtest",
        "app.tasks.strategy",
        "app.tasks.execution",
        "app.tasks.market_data",
    ],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    # Task timeout: 1 hour hard limit, 55 min soft limit for graceful shutdown
    task_time_limit=3600,
    task_soft_time_limit=3300,
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    # Results expire after 24 hours
    result_expires=86400,
    beat_schedule={
        "evaluate-active-strategies": {
            "task": "app.tasks.strategy.evaluate_active_strategies_task",
            "schedule": 60.0,
        },
    },
)
