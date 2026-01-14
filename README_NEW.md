# Telegram Bot - Халявная Звезда ⭐

Полнофункциональный бот для Telegram на Python, работающий 24/7!

## 📋 Функционал

✅ **Реферальная система** - приглашай друзей и получай звёзды  
✅ **Система обмена подарков** - обменивай звёзды на подарки  
✅ **Профиль пользователя** - отслеживай баланс звёзд  
✅ **Админ панель** - рассылка, управление заявками  
✅ **Поддержка пользователей** - система обращений  
✅ **24/7 работа** - веб-сервер для живучести на хостинге  

## 🚀 Быстрая установка (5 минут)

### 1️⃣ Установите Python 3.8+

Скачайте с https://www.python.org/downloads/

**⚠️ ВАЖНО:** При установке отметьте "Add Python to PATH"

Проверьте:
```powershell
python --version
```

### 2️⃣ Установите зависимости

```powershell
cd c:\Users\пк\.vscode\zvezdaBot

# Создайте виртуальное окружение
python -m venv venv

# Активируйте его
.\venv\Scripts\Activate.ps1

# Если ошибка с политикой выполнения:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Установите зависимости
pip install -r requirements.txt
```

### 3️⃣ Запустите бота

```powershell
python main.py
```

Должны увидеть:
```
🚀 BOT STARTED
🌐 Web server started on port 8080
```

### 4️⃣ Тестируйте в Telegram

Найдите бота @zvezda5bot и нажмите /start

---

## 📂 Структура проекта

```
zvezdaBot/
├── main.py                  # Основной файл бота
├── background.py            # Веб-сервер для 24/7
├── database.py              # SQLite база данных
├── requirements.txt         # Python зависимости
├── .env                     # Переменные окружения
├── Procfile                 # Для Railway развёртывания
├── SETUP_PYTHON.md         # Инструкция по установке Python
├── DEPLOYMENT_RAILWAY.md   # Инструкция по развёртыванию
└── README.md               # Этот файл
```

## ⚙️ Настройка

### Изменение администратора
В файле `main.py` найдите строку:
```python
ADMIN_ID = 5313369438
```
Замените на ваш ID.

### Добавление каналов для подписки
```python
REQUIRED_CHANNELS = ["@NasheedI5", "@your_channel"]
```

### Изменение подарков и цен
```python
GIFTS_DATA = {
    "15 ⭐": {
        "cost": 15,
        "items": ["💝", "🧸"]
    },
    # Добавьте свои...
}
```

## 🎮 Доступные команды

### Пользовательские:
- `/start` - начало и проверка подписки
- `📢 Пригласить` - реферальная ссылка
- `⭐ Ввести` - ввести звёзды (от 50)
- `🎁 Обменять подарок` - обмен звёзд на подарки
- `👤 Ваш профиль` - просмотр баланса
- `🆘 Помощь` - обращение в поддержку

### Админские:
- `/broadcast` - рассылка сообщения всем пользователям

## 🌐 Развёртывание на 24/7 сервер

### Railway.app (рекомендуется - $0)

1. Создайте GitHub репо
2. Push проект туда
3. На railway.app подключите GitHub
4. Добавьте `TELEGRAM_BOT_TOKEN` в переменные
5. Deploy!

Подробнее: читайте `DEPLOYMENT_RAILWAY.md`

### Альтернативы:
- **Heroku** - платно теперь
- **Render.com** - $7/месяц за основной план
- **AWS/Google Cloud** - платные
- **Свой VPS** - нужно настроить самостоятельно

## 💾 База данных

Проект использует **SQLite** - данные сохраняются в файл `bot_data.db`:
- 👥 Пользователи и их балансы
- 🔗 Рефералы
- 🎁 Заявки на подарки
- 📥 Заявки на ввод звёзд

При каждом перезапуске данные сохраняются!

## 🔒 Безопасность

- ✅ Токен хранится в `.env` файле
- ✅ `.env` добавлен в `.gitignore` (не попадёт на GitHub)
- ✅ Все данные зашифрованы в SQLite
- ✅ Проверка подписки на каналы

## 🐛 Решение проблем

### "Python не найден"
- Переустановите Python
- Убедитесь, что отмечена опция "Add to PATH"
- Перезагрузитесь

### "No module named 'aiogram'"
```powershell
pip install -r requirements.txt
```

### "Бот не отвечает"
- Проверьте интернет
- Убедитесь, что токен правильный в `.env`
- Посмотрите логи в консоли

### "Ошибка при запуске"
Проверьте, что все файлы на месте:
- main.py
- background.py
- database.py
- requirements.txt
- .env

## 📊 Как работает реферальная система

1. Пользователь A приглашает Пользователя B по ссылке
2. B подписывается на каналы
3. B подтверждает подписку
4. A получает **1.5 ⭐** за приглашение
5. B получает **3 ⭐** за начало

## 💡 Расширение функционала

Добавьте новую команду в `main.py`:

```python
@dp.message(F.text == "🆕 Новая кнопка")
async def new_handler(message: Message):
    uid = message.from_user.id
    await message.answer("Ответ на кнопку!")
```

Добавьте в меню:
```python
def main_menu():
    return ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="📢 Пригласить"),
         KeyboardButton(text="⭐ Ввести")],
        [KeyboardButton(text="🎁 Обменять подарок"),
         KeyboardButton(text="👤 Ваш профиль")],
        [KeyboardButton(text="🆘 Помощь"),
         KeyboardButton(text="🆕 Новая кнопка")]
    ], resize_keyboard=True)
```

## 📞 Документация

- [Aiogram 3.x Docs](https://docs.aiogram.dev/en/latest/)
- [Telegram Bot API](https://core.telegram.org/bots/api)
- [SQLite Python](https://docs.python.org/3/library/sqlite3.html)

## 📄 Лицензия

ISC

---

**Вопросы?** Проверьте файлы `SETUP_PYTHON.md` или `DEPLOYMENT_RAILWAY.md`

**Готово!** Бот готов к работе! 🌟
