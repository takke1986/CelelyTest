import os
from celery import Celery
from django.conf import settings

# Djangoの設定モジュールを指定
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shopping_calculator.settings')

# Celeryアプリケーションを作成
app = Celery('shopping_calculator')

# Djangoの設定を読み込む
app.config_from_object('django.conf:settings', namespace='CELERY')

# 登録されたDjangoアプリケーションから@shared_taskを探す
app.autodiscover_tasks()

# Celeryの設定を更新
app.conf.update(
    task_track_started=True,
    task_time_limit=60,  # タイムアウトを60秒に設定
    broker_connection_max_retries=None,
    worker_prefetch_multiplier=1,
)

# 非同期実行を強制
app.conf.task_always_eager = False

# 開発環境でも非同期実行を維持
if settings.DEBUG:
    app.conf.task_eager_propagates = True