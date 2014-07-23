from flask import current_app
import mercadopago

def get_MP_client():
    mp = mercadopago.MP(current_app.config['MERCADOPAGO_CLIENT_ID'],
                        current_app.config['MERCADOPAGO_CLIENT_SECRET'])

    # are we in sandbox mode?
    mp.sandbox_mode(current_app.config.get('MERCADOPAGO_USE_SANDBOX', False))

    return mp
