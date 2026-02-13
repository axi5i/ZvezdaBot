import asyncio
import logging
import os
import random
from datetime import datetime, timedelta
from dotenv import load_dotenv
from background import keep_alive
from database import init_db, get_user_balance, add_user, update_balance, user_exists
from database import add_referral, is_referral_awarded, mark_referral_awarded, get_referral_inviter, get_all_users
from database import add_gift_request, add_star_input_request
from database import add_sponsor, get_active_sponsors, remove_sponsor, get_or_create_task, mark_task_completed, is_task_completed_today
from database import get_top_users, get_user_rank, get_user_info
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import (Message, ReplyKeyboardMarkup, KeyboardButton,
                           ReplyKeyboardRemove, InlineKeyboardMarkup,
                           InlineKeyboardButton, CallbackQuery)
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage

# ╨Ч╨░╨│╤А╤Г╨╖╨╕╤В╤М ╨┐╨╡╤А╨╡╨╝╨╡╨╜╨╜╤Л╨╡ ╨╕╨╖ .env ╤Д╨░╨╣╨╗╨░
load_dotenv()

# ============ ╨Э╨Р╨б╨в╨а╨Ю╨Щ╨Ъ╨Ш ============
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN environment variable is not set")
ADMIN_ID = 5313369438
BOT_USERNAME = "zvezda5i_bot"
# ╨Я╤А╨╕╨▓╨░╤В╨╜╤Л╨╣ ╨║╨░╨╜╨░╨╗ ╨┤╨╗╤П ╨╗╨╛╨│╨╕╤А╨╛╨▓╨░╨╜╨╕╤П
LOG_CHANNEL_ID = -1003667021274
# ╨б╨┐╨╕╤Б╨╛╨║ ╨║╨░╨╜╨░╨╗╨╛╨▓ ╨┤╨╗╤П ╨╛╨▒╤П╨╖╨░╤В╨╡╨╗╤М╨╜╨╛╨╣ ╨┐╨╛╨┤╨┐╨╕╤Б╨║╨╕
REQUIRED_CHANNELS = ["@NasheedI5"]
# ====================================

# ╨Ш╨╜╨╕╤Ж╨╕╨░╨╗╨╕╨╖╨░╤Ж╨╕╤П ╨▒╨░╨╖╤Л ╨┤╨░╨╜╨╜╤Л╤Е
init_db()

logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())


# ╨б╨╛╤Б╤В╨╛╤П╨╜╨╕╤П
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


class AdminAddSponsor(StatesGroup):
    channel_name = State()
    duration = State()


class AdminRemoveSponsor(StatesGroup):
    channel_name = State()


class AdminAddPermanentSponsor(StatesGroup):
    channel_name = State()


# ╨Ъ╨╗╨░╨▓╨╕╨░╤В╤Г╤А╤Л
def sub_inline_kb():
    keyboard = []
    # ╨д╨╛╤А╨╝╨╕╤А╤Г╨╡╨╝ ╨║╨╜╨╛╨┐╨║╨╕ ╨┐╨╛╨┤╨┐╨╕╤Б╨╛╨║ ╨▓ ╨┤╨▓╨░ ╤Б╤В╨╛╨╗╨▒╤Ж╨░ (╨┐╨╛ 2 ╨▓ ╤А╤П╨┤╤Г)
    for i in range(0, len(REQUIRED_CHANNELS), 2):
        row = []
        # ╨Ы╨╡╨▓╨░╤П ╨║╨╜╨╛╨┐╨║╨░
        row.append(
            InlineKeyboardButton(
                text=f"{i+1} ╨Я╨╛╨┤╨┐╨╕╤Б╨░╤В╤М╤Б╤П",
                url=f"https://t.me/{REQUIRED_CHANNELS[i].replace('@', '')}"))
        # ╨Я╤А╨░╨▓╨░╤П ╨║╨╜╨╛╨┐╨║╨░ (╨╡╤Б╨╗╨╕ ╨╡╤Б╤В╤М)
        if i + 1 < len(REQUIRED_CHANNELS):
            row.append(
                InlineKeyboardButton(
                    text=f"{i+2} ╨Я╨╛╨┤╨┐╨╕╤Б╨░╤В╤М╤Б╤П",
                    url=
                    f"https://t.me/{REQUIRED_CHANNELS[i+1].replace('@', '')}"))
        keyboard.append(row)

    # ╨Ъ╨╜╨╛╨┐╨║╨░ ╨┐╤А╨╛╨▓╨╡╤А╨║╨╕ ╨▓╨╜╨╕╨╖╤Г
    keyboard.append([
        InlineKeyboardButton(text="╨┐╤А╨╛╨▓╨╡╤А╨╕╤В╤М ╨┐╨╛╨┤╨┐╨╕╤Б╨║╤Г тЬЕ",
                             callback_data="check_subscription")
    ])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def main_menu():
    return ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="ЁЯОп ╨Х╨╢╨╡╨┤╨╜╨╡╨▓╨╜╨╛╨╡ ╨Ч╨░╨┤╨░╨╜╨╕╨╡"),
         KeyboardButton(text="ЁЯУв ╨Я╤А╨╕╨│╨╗╨░╤Б╨╕╤В╤М")],
        [KeyboardButton(text="тнР ╨Т╨▓╨╡╤Б╤В╨╕"),
         KeyboardButton(text="ЁЯОБ ╨Ю╨▒╨╝╨╡╨╜╤П╤В╤М ╨┐╨╛╨┤╨░╤А╨╛╨║")],
        [KeyboardButton(text="ЁЯСд ╨Т╨░╤И ╨┐╤А╨╛╤Д╨╕╨╗╤М"),
         KeyboardButton(text="тнР ╨а╨╡╨╣╤В╨╕╨╜╨│")],
        [KeyboardButton(text="ЁЯЖШ ╨Я╨╛╨╝╨╛╤Й╤М")]
    ],
                               resize_keyboard=True)


def back_kb():
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="ЁЯФЩ ╨Э╨░╨╖╨░╨┤ ╨▓ ╨╝╨╡╨╜╤О")]],
        resize_keyboard=True)


# ╨С╨░╨╖╨░ ╨┐╨╛╨╗╤М╨╖╨╛╨▓╨░╤В╨╡╨╗╨╡╨╣ - ╤В╨╡╨┐╨╡╤А╤М ╨╕╤Б╨┐╨╛╨╗╤М╨╖╤Г╨╡╤В╤Б╤П SQLite
# users = {5313369438: 1000, 6692832760: 1000000}
# ╨С╨░╨╖╨░ ╤А╨╡╤Д╨╡╤А╨░╨╗╨╛╨▓ - ╤В╨╡╨┐╨╡╤А╤М ╨╕╤Б╨┐╨╛╨╗╤М╨╖╤Г╨╡╤В╤Б╤П SQLite
# referrals = {}  # invited_id -> inviter_id
# ╨б╨┐╨╕╤Б╨╛╨║ ╤В╨╡╤Е, ╨║╤В╨╛ ╤Г╨╢╨╡ ╨┐╨╛╨╗╤Г╤З╨╕╨╗ ╨╜╨░╨│╤А╨░╨┤╤Г ╨╖╨░ ╨┐╨╛╨┤╨┐╨╕╤Б╨║╤Г ╤А╨╡╤Д╨╡╤А╨░╨╗╨░
# awarded_referrals = set()  # invited_id


async def log_to_channel(text: str):
    """╨Ы╨╛╨│╨╕╤А╨╛╨▓╨░╤В╤М ╤Б╨╛╨▒╤Л╤В╨╕╨╡ ╨▓ ╨┐╤А╨╕╨▓╨░╤В╨╜╤Л╨╣ ╨║╨░╨╜╨░╨╗"""
    try:
        await bot.send_message(LOG_CHANNEL_ID, text)
    except Exception as e:
        print(f"╨Ю╤И╨╕╨▒╨║╨░ ╨╗╨╛╨│╨╕╤А╨╛╨▓╨░╨╜╨╕╤П: {e}")


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
    full_name = message.from_user.full_name or "╨Я╨╛╨╗╤М╨╖╨╛╨▓╨░╤В╨╡╨╗╤М"

    # ╨Ы╨╛╨│╨╕╤А╤Г╨╡╨╝ ╨▓╤Е╨╛╨┤
    await log_to_channel(f"ЁЯСд **╨Я╨╛╨╗╤М╨╖╨╛╨▓╨░╤В╨╡╨╗╤М ╨╖╨░╤Е╨╛╨┤╨╕╤В:** {full_name}\n[╨Я╤А╨╛╤Д╨╕╨╗╤М](tg://user?id={uid})", )

    # ╨Ю╨▒╤А╨░╨▒╨╛╤В╨║╨░ ╤А╨╡╤Д╨╡╤А╨░╨╗╤М╨╜╨╛╨╣ ╤Б╤Б╤Л╨╗╨║╨╕
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
            add_user(uid, full_name, 3)
            # ╨Х╤Б╨╗╨╕ ╨┐╤А╨╕╤И╨╡╨╗ ╨┐╨╛ ╤А╨╡╤Д╨╡╤А╨░╨╗╨║╨╡ ╨╕ ╨┐╨╛╨┤╨┐╨╕╤Б╨░╨╗╤Б╤П
            inviter_id = get_referral_inviter(uid)
            if inviter_id and not is_referral_awarded(uid):
                update_balance(inviter_id, 1.5)
                mark_referral_awarded(uid)
                try:
                    inviter_name = get_user_info(inviter_id)[1] if get_user_info(inviter_id) else "╨Я╨╛╨╗╤М╨╖╨╛╨▓╨░╤В╨╡╨╗╤М"
                    await bot.send_message(
                        inviter_id,
                        f"ЁЯОЙ ╨Т╨░╨╝ ╨╜╨░╤З╨╕╤Б╨╗╨╡╨╜╨╛ 1.5 тнР ╨╖╨░ ╨┐╤А╨╕╨│╨╗╨░╤И╨╡╨╜╨╕╨╡ ╨╜╨╛╨▓╨╛╨│╨╛ ╨а╨╡╤Д╨╡╤А╨░╨╗╨░!\n[{full_name}](tg://user?id={uid})",
                        parse_mode="Markdown")
                    await log_to_channel(
                        f"ЁЯОЙ **╨Э╨╛╨▓╤Л╨╣ ╤А╨╡╤Д╨╡╤А╨░╨╗!**\n"
                        f"╨Я╤А╨╕╨│╨╗╨░╤Б╨╕╨╗: [{inviter_name}](tg://user?id={inviter_id})\n"
                        f"╨Э╨╛╨▓╤Л╨╣ ╨┐╨╛╨╗╤М╨╖╨╛╨▓╨░╤В╨╡╨╗╤М: [{full_name}](tg://user?id={uid})\n"
                        f"╨Э╨░╤З╨╕╤Б╨╗╨╡╨╜╨╛: 1.5 тнР"
                    )
                except:
                    pass

        await message.answer(
            "╨Р╤Б╤Б╨░╨╗╨░╨╝╤Г ╨░╨╗╨╡╨╣╨║╤Г╨╝ ЁЯдН\n\n"
            "╨н╤В╨╛ ╨▒╨╛╤В ┬л╨е╨░╨╗╤П╨▓╨╜╨░╤П ╨Ч╨▓╨╡╨╖╨┤╨░ тнРя╕П┬╗\n\n"
            "ЁЯФ╣ ╨Я╨╛╨╗╤Г╤З╨░╨╣ ╨╖╨▓╤С╨╖╨┤╤Л ╨╖╨░ ╨┐╤А╨╕╨│╨╗╨░╤И╨╡╨╜╨╕╤П\n"
            "ЁЯФ╣ ╨Ю╨▒╨╝╨╡╨╜╨╕╨▓╨░╨╣ ╨╖╨▓╤С╨╖╨┤╤Л ╨╜╨░ ╨┐╨╛╨┤╨░╤А╨║╨╕ ЁЯОБ\n"
            "ЁЯФ╣ ╨Х╨╢╨╡╨┤╨╜╨╡╨▓╨╜╨░╤П ╨Ч╨░╨┤╨░╨╜╨╕╤П!\n\n"
            "тЬЕ ╨Я╨╛╨┤╨┐╨╕╤Б╨║╨░ ╨┐╤А╨╛╨▓╨╡╤А╨╡╨╜╨░! ╨Ф╨╛╨▒╤А╨╛ ╨┐╨╛╨╢╨░╨╗╨╛╨▓╨░╤В╤М!",
            reply_markup=main_menu())
    else:
        await message.answer(
            "тЪая╕П ╨Т╤Л ╨╡╤Й╤С ╨╜╨╡ ╨┐╨╛╨┤╨┐╨╕╤Б╨░╨╗╨╕╤Б╤М ╨╜╨░ ╨▓╤Б╨╡╤Е ╤Б╨┐╨╛╨╜╤Б╨╛╤А╨╛╨▓. \nтЬЕ╨Я╨╛╨┤╨┐╨╕╤И╨╕╤В╨╡╤Б╤М ╨╕ ╨╜╨░╨╢╨╝╨╕╤В╨╡ ┬л╨Я╤А╨╛╨▓╨╡╤А╨╕╤В╤М ╨┐╨╛╨┤╨┐╨╕╤Б╨║╤Г┬╗ ╤Б╨╜╨╛╨▓╨░.",
            reply_markup=sub_inline_kb())


@dp.callback_query(F.data == "check_subscription")
async def process_check_sub(callback: CallbackQuery):
    uid = callback.from_user.id
    full_name = callback.from_user.full_name or "╨Я╨╛╨╗╤М╨╖╨╛╨▓╨░╤В╨╡╨╗╤М"
    
    is_subscribed = await check_all_subs(uid)
    if not is_subscribed:
        await callback.answer("тЭМ ╨Т╤Л ╨╜╨╡ ╨┐╨╛╨┤╨┐╨╕╤Б╨░╨╜╤Л ╨╜╨░ ╨▓╤Б╨╡ ╤Б╨┐╨╛╨╜╤Б╨╛╤А╨╛╨▓!",
                              show_alert=True)
        return

    if not user_exists(uid):
        add_user(uid, full_name, 3)
        # ╨Х╤Б╨╗╨╕ ╨┐╤А╨╕╤И╨╡╨╗ ╨┐╨╛ ╤А╨╡╤Д╨╡╤А╨░╨╗╨║╨╡ ╨╕ ╨┐╨╛╨┤╨┐╨╕╤Б╨░╨╗╤Б╤П ╤З╨╡╤А╨╡╨╖ ╨║╨╜╨╛╨┐╨║╤Г
        inviter_id = get_referral_inviter(uid)
        if inviter_id and not is_referral_awarded(uid):
            update_balance(inviter_id, 1.5)
            mark_referral_awarded(uid)
            try:
                inviter_name = get_user_info(inviter_id)[1] if get_user_info(inviter_id) else "╨Я╨╛╨╗╤М╨╖╨╛╨▓╨░╤В╨╡╨╗╤М"
                await bot.send_message(
                    inviter_id,
                    f"ЁЯОЙ ╨Т╨░╨╝ ╨╜╨░╤З╨╕╤Б╨╗╨╡╨╜╨╛ 1.5 тнР ╨╖╨░ ╨┐╤А╨╕╨│╨╗╨░╤И╨╡╨╜╨╕╨╡ ╨╜╨╛╨▓╨╛╨│╨╛ ╨а╨╡╤Д╨╡╤А╨░╨╗╨░!\n[{full_name}](tg://user?id={uid})",
                    parse_mode="Markdown")
                await log_to_channel(
                    f"ЁЯОЙ **╨Э╨╛╨▓╤Л╨╣ ╤А╨╡╤Д╨╡╤А╨░╨╗ (╨┐╤А╨╛╨▓╨╡╤А╨║╨░ ╨┐╨╛╨┤╨┐╨╕╤Б╨║╨╕)!**\n"
                    f"╨Я╤А╨╕╨│╨╗╨░╤Б╨╕╨╗: [{inviter_name}](tg://user?id={inviter_id})\n"
                    f"╨Э╨╛╨▓╤Л╨╣ ╨┐╨╛╨╗╤М╨╖╨╛╨▓╨░╤В╨╡╨╗╤М: [{full_name}](tg://user?id={uid})\n"
                    f"╨Э╨░╤З╨╕╤Б╨╗╨╡╨╜╨╛: 1.5 тнР"
                )
            except:
                pass
        
        await log_to_channel(f"тЬЕ **╨Э╨╛╨▓╤Л╨╣ ╨┐╨╛╨╗╤М╨╖╨╛╨▓╨░╤В╨╡╨╗╤М ╨┐╨╛╨┤╤В╨▓╨╡╤А╨┤╨╕╨╗ ╨┐╨╛╨┤╨┐╨╕╤Б╨║╤Г:** [{full_name}](tg://user?id={uid})")

    await callback.message.delete()
    await bot.send_message(uid, "тнР ╨Т╤Б╨╡ ╨┐╨╛╨┤╨┐╨╕╤Б╨║╨╕ ╨┐╤А╨╛╨╣╨┤╨╡╨╜╤Л!  \nЁЯОп ╨Ф╨╛╤Б╤В╤Г╨┐ ╨║ ╨▒╨╛╤В╤Г ╨░╨║╤В╨╕╨▓╨╕╤А╨╛╨▓╨░╨╜.  \nтЦ╢я╕П ╨Э╨░╨╢╨╝╨╕╤В╨╡ ╨║╨╜╨╛╨┐╨║╨╕ ╨╜╨╕╨╢╨╡, ╤З╤В╨╛╨▒╤Л ╨╜╨░╤З╨░╤В╤М ╨╕╤Б╨┐╨╛╨╗╤М╨╖╨╛╨▓╨░╤В╤М ╤Д╤Г╨╜╨║╤Ж╨╕╨╕.",
                           reply_markup=main_menu())
    await callback.answer()


# ===== ╨Я╨а╨Ю╨д╨Ш╨Ы╨м =====
@dp.message(F.text == "ЁЯСд ╨Т╨░╤И ╨┐╤А╨╛╤Д╨╕╨╗╤М")
async def profile(message: Message):
    uid = message.from_user.id
    
    is_subscribed = await check_all_subs(uid)
    if not is_subscribed:
        await message.answer(
            "тЪая╕П ╨Т╤Л ╨╡╤Й╤С ╨╜╨╡ ╨┐╨╛╨┤╨┐╨╕╤Б╨░╨╗╨╕╤Б╤М ╨╜╨░ ╨▓╤Б╨╡╤Е ╤Б╨┐╨╛╨╜╤Б╨╛╤А╨╛╨▓. \nтЬЕ╨Я╨╛╨┤╨┐╨╕╤И╨╕╤В╨╡╤Б╤М ╨╕ ╨╜╨░╨╢╨╝╨╕╤В╨╡ ┬л╨Я╤А╨╛╨▓╨╡╤А╨╕╤В╤М ╨┐╨╛╨┤╨┐╨╕╤Б╨║╤Г┬╗ ╤Б╨╜╨╛╨▓╨░.",
            reply_markup=sub_inline_kb())
        return
    
    balance = get_user_balance(uid)
    rank = get_user_rank(uid)
    await message.answer(f"ЁЯСд ╨Т╨░╤И ╨┐╤А╨╛╤Д╨╕╨╗╤М\n\n"
                         f"тнРя╕П ╨Ч╨▓╤С╨╖╨┤: {balance}\n"
                         f"ЁЯПЖ ╨а╨░╨╜╨│: #{rank}",
                         reply_markup=main_menu())
    
    await log_to_channel(f"ЁЯСБя╕П **╨Я╤А╨╛╤Б╨╝╨╛╤В╤А ╨┐╤А╨╛╤Д╨╕╨╗╤П:** [{message.from_user.full_name}](tg://user?id={uid})")


# ===== ╨а╨Х╨Щ╨в╨Ш╨Э╨У =====
@dp.message(F.text == "тнР ╨а╨╡╨╣╤В╨╕╨╜╨│")
async def rating(message: Message):
    uid = message.from_user.id
    
    is_subscribed = await check_all_subs(uid)
    if not is_subscribed:
        await message.answer(
            "тЪая╕П ╨Т╤Л ╨╡╤Й╤С ╨╜╨╡ ╨┐╨╛╨┤╨┐╨╕╤Б╨░╨╗╨╕╤Б╤М ╨╜╨░ ╨▓╤Б╨╡╤Е ╤Б╨┐╨╛╨╜╤Б╨╛╤А╨╛╨▓. \nтЬЕ╨Я╨╛╨┤╨┐╨╕╤И╨╕╤В╨╡╤Б╤М ╨╕ ╨╜╨░╨╢╨╝╨╕╤В╨╡ ┬л╨Я╤А╨╛╨▓╨╡╤А╨╕╤В╤М ╨┐╨╛╨┤╨┐╨╕╤Б╨║╤Г┬╗ ╤Б╨╜╨╛╨▓╨░.",
            reply_markup=sub_inline_kb())
        return
    
    top_users = get_top_users(10)
    
    if not top_users:
        await message.answer("тЭМ ╨а╨╡╨╣╤В╨╕╨╜╨│ ╨┐╤Г╤Б╤В", reply_markup=main_menu())
        return
    
    # ╨б╨╛╨╖╨┤╨░╤С╨╝ ╨║╨╜╨╛╨┐╨║╨╕ ╤Б ╤В╨╛╨┐-10
    keyboard = []
    for i, (user_id, name, balance) in enumerate(top_users, 1):
        button_text = f"{i}. {name} - {balance} тнР"
        keyboard.append([InlineKeyboardButton(text=button_text, callback_data=f"profile_{user_id}")])
    
    rating_kb = InlineKeyboardMarkup(inline_keyboard=keyboard)
    
    await message.answer("ЁЯПЖ *╨в╨Ю╨Я-10 ╨Р╨Ъ╨в╨Ш╨Т╨Э╨л╨е ╨Я╨Ю╨Ы╨м╨Ч╨Ю╨Т╨Р╨в╨Х╨Ы╨Х╨Щ* ЁЯПЖ\n\n╨Э╨░╨╢╨╝╨╕╤В╨╡ ╨╜╨░ ╨╕╨╝╤П ╤З╤В╨╛╨▒╤Л ╨┐╨╡╤А╨╡╨╣╤В╨╕ ╨╜╨░ ╨╡╨│╨╛ ╨┐╤А╨╛╤Д╨╕╨╗╤М:", 
                        parse_mode="Markdown",
                        reply_markup=rating_kb)
    
    await log_to_channel(f"ЁЯУК **╨Я╤А╨╛╤Б╨╝╨╛╤В╤А ╤А╨╡╨╣╤В╨╕╨╜╨│╨░:** [{message.from_user.full_name}](tg://user?id={uid})")


@dp.callback_query(F.data.startswith("profile_"))
async def view_user_profile(callback: CallbackQuery):
    target_user_id = int(callback.data.split("_")[1])
    current_user_id = callback.from_user.id
    
    user_info = get_user_info(target_user_id)
    if not user_info:
        await callback.answer("тЭМ ╨Я╨╛╨╗╤М╨╖╨╛╨▓╨░╤В╨╡╨╗╤М ╨╜╨╡ ╨╜╨░╨╣╨┤╨╡╨╜", show_alert=True)
        return
    
    user_id, user_name, balance = user_info
    rank = get_user_rank(user_id)
    
    text = f"ЁЯСд *╨Я╤А╨╛╤Д╨╕╨╗╤М ╨┐╨╛╨╗╤М╨╖╨╛╨▓╨░╤В╨╡╨╗╤П*\n\n" \
           f"╨Ш╨╝╤П: {user_name}\n" \
           f"тнР ╨Ч╨▓╤С╨╖╨┤: {balance}\n" \
           f"ЁЯПЖ ╨а╨░╨╜╨│: #{rank}"
    
    await callback.message.edit_text(text, parse_mode="Markdown")
    
    # ╨Ы╨╛╨│╨╕╤А╨╛╨▓╨░╨╜╨╕╨╡ ╨┐╤А╨╛╤Б╨╝╨╛╤В╤А╨░ ╨┐╤А╨╛╤Д╨╕╨╗╤П
    await log_to_channel(f"ЁЯСБя╕П **╨Я╤А╨╛╤Б╨╝╨╛╤В╤А ╨┐╤А╨╛╤Д╨╕╨╗╤П ╨┐╨╛╨╗╤М╨╖╨╛╨▓╨░╤В╨╡╨╗╤П:** [{callback.from_user.full_name}](tg://user?id={current_user_id}) ╤Б╨╝╨╛╤В╤А╨╕╤В ╨┐╤А╨╛╤Д╨╕╨╗╤М [{user_name}](tg://user?id={target_user_id})")


# ===== ╨Я╨а╨Ш╨У╨Ы╨Р╨б╨Ш╨в╨м =====
@dp.message(F.text == "ЁЯУв ╨Я╤А╨╕╨│╨╗╨░╤Б╨╕╤В╤М")
async def invite(message: Message):
    uid = message.from_user.id
    
    is_subscribed = await check_all_subs(uid)
    if not is_subscribed:
        await message.answer(
            "тЪая╕П ╨Т╤Л ╨╡╤Й╤С ╨╜╨╡ ╨┐╨╛╨┤╨┐╨╕╤Б╨░╨╗╨╕╤Б╤М ╨╜╨░ ╨▓╤Б╨╡╤Е ╤Б╨┐╨╛╨╜╤Б╨╛╤А╨╛╨▓. \nтЬЕ╨Я╨╛╨┤╨┐╨╕╤И╨╕╤В╨╡╤Б╤М ╨╕ ╨╜╨░╨╢╨╝╨╕╤В╨╡ ┬л╨Я╤А╨╛╨▓╨╡╤А╨╕╤В╤М ╨┐╨╛╨┤╨┐╨╕╤Б╨║╤Г┬╗ ╤Б╨╜╨╛╨▓╨░.",
            reply_markup=sub_inline_kb())
        return
    ref_link = f"https://t.me/{BOT_USERNAME}?start={uid}"
    await message.answer(
        f"╨Т╨░╤И╨░ ╤А╨╡╤Д╨╡╤А╨░╨╗╤М╨╜╨░╤П ╤Б╤Б╤Л╨╗╨║╨░ ЁЯФЧ\n`{ref_link}`\n\n"
        "╨Ч╨░ ╨║╨░╨╢╨┤╨╛╨│╨╛ ╨┐╤А╨╕╨│╨╗╨░╤И╤С╨╜╨╜╨╛╨│╨╛ ╨┤╤А╤Г╨│╨░ ╨▓╤Л ╨┐╨╛╨╗╤Г╤З╨╕╤В╨╡ 1.5 тнР",
        parse_mode="Markdown",
        reply_markup=main_menu())
    
    await log_to_channel(f"ЁЯФЧ **╨Я╤А╨╛╤Б╨╝╨╛╤В╤А ╤А╨╡╤Д. ╤Б╤Б╤Л╨╗╨║╨╕:** [{message.from_user.full_name}](tg://user?id={uid})")


# ===== ╨Ю╨С╨Ь╨Х╨Э ╨Я╨Ю╨Ф╨Р╨а╨Ъ╨Ю╨Т =====
GIFTS_DATA = {
    "15 тнР": {
        "cost": 15,
        "items": ["ЁЯТЭ", "ЁЯз╕"]
    },
    "25 тнР": {
        "cost": 25,
        "items": ["ЁЯМ╣", "ЁЯОБ"]
    },
    "50 тнР": {
        "cost": 50,
        "items": ["ЁЯТР", "ЁЯОВ", "ЁЯЪА"]
    },
    "100 тнР": {
        "cost": 100,
        "items": ["ЁЯПЖ", "ЁЯТН", "ЁЯТО"]
    }
}


@dp.message(F.text == "ЁЯОБ ╨Ю╨▒╨╝╨╡╨╜╤П╤В╤М ╨┐╨╛╨┤╨░╤А╨╛╨║")
async def start_exchange(message: Message, state: FSMContext):
    uid = message.from_user.id
    
    is_subscribed = await check_all_subs(uid)
    if not is_subscribed:
        await message.answer(
            "тЪая╕П ╨Т╤Л ╨╡╤Й╤С ╨╜╨╡ ╨┐╨╛╨┤╨┐╨╕╤Б╨░╨╗╨╕╤Б╤М ╨╜╨░ ╨▓╤Б╨╡╤Е ╤Б╨┐╨╛╨╜╤Б╨╛╤А╨╛╨▓. \nтЬЕ╨Я╨╛╨┤╨┐╨╕╤И╨╕╤В╨╡╤Б╤М ╨╕ ╨╜╨░╨╢╨╝╨╕╤В╨╡ ┬л╨Я╤А╨╛╨▓╨╡╤А╨╕╤В╤М ╨┐╨╛╨┤╨┐╨╕╤Б╨║╤Г┬╗ ╤Б╨╜╨╛╨▓╨░.",
            reply_markup=sub_inline_kb())
        return
    
    kb = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="15 тнР"),
                   KeyboardButton(text="25 тнР")],
                  [KeyboardButton(text="50 тнР"),
                   KeyboardButton(text="100 тнР")],
                  [KeyboardButton(text="ЁЯФЩ ╨Э╨░╨╖╨░╨┤ ╨▓ ╨╝╨╡╨╜╤О")]],
        resize_keyboard=True)
    await message.answer("╨Т╤Л╨▒╨╡╤А╨╕╤В╨╡ ╤Б╤Г╨╝╨╝╤Г ╨╖╨▓╤С╨╖╨┤ ╨┤╨╗╤П ╨╛╨▒╨╝╨╡╨╜╨░:", reply_markup=kb)
    await state.set_state(GiftExchange.choosing_tier)


@dp.message(GiftExchange.choosing_tier)
async def choose_tier(message: Message, state: FSMContext):
    if message.text == "ЁЯФЩ ╨Э╨░╨╖╨░╨┤ ╨▓ ╨╝╨╡╨╜╤О":
        await state.clear()
        await message.answer("╨Т╨╛╨╖╨▓╤А╨░╤Й╨░╤О╤Б╤М...", reply_markup=main_menu())
        return

    if message.text not in GIFTS_DATA:
        await message.answer("тЭМ ╨Т╤Л╨▒╨╡╤А╨╕╤В╨╡ ╨▓╨░╤А╨╕╨░╨╜╤В ╨╕╨╖ ╨║╨╜╨╛╨┐╨╛╨║")
        return

    tier = GIFTS_DATA[message.text]
    uid = message.from_user.id
    balance = get_user_balance(uid)
    if balance < tier["cost"]:
        await message.answer("тЭМ ╨Э╨╡╨┤╨╛╤Б╤В╨░╤В╨╛╤З╨╜╨╛ тнР ╨╜╨░ ╨▒╨░╨╗╨░╨╜╤Б╨╡")
        return

    await state.update_data(cost=tier["cost"], tier_name=message.text)

    buttons = [[KeyboardButton(text=item)] for item in tier["items"]]
    buttons.append([KeyboardButton(text="ЁЯФЩ ╨Э╨░╨╖╨░╨┤ ╨▓ ╨╝╨╡╨╜╤О")])

    kb = ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)
    await message.answer("╨Т╤Л╨▒╨╡╤А╨╕╤В╨╡ ╨┐╨╛╨┤╨░╤А╨╛╨║:", reply_markup=kb)
    await state.set_state(GiftExchange.choosing_gift)


@dp.message(GiftExchange.choosing_gift)
async def finalize_exchange(message: Message, state: FSMContext):
    if message.text == "ЁЯФЩ ╨Э╨░╨╖╨░╨┤ ╨▓ ╨╝╨╡╨╜╤О":
        await state.clear()
        await message.answer("╨Т╨╛╨╖╨▓╤А╨░╤Й╨░╤О╤Б╤М...", reply_markup=main_menu())
        return

    data = await state.get_data()
    cost = data['cost']
    gift_name = message.text
    uid = message.from_user.id

    update_balance(uid, -cost)
    add_gift_request(uid, gift_name, cost)

    await message.answer(
        f"тЬЕ ╨Т╨░╤И╨░ ╨╖╨░╤П╨▓╨║╨░ ╨╛╤В╨┐╤А╨░╨▓╨╗╨╡╨╜╨░ ╨░╨┤╨╝╨╕╨╜╤Г ╨╜╨░ ╨╛╨▒╨╝╨╡╨╜ ╨┐╨╛╨┤╨░╤А╨║╨░ {gift_name}.\n"
        f"тП│ ╨Т ╤В╨╡╤З╨╡╨╜╨╕╨╡ 12╤З ╨▓╨░╨╝ ╨╛╤В╨┐╤А╨░╨▓╨╕╨╝ {gift_name}",
        reply_markup=main_menu())

    # ╨Ъ╨╜╨╛╨┐╨║╨░ ╨┤╨╗╤П ╨░╨┤╨╝╨╕╨╜╨░
    admin_kb = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="╨Ю╤В╨┐╤А╨░╨▓╨╕╨╗ тЬЕ",
                             callback_data=f"gift_{uid}_{gift_name}")
    ]])

    try:
        await bot.send_message(ADMIN_ID, f"ЁЯОБ *╨Э╨╛╨▓╨░╤П ╨╖╨░╤П╨▓╨║╨░ ╨╜╨░ ╨┐╨╛╨┤╨░╤А╨╛╨║!*\n"
                               f"╨Я╨╛╨╗╤М╨╖╨╛╨▓╨░╤В╨╡╨╗╤М: [╤Б╤Б╤Л╨╗╨║╨░](tg://user?id={uid})\n"
                               f"╨Т╤Л╨▒╤А╨░╨╗: {gift_name} (╨╖╨░ {cost} тнР)",
                               parse_mode="Markdown",
                               reply_markup=admin_kb)
    except Exception:
        pass

    await state.clear()


# ===== ╨Ч╨Р╨Ф╨Р╨Э╨Ш╨Х ╨Ф╨Э╨п =====
@dp.message(F.text == "ЁЯОп ╨Х╨╢╨╡╨┤╨╜╨╡╨▓╨╜╨╛╨╡ ╨Ч╨░╨┤╨░╨╜╨╕╨╡")
async def daily_task(message: Message):
    uid = message.from_user.id
    
    is_subscribed = await check_all_subs(uid)
    if not is_subscribed:
        await message.answer(
            "тЪая╕П ╨Т╤Л ╨╡╤Й╤С ╨╜╨╡ ╨┐╨╛╨┤╨┐╨╕╤Б╨░╨╗╨╕╤Б╤М ╨╜╨░ ╨▓╤Б╨╡╤Е ╤Б╨┐╨╛╨╜╤Б╨╛╤А╨╛╨▓. \nтЬЕ╨Я╨╛╨┤╨┐╨╕╤И╨╕╤В╨╡╤Б╤М ╨╕ ╨╜╨░╨╢╨╝╨╕╤В╨╡ ┬л╨Я╤А╨╛╨▓╨╡╤А╨╕╤В╤М ╨┐╨╛╨┤╨┐╨╕╤Б╨║╤Г┬╗ ╤Б╨╜╨╛╨▓╨░.",
            reply_markup=sub_inline_kb())
        return
    
    sponsors = get_active_sponsors()
    
    if not sponsors:
        await message.answer("тЭМ ╨Э╨░ ╨┤╨░╨╜╨╜╤Л╨╣ ╨╝╨╛╨╝╨╡╨╜╤В ╨╖╨░╨┤╨░╨╜╨╕╨╣ ╨╜╨╡╤В", reply_markup=main_menu())
        return
    
    # ╨С╨╡╤А╤С╨╝ ╨┐╨╡╤А╨▓╨╛╨│╨╛ ╨░╨║╤В╨╕╨▓╨╜╨╛╨│╨╛ ╤Б╨┐╨╛╨╜╤Б╨╛╤А╨░
    sponsor_id, sponsor_name = sponsors[0]
    task_id = get_or_create_task(sponsor_id, sponsor_name)
    
    if is_task_completed_today(uid, task_id):
        await message.answer(
            "тЬЕ ╨Т╤Л ╤Г╨╢╨╡ ╨▓╤Л╨┐╨╛╨╗╨╜╨╕╨╗╨╕ ╨╖╨░╨┤╨░╨╜╨╕╨╡ ╨╜╨░ ╤Б╨╡╨│╨╛╨┤╨╜╤П!\n\n"
            "╨Я╤А╨╕╤Е╨╛╨┤╨╕╤В╨╡ ╨╖╨░╨▓╤В╤А╨░ ╨┤╨╗╤П ╨╜╨╛╨▓╨╛╨│╨╛ ╨╖╨░╨┤╨░╨╜╨╕╤П ЁЯМЩ",
            reply_markup=main_menu())
        return
    
    # ╨Я╨╛╨║╨░╨╖╤Л╨▓╨░╨╡╨╝ ╨╖╨░╨┤╨░╨╜╨╕╨╡
    task_kb = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="тЬЕ ╨Т╤Л╨┐╨╛╨╗╨╜╨╕╨╗ ╨╖╨░╨┤╨░╨╜╨╕╨╡", callback_data=f"check_task_{task_id}_{sponsor_id}_{sponsor_name}")
    ]])
    
    await message.answer(
        f"ЁЯОп *╨Ч╨░╨┤╨░╨╜╨╕╨╡ ╨╜╨░ ╤Б╨╡╨│╨╛╨┤╨╜╤П:*\n\n"
        f"╨Я╨╛╨┤╨┐╨╕╤И╨╕╤В╨╡╤Б╤М ╨╜╨░ ╨║╨░╨╜╨░╨╗: *{sponsor_name}*\n\n"
        f"╨Я╨╛╤Б╨╗╨╡ ╨┐╨╛╨┤╨┐╨╕╤Б╨║╨╕ ╨╜╨░╨╢╨╝╨╕╤В╨╡ ╨║╨╜╨╛╨┐╨║╤Г ╨╜╨╕╨╢╨╡ тмЗя╕П",
        parse_mode="Markdown",
        reply_markup=task_kb)


@dp.callback_query(F.data.startswith("check_task_"))
async def check_task_completion(callback: CallbackQuery):
    _, task_id, sponsor_id, sponsor_name = callback.data.split("_", 3)
    task_id = int(task_id)
    sponsor_id = int(sponsor_id)
    uid = callback.from_user.id
    
    # ╨Я╤А╨╛╨▓╨╡╤А╤П╨╡╨╝ ╨┐╨╛╨┤╨┐╨╕╤Б╨║╤Г ╨╜╨░ ╨║╨░╨╜╨░╨╗ ╤Б╨┐╨╛╨╜╤Б╨╛╤А╨░
    try:
        member = await bot.get_chat_member(sponsor_name, uid)
        if member.status not in ["member", "administrator", "creator"]:
            await callback.answer("тЭМ ╨Т╤Л ╨╜╨╡ ╨┐╨╛╨┤╨┐╨╕╤Б╨░╨╜╤Л ╨╜╨░ ╨║╨░╨╜╨░╨╗ ╤Б╨┐╨╛╨╜╤Б╨╛╤А╨░!", show_alert=True)
            return
    except Exception:
        await callback.answer("тЭМ ╨Ю╤И╨╕╨▒╨║╨░ ╨┐╤А╨╛╨▓╨╡╤А╨║╨╕ ╨┐╨╛╨┤╨┐╨╕╤Б╨║╨╕", show_alert=True)
        return
    
    # ╨У╨╡╨╜╨╡╤А╨╕╤А╤Г╨╡╨╝ ╨╜╨░╨│╤А╨░╨┤╤Г
    reward = generate_reward()
    
    # ╨Ю╤В╨╝╨╡╤З╨░╨╡╨╝ ╨╖╨░╨┤╨░╨╜╨╕╨╡ ╨║╨░╨║ ╨▓╤Л╨┐╨╛╨╗╨╜╨╡╨╜╨╜╨╛╨╡
    mark_task_completed(uid, task_id)
    update_balance(uid, reward)
    
    await callback.message.delete()
    await callback.message.answer(
        f"ЁЯОЙ *╨б╨┐╨░╤Б╨╕╨▒╨╛ ╨╖╨░ ╨▓╤Л╨┐╨╛╨╗╨╜╨╡╨╜╨╕╨╡ ╨╖╨░╨┤╨░╨╜╨╕╤П!*\n\n"
        f"тЬЕ ╨Т╤Л ╨┐╨╛╨┤╨┐╨╕╤Б╨░╨╗╨╕╤Б╤М ╨╜╨░ {sponsor_name}\n"
        f"тнР ╨Т╨░╨╝ ╨╜╨░╤З╨╕╤Б╨╗╨╡╨╜╨╛: *{reward}* ╨╖╨▓╤С╨╖╨┤\n\n"
        f"╨Я╤А╨╕╤Е╨╛╨┤╨╕╤В╨╡ ╨╖╨░╨▓╤В╤А╨░ ╨┤╨╗╤П ╨╜╨╛╨▓╨╛╨│╨╛ ╨╖╨░╨┤╨░╨╜╨╕╤П!",
        parse_mode="Markdown",
        reply_markup=main_menu())
    
    await callback.answer("тЬЕ ╨Ч╨░╨┤╨░╨╜╨╕╨╡ ╨▓╤Л╨┐╨╛╨╗╨╜╨╡╨╜╨╛!")


def generate_reward():
    """╨У╨╡╨╜╨╡╤А╨╕╤А╨╛╨▓╨░╤В╤М ╤Б╨╗╤Г╤З╨░╨╣╨╜╤Г╤О ╨╜╨░╨│╤А╨░╨┤╤Г ╨╖╨░ ╨╖╨░╨┤╨░╨╜╨╕╨╡"""
    rand = random.random()
    
    if rand < 0.01:  # 1% - 1 ╨╖╨▓╨╡╨╖╨┤╨░
        return 1.0
    elif rand < 0.15:  # 14% - ╨╛╤В 0.80 ╨┤╨╛ 0.99
        return round(random.uniform(0.80, 0.99), 2)
    else:  # 85% - ╨╛╤В 0.10 ╨┤╨╛ 0.80
        return round(random.uniform(0.10, 0.80), 2)


# ===== ╨Р╨Ф╨Ь╨Ш╨Э ╨Я╨Р╨Э╨Х╨Ы╨м (╨а╨Р╨б╨б╨л╨Ы╨Ъ╨Р) =====
@dp.message(Command("broadcast"))
async def start_broadcast(message: Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return
    await message.answer(
        "╨Т╨▓╨╡╨┤╨╕╤В╨╡ ╤В╨╡╨║╤Б╤В ╤А╨╡╨║╨╗╨░╨╝╤Л/╤Б╨╛╨╛╨▒╤Й╨╡╨╜╨╕╤П ╨┤╨╗╤П ╨▓╤Б╨╡╤Е ╨┐╨╛╨╗╤М╨╖╨╛╨▓╨░╤В╨╡╨╗╨╡╨╣:",
        reply_markup=back_kb())
    await state.set_state(AdminBroadcast.message)


@dp.message(AdminBroadcast.message)
async def process_broadcast(message: Message, state: FSMContext):
    if message.text == "ЁЯФЩ ╨Э╨░╨╖╨░╨┤ ╨▓ ╨╝╨╡╨╜╤О":
        await state.clear()
        await message.answer("╨Ю╤В╨╝╨╡╨╜╨╡╨╜╨╛.", reply_markup=main_menu())
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
        f"тЬЕ ╨а╨░╤Б╤Б╤Л╨╗╨║╨░ ╨╖╨░╨▓╨╡╤А╤И╨╡╨╜╨░! ╨Я╨╛╨╗╤Г╤З╨╕╨╗╨╕: {count} ╨┐╨╛╨╗╤М╨╖╨╛╨▓╨░╤В╨╡╨╗╨╡╨╣.",
        reply_markup=main_menu())
    await state.clear()


# ===== ╨Р╨Ф╨Ь╨Ш╨Э ╨Ъ╨Ю╨Ь╨Р╨Э╨Ф╨л ╨Ф╨Ы╨п ╨б╨Я╨Ю╨Э╨б╨Ю╨а╨Ю╨Т =====

@dp.message(Command("addsponsor"))
async def add_sponsor_cmd(message: Message, state: FSMContext):
    """╨Ф╨╛╨▒╨░╨▓╨╕╤В╤М ╤Б╨┐╨╛╨╜╤Б╨╛╤А╨░ ╤Б ╨▓╤А╨╡╨╝╨╡╨╜╨╜╤Л╨╝ ╤Б╤А╨╛╨║╨╛╨╝: /addsponsor @channel 24h"""
    if message.from_user.id != ADMIN_ID:
        return
    
    args = message.text.split()
    if len(args) != 3:
        await message.answer("тЭМ ╨д╨╛╤А╨╝╨░╤В: /addsponsor @╨║╨░╨╜╨░╨╗ ╨▓╤А╨╡╨╝╤П\n\n╨Я╤А╨╕╨╝╨╡╤А╤Л ╨▓╤А╨╡╨╝╨╡╨╜╨╕: 1h, 24h, 7d, 30d")
        return
    
    channel_name = args[1]
    duration = args[2]
    
    sponsor_id = add_sponsor(channel_name, message.from_user.id)
    if sponsor_id is None:
        await message.answer(f"тЭМ ╨б╨┐╨╛╨╜╤Б╨╛╤А {channel_name} ╤Г╨╢╨╡ ╨┤╨╛╨▒╨░╨▓╨╗╨╡╨╜")
        return
    
    await message.answer(
        f"тЬЕ ╨б╨┐╨╛╨╜╤Б╨╛╤А ╨┤╨╛╨▒╨░╨▓╨╗╨╡╨╜!\n\n"
        f"╨Ъ╨░╨╜╨░╨╗: {channel_name}\n"
        f"╨б╤А╨╛╨║: {duration}\n\n"
        f"╨Я╨╛╨╗╤М╨╖╨╛╨▓╨░╤В╨╡╨╗╨╕ ╤Б╨╝╨╛╨│╤Г╤В ╨▓╤Л╨┐╨╛╨╗╨╜╤П╤В╤М ╨╖╨░╨┤╨░╨╜╨╕╨╡ ╨╜╨░ ╤Н╤В╨╛╤В ╨║╨░╨╜╨░╨╗ ╨▓ ╤В╨╡╤З╨╡╨╜╨╕╨╡ {duration}.")


@dp.message(Command("addsponsorfree"))
async def add_sponsor_free_cmd(message: Message, state: FSMContext):
    """╨Ф╨╛╨▒╨░╨▓╨╕╤В╤М ╨┐╨╛╤Б╤В╨╛╤П╨╜╨╜╨╛╨│╨╛ ╤Б╨┐╨╛╨╜╤Б╨╛╤А╨░: /addsponsorfree @channel"""
    if message.from_user.id != ADMIN_ID:
        return
    
    args = message.text.split()
    if len(args) != 2:
        await message.answer("тЭМ ╨д╨╛╤А╨╝╨░╤В: /addsponsorfree @╨║╨░╨╜╨░╨╗")
        return
    
    channel_name = args[1]
    
    sponsor_id = add_sponsor(channel_name, message.from_user.id)
    if sponsor_id is None:
        await message.answer(f"тЭМ ╨б╨┐╨╛╨╜╤Б╨╛╤А {channel_name} ╤Г╨╢╨╡ ╨┤╨╛╨▒╨░╨▓╨╗╨╡╨╜")
        return
    
    await message.answer(
        f"тЬЕ ╨Я╨╛╤Б╤В╨╛╤П╨╜╨╜╤Л╨╣ ╤Б╨┐╨╛╨╜╤Б╨╛╤А ╨┤╨╛╨▒╨░╨▓╨╗╨╡╨╜!\n\n"
        f"╨Ъ╨░╨╜╨░╨╗: {channel_name}\n\n"
        f"╨Я╨╛╨╗╤М╨╖╨╛╨▓╨░╤В╨╡╨╗╨╕ ╨▒╤Г╨┤╤Г╤В ╨▓╤Л╨┐╨╛╨╗╨╜╤П╤В╤М ╨╖╨░╨┤╨░╨╜╨╕╤П ╨╜╨░ ╤Н╤В╨╛╤В ╨║╨░╨╜╨░╨╗")


@dp.message(Command("removesponsor"))
async def remove_sponsor_cmd(message: Message, state: FSMContext):
    """╨г╨┤╨░╨╗╨╕╤В╤М ╤Б╨┐╨╛╨╜╤Б╨╛╤А╨░: /removesponsor @channel"""
    if message.from_user.id != ADMIN_ID:
        return
    
    args = message.text.split()
    if len(args) != 2:
        await message.answer("тЭМ ╨д╨╛╤А╨╝╨░╤В: /removesponsor @╨║╨░╨╜╨░╨╗")
        return
    
    channel_name = args[1]
    remove_sponsor(channel_name)
    
    await message.answer(f"тЬЕ ╨б╨┐╨╛╨╜╤Б╨╛╤А {channel_name} ╤Г╨┤╨░╨╗╨╡╨╜")


@dp.message(Command("sponsors"))
async def list_sponsors_cmd(message: Message):
    """╨Я╨╛╨║╨░╨╖╨░╤В╤М ╤Б╨┐╨╕╤Б╨╛╨║ ╨░╨║╤В╨╕╨▓╨╜╤Л╤Е ╤Б╨┐╨╛╨╜╤Б╨╛╤А╨╛╨▓"""
    if message.from_user.id != ADMIN_ID:
        return
    
    sponsors = get_active_sponsors()
    if not sponsors:
        await message.answer("тЭМ ╨Р╨║╤В╨╕╨▓╨╜╤Л╤Е ╤Б╨┐╨╛╨╜╤Б╨╛╤А╨╛╨▓ ╨╜╨╡╤В")
        return
    
    text = "ЁЯУЛ *╨Р╨║╤В╨╕╨▓╨╜╤Л╨╡ ╤Б╨┐╨╛╨╜╤Б╨╛╤А╤Л:*\n\n"
    for i, (sponsor_id, channel_name) in enumerate(sponsors, 1):
        text += f"{i}. {channel_name}\n"
    
    await message.answer(text, parse_mode="Markdown")


# ===== ╨Я╨Ю╨Ь╨Ю╨й╨м =====
@dp.message(F.text == "ЁЯЖШ ╨Я╨╛╨╝╨╛╤Й╤М")
async def help_cmd(message: Message, state: FSMContext):
    await message.answer("╨Э╨░╨┐╨╕╤И╨╕╤В╨╡ ╨▓╨░╤И╤Г ╨┐╤А╨╛╨▒╨╗╨╡╨╝╤Г, ╨╝╤Л ╤Б╨║╨╛╤А╨╛ ╨╡╤С ╤А╨╡╤И╨╕╨╝:",
                         reply_markup=back_kb())
    await state.set_state(HelpFlow.message)


@dp.message(HelpFlow.message)
async def process_help(message: Message, state: FSMContext):
    if message.text == "ЁЯФЩ ╨Э╨░╨╖╨░╨┤ ╨▓ ╨╝╨╡╨╜╤О":
        await state.clear()
        await message.answer("╨Т╨╛╨╖╨▓╤А╨░╤Й╨░╤О╤Б╤М...", reply_markup=main_menu())
        return

    uid = message.from_user.id

    # ╨г╨▓╨╡╨┤╨╛╨╝╨╗╨╡╨╜╨╕╨╡ ╨░╨┤╨╝╨╕╨╜╤Г
    admin_kb = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="╨Ю╤В╨▓╨╡╤В╨╕╤В╤М ЁЯТм", callback_data=f"reply_{uid}")
    ]])

    try:
        await bot.send_message(ADMIN_ID, f"ЁЯЖШ *╨Э╨╛╨▓╨╛╨╡ ╨╛╨▒╤А╨░╤Й╨╡╨╜╨╕╨╡ ╨▓ ╨┐╨╛╨┤╨┤╨╡╤А╨╢╨║╤Г!*\n"
                               f"╨Ю╤В: [╤Б╤Б╤Л╨╗╨║╨░](tg://user?id={uid})\n"
                               f"╨б╨╛╨╛╨▒╤Й╨╡╨╜╨╕╨╡: {message.text}",
                               parse_mode="Markdown",
                               reply_markup=admin_kb)
    except Exception:
        pass

    await message.answer(
        "тЬЕ ╨Т╨░╤И╨╡ ╤Б╨╛╨╛╨▒╤Й╨╡╨╜╨╕╨╡ ╨╛╤В╨┐╤А╨░╨▓╨╗╨╡╨╜╨╛ ╨░╨┤╨╝╨╕╨╜╨╕╤Б╤В╤А╨░╤В╨╛╤А╤Г. ╨Ю╨╢╨╕╨┤╨░╨╣╤В╨╡ ╨╛╤В╨▓╨╡╤В╨░.",
        reply_markup=main_menu())
    await state.clear()


# ===== ╨Т╨Т╨Х╨б╨в╨Ш ╨Ч╨Т╨Б╨Ч╨Ф╨л =====
@dp.message(F.text == "тнР ╨Т╨▓╨╡╤Б╤В╨╕")
async def enter_stars(message: Message, state: FSMContext):
    uid = message.from_user.id
    
    is_subscribed = await check_all_subs(uid)
    if not is_subscribed:
        await message.answer(
            "тЪая╕П ╨Т╤Л ╨╡╤Й╤С ╨╜╨╡ ╨┐╨╛╨┤╨┐╨╕╤Б╨░╨╗╨╕╤Б╤М ╨╜╨░ ╨▓╤Б╨╡╤Е ╤Б╨┐╨╛╨╜╤Б╨╛╤А╨╛╨▓. \nтЬЕ╨Я╨╛╨┤╨┐╨╕╤И╨╕╤В╨╡╤Б╤М ╨╕ ╨╜╨░╨╢╨╝╨╕╤В╨╡ ┬л╨Я╤А╨╛╨▓╨╡╤А╨╕╤В╤М ╨┐╨╛╨┤╨┐╨╕╤Б╨║╤Г┬╗ ╤Б╨╜╨╛╨▓╨░.",
            reply_markup=sub_inline_kb())
        return
    
    balance = get_user_balance(uid)

    if balance < 50:
        await message.answer(
            f"тЭМ ╨Э╨░ ╨▓╨░╤И╨╡╨╝ ╨▒╨░╨╗╨░╨╜╤Б╨╡ ╨╜╨╡╨┤╨╛╤Б╤В╨░╤В╨╛╤З╨╜╨╛ ╨╖╨▓╤С╨╖╨┤ ╨┤╨╗╤П ╨▓╨▓╨╛╨┤╨░ тАФ ╨╝╨╕╨╜╨╕╨╝╨░╨╗╤М╨╜╤Л╨╣ ╨▓╨▓╨╛╨┤ ╨╛╤В 50тнР\n\n"
            f"╨Т╨░╤И ╨▒╨░╨╗╨░╨╜╤Б: {balance} тнР",
            reply_markup=main_menu())
        return

    await message.answer(
        f"╨Т╨░╤И ╨▒╨░╨╗╨░╨╜╤Б: {balance} тнРя╕П\n"
        "╨Т╨▓╨╡╨┤╨╕╤В╨╡ ╨║╨╛╨╗╨╕╤З╨╡╤Б╤В╨▓╨╛ ╨╖╨▓╨╡╨╖╨┤ ╨┤╨╗╤П ╤Б╨┐╨╕╤Б╨░╨╜╨╕╤П:",
        reply_markup=back_kb())
    await state.set_state(EnterStarsFlow.amount)


@dp.message(EnterStarsFlow.amount)
async def process_enter_amount(message: Message, state: FSMContext):
    if message.text == "ЁЯФЩ ╨Э╨░╨╖╨░╨┤ ╨▓ ╨╝╨╡╨╜╤О":
        await state.clear()
        await message.answer("╨Т╨╛╨╖╨▓╤А╨░╤Й╨░╤О╤Б╤М...", reply_markup=main_menu())
        return

    uid = message.from_user.id
    try:
        amount = float(message.text)
    except ValueError:
        await message.answer("тЭМ ╨Я╨╛╨╢╨░╨╗╤Г╨╣╤Б╤В╨░, ╨▓╨▓╨╡╨┤╨╕╤В╨╡ ╤З╨╕╤Б╨╗╨╛!")
        return

    if amount < 50:
        await message.answer(
            "тЭМ ╨Ь╨╕╨╜╨╕╨╝╨░╨╗╤М╨╜╤Л╨╣ ╨▓╨▓╨╛╨┤ ╨╛╤В 50тнР. ╨Я╨╛╨┐╤А╨╛╨▒╤Г╨╣╤В╨╡ ╨╡╤Й╨╡ ╤А╨░╨╖ ╨╕╨╗╨╕ ╨╜╨░╨╢╨╝╨╕╤В╨╡ ╨Э╨░╨╖╨░╨┤.")
        return

    balance = get_user_balance(uid)
    if amount > balance:
        await message.answer(
            f"тЭМ ╨Э╨░ ╨▓╨░╤И╨╡╨╝ ╨▒╨░╨╗╨░╨╜╤Б╨╡ ╨╜╨╡╨┤╨╛╤Б╤В╨░╤В╨╛╤З╨╜╨╛ ╨╖╨▓╤С╨╖╨┤. ╨Т╨░╤И ╨▒╨░╨╗╨░╨╜╤Б: {balance} тнР")
        return

    update_balance(uid, -amount)
    add_star_input_request(uid, amount)

    await message.answer(
        f"тЬЕ ╨Т╨░╤И╨░ ╨╖╨░╤П╨▓╨║╨░ ╨╛╤В╨┐╤А╨░╨▓╨╗╨╡╨╜╨░ ╨░╨┤╨╝╨╕╨╜╤Г ╨╜╨░ ╨▓╨▓╨╛╨┤ {amount} тнР.\n"
        f"тП│ ╨Т ╤В╨╡╤З╨╡╨╜╨╕╨╡ 24╤З ╨▓╨░╨╝ ╨╜╨░╤З╨╕╤Б╨╗╤П╤В {amount} тнР.",
        reply_markup=main_menu())

    admin_kb = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="╨Ю╨┐╨╗╨░╤В╨╕╨╗ тЬЕ",
                             callback_data=f"pay_{uid}_{amount}")
    ]])

    try:
        await bot.send_message(ADMIN_ID, f"ЁЯУе *╨Э╨╛╨▓╨░╤П ╨╖╨░╤П╨▓╨║╨░ ╨╜╨░ ╨▓╨▓╨╛╨┤!*\n"
                               f"╨Я╨╛╨╗╤М╨╖╨╛╨▓╨░╤В╨╡╨╗╤М: [╤Б╤Б╤Л╨╗╨║╨░](tg://user?id={uid})\n"
                               f"╨б╤Г╨╝╨╝╨░: {amount} тнР",
                               parse_mode="Markdown",
                               reply_markup=admin_kb)
    except Exception:
        pass

    await state.clear()


# ╨Ю╨▒╤А╨░╨▒╨╛╤В╨║╨░ ╨╜╨░╨╢╨░╤В╨╕╨╣ ╨░╨┤╨╝╨╕╨╜╨╛╨╝
@dp.callback_query(F.data.startswith("pay_"))
async def admin_pay_confirm(callback: CallbackQuery):
    _, uid, amount = callback.data.split("_")
    uid = int(uid)
    amount = float(amount)
    current_balance = get_user_balance(uid)
    try:
        await bot.send_message(
            uid, f"тЬЕ ╨Т╤Л ╤Г╤Б╨┐╨╡╤И╨╜╨╛ ╨▓╨▓╨╡╨╗╨╕ {amount} тнРя╕П\n"
            f"╨Ю╤Б╤В╨░╤В╨╛╨║: {current_balance} тнРя╕П")
        await callback.answer("╨Я╨╛╨╗╤М╨╖╨╛╨▓╨░╤В╨╡╨╗╤М ╤Г╨▓╨╡╨┤╨╛╨╝╨╗╨╡╨╜! тЬЕ")
        await callback.message.edit_text(callback.message.text +
                                         "\n\nтЬЕ ╨Ю╨Я╨Ы╨Р╨з╨Х╨Э╨Ю",
                                         reply_markup=None)
    except Exception as e:
        await callback.answer(f"╨Ю╤И╨╕╨▒╨║╨░ ╤Г╨▓╨╡╨┤╨╛╨╝╨╗╨╡╨╜╨╕╤П: {e}", show_alert=True)


@dp.callback_query(F.data.startswith("gift_"))
async def admin_gift_sent_confirm(callback: CallbackQuery):
    _, uid, gift_name = callback.data.split("_")
    uid = int(uid)
    current_balance = get_user_balance(uid)
    try:
        await bot.send_message(
            uid, f"тЬЕ ╨Т╤Л ╤Г╤Б╨┐╨╡╤И╨╜╨╛ ╨╛╨▒╨╝╨╡╨╜╤П╨╗╨╕ тнР ╨╜╨░ {gift_name}\n"
            f"╨Ю╤Б╤В╨░╤В╨╛╨║: {current_balance} тнРя╕П")
        await callback.answer("╨Я╨╛╨╗╤М╨╖╨╛╨▓╨░╤В╨╡╨╗╤М ╤Г╨▓╨╡╨┤╨╛╨╝╨╗╨╡╨╜! тЬЕ")
        await callback.message.edit_text(callback.message.text +
                                         "\n\nтЬЕ ╨Ю╨в╨Я╨а╨Р╨Т╨Ы╨Х╨Э╨Ю",
                                         reply_markup=None)
    except Exception as e:
        await callback.answer(f"╨Ю╤И╨╕╨▒╨║╨░ ╤Г╨▓╨╡╨┤╨╛╨╝╨╗╨╡╨╜╨╕╤П: {e}", show_alert=True)


# ╨Ю╨▒╤А╨░╨▒╨╛╤В╨║╨░ ╨╛╤В╨▓╨╡╤В╨░ ╨░╨┤╨╝╨╕╨╜╨░ ╨╜╨░ ╨┐╨╛╨╝╨╛╤Й╤М
@dp.callback_query(F.data.startswith("reply_"))
async def admin_start_reply(callback: CallbackQuery, state: FSMContext):
    uid = int(callback.data.split("_")[1])
    await state.update_data(reply_to_uid=uid)
    await callback.message.answer(
        f"╨Т╨▓╨╡╨┤╨╕╤В╨╡ ╨╛╤В╨▓╨╡╤В ╨┤╨╗╤П ╨┐╨╛╨╗╤М╨╖╨╛╨▓╨░╤В╨╡╨╗╤П [ID: {uid}]:", reply_markup=back_kb())
    await state.set_state(AdminSupportReply.message)
    await callback.answer()


@dp.message(AdminSupportReply.message)
async def process_admin_support_reply(message: Message, state: FSMContext):
    if message.text == "ЁЯФЩ ╨Э╨░╨╖╨░╨┤ ╨▓ ╨╝╨╡╨╜╤О":
        await state.clear()
        await message.answer("╨Ю╤В╨╝╨╡╨╜╨╡╨╜╨╛.", reply_markup=main_menu())
        return

    data = await state.get_data()
    user_id = data['reply_to_uid']

    try:
        await bot.send_message(
            user_id,
            f"тЬЙя╕П *╨Ю╤В╨▓╨╡╤В ╨╛╤В ╨░╨┤╨╝╨╕╨╜╨╕╤Б╤В╤А╨░╤Ж╨╕╨╕:*\n\n{message.text}",
            parse_mode="Markdown")
        await message.answer("тЬЕ ╨Ю╤В╨▓╨╡╤В ╤Г╤Б╨┐╨╡╤И╨╜╨╛ ╨╛╤В╨┐╤А╨░╨▓╨╗╨╡╨╜ ╨┐╨╛╨╗╤М╨╖╨╛╨▓╨░╤В╨╡╨╗╤О!",
                             reply_markup=main_menu())
    except Exception as e:
        await message.answer(f"тЭМ ╨Ю╤И╨╕╨▒╨║╨░ ╨┐╤А╨╕ ╨╛╤В╨┐╤А╨░╨▓╨║╨╡ ╨╛╤В╨▓╨╡╤В╨░: {e}",
                             reply_markup=main_menu())

    await state.clear()


# ===== ╨Ю╨С╨а╨Р╨С╨Ю╨в╨Ъ╨Р ╨б╨Ы╨г╨з╨Р╨Щ╨Э╨Ю╨У╨Ю ╨в╨Х╨Ъ╨б╨в╨Р =====
@dp.message()
async def handle_invalid_input(message: Message):
    """╨Ю╨▒╤А╨░╨▒╨╛╤В╨║╨░ ╨▓╤Б╨╡╤Е ╨╛╤Б╤В╨░╨╗╤М╨╜╤Л╤Е ╤Б╨╛╨╛╨▒╤Й╨╡╨╜╨╕╨╣"""
    await message.answer(
        "тЪая╕П ╨Э╨╡╨▓╨╡╤А╨╜╤Л╨╣ ╨▓╨▓╨╛╨┤\n\n"
        "╨С╨╛╤В ╨╜╨╡ ╨╛╨▒╤А╨░╨▒╨░╤В╤Л╨▓╨░╨╡╤В ╨┐╤А╨╛╨╕╨╖╨▓╨╛╨╗╤М╨╜╤Л╨╣ ╤В╨╡╨║╤Б╤В.\n"
        "╨Ш╤Б╨┐╨╛╨╗╤М╨╖╤Г╨╣╤В╨╡ ╨║╨╜╨╛╨┐╨║╨╕ ╨╜╨╕╨╢╨╡ тмЗя╕П",
        reply_markup=main_menu())
    
    await log_to_channel(f"тЭМ **╨Э╨╡╨▓╨╡╤А╨╜╤Л╨╣ ╨▓╨▓╨╛╨┤:** [{message.from_user.full_name}](tg://user?id={message.from_user.id}) ╨╜╨░╨┐╨╕╤Б╨░╨╗: `{message.text}`")


# ===== ╨Ч╨Р╨Я╨г╨б╨Ъ =====
async def main():
    print("ЁЯЪА BOT STARTED")
    keep_alive()  # ╨Ч╨░╨┐╤Г╤Б╨║╨░╨╡╨╝ ╨▓╨╡╨▒-╤Б╨╡╤А╨▓╨╡╤А ╨┤╨╗╤П "╨╢╨╕╨▓╤Г╤З╨╡╤Б╤В╨╕"
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
