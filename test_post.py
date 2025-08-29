import requests
import json

url = 'http://127.0.0.1:5000/api/chat'
payload = {
    'messages': [{ 'role': 'user', 'content': 'Hello test, what is 2+2?' }],
    'stream': False
}

try:
    r = requests.post(url, json=payload, timeout=15)
    print('STATUS', r.status_code)
    try:
        print(json.dumps(r.json(), indent=2))
    except Exception:
        print('RAW:', r.text)
except Exception as e:
    print('ERROR', e)
