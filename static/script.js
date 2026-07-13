let currentChatId = null;
let chats = {};

// Инициализация
document.addEventListener('DOMContentLoaded', () => {
    loadChats();
    setupAutoResize();
});

// Загрузка списка чатов
async function loadChats() {
    try {
        const response = await fetch('/api/chats');
        chats = await response.json();
        renderChatList();
    } catch (error) {
        console.error('Ошибка загрузки чатов:', error);
    }
}

// Создание нового чата
async function createNewChat() {
    try {
        const response = await fetch('/api/chat/new', { method: 'POST' });
        const data = await response.json();
        currentChatId = data.chat_id;
        await loadChats();
        loadChat(currentChatId);
    } catch (error) {
        console.error('Ошибка создания чата:', error);
    }
}

// Загрузка конкретного чата
async function loadChat(chatId) {
    try {
        const response = await fetch(`/api/chat/${chatId}`);
        const chat = await response.json();
        currentChatId = chatId;
        renderMessages(chat.messages || []);
        updateChatTitle();
        highlightActiveChat();
    } catch (error) {
        console.error('Ошибка загрузки чата:', error);
    }
}

// Отправка сообщения
async function sendMessage(message = null) {
    const input = document.getElementById('messageInput');
    const text = message || input.value.trim();
    
    if (!text) return;
    
    if (!currentChatId) {
        await createNewChat();
    }
    
    // Очищаем инпут
    if (!message) {
        input.value = '';
        input.style.height = 'auto';
    }
    
    // Показываем сообщение пользователя
    addMessageToUI('user', text);
    
    // Показываем индикатор загрузки
    showTypingIndicator();
    
    try {
        const response = await fetch(`/api/chat/${currentChatId}/send`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: text })
        });
        
        const data = await response.json();
        
        // Убираем индикатор загрузки
        removeTypingIndicator();
        
        // Показываем ответ AI
        addMessageToUI('ai', data.response);
        
        // Обновляем список чатов
        await loadChats();
        updateChatTitle();
        
    } catch (error) {
        console.error('Ошибка отправки сообщения:', error);
        removeTypingIndicator();
        addMessageToUI('ai', 'Извините, произошла ошибка. Попробуйте еще раз.');
    }
}

// Добавление сообщения в UI
function addMessageToUI(type, text) {
    const container = document.getElementById('messagesContainer');
    
    // Убираем приветственное сообщение
    const welcome = container.querySelector('.welcome-message');
    if (welcome) welcome.remove();
    
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type}`;
    
    const avatar = type === 'user' ? '👤' : '🤖';
    const time = new Date().toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' });
    
    messageDiv.innerHTML = `
        <div class="message-avatar">${avatar}</div>
        <div class="message-content-wrapper">
            <div class="message-content">${text}</div>
            <div class="message-time">${time}</div>
        </div>
    `;
    
    container.appendChild(messageDiv);
    container.scrollTop = container.scrollHeight;
}

// Показ индикатора печати
function showTypingIndicator() {
    const container = document.getElementById('messagesContainer');
    const indicator = document.createElement('div');
    indicator.className = 'typing-indicator';
    indicator.id = 'typingIndicator';
    indicator.innerHTML = '<span></span><span></span><span></span>';
    container.appendChild(indicator);
    container.scrollTop = container.scrollHeight;
}

// Удаление индикатора печати
function removeTypingIndicator() {
    const indicator = document.getElementById('typingIndicator');
    if (indicator) indicator.remove();
}

// Отображение сообщений чата
function renderMessages(messages) {
    const container = document.getElementById('messagesContainer');
    container.innerHTML = '';
    
    if (messages.length === 0) {
        container.innerHTML = `
            <div class="welcome-message">
                <div class="welcome-icon">🤖</div>
                <h2>Добро пожаловать в WebScan AI</h2>
                <p>Я ваш интеллектуальный помощник с доступом к базе знаний и поиску в интернете.</p>
                <div class="suggestions">
                    <button onclick="sendSuggestion('Что ты умеешь?')">Что ты умеешь?</button>
                    <button onclick="sendSuggestion('Расскажи про Python')">Расскажи про Python</button>
                    <button onclick="sendSuggestion('Как стать программистом?')">Как стать программистом?</button>
                </div>
            </div>
        `;
    } else {
        messages.forEach(msg => {
            addMessageToUI('user', msg.user);
            addMessageToUI('ai', msg.ai);
        });
    }
}

// Отображение списка чатов
function renderChatList() {
    const chatList = document.getElementById('chatList');
    chatList.innerHTML = '';
    
    // Сортируем чаты по дате создания (новые сверху)
    const sortedChats = Object.values(chats).sort((a, b) => {
        return new Date(b.created) - new Date(a.created);
    });
    
    sortedChats.forEach(chat => {
        const chatItem = document.createElement('div');
        chatItem.className = `chat-item ${chat.id === currentChatId ? 'active' : ''}`;
        chatItem.innerHTML = `
            <div class="chat-item-title" onclick="loadChat('${chat.id}')">${chat.title || 'Новый чат'}</div>
            <button class="chat-item-delete" onclick="deleteChat('${chat.id}')">✕</button>
        `;
        chatList.appendChild(chatItem);
    });
}

// Удаление чата
async function deleteChat(chatId) {
    if (confirm('Удалить этот чат?')) {
        try {
            await fetch(`/api/chat/${chatId}/delete`, { method: 'DELETE' });
            if (currentChatId === chatId) {
                currentChatId = null;
                renderMessages([]);
                updateChatTitle();
            }
            await loadChats();
        } catch (error) {
            console.error('Ошибка удаления чата:', error);
        }
    }
}

// Удаление текущего чата
function deleteCurrentChat() {
    if (currentChatId) {
        deleteChat(currentChatId);
    }
}

// Обновление заголовка чата
function updateChatTitle() {
    const title = document.getElementById('chatTitle');
    if (currentChatId && chats[currentChatId]) {
        title.textContent = chats[currentChatId].title || 'Новый чат';
    } else {
        title.textContent = 'WebScan AI';
    }
}

// Подсветка активного чата
function highlightActiveChat() {
    document.querySelectorAll('.chat-item').forEach(item => {
        item.classList.remove('active');
    });
    const activeItem = document.querySelector(`[onclick*="${currentChatId}"]`);
    if (activeItem) {
        activeItem.closest('.chat-item').classList.add('active');
    }
}

// Отправка предложения
function sendSuggestion(text) {
    sendMessage(text);
}

// Обработка нажатия Enter
function handleKeyDown(event) {
    if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        sendMessage();
    }
}

// Автоматическое изменение размера textarea
function setupAutoResize() {
    const textarea = document.getElementById('messageInput');
    textarea.addEventListener('input', function() {
        this.style.height = 'auto';
        this.style.height = Math.min(this.scrollHeight, 200) + 'px';
    });
}
