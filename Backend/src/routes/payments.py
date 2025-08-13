from flask.views import MethodView
from flask_smorest import Blueprint
from flask import request, jsonify, current_app, g
from src.utils.auth import verify_supabase_token
from supabase import create_client, Client
from decimal import Decimal, ROUND_HALF_UP
import os
import base64
import hmac
import hashlib
import json
import uuid
import requests
import time


blp = Blueprint('Payments', __name__, description='PayTR payment operations')


def _get_supabase_client() -> Client:
    supabase_url = current_app.config['SUPABASE_URL']
    supabase_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY') or os.getenv('SUPABASE_ANON_KEY')
    return create_client(supabase_url, supabase_key)


def _get_client_ip(flask_request) -> str:
    # Prefer X-Forwarded-For when behind proxies; else fall back to remote_addr
    xff = flask_request.headers.get('X-Forwarded-For', '')
    if xff:
        return xff.split(',')[0].strip()
    return flask_request.remote_addr or ''


def _to_kurus(amount_tl_str: str) -> int:
    # Convert TL string like "9.99" to integer kuruş 999 using Decimal
    amount = Decimal(amount_tl_str).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    return int((amount * 100).to_integral_value(rounding=ROUND_HALF_UP))


def _build_user_basket_base64(items):
    """
    items: list of dicts with keys: name (str), price (string like '18.00'), quantity (int)
    PayTR expects: [[name, price, quantity], ...] as JSON string then base64 encoded
    """
    basket_matrix = []
    for item in items:
        basket_matrix.append([
            str(item.get('name', 'Item')),
            str(item.get('price', '0.00')),
            int(item.get('quantity', 1)),
        ])
    basket_json = json.dumps(basket_matrix, ensure_ascii=False)
    return base64.b64encode(basket_json.encode('utf-8')).decode('utf-8'), basket_matrix


def _compute_payment_amount_kurus_from_basket(basket_matrix) -> int:
    total = Decimal('0.00')
    for row in basket_matrix:
        # row: [name, price_str, qty]
        price = Decimal(str(row[1]))
        qty = Decimal(str(row[2]))
        total += price * qty
    return int((total * 100).to_integral_value(rounding=ROUND_HALF_UP))


def _create_paytr_token(params: dict) -> dict:
    response = requests.post('https://www.paytr.com/odeme/api/get-token', data=params, timeout=30)
    try:
        data = response.json()
    except Exception:
        return { 'status': 'error', 'reason': response.text }
    return data


@blp.route('/payments/paytr/session')
class CreatePaytrSession(MethodView):
    @verify_supabase_token
    def post(self):
        """
        Create PayTR payment session and persist an order in Supabase.
        Request JSON:
        {
          "items": [{"name": "Pro Plan", "price": "9.99", "quantity": 1}],
          "customer": {"email": str, "name": str, "address": str, "phone": str},
          "no_installment": 0|1 (optional),
          "max_installment": number (optional),
          "currency": "TL" (optional)
        }
        """
        body = request.get_json() or {}

        items = body.get('items') or []
        if not items:
            return jsonify({ 'error': 'items is required' }), 400

        customer = body.get('customer') or {}

        user_basket_b64, basket_matrix = _build_user_basket_base64(items)
        payment_amount_kurus = _compute_payment_amount_kurus_from_basket(basket_matrix)

        merchant_id = os.getenv('PAYTR_MERCHANT_ID', '')
        merchant_key = os.getenv('PAYTR_MERCHANT_KEY', '')
        merchant_salt = os.getenv('PAYTR_MERCHANT_SALT', '')
        if not merchant_id or not merchant_key or not merchant_salt:
            return jsonify({ 'error': 'PayTR credentials are not configured' }), 500

        currency = body.get('currency') or os.getenv('PAYTR_CURRENCY', 'TL')
        test_mode = os.getenv('PAYTR_TEST_MODE', '1')  # '1' in dev
        no_installment = str(body.get('no_installment', 0))
        max_installment = str(body.get('max_installment', 0))
        timeout_limit = str(body.get('timeout_limit', 30))

        ok_url = os.getenv('PAYTR_OK_URL') or 'http://localhost:5173/payment/success'
        fail_url = os.getenv('PAYTR_FAIL_URL') or 'http://localhost:5173/payment/fail'

        # Generate alphanumeric merchant_oid (PayTR requirement: no special characters)
        merchant_oid = ''.join([str(uuid.uuid4()).replace('-', '')[:16], str(int(time.time()))])
        user_ip = _get_client_ip(request) or ''

        # Step 1 HMAC per PayTR sample: hash_str + merchant_salt appended as bytes, key=merchant_key
        hash_str = (
            merchant_id + user_ip + merchant_oid + (customer.get('email') or '') + str(payment_amount_kurus)
            + user_basket_b64 + no_installment + max_installment + currency + test_mode
        )
        paytr_token = base64.b64encode(
            hmac.new(
                merchant_key.encode('utf-8'),
                hash_str.encode('utf-8') + merchant_salt.encode('utf-8'),
                hashlib.sha256
            ).digest()
        ).decode('utf-8')

        params = {
            'merchant_id': merchant_id,
            'user_ip': user_ip,
            'merchant_oid': merchant_oid,
            'email': customer.get('email') or '',
            'payment_amount': str(payment_amount_kurus),
            'paytr_token': paytr_token,
            'user_basket': user_basket_b64,
            'debug_on': '1' if os.getenv('PAYTR_DEBUG', '1') == '1' else '0',
            'no_installment': no_installment,
            'max_installment': max_installment,
            'user_name': customer.get('name') or '',
            'user_address': customer.get('address') or '',
            'user_phone': customer.get('phone') or '',
            'merchant_ok_url': ok_url,
            'merchant_fail_url': fail_url,
            'timeout_limit': timeout_limit,
            'currency': currency,
            'test_mode': test_mode
        }

        token_response = _create_paytr_token(params)
        if token_response.get('status') != 'success':
            return jsonify({
                'error': 'PayTR token error',
                'details': token_response
            }), 400

        supabase = _get_supabase_client()
        order_record = {
            'merchant_oid': merchant_oid,
            'user_id': g.current_user.get('id') if hasattr(g, 'current_user') else None,
            'status': 'pending',
            'amount_kurus': payment_amount_kurus,
            'currency': currency,
            'basket_json': basket_matrix,
            'user_basket_base64': user_basket_b64,
            'customer_email': customer.get('email'),
            'customer_name': customer.get('name'),
            'customer_address': customer.get('address'),
            'customer_phone': customer.get('phone'),
            'test_mode': True if test_mode == '1' else False,
            'no_installment': int(no_installment),
            'max_installment': int(max_installment),
            'timeout_limit': int(timeout_limit)
        }

        # Insert order
        insert_res = supabase.table('orders').insert(order_record).execute()
        if not insert_res.data:
            return jsonify({ 'error': 'Failed to persist order' }), 500

        # Insert order event
        try:
            supabase.table('order_events').insert({
                'order_id': insert_res.data[0]['id'],
                'event_type': 'created',
                'event_data': {'params': {k: v for k, v in params.items() if k != 'paytr_token'}}
            }).execute()
        except Exception:
            pass

        return jsonify({
            'token': token_response['token'],
            'merchant_oid': merchant_oid
        }), 200


@blp.route('/payments/paytr/callback')
class PaytrCallback(MethodView):
    def post(self):
        """
        PayTR server-to-server notification handler (Bildirim URL)
        """
        post = request.form

        merchant_key = os.getenv('PAYTR_MERCHANT_KEY', '')
        merchant_salt = os.getenv('PAYTR_MERCHANT_SALT', '')
        if not merchant_key or not merchant_salt:
            return 'CONFIG ERROR', 500

        merchant_oid = post.get('merchant_oid', '')
        status = post.get('status', '')
        total_amount = post.get('total_amount', '')
        posted_hash = post.get('hash', '')

        # Step 2 HMAC per PayTR sample: hash over merchant_oid + merchant_salt + status + total_amount
        hash_str = merchant_oid + merchant_salt + status + total_amount
        computed_hash = base64.b64encode(
            hmac.new(
                merchant_key.encode('utf-8'),
                hash_str.encode('utf-8'),
                hashlib.sha256
            ).digest()
        ).decode('utf-8')

        if computed_hash != posted_hash:
            return 'PAYTR notification failed: bad hash'

        supabase = _get_supabase_client()
        # Find order by merchant_oid
        order_res = supabase.table('orders').select('*').eq('merchant_oid', merchant_oid).limit(1).execute()
        if not order_res.data:
            # No order found; still acknowledge to avoid retries storm but log via event
            try:
                supabase.table('order_events').insert({
                    'order_id': None,
                    'event_type': 'callback_received',
                    'event_data': {'merchant_oid': merchant_oid, 'status': status, 'note': 'Order not found'}
                }).execute()
            except Exception:
                pass
            return 'OK'

        order = order_res.data[0]
        # Idempotency: if already finalized, acknowledge
        if order.get('status') in ('paid', 'failed'):
            return 'OK'

        update_data = {}
        if status == 'success':
            try:
                update_data['status'] = 'paid'
                update_data['total_amount_kurus'] = int(total_amount)
            except Exception:
                update_data['status'] = 'paid'
        else:
            update_data['status'] = 'failed'
            update_data['failed_reason_code'] = post.get('failed_reason_code')
            update_data['failed_reason_msg'] = post.get('failed_reason_msg')

        supabase.table('orders').update(update_data).eq('id', order['id']).execute()

        try:
            supabase.table('order_events').insert({
                'order_id': order['id'],
                'event_type': 'payment_success' if status == 'success' else 'payment_failed',
                'event_data': { 'callback': {k: post.get(k) for k in post.keys()} }
            }).execute()
        except Exception:
            pass

        return 'OK'


@blp.route('/payments/paytr/status')
class PaytrStatus(MethodView):
    @verify_supabase_token
    def get(self):
        merchant_oid = request.args.get('merchant_oid')
        if not merchant_oid:
            return jsonify({ 'error': 'merchant_oid is required' }), 400

        supabase = _get_supabase_client()
        user_id = g.current_user.get('id') if hasattr(g, 'current_user') else None
        if not user_id:
            return jsonify({ 'error': 'Unauthorized' }), 401

        res = (
            supabase
            .table('orders')
            .select('status,total_amount_kurus,failed_reason_code,failed_reason_msg,user_id')
            .eq('merchant_oid', merchant_oid)
            .limit(1)
            .execute()
        )

        if not res.data:
            return jsonify({ 'error': 'Order not found' }), 404

        order = res.data[0]
        if order.get('user_id') != user_id:
            return jsonify({ 'error': 'Forbidden' }), 403

        return jsonify({
            'status': order.get('status'),
            'total_amount_kurus': order.get('total_amount_kurus'),
            'failed_reason_code': order.get('failed_reason_code'),
            'failed_reason_msg': order.get('failed_reason_msg')
        }), 200


