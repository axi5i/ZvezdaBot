# 🚀 Инструкция по установке Python и запуску бота

## ❌ Проблема
Python не установлен на компьютере.

## ✅ Решение

### Шаг 1: Установка Python

**Способ 1: Официальный установщик (рекомендуется)**
1. Перейдите на https://www.python.org/downloads/
2. Нажмите "Download Python 3.11" (или новее)
3. Запустите установщик
4. **⚠️ ВАЖНО:** Отметьте галочку "Add Python to PATH"
5. Нажмите "Install Now"
6. После завершения перезагрузитесь

**Способ 2: Windows Store**
1. Откройте Microsoft Store
2. Поищите "Python 3.11"
3. Установите официальный пакет от Python Software Foundation

### Шаг 2: Проверка установки

После установки откройте PowerShell и введите:
```powershell
python --version
```

Должно вывести что-то типа: `Python 3.11.0`

### Шаг 3: Установка зависимостей бота

Откройте PowerShell в папке проекта и выполните:

```powershell
cd c:\Users\пк\.vscode\zvezdaBot

# Создание виртуального окружения
python -m venv venv

# Активация окружения
.\venv\Scripts\Activate.ps1

# Если ошибка с политикой выполнения, выполните:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Затем снова активируйте
.\venv\Scripts\Activate.ps1

# Установка зависимостей
pip install -r requirements.txt
```

### Шаг 4: Запуск бота

```powershell
python main.py
```

Должны увидеть:
```
🚀 BOT STARTED
```

### Шаг 5: Тестирование

1. Найдите бота в Telegram: @zvezda5bot
2. Нажмите /start
3. Проверьте:
   - Кнопку "Пригласить" 📢
   - Кнопку "Профиль" 👤
   - Команду /broadcast (для админа)

---

## 🐛 Если у вас есть ошибки

### "ModuleNotFoundError: No module named 'aiogram'"
```powershell
pip install -r requirements.txt
```

### "Permission denied" при активации окружения
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.\venv\Scripts\Activate.ps1
```

### "python не распознана"
- Перезагрузитесь после установки Python
- Убедитесь, что Python добавлен в PATH

---

**После установки Python, запустите еще раз команду в шаге 3!** 🌟
