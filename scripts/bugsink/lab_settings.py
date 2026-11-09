from bugsink.settings.default import *
from pathlib import Path
import os
ROOT = Path(os.environ['LAB_STATE']).resolve()
SECRET_KEY = (ROOT / 'django-key').read_text()
ALLOWED_HOSTS = ['127.0.0.1']
DATABASES = {name: {'ENGINE': 'django.db.backends.sqlite3', 'NAME': str(ROOT / (name + '.sqlite3'))} for name in ['default', 'snappea']}
SNAPPEA = {'TASK_ALWAYS_EAGER': True, 'PID_FILE': str(ROOT / 'snappea.pid'), 'WAKEUP_CALLS_DIR': str(ROOT / 'wakeup')}
BUGSINK = {'BASE_URL': os.environ['LAB_BASE_URL'], 'PHONEHOME': False, 'INGEST_STORE_BASE_DIR': str(ROOT / 'ingestion'), 'EVENT_STORAGES': {}, 'OBJECT_STORAGES': {}, 'ALERTS_WEBHOOK_OUTBOUND_MODE': 'allowlist_only', 'ALERTS_WEBHOOK_ALLOW_LIST': [], 'MAX_EMAILS_PER_MONTH': 0}
# Empty storage maps explicitly use the fresh SQLite database for events/files.
EMAIL_BACKEND = 'django.core.mail.backends.dummy.EmailBackend'
MEDIA_ROOT = str(ROOT / 'media')
STATIC_ROOT = str(ROOT / 'static')
LOGGING = {'version': 1, 'disable_existing_loggers': True, 'handlers': {'null': {'class': 'logging.NullHandler'}}, 'root': {'handlers': ['null'], 'level': 'CRITICAL'}}
