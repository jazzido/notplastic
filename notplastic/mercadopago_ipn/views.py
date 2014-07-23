import json

from flask import Blueprint, jsonify, current_app, request, abort
import mercadopago
import blinker

import models
from notplastic import db, utils, csrf

mod = Blueprint('mercadopago_ipn', __name__, url_prefix='/mercadopago')

signals = blinker.Namespace()
signal_ipn_received = signals.signal('ipn-received')

@csrf.exempt
@mod.route('/ipn', methods=['POST'])
def ipn():

    # if not ((request.args.get('topic') == 'payment') and ('id' in request.args)):
    #     abort(400)

    mp = utils.get_MP_client()

    collection_id = request.args['id']

    payment_info = mp.get_payment_info(collection_id)

    # get collection, if exists. otherwise, create
    c = models.Collection.query.filter(models.Collection.collection_id==collection_id).first()
    if c is None:
        c = models.Collection(
            collection_id=collection_id,
            project_id=int(payment_info['response']['collection']['external_reference'])
        )
        db.session.add(c)

    status = models.CollectionStatus(status=payment_info['response']['collection']['status'],
                                     body=json.dumps(payment_info),
                                     collection=c)
    db.session.add(status)

    db.session.commit()

    signal_ipn_received.send(current_app._get_current_object(), collection=c)

    return '              '
