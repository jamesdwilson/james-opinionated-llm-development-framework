"""Fresh-state bootstrap only. Never load an existing conf, env file or database."""
import os, json, secrets, logging, sys
from pathlib import Path
from wsgiref.simple_server import make_server, WSGIRequestHandler
os.umask(0o077)
logging.disable(logging.CRITICAL)
control_out, control_err = sys.stdout, sys.stderr
sys.stdout = sys.stderr = open(os.devnull, 'w')
class Quiet(WSGIRequestHandler):
    def log_message(self, *args): pass
root = Path(os.environ['LAB_STATE'])
try:
    with os.fdopen(os.open(root / 'django-key', os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600), 'w') as f: f.write(secrets.token_hex(32))
    server = make_server('127.0.0.1', 0, lambda e,s: [], handler_class=Quiet)
    assert server.server_port != 8100
    (root / 'listener.json').write_text(json.dumps({'port':server.server_port,'pid':os.getpid()}))
    fail = os.environ.get('LAB_FAIL')
    if fail in {'bootstrap', 'output'}:
        (root / 'failure-reached.json').write_text(json.dumps({'mode': fail}))
    if fail == 'bootstrap': raise RuntimeError()
    if fail == 'output':
        print('x' * 100000, file=control_out, flush=True)
        raise RuntimeError()
    os.environ['LAB_BASE_URL'] = 'http://127.0.0.1:' + str(server.server_port)
    os.environ['DJANGO_SETTINGS_MODULE'] = 'lab_settings'
    import django
    django.setup()
    from django.core.management import call_command
    from io import StringIO
    for db in ['default', 'snappea']:
        call_command('migrate', database=db, interactive=False, verbosity=0, stdout=StringIO(), stderr=StringIO())
    from teams.models import Team
    from projects.models import Project
    from bsmain.models import AuthToken
    assert Team.objects.count() == Project.objects.count() == AuthToken.objects.count() == 0
    team = Team.objects.create(name='Isolated methodology lab')
    project = Project.objects.create(team=team, name='Isolated canary')
    token = AuthToken.objects.create(
        description='Lab verification; project-bound canonical reads',
        is_project_bound=True,
        project=project,
        projects_read=True,
        issues_read=True,
        events_read=True,
    )
    from importlib.metadata import version
    assert version('bugsink') == '2.6.3'
    payload = {'dsn': project.dsn, 'token': token.token, 'project': project.pk, 'port': server.server_port, 'version': version('bugsink')}
    with os.fdopen(os.open(root / 'runtime.json', os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600), 'w') as f: json.dump(payload, f)
    from django.core.wsgi import get_wsgi_application
    server.set_app(get_wsgi_application())
    print('READY', file=control_out, flush=True)
    server.serve_forever()
except BaseException:
    print('Isolated Bugsink setup failed', file=control_err, flush=True)
    sys.exit(1)
