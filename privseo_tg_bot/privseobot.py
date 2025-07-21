import telebot
from telebot.types import (Message, ReplyKeyboardMarkup, 
                          ReplyKeyboardRemove, InlineKeyboardMarkup, 
                          InlineKeyboardButton)
from datetime import datetime
import re
from io import BytesIO
from PIL import Image
import yaml
from dotenv import load_dotenv
import os
import uuid
from pathlib import Path

# Загрузка переменных окружения из .env файла
load_dotenv()

# --- НАСТРОЙКИ ---
BOT_TOKEN = os.getenv("BOT_TOKEN")
AUTHORIZED_USER_ID = int(os.getenv("AUTHORIZED_USER_ID"))
LOCAL_REPO_PATH = Path(os.getenv("LOCAL_REPO_PATH", "D:/privateseo.github.io"))
NEWS_DIR = "_posts/news"
IMAGES_DIR = "assets/images/news"
MENU_PATH = "_data/menu.yml"

# --- КАТЕГОРИИ ---
CATEGORIES = {
    "frontend": "👨‍💻 Frontend",
    "backend": "⚙️ Backend",
    "seo": "🔍 SEO",
    "tools": "🛠️ Инструменты",
    "cases": "📊 Кейсы"
}

# Таблица транслитерации
TRANSLIT_TABLE = {
    'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'yo',
    'ж': 'zh', 'з': 'z', 'и': 'i', 'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm',
    'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u',
    'ф': 'f', 'х': 'h', 'ц': 'ts', 'ч': 'ch', 'ш': 'sh', 'щ': 'sch',
    'ъ': '', 'ы': 'y', 'ь': '', 'э': 'e', 'ю': 'yu', 'я': 'ya'
}

bot = telebot.TeleBot(BOT_TOKEN)
user_states = {}

# --- ОБЩИЕ ФУНКЦИИ ---
def is_authorized(user_id):
    return user_id == AUTHORIZED_USER_ID

def get_menu_data():
    menu_path = LOCAL_REPO_PATH / MENU_PATH
    try:
        with open(menu_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except Exception as e:
        print(f"Error reading menu file: {e}")
        return {"items": []}

def update_menu_data(data):
    menu_path = LOCAL_REPO_PATH / MENU_PATH
    try:
        with open(menu_path, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, allow_unicode=True, sort_keys=False)
        return True
    except Exception as e:
        print(f"Error updating menu file: {e}")
        return False

def get_news_files():
    news_dir = LOCAL_REPO_PATH / NEWS_DIR
    try:
        return [f for f in news_dir.glob("*.md") if f.is_file()]
    except Exception as e:
        print(f"Error listing news files: {e}")
        return []

def get_news_file_content(path):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"Error reading news file: {e}")
        return None

def save_news_file(filename, content):
    news_path = LOCAL_REPO_PATH / NEWS_DIR / filename
    try:
        news_path.parent.mkdir(parents=True, exist_ok=True)
        with open(news_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return {"success": True, "path": str(news_path)}
    except Exception as e:
        print(f"Error saving news file: {e}")
        return {"success": False, "error": str(e)}

def save_image(image_bytes, filename):
    images_dir = LOCAL_REPO_PATH / IMAGES_DIR
    try:
        images_dir.mkdir(parents=True, exist_ok=True)
        image_path = images_dir / filename
        with open(image_path, 'wb') as f:
            f.write(image_bytes)
        return str(image_path.relative_to(LOCAL_REPO_PATH))
    except Exception as e:
        print(f"Error saving image: {e}")
        return None

def delete_news_file(filename):
    news_path = LOCAL_REPO_PATH / NEWS_DIR / filename
    try:
        if news_path.exists():
            news_path.unlink()
            return True
        return False
    except Exception as e:
        print(f"Error deleting news file: {e}")
        return False

def menu_keyboard():
    markup = InlineKeyboardMarkup()
    markup.row(
        InlineKeyboardButton("📋 Показать меню", callback_data="show_menu"),
        InlineKeyboardButton("➕ Добавить пункт", callback_data="add_item")
    )
    markup.row(
        InlineKeyboardButton("✏️ Редактировать пункт", callback_data="edit_item"),
        InlineKeyboardButton("❌ Удалить пункт", callback_data="delete_item")
    )
    return markup

def news_management_keyboard():
    markup = InlineKeyboardMarkup()
    markup.row(
        InlineKeyboardButton("📝 Добавить новость", callback_data="add_news"),
        InlineKeyboardButton("📋 Список новостей", callback_data="list_news")
    )
    markup.row(
        InlineKeyboardButton("✏️ Редактировать новость", callback_data="edit_news"),
        InlineKeyboardButton("❌ Удалить новость", callback_data="delete_news")
    )
    return markup

def category_keyboard():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    for cat in CATEGORIES.values():
        markup.add(cat)
    return markup

def transliterate(text):
    text = text.lower()
    result = []
    for char in text:
        if char in TRANSLIT_TABLE:
            result.append(TRANSLIT_TABLE[char])
        elif re.match(r'[a-z0-9-]', char):
            result.append(char)
        else:
            result.append('-')
    return ''.join(result)

def optimize_image(image_bytes, quality=80):
    try:
        img = Image.open(BytesIO(image_bytes))
        if img.mode in ('RGBA', 'P'):
            img = img.convert('RGB')
        output = BytesIO()
        img.save(output, format='WEBP', quality=quality, method=6)
        optimized_bytes = output.getvalue()
        output.close()
        return optimized_bytes
    except Exception as e:
        raise Exception(f"Ошибка оптимизации изображения: {str(e)}")

def parse_front_matter(content):
    try:
        parts = content.split('---')
        if len(parts) >= 3:
            front_matter = yaml.safe_load(parts[1])
            body = '---'.join(parts[2:])
            return front_matter, body
        return None, content
    except Exception:
        return None, content

def create_news_file_content(user_data, content, image_url=None):
    date = datetime.now().strftime('%Y-%m-%d')
    image_path = f"/{image_url}" if image_url else ""
    
    news_id = uuid.uuid4().hex[:16]
    
    return f"""---
layout: news
news_id: {news_id}
name: "{user_data['name']}"
title: "{user_data['title']}"
description: "{user_data['description']}"
date: {date}
image: "{image_path}"
category: {user_data['category']}
---

{content}
"""

def update_news_file_content(old_content, updates):
    front_matter, body = parse_front_matter(old_content)
    
    if front_matter is None:
        return old_content
    
    if 'news_id' not in front_matter:
        front_matter['news_id'] = str(uuid.uuid4().hex[:16])
    
    for key, value in updates.items():
        if value is not None:
            front_matter[key] = value
    
    new_content = "---\n" + yaml.dump(front_matter, allow_unicode=True, sort_keys=False) + "---\n\n" + body
    return new_content

# --- ОБРАБОТЧИКИ КОМАНД ---
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    if is_authorized(message.from_user.id):
        bot.send_message(
            message.chat.id,
            "🌐 Управление сайтом\n\n"
            "/news - Управление новостями\n"
            "/menu - Управление меню\n"
            "/help - Справка"
        )
    else:
        bot.reply_to(message, "⛔ Доступ запрещен")

@bot.message_handler(commands=['menu'])
def manage_menu(message):
    if not is_authorized(message.from_user.id):
        return
    bot.send_message(message.chat.id, "🔧 Управление меню сайта:", reply_markup=menu_keyboard())

@bot.message_handler(commands=['news'])
def manage_news(message):
    if not is_authorized(message.from_user.id):
        return
    bot.send_message(message.chat.id, "📰 Управление новостями:", reply_markup=news_management_keyboard())

# --- ОБРАБОТЧИКИ СООБЩЕНИЙ ---
@bot.message_handler(func=lambda m: user_states.get(m.chat.id, {}).get('step') == 'waiting_for_category' and m.text in CATEGORIES.values())
def process_category(message):
    category = next(k for k, v in CATEGORIES.items() if v == message.text)
    user_states[message.chat.id] = {
        'step': 'waiting_for_name',
        'category': category,
        'media': None
    }
    bot.send_message(message.chat.id, "📝 Введите название новости (для отображения на сайте):", reply_markup=ReplyKeyboardRemove())

@bot.message_handler(func=lambda m: user_states.get(m.chat.id, {}).get('step') == 'waiting_for_name')
def process_name(message):
    user_states[message.chat.id]['name'] = message.text
    user_states[message.chat.id]['step'] = 'waiting_for_title'
    bot.send_message(message.chat.id, "🏷 Введите title (для SEO заголовка):")

@bot.message_handler(func=lambda m: user_states.get(m.chat.id, {}).get('step') == 'waiting_for_title')
def process_title(message):
    user_states[message.chat.id]['title'] = message.text
    user_states[message.chat.id]['step'] = 'waiting_for_description'
    bot.send_message(message.chat.id, "📄 Введите описание новости:")

@bot.message_handler(func=lambda m: user_states.get(m.chat.id, {}).get('step') == 'waiting_for_description')
def process_description(message):
    user_states[message.chat.id]['description'] = message.text
    user_states[message.chat.id]['step'] = 'waiting_for_media'
    bot.send_message(message.chat.id, "🖼 Отправьте изображение для новости (или /skip чтобы пропустить):")

@bot.message_handler(commands=['skip'], func=lambda m: user_states.get(m.chat.id, {}).get('step') == 'waiting_for_media')
def skip_media(message):
    user_states[message.chat.id]['step'] = 'waiting_for_content'
    bot.send_message(message.chat.id, "💬 Введите основной текст новости (HTML/Markdown):")

@bot.message_handler(content_types=['photo'], func=lambda m: user_states.get(m.chat.id, {}).get('step') == 'waiting_for_media')
def process_media(message):
    try:
        file_info = bot.get_file(message.photo[-1].file_id)
        original_image = bot.download_file(file_info.file_path)
        
        bot.send_chat_action(message.chat.id, 'upload_photo')
        optimized_image = optimize_image(original_image)
        
        user_states[message.chat.id]['media'] = optimized_image
        user_states[message.chat.id]['step'] = 'waiting_for_content'
        bot.send_message(message.chat.id, "✅ Изображение оптимизировано и готово к загрузке! Теперь введите основной текст:")
    except Exception as e:
        bot.reply_to(message, f"❌ Ошибка обработки изображения: {str(e)}")

@bot.message_handler(func=lambda m: user_states.get(m.chat.id, {}).get('step') == 'waiting_for_content')
def process_content(message):
    try:
        user_data = user_states[message.chat.id]
        category = user_data['category']
        
        image_url = ""
        if user_data.get('media'):
            image_name = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}.webp"
            saved_image_path = save_image(user_data['media'], image_name)
            if saved_image_path:
                image_url = saved_image_path.replace('\\', '/')

        transliterated_name = transliterate(user_data['name'])
        filename = f"{datetime.now().strftime('%Y-%m-%d')}-{transliterated_name}.md"
        content = create_news_file_content(user_data, message.text, image_url)

        result = save_news_file(filename, content)
        if result['success']:
            bot.send_message(
                message.chat.id,
                f"""✅ Новость успешно добавлена!
                
📌 Категория: {CATEGORIES[category]}
📝 Название: {user_data['name']}
📁 Путь: {result['path']}
🌐 URL на сайте: /news/{transliterated_name}/
🖼 Изображение: {'сохранено' if image_url else 'отсутствует'}"""
            )
        else:
            raise Exception(result.get('error', 'Неизвестная ошибка'))
    
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Ошибка при сохранении новости: {str(e)}")
    finally:
        if message.chat.id in user_states:
            del user_states[message.chat.id]

# --- ОБРАБОТЧИКИ INLINE КНОПОК ---
@bot.callback_query_handler(func=lambda call: call.data == "show_menu")
def show_menu(call):
    try:
        menu = get_menu_data()
        text = "📋 Текущее меню:\n\n"
        for i, item in enumerate(menu['items'], 1):
            text += f"{i}. {item['title']} → {item['url']}\n"
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=menu_keyboard())
    except Exception as e:
        bot.send_message(call.message.chat.id, f"❌ Ошибка при получении меню: {str(e)}")

@bot.callback_query_handler(func=lambda call: call.data == "add_item")
def add_item_start(call):
    user_states[call.message.chat.id] = {"action": "add_item", "step": "title"}
    bot.edit_message_text(
        "Введите название нового пункта меню:",
        call.message.chat.id,
        call.message.message_id
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith("edit_item"))
def edit_item_start(call):
    try:
        menu = get_menu_data()
        markup = InlineKeyboardMarkup()
        for i, item in enumerate(menu['items']):
            markup.add(InlineKeyboardButton(f"{i+1}. {item['title']}", callback_data=f"edit_select_{i}"))
        markup.add(InlineKeyboardButton("🔙 Назад", callback_data="back_to_menu"))
        bot.edit_message_text(
            "Выберите пункт для редактирования:",
            call.message.chat.id,
            call.message.message_id,
            reply_markup=markup
        )
    except Exception as e:
        bot.send_message(call.message.chat.id, f"❌ Ошибка при редактировании меню: {str(e)}")

@bot.callback_query_handler(func=lambda call: call.data.startswith("delete_item"))
def delete_item_start(call):
    try:
        menu = get_menu_data()
        markup = InlineKeyboardMarkup()
        for i, item in enumerate(menu['items']):
            markup.add(InlineKeyboardButton(f"{i+1}. {item['title']}", callback_data=f"delete_confirm_{i}"))
        markup.add(InlineKeyboardButton("🔙 Назад", callback_data="back_to_menu"))
        bot.edit_message_text(
            "Выберите пункт для удаления:",
            call.message.chat.id,
            call.message.message_id,
            reply_markup=markup
        )
    except Exception as e:
        bot.send_message(call.message.chat.id, f"❌ Ошибка при удалении пункта: {str(e)}")

@bot.callback_query_handler(func=lambda call: call.data.startswith("edit_select_"))
def edit_item_select(call):
    try:
        index = int(call.data.split("_")[2])
        menu = get_menu_data()
        item = menu['items'][index]
        
        user_states[call.message.chat.id] = {
            "action": "edit_item",
            "index": index,
            "step": "title"
        }
        
        bot.edit_message_text(
            f"Редактирование пункта меню:\n\nТекущее название: {item['title']}\nТекущий URL: {item['url']}\n\nВведите новое название (или /skip чтобы оставить текущее):",
            call.message.chat.id,
            call.message.message_id
        )
    except Exception as e:
        bot.send_message(call.message.chat.id, f"❌ Ошибка при выборе пункта: {str(e)}")

@bot.callback_query_handler(func=lambda call: call.data.startswith("delete_confirm_"))
def delete_item_confirm(call):
    try:
        index = int(call.data.split("_")[2])
        menu = get_menu_data()
        item = menu['items'][index]
        
        markup = InlineKeyboardMarkup()
        markup.row(
            InlineKeyboardButton("✅ Да, удалить", callback_data=f"delete_execute_{index}"),
            InlineKeyboardButton("❌ Нет, отмена", callback_data="back_to_menu")
        )
        
        bot.edit_message_text(
            f"Вы уверены, что хотите удалить пункт меню?\n\n{item['title']} → {item['url']}",
            call.message.chat.id,
            call.message.message_id,
            reply_markup=markup
        )
    except Exception as e:
        bot.send_message(call.message.chat.id, f"❌ Ошибка при подтверждении удаления: {str(e)}")

@bot.callback_query_handler(func=lambda call: call.data.startswith("delete_execute_"))
def delete_item_execute(call):
    try:
        index = int(call.data.split("_")[2])
        menu = get_menu_data()
        item = menu['items'][index]
        
        del menu['items'][index]
        
        if update_menu_data(menu):
            bot.edit_message_text(
                f"✅ Пункт меню удален: {item['title']}",
                call.message.chat.id,
                call.message.message_id,
                reply_markup=menu_keyboard()
            )
        else:
            raise Exception("Не удалось обновить меню")
    except Exception as e:
        bot.send_message(call.message.chat.id, f"❌ Ошибка при удалении пункта: {str(e)}")

@bot.callback_query_handler(func=lambda call: call.data == "add_news")
def add_news_start(call):
    if not is_authorized(call.from_user.id):
        return
    
    bot.send_message(call.message.chat.id, "Выберите категорию:", reply_markup=category_keyboard())
    user_states[call.message.chat.id] = {'step': 'waiting_for_category'}
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda call: call.data == "list_news")
def list_news(call):
    try:
        news_files = get_news_files()
        if not news_files:
            raise Exception("Не удалось получить список новостей")
        
        text = "📰 Список последних новостей:\n\n"
        for i, news in enumerate(news_files[:10], 1):
            text += f"{i}. {news.name.replace('.md', '')}\n"
        
        bot.edit_message_text(
            text,
            call.message.chat.id,
            call.message.message_id,
            reply_markup=news_management_keyboard()
        )
    except Exception as e:
        bot.send_message(call.message.chat.id, f"❌ Ошибка при получении списка новостей: {str(e)}")

@bot.callback_query_handler(func=lambda call: call.data == "edit_news")
def edit_news_start(call):
    try:
        news_files = get_news_files()
        if not news_files:
            raise Exception("Не удалось получить список новостей")
        
        markup = InlineKeyboardMarkup()
        for i, news in enumerate(news_files[:10]):
            markup.add(InlineKeyboardButton(f"{i+1}. {news.name.replace('.md', '')}", callback_data=f"edit_news_select_{i}"))
        markup.add(InlineKeyboardButton("🔙 Назад", callback_data="back_to_news"))
        
        bot.edit_message_text(
            "Выберите новость для редактирования:",
            call.message.chat.id,
            call.message.message_id,
            reply_markup=markup
        )
    except Exception as e:
        bot.send_message(call.message.chat.id, f"❌ Ошибка при выборе новости: {str(e)}")

@bot.callback_query_handler(func=lambda call: call.data.startswith("edit_news_select_"))
def edit_news_select(call):
    try:
        index = int(call.data.split("_")[3])
        news_files = get_news_files()
        if not news_files:
            raise Exception("Не удалось получить список новостей")
        
        news_file = news_files[index]
        content = get_news_file_content(news_file)
        if not content:
            raise Exception("Не удалось получить содержимое новости")
        
        front_matter, _ = parse_front_matter(content)
        if not front_matter:
            raise Exception("Не удалось разобрать front matter новости")
        
        user_states[call.message.chat.id] = {
            "action": "edit_news",
            "news_path": news_file,
            "current_content": content,
            "step": "edit_field"
        }
        
        markup = InlineKeyboardMarkup()
        markup.row(
            InlineKeyboardButton("📝 Название", callback_data="edit_field_name"),
            InlineKeyboardButton("🏷 Title", callback_data="edit_field_title")
        )
        markup.row(
            InlineKeyboardButton("📄 Описание", callback_data="edit_field_description"),
            InlineKeyboardButton("📌 Категория", callback_data="edit_field_category")
        )
        markup.row(
            InlineKeyboardButton("🖼 Изображение", callback_data="edit_field_image"),
            InlineKeyboardButton("📝 Контент", callback_data="edit_field_content")
        )
        markup.add(InlineKeyboardButton("🔙 Назад", callback_data="back_to_news"))
        
        bot.edit_message_text(
            f"Выберите поле для редактирования:\n\nТекущие данные:\n"
            f"Название: {front_matter.get('name', 'нет')}\n"
            f"Title: {front_matter.get('title', 'нет')}\n"
            f"Описание: {front_matter.get('description', 'нет')}\n"
            f"Категория: {front_matter.get('category', 'нет')}",
            call.message.chat.id,
            call.message.message_id,
            reply_markup=markup
        )
    except Exception as e:
        bot.send_message(call.message.chat.id, f"❌ Ошибка при выборе новости: {str(e)}")

@bot.callback_query_handler(func=lambda call: call.data.startswith("edit_field_"))
def edit_news_field(call):
    field = call.data.split("_")[2]
    user_data = user_states.get(call.message.chat.id, {})
    
    if user_data.get("action") != "edit_news":
        return
    
    user_data["edit_field"] = field
    user_data["step"] = "waiting_edit_value"
    
    if field == "category":
        bot.send_message(call.message.chat.id, "Выберите новую категорию:", reply_markup=category_keyboard())
    elif field == "image":
        bot.send_message(call.message.chat.id, "Отправьте новое изображение (или /skip чтобы оставить текущее):")
    else:
        prompt = {
            "name": "Введите новое название новости:",
            "title": "Введите новый title:",
            "description": "Введите новое описание:",
            "content": "Введите новый контент:"
        }.get(field, "Введите новое значение:")
        
        bot.send_message(call.message.chat.id, prompt)
    
    bot.answer_callback_query(call.id)

@bot.message_handler(func=lambda m: user_states.get(m.chat.id, {}).get('step') == 'waiting_edit_value')
def process_news_edit(message):
    try:
        user_data = user_states[message.chat.id]
        field = user_data["edit_field"]
        updates = {}
        
        if field == "category":
            if message.text in CATEGORIES.values():
                category = next(k for k, v in CATEGORIES.items() if v == message.text)
                updates["category"] = category
            else:
                raise Exception("Неверная категория")
        elif field == "image":
            if message.photo:
                file_info = bot.get_file(message.photo[-1].file_id)
                original_image = bot.download_file(file_info.file_path)
                optimized_image = optimize_image(original_image)
                
                image_name = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}.webp"
                saved_image_path = save_image(optimized_image, image_name)
                
                if saved_image_path:
                    updates["image"] = f"/{saved_image_path.replace('\\', '/')}"
            elif message.text != "/skip":
                raise Exception("Пожалуйста, отправьте изображение или используйте /skip")
        else:
            if field == "name":
                updates["name"] = message.text
            elif field == "title":
                updates["title"] = message.text
            elif field == "description":
                updates["description"] = message.text
            elif field == "content":
                front_matter, _ = parse_front_matter(user_data["current_content"])
                new_content = f"---\n{yaml.dump(front_matter, allow_unicode=True, sort_keys=False)}---\n\n{message.text}"
                
                try:
                    with open(user_data["news_path"], 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    bot.send_message(
                        message.chat.id,
                        f"✅ Контент новости успешно обновлен!\n"
                        f"📁 Путь: {user_data['news_path']}"
                    )
                except Exception as e:
                    raise Exception(f"Не удалось обновить контент: {str(e)}")
                
                del user_states[message.chat.id]
                return
        
        if field != "content":
            new_content = update_news_file_content(user_data["current_content"], updates)
            
            try:
                with open(user_data["news_path"], 'w', encoding='utf-8') as f:
                    f.write(new_content)
                bot.send_message(
                    message.chat.id,
                    f"✅ Новость успешно обновлена!\n"
                    f"📁 Путь: {user_data['news_path']}"
                )
            except Exception as e:
                raise Exception(f"Не удалось обновить новость: {str(e)}")
        
        del user_states[message.chat.id]
    
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Ошибка при обновлении новости: {str(e)}")
        if message.chat.id in user_states:
            del user_states[message.chat.id]

@bot.callback_query_handler(func=lambda call: call.data == "delete_news")
def delete_news_start(call):
    try:
        news_files = get_news_files()
        if not news_files:
            raise Exception("Не удалось получить список новостей")
        
        markup = InlineKeyboardMarkup()
        for i, news in enumerate(news_files[:10]):
            markup.add(InlineKeyboardButton(f"{i+1}. {news.name.replace('.md', '')}", callback_data=f"delete_news_confirm_{i}"))
        markup.add(InlineKeyboardButton("🔙 Назад", callback_data="back_to_news"))
        
        bot.edit_message_text(
            "Выберите новость для удаления:",
            call.message.chat.id,
            call.message.message_id,
            reply_markup=markup
        )
    except Exception as e:
        bot.send_message(call.message.chat.id, f"❌ Ошибка при выборе новости: {str(e)}")

@bot.callback_query_handler(func=lambda call: call.data.startswith("delete_news_confirm_"))
def delete_news_confirm(call):
    try:
        index = int(call.data.split("_")[3])
        news_files = get_news_files()
        if not news_files:
            raise Exception("Не удалось получить список новостей")
        
        news_file = news_files[index]
        front_matter, _ = parse_front_matter(get_news_file_content(news_file) or {})
        
        markup = InlineKeyboardMarkup()
        markup.row(
            InlineKeyboardButton("✅ Да, удалить", callback_data=f"delete_news_execute_{index}"),
            InlineKeyboardButton("❌ Нет, отмена", callback_data="back_to_news")
        )
        
        bot.edit_message_text(
            f"Вы уверены, что хотите удалить новость?\n\n{front_matter.get('name', 'Без названия')}",
            call.message.chat.id,
            call.message.message_id,
            reply_markup=markup
        )
    except Exception as e:
        bot.send_message(call.message.chat.id, f"❌ Ошибка при подтверждении удаления: {str(e)}")

@bot.callback_query_handler(func=lambda call: call.data.startswith("delete_news_execute_"))
def delete_news_execute(call):
    try:
        index = int(call.data.split("_")[3])
        news_files = get_news_files()
        if not news_files:
            raise Exception("Не удалось получить список новостей")
        
        news_file = news_files[index]
        
        if delete_news_file(news_file.name):
            bot.edit_message_text(
                f"✅ Новость успешно удалена: {news_file.name}",
                call.message.chat.id,
                call.message.message_id,
                reply_markup=news_management_keyboard()
            )
        else:
            raise Exception("Не удалось удалить файл новости")
    
    except Exception as e:
        bot.send_message(call.message.chat.id, f"❌ Ошибка при удалении новости: {str(e)}")

@bot.callback_query_handler(func=lambda call: call.data == "back_to_news")
def back_to_news(call):
    bot.edit_message_text(
        "📰 Управление новостями:",
        call.message.chat.id,
        call.message.message_id,
        reply_markup=news_management_keyboard()
    )

@bot.callback_query_handler(func=lambda call: call.data == "back_to_menu")
def back_to_menu(call):
    bot.edit_message_text(
        "🔧 Управление меню сайта:",
        call.message.chat.id,
        call.message.message_id,
        reply_markup=menu_keyboard()
    )

@bot.message_handler(func=lambda m: user_states.get(m.chat.id, {}).get('action') in ('add_item', 'edit_item') and 
                                  user_states[m.chat.id]['step'] == 'title')
def process_menu_item_title(message):
    try:
        user_data = user_states[message.chat.id]
        if message.text != '/skip':
            user_data['title'] = message.text
        user_data['step'] = 'url'
        bot.send_message(message.chat.id, "🌐 Введите URL для пункта меню:")
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Ошибка обработки названия: {str(e)}")

@bot.message_handler(func=lambda m: user_states.get(m.chat.id, {}).get('action') in ('add_item', 'edit_item') and 
                                  user_states[m.chat.id]['step'] == 'url')
def process_menu_item_url(message):
    try:
        user_data = user_states[message.chat.id]
        menu = get_menu_data()
        
        if user_data['action'] == 'add_item':
            menu['items'].append({
                'title': user_data['title'],
                'url': message.text
            })
            success_msg = "✅ Пункт меню добавлен!"
        else:
            index = user_data['index']
            if 'title' in user_data:
                menu['items'][index]['title'] = user_data['title']
            menu['items'][index]['url'] = message.text
            success_msg = "✅ Пункт меню обновлен!"
        
        if update_menu_data(menu):
            bot.send_message(message.chat.id, success_msg, reply_markup=menu_keyboard())
        else:
            bot.send_message(message.chat.id, "❌ Ошибка при сохранении меню")
        
        del user_states[message.chat.id]
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Ошибка обработки URL: {str(e)}")

# --- ЗАПУСК БОТА ---
if __name__ == "__main__":
    print("🟢 Бот запущен! Ожидание сообщений...")
    bot.infinity_polling()