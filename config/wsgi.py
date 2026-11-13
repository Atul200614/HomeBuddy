"""
WSGI config for HomeBuddy project.
"""
import os
import sys
import shutil
from pathlib import Path
from django.core.wsgi import get_wsgi_application

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

IS_VERCEL = os.path.exists('/var/task') or bool(os.environ.get('VERCEL'))

# Copy SQLite database into writable /tmp folder on Vercel
if IS_VERCEL:
    tmp_db = Path('/tmp/db.sqlite3')
    bundled_db = BASE_DIR / 'homebuddy.sqlite3'
    if not bundled_db.exists():
        bundled_db = Path('/var/task/homebuddy.sqlite3')

    if not tmp_db.exists() and bundled_db.exists():
        try:
            shutil.copy2(bundled_db, tmp_db)
        except Exception as e:
            print(f"Error copying bundled db: {e}")

application = get_wsgi_application()

# Wrap with WhiteNoise to serve static files reliably
try:
    from whitenoise import WhiteNoise
    static_dir = BASE_DIR / 'staticfiles'
    if not static_dir.exists():
        static_dir = BASE_DIR / 'static'
    if not static_dir.exists():
        static_dir = Path('/var/task/staticfiles')
    if not static_dir.exists():
        static_dir = Path('/var/task/static')

    if static_dir.exists():
        application = WhiteNoise(application, root=str(static_dir), prefix='/static/')
except Exception as e:
    print(f"WhiteNoise WSGI notice: {e}")

app = application
