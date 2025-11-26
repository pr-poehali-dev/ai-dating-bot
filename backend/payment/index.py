'''
Business: Payment processing for subscriptions and one-time purchases
Args: event with httpMethod, body (productId, productType, amount, paymentMethod, paymentData)
Returns: HTTP response with payment status and transaction details
'''

import json
import os
import uuid
from typing import Dict, Any
from datetime import datetime, timedelta

def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    method: str = event.get('httpMethod', 'GET')
    
    if method == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'POST, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type, X-User-Id',
                'Access-Control-Max-Age': '86400'
            },
            'body': '',
            'isBase64Encoded': False
        }
    
    if method != 'POST':
        return {
            'statusCode': 405,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'error': 'Method not allowed'}),
            'isBase64Encoded': False
        }
    
    body_data = json.loads(event.get('body', '{}'))
    
    product_id = body_data.get('productId')
    product_type = body_data.get('productType')
    amount = body_data.get('amount')
    payment_method = body_data.get('paymentMethod')
    payment_data = body_data.get('paymentData', {})
    
    if not all([product_id, product_type, amount, payment_method]):
        return {
            'statusCode': 400,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'error': 'Missing required fields'}),
            'isBase64Encoded': False
        }
    
    transaction_id = str(uuid.uuid4())
    
    if payment_method == 'card':
        card_number = payment_data.get('cardNumber', '')
        if len(card_number.replace(' ', '')) < 16:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({'error': 'Invalid card number'}),
                'isBase64Encoded': False
            }
        
        payment_status = 'success'
        masked_card = f"**** **** **** {card_number.replace(' ', '')[-4:]}"
        payment_details = {'maskedCard': masked_card}
        
    elif payment_method == 'sbp':
        phone_number = payment_data.get('phoneNumber', '')
        if not phone_number:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({'error': 'Phone number required for SBP'}),
                'isBase64Encoded': False
            }
        
        payment_status = 'success'
        payment_details = {'phone': phone_number}
    else:
        return {
            'statusCode': 400,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'error': 'Invalid payment method'}),
            'isBase64Encoded': False
        }
    
    subscription_end = None
    if product_type == 'subscription':
        subscription_end = (datetime.now() + timedelta(days=30)).isoformat()
    
    result = {
        'success': True,
        'transactionId': transaction_id,
        'productId': product_id,
        'productType': product_type,
        'amount': amount,
        'paymentMethod': payment_method,
        'paymentStatus': payment_status,
        'paymentDetails': payment_details,
        'subscriptionEnd': subscription_end,
        'timestamp': datetime.now().isoformat()
    }
    
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps(result),
        'isBase64Encoded': False
    }
