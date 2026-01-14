# 🚀 Развёртывание на Railway.app (24/7 Бесплатно)

## Преимущества Railway:
✅ **Бесплатная микро-дайна** - $5/месяц (обычно хватает)  
✅ **24/7 работа** - без останова  
✅ **Автоматический перезапуск** - если бот упадёт  
✅ **Простое развёртывание** - через GitHub  

## Быстрый старт на Railway (5 минут):

```powershell
# 1. Подготовьте Git
git init
git add .
git commit -m "Bot ready for Railway"

# 2. Создайте GitHub репо и push
git push https://github.com/YOUR_USERNAME/zvezdaBot.git

# 3. На railway.app:
# - Connect GitHub
# - Select zvezdaBot repo
# - Add переменную: TELEGRAM_BOT_TOKEN=ваш_токен
# - Deploy!
```

---

## Альтернативы (если Railway не нравится):

### 1. Heroku
```bash
heroku login
heroku create zvezda-bot
git push heroku main
heroku config:set TELEGRAM_BOT_TOKEN=ваш_токен
```

### 2. Render.com
- Как Railway, но с лучше UI

### 3. Replit
- Онлайн IDE + 24/7 бесплатный хост

### 4. Облако (AWS, Google Cloud, Azure)
- Платно, но более надёжно

---

## 🔧 Решение проблем

**"Bот не запускается"**
- Проверьте логи в Railway
- Убедитесь, что токен правильный
- Проверьте requirements.txt

**"Данные теряются после перезагрузки"**
- Это нормально! Это значит бот перезагружается
- Данные сохраняются в SQLite (файл `bot_data.db`)
- На Railway этот файл тоже может потеряться

**Если нужна ПОСТОЯННАЯ база данных:**
- Подключите PostgreSQL (можно бесплатный на Railway)
- Или используйте облачное хранилище

---

## 📊 Мониторинг

После развёртывания:
1. Тестируйте команды бота
2. Смотрите логи в Railway
3. Проверяйте работу 24/7

**Готово! Бот будет работать 24/7 на Railway!** 🌟
