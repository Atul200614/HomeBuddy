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
    if not tmp_db.exists() and bundled_db.exists():
        shutil.copy2(bundled_db, tmp_db)

application = get_wsgi_application()
app = application

# Automatically create or update database tables on Vercel
if IS_VERCEL:
    from django.core.management import call_command
    try:
        call_command('migrate', '--noinput')
    except Exception as e:
        print(f"Migration notice: {e}")