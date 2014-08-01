from datetime import datetime
from urlparse import urlparse
import os, json

from flask import Blueprint, request, abort, send_file, redirect, url_for, render_template, make_response, session, current_app
from flask.ext.cors import cross_origin

from notplastic import db, limiter, csrf
from notplastic.mercadopago_ipn import models as mp_models
import models, forms, signal_handlers

mod = Blueprint('notplastic_site',
                __name__,
                url_prefix='/p',
                template_folder='templates',
                static_folder='static')

@mod.route('/<project>')
def index(project):
    p = db.session.query(models.Project) \
                  .filter(models.Project.slug==project) \
                  .first()
    if p is None:
        abort(404)

    return render_template('project_landing.html',
                           project=p,
                           download_code_form=forms.DownloadCode(),
                           payment_form=forms.Payment())


@mod.route('/<project>/dl/<ticket>')
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
        abort(410)

    t.downloaded_at = datetime.now()

    db.session.add(t)
    db.session.commit()

    return send_file(os.path.join(current_app.config['PROJECT_FILES_PATH'],
                                  p.file),
                     as_attachment=True)

@mod.route('/<project>/check_download_code', methods=['POST'])
@limiter.limit('5/minute')
def validate_download_code(project):
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

@mod.route('/<project>/payment', methods=['POST'])
def payment(project):
    p = db.session.query(models.Project) \
                  .filter(models.Project.slug==project) \
                  .first()

    if p is None:
        return make_response('', 404)

    form = forms.Payment(request.form)

    amount = form.data['amount'] if p.is_variable_price else int(p.amount)

    # if not form.validate():
    #     return make_response('', 400)

    mppp = db.session.query(models.MercadoPagoPaymentPreference) \
                     .filter(models.MercadoPagoPaymentPreference.project == p) \
                     .filter(models.MercadoPagoPaymentPreference.amount == amount) \
                     .first()

    # if no preference created for this amount, create a new one
    if mppp is None:
        mppp = models.MercadoPagoPaymentPreference \
                     .save_to_mercadopago(models.MercadoPagoPaymentPreference(project=p,
                                                                              amount=amount))

        db.session.add(mppp)
        db.session.commit()

    mppp_def = json.loads(mppp.definition)

    return redirect(mppp_def['init_point']
                    if not current_app.config.get('MERCADOPAGO_USE_SANDBOX')
                    else mppp_def['sandbox_init_point'])

# http://dev.local.unabanda.cc:5000/p/el-abrigo-del-viento/payment/pending?collection_id=1406141035&collection_status=pending&preference_id=163048080-833a476d-9dd4-430e-b5a1-235fb65ddb39&external_reference=1&payment_type=credit_card
@mod.route('/<project>/payment/<status>')
def payment_confirmation(project, status):
    p = db.session.query(models.Project) \
                  .filter(models.Project.slug==project) \
                  .first()

    if p is None or status not in ('success', 'failure', 'pending'):
        return abort(404)

    if db.session.query(models.MercadoPagoPaymentPreference) \
                 .filter(models.MercadoPagoPaymentPreference.project == p) \
                 .filter(models.MercadoPagoPaymentPreference.payment_preference_id == request.args['preference_id']) \
                 .count() != 1:
        abort(400)

    template_vars = {
        'status': status,
        'project': p,
        'message': '',
    }

    if status == 'success':
        # Check if we received an IPN notification of the successful payment
        cs = db.session.query(mp_models.CollectionStatus) \
                       .join(mp_models.Collection) \
                       .filter(mp_models.Collection.collection_id == request.args['collection_id']) \
                       .filter(mp_models.CollectionStatus.status == 'approved').first()

        if cs is not None:
            download_code = db.session.query(models.DownloadCode) \
                                      .filter(models.DownloadCode.mercadopago_collection_id==cs.collection.id) \
                                      .first()
            template_vars.update({
                'download_code': download_code,
            })
        else:
            # MP reports payment approved (or user trying to forge the query string)
            # but we didn't receive the IPN yet, force 'pending' state.
            template_vars.update({
                'status': 'pending',
                'collection_id': request.args.get('collection_id')
            })

    elif status == 'pending':
        template_vars['collection_id'] = request.args.get('collection_id')
    elif status == 'failure':
        pass

    return make_response(render_template('payment_confirmation.html',
                                         **template_vars))

# @mod.route('/<project>/embed')
# def embed(project):
#     p = db.session.query(models.Project) \
#                   .filter(models.Project.slug==project) \
#                   .first()
#     if p is None:
#         abort(404)

#     embed_css_contents = ''
#     with open(os.path.join(mod.static_folder, 'css/embed.css')) as f:
#         embed_css_contents = f.read()

#     r = make_response(render_template('embed.js',
#                                       embed_content=render_template('embed_content.html',
#                                                                     project=p,
#                                                                     form=forms.DownloadCode(),
#                                                                     css=embed_css_contents),
#                                       project=p))
#     r.headers['Content-Type'] = 'text/javascript'
#     return r
