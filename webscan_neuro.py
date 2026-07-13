import json
import os
import re
from difflib import SequenceMatcher
import requests
from urllib.parse import quote

class WebScanNeuro:
    def __init__(self):
        # Загрузка базы знаний
        self.knowledge_base = self.load_knowledge_base()
        
        # Serpstack API ключ
        self.serpstack_api_key = os.environ.get('SERPSTACK_API_KEY', '')
        
    def load_knowledge_base(self):
        """Загрузка базы знаний из JSON файла"""
        try:
            with open('neuro_smart.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('knowledge_base', [])
        except FileNotFoundError:
            print("Файл neuro_smart.json не найден. Создаю базовую базу знаний.")
            return self.create_default_knowledge_base()
        except json.JSONDecodeError:
            print("Ошибка чтения neuro_smart.json. Использую базовую базу.")
            return self.create_default_knowledge_base()
    
    def create_default_knowledge_base(self):
        """Создание базовой базы знаний"""
        base_knowledge = [
            {
                "question": "привет",
                "answer": "Привет! Я WebScan AI - ваш интеллектуальный помощник. Я могу отвечать на вопросы, используя базу знаний или поиск в интернете. Чем могу помочь?"
            },
            {
                "question": "как дела",
                "answer": "Отлично! Я всегда готов помочь вам найти нужную информацию. Задавайте любой вопрос!"
            },
            {
                "question": "что ты умеешь",
                "answer": "Я умею многое:\n- Отвечать на вопросы из моей базы знаний\n- Искать информацию в интернете через Serpstack\n- Вести диалог и помнить контекст\n- Работать в режиме реального времени\n- Поддерживать множественные чаты\n\nПросто спросите меня о чем угодно!"
            },
            {
                "question": "кто тебя создал",
                "answer": "Меня создала команда WebScan AI как часть проекта по созданию интеллектуального веб-ассистента. Я постоянно совершенствуюсь и учусь новому!"
            },
            {
                "question": "пока",
                "answer": "До свидания! Буду рад помочь снова. Если появятся вопросы - обращайтесь!"
            }
        ]
        return base_knowledge
    
    def find_best_match(self, query):
        """Поиск лучшего совпадения в базе знаний"""
        best_match = None
        best_score = 0
        
        query_lower = query.lower()
        query_words = set(query_lower.split())
        
        for item in self.knowledge_base:
            question = item['question'].lower()
            
            # Проверка точного совпадения
            if query_lower == question:
                return item['answer']
            
            # Проверка содержания запроса в вопросе
            question_words = set(question.split())
            word_overlap = len(query_words & question_words)
            
            # Коэффициент схожести
            similarity = SequenceMatcher(None, query_lower, question).ratio()
            
            # Комбинированная оценка
            combined_score = (word_overlap * 0.3) + (similarity * 0.7)
            
            if combined_score > best_score:
                best_score = combined_score
                best_match = item['answer']
        
        # Порог схожести
        if best_score >= 0.3:
            return best_match
        return None
    
    def search_web(self, query):
        """Поиск в интернете через Serpstack API"""
        if not self.serpstack_api_key:
            return self.generate_fallback_response(query)
        
        try:
            url = "http://api.serpstack.com/search"
            params = {
                'access_key': self.serpstack_api_key,
                'query': query,
                'num': 3,
                'language': 'ru'
            }
            
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            
            if 'organic_results' in data and data['organic_results']:
                results_text = "Вот что я нашел в интернете:\n\n"
                for i, result in enumerate(data['organic_results'][:3], 1):
                    title = result.get('title', 'Без названия')
                    snippet = result.get('snippet', 'Нет описания')
                    results_text += f"{i}. {title}\n{snippet}\n\n"
                results_text += "Источник: поиск через Serpstack"
                return results_text
            else:
                return self.generate_fallback_response(query)
        except Exception as e:
            print(f"Ошибка поиска: {e}")
            return self.generate_fallback_response(query)
    
    def generate_fallback_response(self, query):
        """Генерация ответа если ничего не найдено"""
        responses = [
            f"Интересный вопрос про '{query}'. Давайте разберемся вместе!",
            f"Я понимаю ваш вопрос о '{query}'. К сожалению, в моей базе нет точного ответа.",
            f"Хороший вопрос! '{query}' - это важная тема. Позвольте мне подумать...",
        ]
        import random
        base_response = random.choice(responses)
        
        # Добавляем полезную информацию
        helpful_text = "\n\n💡 Совет: Попробуйте переформулировать вопрос или задать его более конкретно. Например:\n"
        helpful_text += "- Используйте ключевые слова\n"
        helpful_text += "- Задайте вопрос по-другому\n"
        helpful_text += "- Уточните контекст вопроса"
        
        return base_response + helpful_text
    
    def get_response(self, message):
        """Основной метод получения ответа"""
        # Поиск в базе знаний
        db_response = self.find_best_match(message)
        if db_response:
            return db_response
        
        # Если нет в базе - ищем в интернете
        web_response = self.search_web(message)
        return web_response

# Тестирование при запуске
if __name__ == "__main__":
    neuro = WebScanNeuro()
    
    test_questions = [
        "Привет!",
        "Как дела?",
        "Что такое Python?",
        "Расскажи про искусственный интеллект",
        "Пока!"
    ]
    
    for question in test_questions:
        print(f"\nВопрос: {question}")
        print(f"Ответ: {neuro.get_response(question)}")
        print("-" * 50)
