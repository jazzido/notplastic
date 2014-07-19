import unittest

from flask.ext.testing import TestCase
from mixer.backend.flask import mixer
import flask
import mock
import mercadopago

from notplastic import create_app, db
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
                                 u'external_reference': None,
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

class NPTest(TestCase):
    def create_app(self):
        self.app = create_app(
            TESTING=True,
            SQLALCHEMY_DATABASE_URI='sqlite://',
            MERCADOPAGO_CLIENT_ID='foo',
            MERCADOPAGO_CLIENT_SECRET='bar'
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
        self.client.get('/p/foo/foobarquux')
        mock_send_file.assert_called_with(p.file, as_attachment=True)
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

        mock_send_file.assert_called_with(p.file, as_attachment=True)



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


if __name__ == '__main__':
    unittest.main()
