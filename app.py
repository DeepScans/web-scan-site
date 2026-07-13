from flask import Flask, render_template, request, jsonify, session
from webscan_neuro import WebScanNeuro
from datetime import datetime
import uuid
import json
import os

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'webscan-secret-key-2024')

# Инициализация нейросети
neuro = WebScanNeuro()

# Хранилище чатов (в памяти)
if os.path.exists('chats.json'):
    with open('chats.json', 'r', encoding='utf-8') as f:
        chats = json.load(f)
else:
    chats = {}

def save_chats():
    with open('chats.json', 'w', encoding='utf-8') as f:
        json.dump(chats, f, ensure_ascii=False, indent=2)

@app.route('/')
def index():
    if 'user_id' not in session:
        session['user_id'] = str(uuid.uuid4())
    return render_template('index.html')

@app.route('/api/chats', methods=['GET'])
def get_chats():
    user_id = session.get('user_id', 'default')
    user_chats = chats.get(user_id, {})
    return jsonify(user_chats)

@app.route('/api/chat/new', methods=['POST'])
def new_chat():
    user_id = session.get('user_id', 'default')
    chat_id = str(uuid.uuid4())[:8]
    
    if user_id not in chats:
        chats[user_id] = {}
    
    chats[user_id][chat_id] = {
        'id': chat_id,
        'title': 'Новый чат',
        'messages': [],
        'created': datetime.now().isoformat()
    }
    save_chats()
    return jsonify({'chat_id': chat_id})

@app.route('/api/chat/<chat_id>', methods=['GET'])
def get_chat(chat_id):
    user_id = session.get('user_id', 'default')
    user_chats = chats.get(user_id, {})
    chat = user_chats.get(chat_id, {'messages': []})
    return jsonify(chat)

@app.route('/api/chat/<chat_id>/send', methods=['POST'])
def send_message(chat_id):
    user_id = session.get('user_id', 'default')
    data = request.json
    user_message = data.get('message', '')
    
    if not user_message:
        return jsonify({'error': 'Пустое сообщение'}), 400
    
    # Создаем чат если не существует
    if user_id not in chats:
        chats[user_id] = {}
    if chat_id not in chats[user_id]:
        chats[user_id][chat_id] = {
            'id': chat_id,
            'title': user_message[:50],
            'messages': [],
            'created': datetime.now().isoformat()
        }
    
    # Получаем ответ от нейросети
    ai_response = neuro.get_response(user_message)
    
    # Сохраняем сообщения
    message_pair = {
        'user': user_message,
        'ai': ai_response,
        'timestamp': datetime.now().isoformat()
    }
    chats[user_id][chat_id]['messages'].append(message_pair)
    
    # Обновляем заголовок чата если это первое сообщение
    if len(chats[user_id][chat_id]['messages']) == 1:
        chats[user_id][chat_id]['title'] = user_message[:50] + ('...' if len(user_message) > 50 else '')
    
    save_chats()
    return jsonify({
        'response': ai_response,
        'chat': chats[user_id][chat_id]
    })

@app.route('/api/chat/<chat_id>/delete', methods=['DELETE'])
def delete_chat(chat_id):
    user_id = session.get('user_id', 'default')
    if user_id in chats and chat_id in chats[user_id]:
        del chats[user_id][chat_id]
        save_chats()
    return jsonify({'status': 'ok'})

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok', 'timestamp': datetime.now().isoformat()})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
