import json

from flask import Blueprint, jsonify, current_app, request, abort
import mercadopago
import blinker

import models
from notplastic import db

mod = Blueprint('mercadopago_ipn', __name__, url_prefix='/mercadopago')

signals = blinker.Namespace()
signal_ipn_received = signals.signal('ipn-received')

@mod.route('/ipn', methods=['POST'])
def ipn():

    if not ((request.args.get('topic') == 'payment') and ('id' in request.args)):
        abort(400)

    mp = mercadopago.MP(current_app.config['MERCADOPAGO_CLIENT_ID'],
                        current_app.config['MERCADOPAGO_CLIENT_SECRET'])

    collection_id = request.args['id']

    try:
        payment_info = mp.get_payment_info(collection_id)
    except:
        abort(400)

    # get collection, if exists. otherwise, create
    c = models.Collection.query.filter(models.Collection.collection_id==collection_id).first()
    if c is None:
        c = models.Collection(collection_id=collection_id)
        db.session.add(c)

    status = models.CollectionStatus(status=payment_info['response']['collection']['status'],
                                     body=json.dumps(payment_info))
    c.statuses.append(status)

    db.session.commit()

    signal_ipn_received.send(current_app._get_current_object(), collection=c)

    return '              '
