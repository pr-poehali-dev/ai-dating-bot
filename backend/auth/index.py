'''
Business: User authentication - registration, login, token validation
Args: event with httpMethod POST, body with action (register/login/validate), email, password, name
      context with request_id attribute
Returns: JWT token on success or user data for validation
'''

import json
import os
import jwt
import bcrypt
import psycopg2
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    method: str = event.get('httpMethod', 'POST')
    
    if method == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'POST, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type, X-Auth-Token',
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
    
    try:
        body_str = event.get('body', '{}')
        if isinstance(body_str, dict):
            body_data = body_str
        else:
            body_data = json.loads(body_str) if body_str else {}
    except json.JSONDecodeError:
        return {
            'statusCode': 400,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'error': 'Invalid JSON'}),
            'isBase64Encoded': False
        }
    
    action = body_data.get('action')
    
    if action == 'register':
        return handle_register(body_data)
    elif action == 'login':
        return handle_login(body_data)
    elif action == 'validate':
        return handle_validate(event)
    else:
        return {
            'statusCode': 400,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'error': 'Invalid action. Use: register, login, validate'}),
            'isBase64Encoded': False
        }

def get_db_connection():
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        raise Exception('DATABASE_URL not configured')
    return psycopg2.connect(database_url)

def generate_token(user_id: int, email: str) -> str:
    jwt_secret = os.environ.get('JWT_SECRET')
    if not jwt_secret:
        raise Exception('JWT_SECRET not configured')
    
    payload = {
        'user_id': user_id,
        'email': email,
        'exp': datetime.utcnow() + timedelta(days=30)
    }
    
    return jwt.encode(payload, jwt_secret, algorithm='HS256')

def verify_token(token: str) -> Optional[Dict[str, Any]]:
    jwt_secret = os.environ.get('JWT_SECRET')
    if not jwt_secret:
        return None
    
    try:
        payload = jwt.decode(token, jwt_secret, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def handle_register(body_data: Dict[str, Any]) -> Dict[str, Any]:
    email = body_data.get('email', '').strip().lower()
    password = body_data.get('password', '')
    name = body_data.get('name', '').strip()
    
    if not email or not password or not name:
        return {
            'statusCode': 400,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'error': 'Email, password and name are required'}),
            'isBase64Encoded': False
        }
    
    if len(password) < 6:
        return {
            'statusCode': 400,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'error': 'Password must be at least 6 characters'}),
            'isBase64Encoded': False
        }
    
    if '@' not in email or '.' not in email:
        return {
            'statusCode': 400,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'error': 'Invalid email format'}),
            'isBase64Encoded': False
        }
    
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute(
            "SELECT id FROM t_p77610913_ai_dating_bot.users WHERE email = %s",
            (email,)
        )
        existing_user = cur.fetchone()
        
        if existing_user:
            cur.close()
            conn.close()
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({'error': 'Email already registered'}),
                'isBase64Encoded': False
            }
        
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        import uuid
        user_id_str = str(uuid.uuid4())
        
        cur.execute(
            """
            INSERT INTO t_p77610913_ai_dating_bot.users 
            (user_id, email, password_hash, name, created_at, last_active)
            VALUES (%s, %s, %s, %s, NOW(), NOW())
            RETURNING id
            """,
            (user_id_str, email, password_hash, name)
        )
        
        user_id = cur.fetchone()[0]
        conn.commit()
        
        cur.execute(
            """
            INSERT INTO t_p77610913_ai_dating_bot.subscriptions
            (user_id, flirt, intimate, premium)
            VALUES (%s, false, false, false)
            """,
            (user_id_str,)
        )
        conn.commit()
        
        cur.close()
        conn.close()
        
        token = generate_token(user_id, email)
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'success': True,
                'token': token,
                'user': {
                    'id': user_id,
                    'email': email,
                    'name': name
                }
            }),
            'isBase64Encoded': False
        }
    
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'error': f'Registration failed: {str(e)}'}),
            'isBase64Encoded': False
        }

def handle_login(body_data: Dict[str, Any]) -> Dict[str, Any]:
    email = body_data.get('email', '').strip().lower()
    password = body_data.get('password', '')
    
    if not email or not password:
        return {
            'statusCode': 400,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'error': 'Email and password are required'}),
            'isBase64Encoded': False
        }
    
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute(
            """
            SELECT id, email, password_hash, name 
            FROM t_p77610913_ai_dating_bot.users 
            WHERE email = %s
            """,
            (email,)
        )
        
        user = cur.fetchone()
        
        if not user:
            cur.close()
            conn.close()
            return {
                'statusCode': 401,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({'error': 'Invalid email or password'}),
                'isBase64Encoded': False
            }
        
        user_id, user_email, password_hash, name = user
        
        if not password_hash:
            cur.close()
            conn.close()
            return {
                'statusCode': 401,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({'error': 'Account exists but password not set. Please use social login or reset password.'}),
                'isBase64Encoded': False
            }
        
        if not bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8')):
            cur.close()
            conn.close()
            return {
                'statusCode': 401,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({'error': 'Invalid email or password'}),
                'isBase64Encoded': False
            }
        
        cur.execute(
            "UPDATE t_p77610913_ai_dating_bot.users SET last_active = NOW() WHERE id = %s",
            (user_id,)
        )
        conn.commit()
        
        cur.close()
        conn.close()
        
        token = generate_token(user_id, user_email)
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'success': True,
                'token': token,
                'user': {
                    'id': user_id,
                    'email': user_email,
                    'name': name
                }
            }),
            'isBase64Encoded': False
        }
    
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'error': f'Login failed: {str(e)}'}),
            'isBase64Encoded': False
        }

def handle_validate(event: Dict[str, Any]) -> Dict[str, Any]:
    headers = event.get('headers', {})
    token = headers.get('X-Auth-Token') or headers.get('x-auth-token')
    
    if not token:
        return {
            'statusCode': 401,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'error': 'No token provided'}),
            'isBase64Encoded': False
        }
    
    payload = verify_token(token)
    
    if not payload:
        return {
            'statusCode': 401,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'error': 'Invalid or expired token'}),
            'isBase64Encoded': False
        }
    
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute(
            """
            SELECT u.id, u.email, u.name, u.user_id,
                   s.flirt, s.intimate, s.premium
            FROM t_p77610913_ai_dating_bot.users u
            LEFT JOIN t_p77610913_ai_dating_bot.subscriptions s ON u.user_id = s.user_id
            WHERE u.id = %s
            """,
            (payload['user_id'],)
        )
        
        user = cur.fetchone()
        
        if not user:
            cur.close()
            conn.close()
            return {
                'statusCode': 401,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({'error': 'User not found'}),
                'isBase64Encoded': False
            }
        
        user_id, email, name, user_id_str, flirt, intimate, premium = user
        
        cur.close()
        conn.close()
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'valid': True,
                'user': {
                    'id': user_id,
                    'user_id': user_id_str,
                    'email': email,
                    'name': name,
                    'subscription': {
                        'flirt': flirt or False,
                        'intimate': intimate or False,
                        'premium': premium or False
                    }
                }
            }),
            'isBase64Encoded': False
        }
    
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'error': f'Validation failed: {str(e)}'}),
            'isBase64Encoded': False
        }
