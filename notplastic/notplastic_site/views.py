from datetime import datetime
from urlparse import urlparse
import os

from flask import Blueprint, request, abort, send_file, redirect, url_for, render_template, make_response, session
from flask.ext.cors import cross_origin

from notplastic import db, limiter, csrf
import models, forms

mod = Blueprint('notplastic_site',
                __name__,
                url_prefix='/p',
                template_folder='templates',
                static_folder='static')#,
                #static_url_path='/%s' % __name__)

@mod.route('/<project>/embed')
def embed(project):
    p = db.session.query(models.Project) \
                  .filter(models.Project.slug==project) \
                  .first()
    if p is None:
        abort(404)

    embed_css_contents = ''
    with open(os.path.join(mod.static_folder, 'css/embed.css')) as f:
        embed_css_contents = f.read()

    response = make_response(render_template('embed.js',
                                             embed_content=render_template('embed_content.html',
                                                                           project=p,
                                                                           form=forms.DownloadCode(),
                                                                           css=embed_css_contents),
                                             project=p))
    response.headers['Content-Type'] = 'text/javascript'
    return response

@mod.route('/_sess')
def session_init():
    session['origin##%s' % reques.args.get('_embedGUID')] = request.args.get('_ref')
    r = make_response('', 200)
    r.headers['Content-Type'] = 'text/javascript'
    return r

@mod.route('/<project>/<ticket>')
def download(project, ticket):

    p = db.session.query(models.Project) \
                  .join(models.DownloadCode) \
                  .join(models.DownloadTicket) \
                  .filter(models.Project.slug==project) \
                  .filter(models.DownloadTicket.ticket==ticket) \
                  .first()

    if p is None:
        abort(404)

    t = db.session.query(models.DownloadTicket) \
                  .join(models.DownloadCode) \
                  .join(models.Project) \
                  .filter(models.DownloadTicket.ticket==ticket) \
                  .first()


    if (t is None) or (t.downloaded_at is not None) or t.has_expired():
        abort(404)

    t.downloaded_at = datetime.now()

    db.session.add(t)
    db.session.commit()

    # TODO: corregir path del send_file
    return send_file(p.file, as_attachment=True)

@mod.route('/<project>/check_download_code', methods=['POST'])
@limiter.limit('5/minute')
def validate_download_code(project):

    def inner(*args, **kwargs):
        p = db.session.query(models.Project) \
                      .filter(models.Project.slug==project) \
                      .first()

        if p is None:
            return make_response('', 404)

        download_code = request.form.get('download_code')

        if download_code is None:
            return make_response('', 400)

        c = db.session.query(models.DownloadCode) \
                      .filter(models.DownloadCode.project==p) \
                      .filter(models.DownloadCode.code==download_code.lower().strip()) \
                      .first()

        if c is None:
            return make_response('', 404)

        used_tickets = c.times_downloaded()

        if used_tickets >= c.max_downloads:
            make_response('', 410) # TODO: fijarse si este status code esta bien

        # create new ticket and redirect
        t = models.DownloadTicket(download_code=c,
                                  ticket=models.DownloadTicket.get_unique_ticket())
        db.session.add(t)
        db.session.commit()

        return redirect(url_for('.download', project=p.slug, ticket=t.ticket))

    cors = cross_origin(methods=['POST'],
                        supports_credentials=True,
                        origins=[session.get('origin')])
    return cors(inner)()

# @csrf.error_handler
# def csrf_error(reason):
#     print 'cacarulo'
#     return 'mierda', 400
