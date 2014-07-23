from flask import url_for
from flask.ext.script import Manager
from flask.ext.migrate import Migrate, MigrateCommand

from notplastic import create_app, db, DEV_CONFIG

##### THIS IS FOR DEV ENVIRONMENT
from notplastic.mp_creds import MP_CREDS

DEV_CONFIG.update(MP_CREDS)

app = create_app(**DEV_CONFIG)
app.debug = True

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
