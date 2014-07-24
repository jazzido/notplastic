import os
from flask import url_for
from flask.ext.script import Manager
from flask.ext.migrate import Migrate, MigrateCommand

from notplastic import create_app, db, DEV_CONFIG, prod_config


conf = {}
if not os.environ.get('PROD'):
    ##### THIS IS FOR DEV ENVIRONMENT
    from notplastic.mp_creds import MP_CREDS
    conf = DEV_CONFIG
    conf.update(MP_CREDS)
else:
    conf = prod_config.PROD_CONFIG

app = create_app(**conf)
app.debug = not os.environ.get('PROD') is None

migrate = Migrate(app, db)

manager = Manager(app)
manager.add_command('db', MigrateCommand)

@manager.command
def list_routes():
    import urllib
    output = []
    for rule in app.url_map.iter_rules():
        options = {}
        for arg in rule.arguments:
            options[arg] = "[{0}]".format(arg)

        methods = ','.join(rule.methods)
        url = url_for(rule.endpoint, **options)
        line = urllib.unquote("{:50s} {:20s} {}".format(rule.endpoint, methods, url))
        output.append(line)

    for line in sorted(output):
        print line

if __name__ == '__main__':
    manager.run()
