# Telegram Bot - Халявная Звезда ⭐

Полнофункциональный бот для Telegram на Python, работающий 24/7!

## 📋 Функционал

✅ **Реферальная система** - приглашай друзей и получай звёзды  
✅ **Система обмена подарков** - обменивай звёзды на подарки  
✅ **Профиль пользователя** - отслеживай баланс звёзд  
✅ **Админ панель** - рассылка, управление заявками  
✅ **Поддержка пользователей** - система обращений  
✅ **24/7 работа** - веб-сервер для живучести на хостинге  

## 🚀 Быстрая установка

### 1. Установите Python 3.8+
Убедитесь, что Python установлен:
```bash
python --version
```

### 2. Клонируйте/скопируйте проект
```bash
cd c:\Users\пк\.vscode\zvezdaBot
```

### 3. Создайте виртуальное окружение
```bash
python -m venv venv
venv\Scripts\activate
```

### 4. Установите зависимости
```bash
pip install -r requirements.txt
```

### 5. Настройте .env файл
Откройте `.env` и убедитесь, что там ваш токен:
```
TELEGRAM_BOT_TOKEN=ваш_токен_от_botfather
```

### 6. Запустите бота
```bash
python src/index.js
```

Бот запустится и будет готов принимать команды!

## 📂 Структура проекта

```
zvezdaBot/
├── src/
│   └── index.js          # Основной файл бота с обработчиками
├── background.py         # Веб-сервер для живучести на 24/7
├── .env                  # Переменные окружения (токен)
├── .gitignore           # Игнорирование файлов в Git
├── requirements.txt     # Python зависимости
└── README.md            # Документация
```

## ⚙️ Настройка

### Изменение админа
В `src/index.js` найдите строку:
```python
ADMIN_ID = 5313369438
```
Замените на ваш ID.

### Добавление каналов подписки
```python
REQUIRED_CHANNELS = ["@NasheedI5"]  # Добавьте нужные каналы
```

### Изменение размеров звёзд за действия
```python
GIFTS_DATA = {
    "15 ⭐": {...},
    "25 ⭐": {...},
    ...
}
```

## 🎮 Доступные команды

**Пользовательские:**
- `/start` - начало и проверка подписки
- `📢 Пригласить` - реферальная ссылка
- `⭐ Ввести` - ввести звёзды (от 50)
- `🎁 Обменять подарок` - обмен звёзд на подарки
- `👤 Ваш профиль` - просмотр баланса
- `🆘 Помощь` - обращение в поддержку

**Админские:**
- `/broadcast` - рассылка сообщения всем пользователям

## 🌐 Развертывание на 24/7 сервер

### Вариант 1: На сервере Linux/VPS (рекомендуется)

```bash
# Установите экземпляр на сервере
ssh root@your_server_ip
git clone https://github.com/your-repo/zvezdaBot
cd zvezdaBot
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Запустите с PM2
npm install -g pm2
pm2 start "python src/index.js" --name "telegram-bot"
pm2 startup
pm2 save
```

### Вариант 2: Systemd (Linux)

Создайте файл `/etc/systemd/system/telegram-bot.service`:
```ini
[Unit]
Description=Telegram Zvezda Bot
After=network.target

[Service]
Type=simple
User=your_user
WorkingDirectory=/path/to/zvezdaBot
Environment="PATH=/path/to/zvezdaBot/venv/bin"
ExecStart=/path/to/zvezdaBot/venv/bin/python src/index.js
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Затем:
```bash
sudo systemctl daemon-reload
sudo systemctl enable telegram-bot
sudo systemctl start telegram-bot
sudo systemctl status telegram-bot
```

### Вариант 3: Docker

Создайте `Dockerfile`:
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "src/index.js"]
```

Запуск:
```bash
docker build -t telegram-bot .
docker run -d --restart always -e TELEGRAM_BOT_TOKEN=your_token telegram-bot
```

## 🛠️ Расширение функционала

Добавьте новый обработчик в `src/index.js`:

```python
@dp.message(F.text == "🆕 Новая кнопка")
async def new_handler(message: Message):
    uid = message.from_user.id
    await message.answer("Ответ на новую кнопку!")
```

Добавьте кнопку в меню:
```python
def main_menu():
    return ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="📢 Пригласить"),
         KeyboardButton(text="⭐ Ввести")],
        [
            KeyboardButton(text="🎁 Обменять подарок"),
            KeyboardButton(text="👤 Ваш профиль")
        ], 
        [KeyboardButton(text="🆘 Помощь"),
         KeyboardButton(text="🆕 Новая кнопка")]
    ],
                           resize_keyboard=True)
```

## 📖 Документация

- [Aiogram 3.x Документация](https://docs.aiogram.dev/en/latest/)
- [Telegram Bot API](https://core.telegram.org/bots/api)

## 🐛 Решение проблем

**Ошибка: "TELEGRAM_BOT_TOKEN environment variable is not set"**
- Убедитесь, что в файле `.env` правильно указан токен

**Бот не отвечает**
- Проверьте интернет соединение
- Убедитесь, что токен правильный
- Посмотрите логи: проверьте консоль на ошибки

**"ModuleNotFoundError: No module named 'aiogram'"**
```bash
pip install -r requirements.txt
```

## 📞 Контакты

Вопросы? Пишите в поддержку бота через команду `/help`

## 📄 Лицензия

ISC
