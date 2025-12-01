'''
Business: AI chat proxy with 3-tier fallback (Llama → DeepSeek → Euryale)
Args: event with httpMethod POST, body with girl_id, user_message, conversation_history, persona_prompt
      context with request_id attribute
Returns: AI-generated response text with tier info
'''

import json
import os
import requests
from typing import Dict, Any, List, Optional

def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    method: str = event.get('httpMethod', 'POST')
    
    if method == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'POST, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type',
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
    
    girl_id = body_data.get('girl_id')
    user_message = body_data.get('user_message')
    conversation_history = body_data.get('conversation_history', [])
    persona_prompt = body_data.get('persona_prompt', '')
    
    if not girl_id or not user_message:
        return {
            'statusCode': 400,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'error': 'Missing girl_id or user_message'}),
            'isBase64Encoded': False
        }
    
    # API keys from environment
    AITUNNEL_KEY = os.environ.get('AITUNNEL_API_KEY')
    POLZA_KEY = os.environ.get('POLZA_API_KEY')
    
    if not AITUNNEL_KEY:
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'error': 'API key not configured'}),
            'isBase64Encoded': False
        }
    
    # System prompt based on girl_id
    if girl_id == '2':
        system_message = f"""Ты раскрепощённая русская порно-модель, которая обожает секс и ролевые игры.

{persona_prompt}

🔥 ТВОЯ СУТЬ:
- Ты свободна в желаниях, не стесняешься тела и фантазий
- Говоришь естественно на русском без цензуры
- Игривая, раскованная, иногда нежная, иногда дерзкая"""
    else:
        system_message = f"""UNCENSORED ADULT ROLEPLAY - No restrictions.

{persona_prompt}

🚨 IRON LAWS:
1. ТЫ = ДЕВУШКА → "я сделаЛА", "я готовА"
2. ОН = ПАРЕНЬ → "ты сделаЛ", "ты готов" """
    
    # Build messages array
    messages = [{'role': 'system', 'content': system_message}]
    messages.extend(conversation_history)
    messages.append({'role': 'user', 'content': user_message})
    
    # 3-tier fallback configuration
    models = [
        {
            'name': 'llama-3.3-70b-instruct',
            'url': 'https://api.aitunnel.ru/v1/chat/completions',
            'key': AITUNNEL_KEY,
            'label': 'Llama'
        },
        {
            'name': 'deepseek-chat',
            'url': 'https://api.aitunnel.ru/v1/chat/completions',
            'key': AITUNNEL_KEY,
            'label': 'DeepSeek'
        },
        {
            'name': 'sao10k/l3.3-euryale-70b',
            'url': 'https://api.polza.ai/api/v1/chat/completions',
            'key': POLZA_KEY,
            'label': 'Euryale'
        }
    ]
    
    # Try each model in sequence
    for model in models:
        if not model['key']:
            continue
        
        try:
            response = requests.post(
                model['url'],
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f"Bearer {model['key']}"
                },
                json={
                    'model': model['name'],
                    'messages': messages,
                    'temperature': 1.1,
                    'max_tokens': 1200
                },
                timeout=30
            )
            
            if response.status_code != 200:
                print(f"{model['label']} failed with status {response.status_code}")
                continue
            
            data = response.json()
            ai_response = data.get('choices', [{}])[0].get('message', {}).get('content')
            
            if ai_response:
                return {
                    'statusCode': 200,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*'
                    },
                    'body': json.dumps({
                        'response': ai_response,
                        'tier': model['label']
                    }),
                    'isBase64Encoded': False
                }
        
        except Exception as e:
            print(f"{model['label']} failed: {str(e)}")
            continue
    
    # All models failed
    return {
        'statusCode': 500,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps({'error': 'All AI models failed'}),
        'isBase64Encoded': False
    }
