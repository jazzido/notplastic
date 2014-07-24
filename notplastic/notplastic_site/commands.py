from flask.ext.script import Manager
from notplastic import db
import models

NotPlasticCommand = Manager(usage='NotPlastic commands')

@NotPlasticCommand.command
def download_codes(project_slug, qty, length=6, max_downloads=5):
    project = db.session.query(models.Project) \
                        .filter(models.Project.slug == project_slug) \
                        .first()

    codes = []
    for _ in range(int(qty)):
        c = models.DownloadCode.get_unique_code(project)
        codes.append(c)
        dc = models.DownloadCode(code=c,
                                 max_downloads=max_downloads,
                                 is_download_card=True,
                                 project=project)
        db.session.add(dc)

    db.session.commit()

    print "Created %d codes for `%s`:" % (len(codes), project.name)
    print
    for c in codes:
        print "\t%s" % c

    print
