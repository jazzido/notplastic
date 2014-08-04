import unittest, json, os

from flask.ext.testing import TestCase
from mixer.backend.flask import mixer
import flask
import mock
import mercadopago

from notplastic import create_app, db, mail
from notplastic import mercadopago_ipn, notplastic_site

PAYMENT_INFO = {
    'response': {u'collection': {u'amount_refunded': 0,
                                 u'collector': {u'email': u'foo@bar.com',
                                                u'first_name': u'Manuel',
                                                u'id': 37156506,
                                                u'last_name': u'Aristar\xe1n',
                                                u'nickname': u'JAZZIDO',
                                                u'phone': {u'area_code': u'0291',
                                                           u'extension': u'',
                                                           u'number': u'424242'}},
                                 u'coupon_amount': 0,
                                 u'coupon_fee': 0,
                                 u'coupon_id': None,
                                 u'currency_id': u'ARS',
                                 u'date_approved': None,
                                 u'date_created': u'2014-07-05T16:40:06.000-04:00',
                                 u'discount_fee': 0,
                                 u'external_reference': u'1',
                                 u'finance_fee': 0,
                                 u'id': 804096907,
                                 u'last_modified': u'2014-07-05T16:40:06.000-04:00',
                                 u'marketplace': u'NONE',
                                 u'marketplace_fee': 0,
                                 u'merchant_order_id': 39115638,
                                 u'money_release_date': None,
                                 u'net_received_amount': 18.8,
                                 u'operation_type': u'regular_payment',
                                 u'order_id': None,
                                 u'payer': {u'email': u'foo@bar.com',
                                            u'first_name': u'',
                                            u'id': 162008512,
                                            u'identification': {u'number': None, u'type': None},
                                            u'last_name': u'yeh',
                                            u'nickname': u'@162008512',
                                            u'phone': {u'area_code': None, u'extension': u'', u'number': None}},
                                 u'payment_type': u'ticket',
                                 u'reason': u'bar bar bar',
                                 u'refunds': [],
                                 u'shipping_cost': 0,
                                 u'site_id': u'MLA',
                                 u'status': u'pending',
                                 u'status_detail': u'pending_waiting_payment',
                                 u'total_paid_amount': 20,
                                 u'transaction_amount': 20}},
    'status': 200
}

PAYMENT_INFO_APPROVED = {
    u'response': {
        u'collection': {u'collector': {u'email': u'test_user_43412472@testuser.com',
                                       u'first_name': u'Test',
                                       u'id': 163048080,
                                       u'last_name': u'Test',
                                       u'nickname': u'TETE4009168',
                                       u'phone': {u'area_code': u'01',
                                                  u'extension': u'',
                                                  u'number': u'1111-1111'}},
                        u'currency_id': u'ARS',
                        u'date_approved': u'2014-07-22T20:13:10-03:00',
                        u'date_created': u'2014-07-22T20:13:10-03:00',
                        u'external_reference': u'1',
                        u'id': 1406070791,
                        u'installments': 1,
                        u'last_modified': u'2014-07-22T20:13:10-03:00',
                        u'marketplace': u'NONE',
                        u'marketplace_fee': 0,
                        u'money_release_date': u'2014-07-22T20:13:10-03:00',
                        u'net_received_amount': 30,
                        u'operation_type': u'regular_payment',
                        u'order_id': u'1',
                        u'payer': {u'email': u'cacarulo@mailinator.com',
                                   u'first_name': u'',
                                   u'id': 163045167,
                                   u'identification': {u'number': None, u'type': None},
                                   u'last_name': u'cacarulo',
                                   u'nickname': u'@163045167',
                                   u'phone': {u'area_code': None, u'extension': u'', u'number': None}},
                        u'payment_method_id': u'visa',
                        u'payment_type': u'credit_card',
                        u'reason': u'El abrigo del viento',
                        u'sandbox': True,
                        u'shipping_cost': 0,
                        u'site_id': u'MLA',
                        u'status': u'approved',
                        u'status_detail': u'accredited',
                        u'total_paid_amount': 30,
                        u'transaction_amount': 30}},
    u'status': 200}


PAYMENT_PREFERENCE_RESPONSE = {'response': {u'additional_info': u'',
                                            u'auto_return': u'',
                                            u'back_urls': {u'failure': u'', u'pending': u'', u'success': u''},
                                            u'client_id': u'963',
                                            u'collector_id': 37156506,
                                            u'date_created': u'2014-07-22T11:00:04.429-04:00',
                                            u'expiration_date_from': None,
                                            u'expiration_date_to': None,
                                            u'expires': False,
                                            u'external_reference': u'',
                                            u'id': u'37156506-b7a70e94-2b7a-46e4-9083-53c8170178fa',
                                            u'init_point': u'https://www.mercadopago.com/mla/checkout/pay?pref_id=37156506-b7a70e94-2b7a-46e4-9083-53c8170178fa',
                                            u'items': [{u'category_id': u'',
                                                        u'currency_id': u'ARS',
                                                        u'description': u'',
                                                        u'id': u'',
                                                        u'picture_url': u'',
                                                        u'quantity': 1,
                                                        u'title': u'El abrigo del viento',
                                                        u'unit_price': 20}],
                                            u'marketplace': u'NONE',
                                            u'marketplace_fee': 0,
                                            u'notification_url': None,
                                            u'operation_type': u'regular_payment',
                                            u'payer': {u'address': {u'street_name': u'',
                                                                    u'street_number': None,
                                                                    u'zip_code': u''},
                                                       u'date_created': u'',
                                                       u'email': u'',
                                                       u'identification': {u'number': u'', u'type': u''},
                                                       u'name': u'',
                                                       u'phone': {u'area_code': u'', u'number': u''},
                                                       u'surname': u''},
                                            u'payment_methods': {u'default_installments': None,
                                                                 u'default_payment_method_id': None,
                                                                 u'excluded_payment_methods': [{u'id': u''}],
                                                                 u'excluded_payment_types': [{u'id': u''}],
                                                                 u'installments': None},
                                            u'sandbox_init_point': u'https://sandbox.mercadopago.com/mla/checkout/pay?pref_id=37156506-b7a70e94-2b7a-46e4-9083-53c8170178fa',
                                            u'shipments': {u'receiver_address': {u'apartment': u'',
                                                                                 u'floor': u'',
                                                                                 u'street_name': u'',
                                                                                 u'street_number': None,
                                                                                 u'zip_code': u''}}},
                               'status': 201}



class NPTest(TestCase):
    def create_app(self):
        self.app = create_app(
            TESTING=True,
            SQLALCHEMY_DATABASE_URI='sqlite://',
            #SQLALCHEMY_ECHO=True,
            MERCADOPAGO_CLIENT_ID='foo',
            MERCADOPAGO_CLIENT_SECRET='bar',
            WTF_CSRF_ENABLED=False,
            DEFAULT_MAIL_SENDER='testing@unabanda.cc',
            PROJECT_FILES_PATH='/foo/bar/quux'
        )
        mixer.init_app(self.app)

        return self.app

    def setUp(self):
        db.create_all(app=self.app)

    def tearDown(self):
        db.session.remove()
        db.drop_all(app=self.app)


class NotPlasticSiteTest(NPTest):

    @mock.patch('notplastic.notplastic_site.views.send_file')
    def test_valid_download_ticket(self, mock_send_file):
        mock_send_file.return_value = self.app.make_response('')
        p = mixer.blend(notplastic_site.models.Project,
                        name=u'foo',
                        file=u'bar')
        c = mixer.blend(notplastic_site.models.DownloadCode,
                       code=u'quux',
                       is_download_card=True,
                       project=p)
        t = mixer.blend(notplastic_site.models.DownloadTicket,
                        ticket=u'foobarquux',
                        time_to_live=1000,
                        download_code=c)

        assert t.downloaded_at is None
        self.client.get('/p/foo/dl/foobarquux')
        mock_send_file.assert_called_with(os.path.join(self.app.config['PROJECT_FILES_PATH'],
                                                       p.file),
                                          as_attachment=True)
        assert t.downloaded_at is not None

    @mock.patch('notplastic.notplastic_site.views.send_file')
    def test_valid_download_code(self, mock_send_file):
        mock_send_file.return_value = self.app.make_response('')
        p = mixer.blend(notplastic_site.models.Project,
                        name=u'foo',
                        file=u'bar')
        c = mixer.blend(notplastic_site.models.DownloadCode,
                       code=u'quux',
                       is_download_card=True,
                       project=p)

        resp = self.client.post('/p/foo/check_download_code',
                                data=dict(download_code='quux'),
                                follow_redirects=True)

        mock_send_file.assert_called_with(os.path.join(self.app.config['PROJECT_FILES_PATH'], p.file), as_attachment=True)

    @mock.patch('notplastic.utils.get_MP_client')
    def test_create_payment_preference(self, mock_get_MP_client):
        mock_get_MP_client.return_value.create_preference.return_value = PAYMENT_PREFERENCE_RESPONSE

        p = mixer.blend(notplastic_site.models.Project,
                        name=u'foo',
                        description=u'quuxor',
                        file=u'bar',
                        amount=42)

        resp = self.client.post('/p/foo/payment',
                                data=dict(amount=42))

        mock_get_MP_client.return_value.create_preference.assert_called_with({
            'external_reference': p.id,
            'back_urls': {
                'failure': 'http://localhost/p/foo/payment/failure',
                'pending': 'http://localhost/p/foo/payment/pending',
                'success': 'http://localhost/p/foo/payment/success'
            },
            'items': [
                {
                    'title': p.name,
                    'description': p.description,
                    'quantity': 1,
                    'currency_id': 'ARS',
                    'unit_price': 42
                }
            ]
        })

        q = db.session.query(notplastic_site.models.MercadoPagoPaymentPreference) \
                      .filter(notplastic_site.models.MercadoPagoPaymentPreference.project == p)
        assert q.count() == 1
        assert q.first().amount == 42
        assert q.first().payment_preference_id == PAYMENT_PREFERENCE_RESPONSE['response']['id']

    @mock.patch('notplastic.utils.get_MP_client')
    def test_dont_create_payment_preference_because_already_exists(self, mock_get_MP_client):
        mock_get_MP_client.return_value.create_preference.return_value = PAYMENT_PREFERENCE_RESPONSE

        p = mixer.blend(notplastic_site.models.Project,
                        name=u'foo',
                        description=u'quuxor',
                        file=u'bar',
                        amount=42)

        mppp = mixer.blend(notplastic_site.models.MercadoPagoPaymentPreference,
                           project=p,
                           payment_preference_id=PAYMENT_PREFERENCE_RESPONSE['response']['id'],
                           amount=42,
                           definition=json.dumps(PAYMENT_PREFERENCE_RESPONSE['response']))

        resp = self.client.post('/p/foo/payment',
                                data=dict(amount=42))

        assert not mock_get_MP_client.return_value.create_preference.called

        q = db.session.query(notplastic_site.models.MercadoPagoPaymentPreference) \
                      .filter(notplastic_site.models.MercadoPagoPaymentPreference.project == p)
        assert q.count() == 1
        assert q.first().amount == 42
        assert q.first().payment_preference_id == PAYMENT_PREFERENCE_RESPONSE['response']['id']




class MercadoPagoIPNTest(NPTest):

    @mock.patch('mercadopago.MP')
    def test_ipn_new_collection(self, mock_mp):
        mock_mp.return_value.get_payment_info.return_value = PAYMENT_INFO
        self.client.post('/mercadopago/ipn?topic=payment&id=4242424242')
        q = db.session.query(mercadopago_ipn.models.Collection) \
                      .filter(mercadopago_ipn.models.Collection.collection_id=='4242424242')
        assert q.count() == 1
        assert len(q.first().statuses) == 1
        assert q.first().statuses[0].status == 'pending'

    @mock.patch('mercadopago.MP')
    def test_ipn_existing_collection(self, mock_mp):

        mock_callback = mock.Mock(spec=lambda: 0)
        mercadopago_ipn.views.signal_ipn_received.connect(mock_callback, self.app)

        c = mixer.blend(mercadopago_ipn.models.Collection, collection_id='4242424242')
        c.statuses.append(mercadopago_ipn.models.CollectionStatus(status='foo', body='quux'))
        db.session.commit()

        mock_mp.return_value.get_payment_info.return_value = PAYMENT_INFO
        self.client.post('/mercadopago/ipn?topic=payment&id=4242424242')
        q = db.session.query(mercadopago_ipn.models.Collection).filter(mercadopago_ipn.models.Collection.collection_id=='4242424242')
        assert q.count() == 1
        assert len(q.first().statuses) == 2
        assert q.first().statuses[0].status == 'foo'
        assert q.first().statuses[1].status == 'pending'

        assert mock_callback.call_args[0][0] == self.app
        assert mock_callback.call_args[1]['collection'] == c

class IntegrationTest(NPTest):

    def test_ipn_received_signal_handler(self):

        p = mixer.blend(notplastic_site.models.Project,
                        name=u'foo',
                        description=u'quuxor',
                        file=u'bar')
        c = mixer.blend(mercadopago_ipn.models.Collection,
                        project_id=p.id,
                        collection_id='4242424242')
        cs = mixer.blend(mercadopago_ipn.models.CollectionStatus,
                         collection=c,
                         status=u'approved',
                         body=json.dumps(PAYMENT_INFO_APPROVED))

        assert db.session.query(notplastic_site.models.DownloadCode).count() == 0
        assert c.email_sent_at is None

        with mail.record_messages() as outbox:
            notplastic_site.signal_handlers.ipn_received(self.app, c)
            assert len(outbox) == 1
            q = db.session.query(notplastic_site.models.DownloadCode)

            assert q.count() == 1
            dc = q.first()

            assert dc.code in outbox[0].body
            assert c.email_sent_at is not None
            assert outbox[0].recipients[0] == cs.payer_email









if __name__ == '__main__':
    unittest.main()
