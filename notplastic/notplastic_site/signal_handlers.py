# coding: utf-8
import os
from datetime import datetime

from flask import render_template_string
from flask.ext.mail import Message

from notplastic.mercadopago_ipn.views import signal_ipn_received
from notplastic import db, mail, mercadopago_ipn, notplastic_site

def ipn_received(app, collection):
    # send mail to buyer if collection is approved
    cs = db.session.query(mercadopago_ipn.models.CollectionStatus) \
                   .filter(mercadopago_ipn.models.CollectionStatus.collection==collection) \
                   .order_by(mercadopago_ipn.models.CollectionStatus.created_at.desc()) \
                   .first()

    if cs is None or cs.status != 'approved' or collection.email_sent_at is not None:
        return

    project = db.session.query(notplastic_site.models.Project) \
              .filter(notplastic_site.models.Project.id == collection.project_id) \
              .first()

    if project is None:
        abort(500)

    rcpt = cs.payer_email

    # generate a download code
    download_code = notplastic_site.models.DownloadCode(
        code=notplastic_site.models.DownloadCode.get_unique_code(project),
        max_downloads=project.max_downloads,
        mercadopago_collection_id=collection.id,
        project=project
    )

    db.session.add(download_code)

    db.session.commit()

    templ_path = os.path.join(notplastic_site.views.mod.root_path,
                           notplastic_site.views.mod.template_folder,
                           'emails',
                           'download_code.html')

    with open(templ_path) as t:
        msg_body = render_template_string(t.read().decode('utf-8'),
                                          project=project,
                                          download_code=download_code)


    collection.email_sent_at = datetime.now()

    msg = Message(subject=u"Tu código de descarga para %s!" % project.name,
                  recipients=[rcpt],
                  body=msg_body,
                  sender=(app.config['DEFAULT_MAIL_SENDER'], app.config['DEFAULT_MAIL_SENDER']))

    if not app.debug:
        mail.send(msg)
    else:
        print "SENDING MAIL: %s" % msg

    db.session.add(collection)

    db.session.commit()


signal_ipn_received.connect(ipn_received)
