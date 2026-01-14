import asyncio
import logging
import os
from background import keep_alive
from database import init_db, get_user_balance, add_user, update_balance, user_exists
from database import add_referral, is_referral_awarded, mark_referral_awarded, get_referral_inviter, get_all_users
from database import add_gift_request, add_star_input_request
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import (Message, ReplyKeyboardMarkup, KeyboardButton,
                           ReplyKeyboardRemove, InlineKeyboardMarkup,
                           InlineKeyboardButton, CallbackQuery)
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage

# ============ НАСТРОЙКИ ============
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN environment variable is not set")
ADMIN_ID = 5313369438
BOT_USERNAME = "zvezda5bot"
# Список каналов для обязательной подписки
REQUIRED_CHANNELS = ["@NasheedI5"]
# ====================================

# Инициализация базы данных
init_db()

logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())


# Состояния
class GiftExchange(StatesGroup):
    choosing_tier = State()
    choosing_gift = State()


class EnterStarsFlow(StatesGroup):
    amount = State()


class HelpFlow(StatesGroup):
    message = State()


class AdminBroadcast(StatesGroup):
    message = State()


class AdminSupportReply(StatesGroup):
    message = State()


# Клавиатуры
def sub_inline_kb():
    keyboard = []
    # Формируем кнопки подписок в два столбца (по 2 в ряду)
    for i in range(0, len(REQUIRED_CHANNELS), 2):
        row = []
        # Левая кнопка
        row.append(
            InlineKeyboardButton(
                text=f"{i+1} Подписаться",
                url=f"https://t.me/{REQUIRED_CHANNELS[i].replace('@', '')}"))
        # Правая кнопка (если есть)
        if i + 1 < len(REQUIRED_CHANNELS):
            row.append(
                InlineKeyboardButton(
                    text=f"{i+2} Подписаться",
                    url=
                    f"https://t.me/{REQUIRED_CHANNELS[i+1].replace('@', '')}"))
        keyboard.append(row)

    # Кнопка проверки внизу
    keyboard.append([
        InlineKeyboardButton(text="проверить подписку ✅",
                             callback_data="check_subscription")
    ])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def main_menu():
    return ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="📢 Пригласить"),
         KeyboardButton(text="⭐ Ввести")],
        [
            KeyboardButton(text="🎁 Обменять подарок"),
            KeyboardButton(text="👤 Ваш профиль")
        ], [KeyboardButton(text="🆘 Помощь")]
    ],
                               resize_keyboard=True)


def back_kb():
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="🔙 Назад в меню")]],
        resize_keyboard=True)


# База пользователей - теперь используется SQLite
# users = {5313369438: 1000, 6692832760: 1000000}
# База рефералов - теперь используется SQLite
# referrals = {}  # invited_id -> inviter_id
# Список тех, кто уже получил награду за подписку реферала
# awarded_referrals = set()  # invited_id


async def check_all_subs(user_id: int):
    for channel in REQUIRED_CHANNELS:
        try:
            member = await bot.get_chat_member(channel, user_id)
            if member.status not in ["member", "administrator", "creator"]:
                return False
        except Exception:
            return False
    return True


# ===== START =====
@dp.message(Command("start"))
async def start_cmd(message: Message):
    args = message.text.split()
    uid = message.from_user.id

    # Обработка реферальной ссылки
    if len(args) > 1:
        try:
            inviter_id = int(args[1])
            if inviter_id != uid and not user_exists(uid):
                add_referral(uid, inviter_id)
        except ValueError:
            pass

    is_subscribed = await check_all_subs(uid)
    if is_subscribed:
        if not user_exists(uid):
            add_user(uid, message.from_user.full_name, 3)
            # Если пришел по рефералке и подписался
            inviter_id = get_referral_inviter(uid)
            if inviter_id and not is_referral_awarded(uid):
                update_balance(inviter_id, 1.5)
                mark_referral_awarded(uid)
                try:
                    await bot.send_message(
                        inviter_id,
                        f"🎉 Вам начислено 1.5 ⭐ за приглашение нового пользователя: [{message.from_user.full_name}](tg://user?id={uid})",
                        parse_mode="Markdown")
                except:
                    pass

        await message.answer(
            "Ассаламу алейкум 🤍\n\n"
            "Это бот «Халявная Звезда ⭐️»\n\n"
            "🔹 Получай звёзды за приглашения\n"
            "🔹 Обменивай звёзды на подарки 🎁\n\n"
            "Добро пожаловать в главное меню!",
            reply_markup=main_menu())
    else:
        await message.answer(
            "Чтобы продолжить пользоваться ботом подпишитесь на каналов:",
            reply_markup=sub_inline_kb())


@dp.callback_query(F.data == "check_subscription")
async def process_check_sub(callback: CallbackQuery):
    uid = callback.from_user.id
    is_subscribed = await check_all_subs(uid)
    if not is_subscribed:
        await callback.answer("❌ Вы не подписаны на все каналы!",
                              show_alert=True)
        return

    if not user_exists(uid):
        add_user(uid, callback.from_user.full_name, 3)
        # Если пришел по рефералке и подписался через кнопку
        inviter_id = get_referral_inviter(uid)
        if inviter_id and not is_referral_awarded(uid):
            update_balance(inviter_id, 1.5)
            mark_referral_awarded(uid)
            try:
                await bot.send_message(
                    inviter_id,
                    f"🎉 Вам начислено 1.5 ⭐ за приглашение нового пользователя: [{callback.from_user.full_name}](tg://user?id={uid})",
                    parse_mode="Markdown")
            except:
                pass

    await callback.message.delete()
    await bot.send_message(uid, "Ассаламу алейкум 🤍\n\n"
                           "Это бот «Халявная Звезда ⭐️»\n\n"
                           "🔹 Получай звёзды за приглашения\n"
                           "🔹 Обменивай звёзды на подарки 🎁\n\n"
                           "✅ Подписка проверена! Добро пожаловать!",
                           reply_markup=main_menu())
    await callback.answer()


# ===== ПРОФИЛЬ =====
@dp.message(F.text == "👤 Ваш профиль")
async def profile(message: Message):
    uid = message.from_user.id
    balance = get_user_balance(uid)
    await message.answer(f"👤 Ваш профиль\n\n"
                         f"⭐️ Звёзд: {balance}",
                         reply_markup=main_menu())


# ===== ПРИГЛАСИТЬ =====
@dp.message(F.text == "📢 Пригласить")
async def invite(message: Message):
    uid = message.from_user.id
    ref_link = f"https://t.me/{BOT_USERNAME}?start={uid}"
    await message.answer(
        f"Ваша реферальная ссылка 🔗\n`{ref_link}`\n\n"
        "За каждого приглашённого друга вы получите 1.5 ⭐",
        parse_mode="Markdown",
        reply_markup=main_menu())


# ===== ОБМЕН ПОДАРКОВ =====
GIFTS_DATA = {
    "15 ⭐": {
        "cost": 15,
        "items": ["💝", "🧸"]
    },
    "25 ⭐": {
        "cost": 25,
        "items": ["🌹", "🎁"]
    },
    "50 ⭐": {
        "cost": 50,
        "items": ["💐", "🎂", "🚀"]
    },
    "100 ⭐": {
        "cost": 100,
        "items": ["🏆", "💍", "💎"]
    }
}


@dp.message(F.text == "🎁 Обменять подарок")
async def start_exchange(message: Message, state: FSMContext):
    kb = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="15 ⭐"),
                   KeyboardButton(text="25 ⭐")],
                  [KeyboardButton(text="50 ⭐"),
                   KeyboardButton(text="100 ⭐")],
                  [KeyboardButton(text="🔙 Назад в меню")]],
        resize_keyboard=True)
    await message.answer("Выберите сумму звёзд для обмена:", reply_markup=kb)
    await state.set_state(GiftExchange.choosing_tier)


@dp.message(GiftExchange.choosing_tier)
async def choose_tier(message: Message, state: FSMContext):
    if message.text == "🔙 Назад в меню":
        await state.clear()
        await message.answer("Возвращаюсь...", reply_markup=main_menu())
        return

    if message.text not in GIFTS_DATA:
        await message.answer("❌ Выберите вариант из кнопок")
        return

    tier = GIFTS_DATA[message.text]
    uid = message.from_user.id
    balance = get_user_balance(uid)
    if balance < tier["cost"]:
        await message.answer("❌ Недостаточно ⭐ на балансе")
        return

    await state.update_data(cost=tier["cost"], tier_name=message.text)

    buttons = [[KeyboardButton(text=item)] for item in tier["items"]]
    buttons.append([KeyboardButton(text="🔙 Назад в меню")])

    kb = ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)
    await message.answer("Выберите подарок:", reply_markup=kb)
    await state.set_state(GiftExchange.choosing_gift)


@dp.message(GiftExchange.choosing_gift)
async def finalize_exchange(message: Message, state: FSMContext):
    if message.text == "🔙 Назад в меню":
        await state.clear()
        await message.answer("Возвращаюсь...", reply_markup=main_menu())
        return

    data = await state.get_data()
    cost = data['cost']
    gift_name = message.text
    uid = message.from_user.id

    update_balance(uid, -cost)
    add_gift_request(uid, gift_name, cost)

    await message.answer(
        f"✅ Ваша заявка отправлена админу на обмен подарка {gift_name}.\n"
        f"⏳ В течение 12ч вам отправим {gift_name}",
        reply_markup=main_menu())

    # Кнопка для админа
    admin_kb = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="Отправил ✅",
                             callback_data=f"gift_{uid}_{gift_name}")
    ]])

    try:
        await bot.send_message(ADMIN_ID, f"🎁 *Новая заявка на подарок!*\n"
                               f"Пользователь: [ссылка](tg://user?id={uid})\n"
                               f"Выбрал: {gift_name} (за {cost} ⭐)",
                               parse_mode="Markdown",
                               reply_markup=admin_kb)
    except Exception:
        pass

    await state.clear()


# ===== АДМИН ПАНЕЛЬ (РАССЫЛКА) =====
@dp.message(Command("broadcast"))
async def start_broadcast(message: Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return
    await message.answer(
        "Введите текст рекламы/сообщения для всех пользователей:",
        reply_markup=back_kb())
    await state.set_state(AdminBroadcast.message)


@dp.message(AdminBroadcast.message)
async def process_broadcast(message: Message, state: FSMContext):
    if message.text == "🔙 Назад в меню":
        await state.clear()
        await message.answer("Отменено.", reply_markup=main_menu())
        return

    count = 0
    all_users = get_all_users()
    for user_id in all_users:
        try:
            await bot.send_message(user_id, message.text)
            count += 1
            await asyncio.sleep(0.05)
        except Exception:
            pass

    await message.answer(
        f"✅ Рассылка завершена! Получили: {count} пользователей.",
        reply_markup=main_menu())
    await state.clear()


# ===== ПОМОЩЬ =====
@dp.message(F.text == "🆘 Помощь")
async def help_cmd(message: Message, state: FSMContext):
    await message.answer("Напишите вашу проблему, мы скоро её решим:",
                         reply_markup=back_kb())
    await state.set_state(HelpFlow.message)


@dp.message(HelpFlow.message)
async def process_help(message: Message, state: FSMContext):
    if message.text == "🔙 Назад в меню":
        await state.clear()
        await message.answer("Возвращаюсь...", reply_markup=main_menu())
        return

    uid = message.from_user.id

    # Уведомление админу
    admin_kb = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="Ответить 💬", callback_data=f"reply_{uid}")
    ]])

    try:
        await bot.send_message(ADMIN_ID, f"🆘 *Новое обращение в поддержку!*\n"
                               f"От: [ссылка](tg://user?id={uid})\n"
                               f"Сообщение: {message.text}",
                               parse_mode="Markdown",
                               reply_markup=admin_kb)
    except Exception:
        pass

    await message.answer(
        "✅ Ваше сообщение отправлено администратору. Ожидайте ответа.",
        reply_markup=main_menu())
    await state.clear()


# ===== ВВЕСТИ ЗВЁЗДЫ =====
@dp.message(F.text == "⭐ Ввести")
async def enter_stars(message: Message, state: FSMContext):
    uid = message.from_user.id
    balance = get_user_balance(uid)

    if balance < 50:
        await message.answer(
            f"❌ На вашем балансе недостаточно звёзд для ввода — минимальный ввод от 50⭐\n\n"
            f"Ваш баланс: {balance} ⭐",
            reply_markup=main_menu())
        return

    await message.answer(
        f"Ваш баланс: {balance} ⭐️\n"
        "Введите количество звезд для списания:",
        reply_markup=back_kb())
    await state.set_state(EnterStarsFlow.amount)


@dp.message(EnterStarsFlow.amount)
async def process_enter_amount(message: Message, state: FSMContext):
    if message.text == "🔙 Назад в меню":
        await state.clear()
        await message.answer("Возвращаюсь...", reply_markup=main_menu())
        return

    uid = message.from_user.id
    try:
        amount = float(message.text)
    except ValueError:
        await message.answer("❌ Пожалуйста, введите число!")
        return

    if amount < 50:
        await message.answer(
            "❌ Минимальный ввод от 50⭐. Попробуйте еще раз или нажмите Назад.")
        return

    balance = get_user_balance(uid)
    if amount > balance:
        await message.answer(
            f"❌ На вашем балансе недостаточно звёзд. Ваш баланс: {balance} ⭐")
        return

    update_balance(uid, -amount)
    add_star_input_request(uid, amount)

    await message.answer(
        f"✅ Ваша заявка отправлена админу на ввод {amount} ⭐.\n"
        f"⏳ В течение 24ч вам начислят {amount} ⭐.",
        reply_markup=main_menu())

    admin_kb = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="Оплатил ✅",
                             callback_data=f"pay_{uid}_{amount}")
    ]])

    try:
        await bot.send_message(ADMIN_ID, f"📥 *Новая заявка на ввод!*\n"
                               f"Пользователь: [ссылка](tg://user?id={uid})\n"
                               f"Сумма: {amount} ⭐",
                               parse_mode="Markdown",
                               reply_markup=admin_kb)
    except Exception:
        pass

    await state.clear()


# Обработка нажатий админом
@dp.callback_query(F.data.startswith("pay_"))
async def admin_pay_confirm(callback: CallbackQuery):
    _, uid, amount = callback.data.split("_")
    uid = int(uid)
    amount = float(amount)
    current_balance = get_user_balance(uid)
    try:
        await bot.send_message(
            uid, f"✅ Вы успешно ввели {amount} ⭐️\n"
            f"Остаток: {current_balance} ⭐️")
        await callback.answer("Пользователь уведомлен! ✅")
        await callback.message.edit_text(callback.message.text +
                                         "\n\n✅ ОПЛАЧЕНО",
                                         reply_markup=None)
    except Exception as e:
        await callback.answer(f"Ошибка уведомления: {e}", show_alert=True)


@dp.callback_query(F.data.startswith("gift_"))
async def admin_gift_sent_confirm(callback: CallbackQuery):
    _, uid, gift_name = callback.data.split("_")
    uid = int(uid)
    current_balance = get_user_balance(uid)
    try:
        await bot.send_message(
            uid, f"✅ Вы успешно обменяли ⭐ на {gift_name}\n"
            f"Остаток: {current_balance} ⭐️")
        await callback.answer("Пользователь уведомлен! ✅")
        await callback.message.edit_text(callback.message.text +
                                         "\n\n✅ ОТПРАВЛЕНО",
                                         reply_markup=None)
    except Exception as e:
        await callback.answer(f"Ошибка уведомления: {e}", show_alert=True)


# Обработка ответа админа на помощь
@dp.callback_query(F.data.startswith("reply_"))
async def admin_start_reply(callback: CallbackQuery, state: FSMContext):
    uid = int(callback.data.split("_")[1])
    await state.update_data(reply_to_uid=uid)
    await callback.message.answer(
        f"Введите ответ для пользователя [ID: {uid}]:", reply_markup=back_kb())
    await state.set_state(AdminSupportReply.message)
    await callback.answer()


@dp.message(AdminSupportReply.message)
async def process_admin_support_reply(message: Message, state: FSMContext):
    if message.text == "🔙 Назад в меню":
        await state.clear()
        await message.answer("Отменено.", reply_markup=main_menu())
        return

    data = await state.get_data()
    user_id = data['reply_to_uid']

    try:
        await bot.send_message(
            user_id,
            f"✉️ *Ответ от администрации:*\n\n{message.text}",
            parse_mode="Markdown")
        await message.answer("✅ Ответ успешно отправлен пользователю!",
                             reply_markup=main_menu())
    except Exception as e:
        await message.answer(f"❌ Ошибка при отправке ответа: {e}",
                             reply_markup=main_menu())

    await state.clear()

# ===== ЗАПУСК =====
async def main():
    print("🚀 BOT STARTED")
    keep_alive()  # Запускаем веб-сервер для "живучести"
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
