# -*- coding: utf-8 -*-

import os
import re
import requests
import uuid

from aiohttp import web
from aiogram import Bot, Dispatcher, types
from aiogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ReplyKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardRemove,
    MenuButtonWebApp,
    WebAppInfo,
)

# ================== НАЛАШТУВАННЯ ==================

API_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
MONO_TOKEN = os.getenv("MONO_TOKEN")
MONO_BACKEND_URL = os.getenv("MONO_BACKEND_URL")
PAY_SERVER_URL = os.getenv("PAY_SERVER_URL", "https://monal-mono-pay-production.up.railway.app")

if not API_TOKEN:
    raise RuntimeError("BOT_TOKEN missing")

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# ⬇️ КРИТИЧНО ВАЖЛИВО ДЛЯ WEBHOOK
Bot.set_current(bot)
Dispatcher.set_current(dp)

# ================== TELEGRAM WEBHOOK ==================

async def telegram_webhook(request: web.Request):
    data = await request.json()
    update = types.Update(**data)
    await dp.process_update(update)
    return web.Response(text="ok")

# ================== STARTUP ==================

async def on_startup(app):
    # 1️⃣ Telegram webhook
    base_url = os.getenv("RAILWAY_PUBLIC_URL")
    await bot.set_webhook(f"{base_url}/webhook/telegram")
    print("✅ Telegram webhook set")

    # 2️⃣ Кнопка "Сайт" внизу чату
    await bot.set_chat_menu_button(
        menu_button=MenuButtonWebApp(
            text="🌐 Сайт",
            web_app=WebAppInfo(url="https://monal.com.ua/")
        )
    )
    print("✅ Menu button set")

# ================== ДАНІ ==================

CATEGORIES = {
    "diffusers": "🧴 Аромадифузери",
    "home": "🏠 Парфумерія для дому",
    "discovery": "🎁 Discovery set",
    "refill": "♻️ Рефіли для аромадифузерів",
    "certificates": "🎟 Подарункові сертифікати",
    "gifts": "🎀 Подарункові набори",
}

PRODUCTS = {
    "diffusers": [
        {"id": "d1", "name": "FAIRYTALE 200мл", "price": 1590},
        {"id": "d2", "name": "VESPER 200мл", "price": 1590},
        {"id": "d3", "name": "NOCTURNE 200мл", "price": 1590},
        {"id": "d4", "name": "ROSALYA 200мл", "price": 1590},
        {"id": "d5", "name": "DRIFT 200мл", "price": 1590},
        {"id": "d6", "name": "STONE & SALT 200мл", "price": 1590},
        {"id": "d7", "name": "FREEDOM 200мл", "price": 1590},
        {"id": "d8", "name": "CROWN OF OLIVE 200мл", "price": 1590},
        {"id": "d9", "name": "SHADOW OF FIG 200мл", "price": 1590},
        {"id": "d10", "name": "GOLDEN RUM 200мл", "price": 1590},
        {"id": "d11", "name": "GREEN HAVEN 200мл", "price": 1590},
    ],
    "home": [
        {"id": "h1", "name": "FAIRYTALE 100мл", "price": 990},
        {"id": "h2", "name": "VESPER 100мл", "price": 990},
        {"id": "h3", "name": "NOCTURNE 100мл", "price": 990},
        {"id": "h4", "name": "ROSALYA 100мл", "price": 990},
        {"id": "h5", "name": "DRIFT 100мл", "price": 990},
        {"id": "h6", "name": "STONE & SALT 100мл", "price": 990},
        {"id": "h7", "name": "FREEDOM 100мл", "price": 990},
        {"id": "h8", "name": "CROWN OF OLIVE 100мл", "price": 990},
        {"id": "h9", "name": "SHADOW OF FIG 100мл", "price": 990},
        {"id": "h10", "name": "GOLDEN RUM 100мл", "price": 990},
        {"id": "h11", "name": "GREEN HAVEN 100мл", "price": 990},
        {"id": "h12", "name": "LEATHER ABSOLUTE 15мл", "price": 385},
        {"id": "h13", "name": "AMBER ELITE 15мл", "price": 385},
        {"id": "h14", "name": "BOIS NOIR 15мл", "price": 385},
        {"id": "h15", "name": "VESPER 15мл", "price": 385},
        {"id": "h16", "name": "NOCTURNE 15мл", "price": 385},
        {"id": "h17", "name": "ROSALYA 15мл", "price": 385},
        {"id": "h18", "name": "DRIFT 15мл", "price": 385},
        {"id": "h19", "name": "STONE & SALT 15мл", "price": 385},
        {"id": "h20", "name": "FREEDOM 15мл", "price": 385},
        {"id": "h21", "name": "CROWN OF OLIVE 15мл", "price": 385},
        {"id": "h22", "name": "SHADOW OF FIG 15мл", "price": 385},
        {"id": "h23", "name": "GOLDEN RUM 15мл", "price": 385},
        {"id": "h24", "name": "GREEN HAVEN 15мл", "price": 385},        
    ],
    "refill": [
        {"id": "r1", "name": "VESPER 275мл", "price": 1300},
        {"id": "r2", "name": "NOCTURNE 275мл", "price": 1300},
        {"id": "r3", "name": "ROSALYA 275мл", "price": 1300},
        {"id": "r4", "name": "DRIFT 275мл", "price": 1300},
        {"id": "r5", "name": "STONE & SALT 275мл", "price": 1300},
        {"id": "r6", "name": "FREEDOM 275мл", "price": 1300},
        {"id": "r7", "name": "CROWN OF OLIVE 275мл", "price": 1300},
        {"id": "r8", "name": "SHADOW OF FIG 275мл", "price": 1300},
        {"id": "r9", "name": "GOLDEN RUM 275мл", "price": 1300},
        {"id": "r10", "name": "GREEN HAVEN 275мл", "price": 1300},
    ],
    "certificates": [
        {"id": "c1000", "name": "Сертифікат 1000 грн", "price": 1000, "label": "Сертифікат"},
        {"id": "c2500", "name": "Сертифікат 2500 грн", "price": 2500, "label": "Сертифікат"},
        {"id": "c3500", "name": "Сертифікат 3500 грн", "price": 3500, "label": "Сертифікат"},
        {"id": "c5000", "name": "Сертифікат 5000 грн", "price": 5000, "label": "Сертифікат"},
    ],
    "gifts": [        
        {"id": "g1", "name": "TEN MINI 10х3мл", "price": 750},
    ],
}

user_sessions = {}
pending_payments = {}

def cart_count(cart: dict) -> int:
    count = 0
    for item in cart.values():
        if item.get("type") == "discovery":
            count += 1
        else:
            count += item.get("qty", 1)
    return count

# ================== DISCOVERY SET ==================

DISCOVERY_PRICE = 395
DISCOVERY_SAMPLE_ML = 3

DISCOVERY_AROMAS = [
    "VESPER",
    "NOCTURNE",
    "ROSALYA",
    "DRIFT",
    "STONE & SALT",
    "FREEDOM",
    "CROWN OF OLIVE",
    "SHADOW OF FIG",
    "GOLDEN RUM",
    "GREEN HAVEN",
]

# ================== ХЕНДЛЕРИ ==================

def start_keyboard():
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("Почати", callback_data="start_menu"))
    return kb


def categories_keyboard(uid=None):
    kb = InlineKeyboardMarkup(row_width=1)

    for key, title in CATEGORIES.items():
        kb.add(InlineKeyboardButton(title, callback_data=f"cat:{key}"))

    cart_items = 0
    if uid and uid in user_sessions:
        cart_items = cart_count(user_sessions[uid].get("cart", {}))

    cart_text = f"🛒 Кошик ({cart_items})" if cart_items else "🛒 Кошик"
    kb.add(InlineKeyboardButton(cart_text, callback_data="view_cart"))

    return kb


def persistent_keyboard():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton("🛒 Почати замовлення"))
    return kb


def products_keyboard(cat_key):
    kb = InlineKeyboardMarkup(row_width=1)

    for p in PRODUCTS.get(cat_key, []):
        kb.add(
            InlineKeyboardButton(
                f"{p['name']} — {p['price']} грн",
                callback_data=f"add:{p['id']}"
            )
        )


def products_keyboard(cat_key, user_id):
    kb = InlineKeyboardMarkup(row_width=1)

    for p in PRODUCTS.get(cat_key, []):
        kb.add(
            InlineKeyboardButton(
                f"{p['name']} — {p['price']} грн",
                callback_data=f"add:{p['id']}"
            )
        )

    cart = user_sessions.get(user_id, {}).get("cart", {})
    total_items = 0

    for item in cart.values():
        if "qty" in item:
            total_items += item["qty"]
        else:
            total_items += 1

    cart_text = f"🛒 Кошик ({total_items})" if total_items else "🛒 Кошик"

    # ✅ ТІЛЬКИ ДЛЯ СЕРТИФІКАТІВ: кнопка друку НАД "Назад"
    if cat_key == "certificates":
        session = user_sessions.setdefault(user_id, {})
        certificates = session.setdefault("certificates", {})
        is_physical = certificates.get("physical", False)

        kb.add(
            InlineKeyboardButton(
                "☑️ Друкований сертифікат" if is_physical else "☐ Хочу друкований сертифікат",
                callback_data="toggle_physical_certificate"
            )
        )

    kb.add(
        InlineKeyboardButton("⬅️ Назад", callback_data="back_categories"),
        InlineKeyboardButton(cart_text, callback_data="view_cart"),
    )

    return kb


def discovery_start_keyboard():
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("✨ Сформувати сет", callback_data="discovery_start"))
    kb.add(InlineKeyboardButton("⬅️ Назад до категорій", callback_data="back_categories"))
    return kb


def discovery_aromas_keyboard(selected: list):
    kb = InlineKeyboardMarkup(row_width=1)

    for aroma in DISCOVERY_AROMAS:
        # відмітка вибраних
        mark = "✓ " if aroma in selected else ""
        kb.add(
            InlineKeyboardButton(
                f"{mark}{aroma}",
                callback_data=f"disc_toggle::{aroma}"
            )
        )

    kb.add(
        InlineKeyboardButton(
            f"Обрано: {len(selected)} / 4",
            callback_data="disc_counter"
        )
    )

    if len(selected) == 4:
        kb.add(
            InlineKeyboardButton(
                "✅ Додати discovery у кошик",
                callback_data="disc_confirm"
            )
        )

    # ⬇️ ОЦЕ ДОДАНО: кнопка КОШИК
    kb.add(InlineKeyboardButton("🛒 Кошик", callback_data="view_cart"))
    kb.add(InlineKeyboardButton("⬅️ Назад", callback_data="back_categories"))

    return kb


def share_phone_keyboard():
    kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    kb.add(
        KeyboardButton(
            text="📱 Поділитись номером телефону",
            request_contact=True
        )
    )
    return kb


def admin_keyboard():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(
        KeyboardButton("📦 Активні замовлення"),
        KeyboardButton("✅ Виконані замовлення")
    )
    return kb

async def finalize_order(uid: int, text: str):
    session = user_sessions.get(uid)
    if session:
        session["cart"] = {}
        session.pop("checkout", None)

    # прибрати всі "очікування оплати" цього користувача
    refs_to_remove = [
        ref for ref, data in pending_payments.items()
        if data.get("user_id") == uid
    ]
    for ref in refs_to_remove:
        pending_payments.pop(ref, None)

    await bot.send_message(
        uid,
        text,
        reply_markup=persistent_keyboard()
    )

    await bot.send_message(
        uid,
        "Оберіть категорію:",
        reply_markup=categories_keyboard(uid)
    )
    
# ================== CERTIFICATE HELPERS ==================

def cart_has_certificate(cart: dict) -> bool:
    """
    Повертає True, якщо в кошику є подарунковий сертифікат
    """
    for item in cart.values():
        # сертифікати визначаємо по назві або label
        if "сертифікат" in item.get("name", "").lower():
            return True
        if item.get("label") == "Сертифікат":
            return True
    return False

def can_apply_certificate(cart: dict) -> bool:
    """
    Сертифікат можна вводити,
    якщо в кошику НЕ купують сертифікат
    """
    for item in cart.values():
        if "сертифікат" in item.get("name", "").lower():
            return False
    return True    

def check_certificate_remote(code: str):
    """
    Викликає Railway /check-certificate
    Повертає (valid: bool, nominal: int|None)
    """
    try:
        r = requests.post(
            f"{PAY_SERVER_URL}/check-certificate",
            json={"code": code},
            timeout=8,
        )
        data = r.json() if r.ok else {}
        if data.get("valid") is True:
            return True, int(data.get("nominal") or 0)
        return False, None
    except Exception as e:
        print("❌ check_certificate_remote error:", e)
        return False, None

def calculate_amounts_with_certificate(total: int, certificate_nominal: int):
    """
    Повертає (paid_by_certificate, mono_amount)
    """
    if certificate_nominal >= total:
        return total, 0
    return certificate_nominal, total - certificate_nominal

def send_free_order_to_server(order_id: str, used_certificates=None):
    """
    Викликає Railway /send-free-order для 100% оплати сертифікатом
    """
    payload = {"orderId": order_id}

    # (передамо коди сертифікатів у КРОЦІ 8; зараз залишимо підтримку поля)
    if used_certificates:
        payload["usedCertificates"] = used_certificates

    try:
        r = requests.post(
            f"{PAY_SERVER_URL}/send-free-order",
            json=payload,
            timeout=8,
        )
        return r.ok
    except Exception as e:
        print("❌ send_free_order_to_server error:", e)
        return False

# ================== ХЕНДЛЕР/START ==================

@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    uid = message.from_user.id
    user_sessions.setdefault(uid, {"cart": {}})

    # 👑 АДМІН
    if uid == ADMIN_ID:
        await message.answer(
            "Панель адміністратора 👇",
            reply_markup=admin_keyboard()
        )
        return

    # 👤 КЛІЄНТ
    await message.answer(
        "Натисніть кнопку внизу, щоб почати замовлення 👇",
        reply_markup=persistent_keyboard()
    )

    # одразу показуємо категорії (щоб було “без зайвого кліку”)
    await message.answer(
        "Оберіть категорію товарів:",
        reply_markup=categories_keyboard(message.from_user.id)
    )


# ================== ХЕНДЛЕР ПОЧАТИ ==================

@dp.message_handler(lambda message: message.text == "🛒 Почати замовлення")
async def start_order(message: types.Message):
    user_sessions.setdefault(message.from_user.id, {"cart": {}})

    await message.answer(
        "Оберіть категорію товарів:",
        reply_markup=categories_keyboard(message.from_user.id)
    )

# ================== КАТЕГОРІЇ ==================

@dp.callback_query_handler(lambda c: c.data.startswith("cat:"))
async def open_category(call: types.CallbackQuery):
    cat = call.data.split(":")[1]

    uid = call.from_user.id
    user_sessions.setdefault(uid, {})["current_category"] = cat

    # спеціальна логіка для discovery
    if cat == "discovery":
        await call.message.edit_text(
            f"🎁 Discovery set\n\n"
            f"Оберіть 4 аромати з {len(DISCOVERY_AROMAS)} "
            f"для вашого discovery set ({DISCOVERY_SAMPLE_ML} мл кожен).",
            reply_markup=discovery_start_keyboard()
        )
        await call.answer()
        return

    # 👇 СЕРТИФІКАТИ = ТОВАРИ + 1 ПРИМІТКА
    if cat == "certificates":
        uid = call.from_user.id
        kb = products_keyboard("certificates", uid)        
        
        await call.message.edit_text(
            "🎫 *Подарункові сертифікати:*",
            reply_markup=kb,
            parse_mode="Markdown"
        )
        await call.answer()
        return

    # стандартна логіка для інших категорій
    await call.message.edit_text(
        f"{CATEGORIES[cat]}:",
        reply_markup=products_keyboard(cat, call.from_user.id)
    )
    await call.answer()

# ================== ДОДАТИ В КОШИК ==================

def find_product(pid):
    for items in PRODUCTS.values():
        for p in items:
            if p["id"] == pid:
                return p
    return None

@dp.callback_query_handler(lambda c: c.data.startswith("add:"))
async def add_to_cart(call: types.CallbackQuery):
    uid = call.from_user.id
    product_id = call.data.split(":")[1]

    product = find_product(product_id)
    if not product:
        await call.answer("Товар не знайдено", show_alert=True)
        return

    session = user_sessions.setdefault(uid, {"cart": {}})
    cart = session.setdefault("cart", {})

    cart[product_id] = cart.get(
        product_id,
        {
            "name": product["name"],
            "price": product["price"],
            "qty": 0,
            "label": product.get("label")
        }
    )
    cart[product_id]["qty"] += 1

    await call.answer("Додано в кошик ✅")

    try:
        await call.message.edit_reply_markup(
            reply_markup=products_keyboard(
                session.get("current_category"),
                call.from_user.id
            )
        )
    except Exception:
        pass

# ================== КОШИК ==================

@dp.callback_query_handler(lambda c: c.data == "view_cart")
async def view_cart(call: types.CallbackQuery):
    cart = user_sessions[call.from_user.id]["cart"]

    if not cart:
        # щоб не ловити MessageNotModified — шлемо новим повідомленням
        await call.message.answer(
            "Ваш кошик порожній 🛒",
            reply_markup=categories_keyboard(call.from_user.id)
        )
        await call.answer()
        return

    text = "🛒 Ваш кошик:\n\n"
    total = 0

    # КЛАВІАТУРА — спочатку порожня, потім додаємо рядки
    kb = InlineKeyboardMarkup(row_width=4)

    for key, item in cart.items():
        # DISCOVERY
        if item.get("type") == "discovery":
            text += (
                f"🎁 {item['name']} — {item['price']} грн\n"
                + "\n".join([f" • {a}" for a in item["aromas"]])
                + "\n\n"
            )
            total += item["price"]

            # 1 рядок кнопок для сету (тільки видалити)
            kb.row(
                InlineKeyboardButton(
                    "Видалити сет 🗑",
                    callback_data=f"cart_del:{key}"
                )
            )

        # ЗВИЧАЙНИЙ ТОВАР
        else:
            qty = item.get("qty", 1)
            text += (
                f"{item['name']} × {qty} — "
                f"{item['price'] * qty} грн\n"
            )
            total += item["price"] * qty

            # 1 рядок кнопок для товару: + / - / 🗑
            kb.row(
                InlineKeyboardButton("+", callback_data=f"cart_inc:{key}"),
                InlineKeyboardButton("-", callback_data=f"cart_dec:{key}"),
                InlineKeyboardButton("🗑", callback_data=f"cart_del:{key}")
            )

    text += f"\nСума: {total} грн"

    # Нижні кнопки (як ти хочеш)
    kb.row(
        InlineKeyboardButton(
            "⬅️ Продовжити покупки",
            callback_data="back_categories"
        )
    )
    kb.row(
        InlineKeyboardButton(
            "✅ Оформити замовлення",
            callback_data="checkout_start"
        )
    )

    # ВАЖЛИВО: edit_text може дати MessageNotModified — ловимо і шлемо новим
    try:
        await call.message.edit_text(text, reply_markup=kb)
    except Exception:
        pass

    await call.answer()

# ================== НАЗАД ==================

@dp.callback_query_handler(lambda c: c.data == "back_categories")
async def back_categories(call: types.CallbackQuery):
    await call.message.edit_text(
        "Оберіть категорію:",
        reply_markup=categories_keyboard(call.from_user.id)
    )
    await call.answer()

# ================== DISCOVERY: старт формування ==================

@dp.callback_query_handler(lambda c: c.data == "discovery_start")
async def discovery_start(call: types.CallbackQuery):
    session = user_sessions.setdefault(call.from_user.id, {"cart": {}})
    session["discovery_builder"] = {"selected": []}

    await call.message.edit_text(
        "🎁 Discovery set\n\n"
        "Оберіть 4 аромати з 10 (3 мл кожен):",
        reply_markup=discovery_aromas_keyboard([])
    )
    await call.answer()

# ================== DISCOVERY: вибір позицій у формуванні сету ==================

@dp.callback_query_handler(lambda c: c.data.startswith("disc_toggle::"))
async def discovery_toggle(call: types.CallbackQuery):
    uid = call.from_user.id
    aroma = call.data.split("disc_toggle::", 1)[1]

    session = user_sessions.setdefault(uid, {"cart": {}})
    builder = session.setdefault("discovery_builder", {"selected": []})
    selected = builder["selected"]

    if aroma in selected:
        selected.remove(aroma)
    else:
        if len(selected) >= 4:
            await call.answer(
                "Можна обрати тільки 4 аромати",
                show_alert=True
            )
            return
        selected.append(aroma)

    # ⬇️ КЛЮЧОВЕ: ПОВНЕ ПЕРЕМАЛЮВАННЯ
    await call.message.edit_text(
        "🎁 Discovery set\n\n"
        "Оберіть 4 аромати з 10 (3 мл кожен):",
        reply_markup=discovery_aromas_keyboard(selected)
    )
    await call.answer()

@dp.callback_query_handler(lambda c: c.data == "disc_confirm")
async def discovery_confirm(call: types.CallbackQuery):
    uid = call.from_user.id
    session = user_sessions.setdefault(uid, {"cart": {}})
    builder = session.get("discovery_builder")

    if not builder or len(builder.get("selected", [])) != 4:
        await call.answer(
            "Оберіть рівно 4 аромати",
            show_alert=True
        )
        return

    selected = builder["selected"]

    # формуємо один товар discovery
    discovery_item = {
        "type": "discovery",
        "name": "Discovery set (4 × 3 мл)",
        "aromas": selected.copy(),
        "price": DISCOVERY_PRICE,
    }

    # додаємо в кошик як окрему позицію
    cart = session.setdefault("cart", {})
    key = (
        f"discovery_"
        f"{len([k for k in cart if k.startswith('discovery_')]) + 1}"
    )
    cart[key] = discovery_item

    # очищаємо builder, щоб можна було створити ще один set
    session.pop("discovery_builder", None)

    await call.message.edit_text(
        "🎁 Discovery set\n\n"
        "Discovery set додано у кошик ✅\n"
        "Ви можете сформувати ще один або перейти до оформлення.",
        reply_markup=discovery_start_keyboard()
    )
    await call.answer()

# ================== СЕРТИФІКАТИ ==================

@dp.callback_query_handler(lambda c: c.data == "toggle_physical_certificate")
async def toggle_physical_certificate(call: types.CallbackQuery):
    uid = call.from_user.id

    session = user_sessions.setdefault(uid, {})
    certificates = session.setdefault("certificates", {})
    certificates["physical"] = not certificates.get("physical", False)

    kb = products_keyboard("certificates", uid)
    await call.message.edit_reply_markup(reply_markup=kb)
    await call.answer()

# ================== ОФОРМЛЕННЯ: СТАРТ ==================

@dp.callback_query_handler(lambda c: c.data == "checkout_start")
async def checkout_start(call: types.CallbackQuery):
    uid = call.from_user.id
    session = user_sessions.setdefault(uid, {"cart": {}})
    session["checkout"] = {}

    await call.message.answer(
        "✍️ Введіть *Імʼя та Прізвище* одним повідомленням:",
        parse_mode="Markdown"
    )
    await call.answer()

# ================== CHECKOUT: ІМʼЯ ==================

@dp.message_handler(
    lambda m: (
        "checkout" in user_sessions.get(m.from_user.id, {})
        and "name" not in user_sessions[m.from_user.id]["checkout"]
    )
)
async def checkout_name(m: types.Message):
    uid = m.from_user.id
    checkout = user_sessions[uid]["checkout"]

    checkout["name"] = m.text.strip()
    checkout["phone_mode"] = "share"

    await m.answer(
        "📞 Поділіться номером телефону отримувача 👇",
        reply_markup=share_phone_keyboard()
    )

# ================== CHECKOUT: ОТРИМАНО НОМЕР ==================

@dp.message_handler(content_types=types.ContentType.CONTACT)
async def checkout_phone_shared(m: types.Message):
    uid = m.from_user.id
    session = user_sessions.get(uid)

    if not session or "checkout" not in session:
        return

    checkout = session["checkout"]

    if checkout.get("phone_mode") != "share":
        return

    checkout["phone"] = m.contact.phone_number
    checkout["phone_mode"] = "confirm"

    kb = InlineKeyboardMarkup()
    kb.add(
        InlineKeyboardButton("✅ Так", callback_data="phone_ok"),
        InlineKeyboardButton("✏️ Інший", callback_data="phone_other"),
    )

    await m.answer(
        f"📞 Отримано номер:\n"
        f"<b>{checkout['phone']}</b>\n\n"
        f"Це номер отримувача?",
        reply_markup=kb,
        parse_mode="HTML"
    )

# ================== CHECKOUT: НОМЕР ПІДТВЕРДЖЕНО ==================

@dp.callback_query_handler(lambda c: c.data == "phone_ok")
async def phone_ok(call: types.CallbackQuery):
    uid = call.from_user.id
    checkout = user_sessions[uid]["checkout"]

    checkout["phone_mode"] = "done"

    await call.message.answer(
        "📦 Вкажіть місто та № відділення / поштомату Нової Пошти:",
        parse_mode="Markdown"
    )
    await call.answer()

# ================== CHECKOUT: ІНШИЙ НОМЕР ==================

@dp.callback_query_handler(lambda c: c.data == "phone_other")
async def phone_other(call: types.CallbackQuery):
    uid = call.from_user.id
    checkout = user_sessions[uid]["checkout"]

    checkout["phone_mode"] = "manual"
    checkout.pop("phone", None)

    await call.message.answer(
        "📞 Введіть номер телефону отримувача:",
        parse_mode="Markdown"
    )
    await call.answer()

# ================== CHECKOUT: РУЧНИЙ НОМЕР ==================

@dp.message_handler(
    lambda m: (
        "checkout" in user_sessions.get(m.from_user.id, {})
        and user_sessions[m.from_user.id]["checkout"].get("phone_mode") == "manual"
    )
)
async def checkout_phone_manual(m: types.Message):
    uid = m.from_user.id
    checkout = user_sessions[uid]["checkout"]

    checkout["phone"] = m.text.strip()
    checkout["phone_mode"] = "done"

    await m.answer(
        "📦 Вкажіть місто та № відділення / поштомату Нової Пошти:",
        parse_mode="Markdown"
    )

# ================== CHECKOUT: Е-МАЙЛ І ВИБІР ОПЛАТИ ==================

def is_valid_email(value: str) -> bool:
    value = (value or "").strip()
    return re.match(r"^[^\s@]+@[^\s@]+\.[^\s@]+$", value) is not None


def loyalty_email_keyboard():
    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(
        InlineKeyboardButton(
            "⬅️ Повернутись до кошика",
            callback_data="view_cart"
        )
    )
    kb.add(
        InlineKeyboardButton(
            "Пропустити",
            callback_data="skip_loyalty_email"
        )
    )
    return kb


async def show_payment_options(message, uid: int):
    session = user_sessions[uid]
    cart = session.get("cart", {})

    has_certificate = cart_has_certificate(cart)

    has_certificate_product = False
    for item in cart.values():
        if "сертифікат" in item.get("name", "").lower():
            has_certificate_product = True
            break

    kb = InlineKeyboardMarkup(row_width=1)

    if has_certificate:
        kb.add(
            InlineKeyboardButton(
                "💳 Оплата 100%",
                callback_data="pay_full"
            )
        )

        if can_apply_certificate(cart):
            kb.add(
                InlineKeyboardButton(
                    "🎟 Ввести сертифікат",
                    callback_data="enter_certificate"
                )
            )

        warning_text = (
            "⚠️ У кошику міститься сертифікат.\n"
            "Для таких замовлень можлива лише повна оплата."
        )

        if has_certificate_product:
            warning_text += (
                "\n\n🚫 Неможливо застосувати сертифікат "
                "при купівлі сертифікату."
            )

        await message.answer(
            warning_text,
            reply_markup=kb
        )

    else:
        kb.add(
            InlineKeyboardButton("💳 Оплата 100%", callback_data="pay_full"),
            InlineKeyboardButton("💵 Передплата 150 грн", callback_data="pay_deposit"),
            InlineKeyboardButton("🎟 Оплатити сертифікатом", callback_data="enter_certificate"),
        )
        kb.add(
            InlineKeyboardButton("⬅️ Повернутись до кошика", callback_data="view_cart")
        )

        await message.answer(
            "💳 Оберіть спосіб оплати:",
            reply_markup=kb
        )

# ================== CHECKOUT: ДОСТАВКА → EMAIL ЛОЯЛЬНОСТІ ==================

@dp.message_handler(
    lambda m: (
        "checkout" in user_sessions.get(m.from_user.id, {})
        and "phone" in user_sessions[m.from_user.id]["checkout"]
        and "delivery" not in user_sessions[m.from_user.id]["checkout"]
    )
)
async def checkout_payment(m: types.Message):
    uid = m.from_user.id
    session = user_sessions[uid]

    # зберігаємо доставку
    session["checkout"]["delivery"] = m.text.strip()

    # просимо email для програми лояльності
    session["checkout"]["waiting_loyalty_email"] = True

    await m.answer(
        "💛 Якщо ви зареєстровані в програмі лояльності Mōnal, "
        "введіть email, який вказували при реєстрації.\n\n"
        "Якщо не зареєстровані або не хочете привʼязувати замовлення, натисніть «Пропустити».",
        reply_markup=loyalty_email_keyboard()
    )

# ================== CHECKOUT: EMAIL ЛОЯЛЬНОСТІ ==================

@dp.message_handler(
    lambda m: (
        "checkout" in user_sessions.get(m.from_user.id, {})
        and user_sessions[m.from_user.id]["checkout"].get("waiting_loyalty_email") is True
    )
)
async def receive_loyalty_email(m: types.Message):
    uid = m.from_user.id
    checkout = user_sessions[uid]["checkout"]

    email = m.text.strip().lower()

    if not is_valid_email(email):
        await m.answer(
            "Email виглядає некоректно.\n"
            "Введіть email ще раз або натисніть «Пропустити».",
            reply_markup=loyalty_email_keyboard()
        )
        return

    checkout["loyalty_email"] = email
    checkout["waiting_loyalty_email"] = False

    await m.answer(
        "✅ Email збережено для привʼязки до програми лояльності."
    )

    await show_payment_options(m, uid)


@dp.callback_query_handler(lambda c: c.data == "skip_loyalty_email")
async def skip_loyalty_email(call: types.CallbackQuery):
    uid = call.from_user.id
    session = user_sessions.get(uid)

    if not session or "checkout" not in session:
        user_sessions.setdefault(uid, {"cart": {}})

        await call.message.answer(
            "Сесія оформлення оновилась. Почніть замовлення ще раз 👇",
            reply_markup=persistent_keyboard()
        )

        await call.message.answer(
            "Оберіть категорію товарів:",
            reply_markup=categories_keyboard(uid)
        )

        await call.answer()
        return

    checkout = session["checkout"]

    if checkout.get("waiting_loyalty_email") is not True:
        await call.answer(
            "Цей крок уже пройдений.",
            show_alert=True
        )
        return

    checkout["loyalty_email"] = ""
    checkout["waiting_loyalty_email"] = False

    await call.message.answer(
        "Добре, продовжуємо без привʼязки до програми лояльності."
    )

    await show_payment_options(call.message, uid)
    await call.answer()

# ================== НОВА ФУНКЦІЯ ПО СЕРТИФІКАТАМ ==================
@dp.callback_query_handler(lambda c: c.data == "enter_certificate")
async def enter_certificate(call: types.CallbackQuery):
    uid = call.from_user.id
    session = user_sessions.setdefault(uid, {})

    checkout = session.setdefault("checkout", {})
    checkout["waiting_certificate"] = True

    await call.message.answer(
        "🎟 Введіть код сертифіката одним повідомленням:"
    )
    await call.answer()

@dp.message_handler(
    lambda m: (
        "checkout" in user_sessions.get(m.from_user.id, {})
        and user_sessions[m.from_user.id]["checkout"].get("waiting_certificate") is True
    )
)
async def receive_certificate_code(m: types.Message):
    uid = m.from_user.id
    checkout = user_sessions[uid]["checkout"]

    code = m.text.strip().upper()

    valid, nominal = check_certificate_remote(code)

    if not valid:
        checkout.pop("certificate_code", None)
        checkout["waiting_certificate"] = True

        await m.answer(
            "🚫 Сертифікат не знайдено або він вже використаний.\n"
            "Спробуйте ввести інший код одним повідомленням:",
        )
        return

    # ✅ валідний сертифікат
    checkout["certificate_code"] = code
    checkout["certificate_nominal"] = nominal
    checkout["waiting_certificate"] = False

    await m.answer(
        f"✅ Сертифікат **{code}** підтверджено.\n"
        f"Номінал: **{nominal} грн**.\n"
        "Переходимо далі.",
        parse_mode="Markdown"
    )

    # ➕ Розрахунок оплати
    cart = user_sessions[uid].get("cart", {})
    total = 0

    for item in cart.values():
        if item.get("type") == "discovery":
            total += item["price"]
        else:
            total += item["price"] * item.get("qty", 1)

    paid_by_cert, mono_amount = calculate_amounts_with_certificate(
        total,
        nominal
    )

    await m.answer(
        f"💳 *Розрахунок оплати:*\n\n"
        f"🧾 Сума замовлення: {total} грн\n"
        f"🎟 Сертифікатом: {paid_by_cert} грн\n"
        f"💳 Через monobank: {mono_amount} грн\n\n"
        f"Продовжуємо оформлення 👇",
        parse_mode="Markdown"
    )

    # ================== ПЕРЕХІД ДО ОПЛАТИ ==================

    # ================== 100% СЕРТИФІКАТ ==================
    if mono_amount == 0:
        # 🔐 гарантуємо orderId
        if not checkout.get("invoice_ref"):
            import random
            import string
            part1 = "".join(random.choices(string.ascii_uppercase + string.digits, k=4))
            part2 = "".join(random.choices(string.ascii_uppercase + string.digits, k=4))
            checkout["invoice_ref"] = f"{part1}-{part2}"

        invoice_ref = checkout["invoice_ref"]

        # 🧾 1️⃣ РЕЄСТРУЄМО ЗАМОВЛЕННЯ (ОБОВʼЯЗКОВО) — ЗАХИСТ ВІД ПАДІННЯ
        if not MONO_BACKEND_URL:
            await m.answer("❌ MONO_BACKEND_URL missing. Не можу завершити оплату сертифікатом.")
            return

        try:
            r = requests.post(
                f"{MONO_BACKEND_URL}/register-order",
                json={
                    "orderId": invoice_ref,
                    "userId": uid,
                    "userEmail": checkout.get("loyalty_email", ""),
                    "text": "🛒 Замовлення з Telegram-бота",
                    "source": "bot",
                    "usedCertificates": [checkout.get("certificate_code")],
                    "buyerName": checkout.get("name", ""),
                    "buyerPhone": checkout.get("phone", ""),
                    "delivery": checkout.get("delivery", ""),
                    "itemsText": "Оплачено сертифікатом 100%",
                    "totalAmount": total,
                    "paidAmount": total,
                    "dueAmount": 0,
                    "paymentLabel": "Сертифікат 100%",
                },
                timeout=10,
            )
            if not r.ok:
                await m.answer("❌ Не вдалося зареєструвати замовлення на сервері (register-order).")
                return
        except Exception as e:
            await m.answer("❌ Помилка реєстрації замовлення (register-order).")
            return

        # 🎟 2️⃣ ПОГАШАЄМО СЕРТИФІКАТ
        ok = send_free_order_to_server(
            order_id=invoice_ref,
            used_certificates=[checkout.get("certificate_code")]
        )

        if ok:
            # 📩 СПОВІЩЕННЯ АДМІНУ
            admin_text = "🔔 *НОВЕ ЗАМОВЛЕННЯ*\n\n"
            admin_text += f"👤 {checkout.get('name', '—')}\n"
            admin_text += f"📞 {checkout.get('phone', '—')}\n"
            admin_text += f"📦 {checkout.get('delivery', '—')}\n"
            admin_text += f"💳 Сертифікат 100%\n\n"
            admin_text += "🛒 *Товари:*\n"

            for item in cart.values():
                if item.get("type") == "discovery":
                    admin_text += (
                        f"🎁 {item['name']} — {item['price']} грн\n"
                        + "\n".join([f" • {a}" for a in item["aromas"]])
                        + "\n\n"
                    )
                else:
                    qty = item.get("qty", 1)
                    admin_text += f"{item['name']} × {qty} — {item['price'] * qty} грн\n"

            admin_text += (
                f"\n💰 *Сума замовлення:* {total} грн\n"
                f"🎟 *Оплачено сертифікатом:* {total} грн\n"
                f"📦 *До оплати:* 0 грн\n"
                f"🧾 ref: {invoice_ref}"
            )

            try:
                await bot.send_message(ADMIN_ID, admin_text, parse_mode="Markdown")
            except Exception:
                pass

            await finalize_order(
                uid,
                "✅ Оплату отримано сертифікатом!\n\nДякуємо за замовлення 💛"
            )
        else:
            await m.answer("❌ Не вдалося завершити оплату сертифікатом (send-free-order).")

        return  # ❗ КРИТИЧНО: вихід лише тут


    # ================== СЕРТИФІКАТ + MONO ==================
    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(
        InlineKeyboardButton(
            f"💳 Оплатити через monobank ({mono_amount} грн)",
            callback_data="pay_full"
        )
    )

    await m.answer(
        "Для завершення замовлення виконайте оплату 👇",
        reply_markup=kb
    )

# ================== CHECKOUT: РЕЗЮМЕ ==================

async def show_order_summary(uid, chat_id):
    session = user_sessions[uid]
    cart = session.get("cart", {})
    checkout = session.get("checkout", {})

    text = "🧾 *Ваше замовлення:*\n\n"
    total = 0

    for item in cart.values():
        if item.get("type") == "discovery":
            text += (
                f"🎁 {item['name']} — {item['price']} грн\n"
                + "\n".join([f" • {a}" for a in item["aromas"]])
                + "\n\n"
            )
            total += item["price"]
        else:
            qty = item.get("qty", 1)
            text += (
                f"{item['name']} × {qty} — "
                f"{item['price'] * qty} грн\n"
            )
            total += item["price"] * qty

    text += (
        f"\n📦 *Доставка:* {checkout.get('delivery', '—')}\n"
        f"📞 *Телефон:* {checkout.get('phone', '—')}\n"
        f"💳 *Оплата:* {checkout.get('payment', '—')}\n"
        f"\n*Сума:* {total} грн"
    )

    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(
        InlineKeyboardButton(
            "✅ Підтвердити замовлення",
            callback_data="confirm_order"
        ),
        InlineKeyboardButton(
            "⬅️ Повернутись до покупок",
            callback_data="back_categories"
        ),
    )

    await bot.send_message(
        chat_id,
        text,
        reply_markup=kb,
        parse_mode="Markdown"
    )

# ================== CHECKOUT: ОПЛАТА_ВИБІР ==================

@dp.callback_query_handler(lambda c: c.data == "pay_full")
async def pay_full(call: types.CallbackQuery):
    uid = call.from_user.id
    session = user_sessions[uid]

    # рахуємо повну суму
    total = 0
    for item in session["cart"].values():
        if item.get("type") == "discovery":
            total += item["price"]
        else:
            total += item["price"] * item.get("qty", 1)

    # ===== КРОК 6: розрахунок з сертифікатом =====
    checkout = session.get("checkout", {})
    certificate_nominal = checkout.get("certificate_nominal")

    # 🔥 якщо використовується сертифікат — збережемо код для сервера
    if certificate_nominal:
        session["checkout"]["usedCertificates"] = [
            checkout.get("certificate_code")
        ]

    if certificate_nominal:
        paid_by_cert, mono_amount = calculate_amounts_with_certificate(
            total,
            certificate_nominal
        )
    else:
        paid_by_cert, mono_amount = 0, total

    def generate_bot_reference():
        import random
        import string

        part1 = "".join(random.choices(string.ascii_uppercase + string.digits, k=4))
        part2 = "".join(random.choices(string.ascii_uppercase + string.digits, k=4))
        return f"{part1}-{part2}"

    invoice_ref = generate_bot_reference()

    session.setdefault("checkout", {})
    session["checkout"]["invoice_ref"] = invoice_ref
    
    # 🔥 ВСТАНОВЛЮЄМО КОРЕКТНИЙ ТИП ОПЛАТИ
    if certificate_nominal and mono_amount > 0:
        session["checkout"]["payment"] = "Сертифікат + mono"
    elif certificate_nominal and mono_amount == 0:
        session["checkout"]["payment"] = "Сертифікат 100%"
    else:
        session["checkout"]["payment"] = "100% оплата"

    session["checkout"]["paid"] = False

    # ⬇️ СТАБІЛЬНА ЛОГІКА СУМ (НЕ МІНЯЄМО)
    session["checkout"]["total_amount"] = total
    session["checkout"]["paid_amount"] = mono_amount
    session["checkout"]["due_amount"] = 0

    # ⬇️ ДЛЯ WEBHOOK
    pending_payments[invoice_ref] = {
        "user_id": uid,
        "cart": session["cart"],
        "checkout": session["checkout"],
        "payment_type": "100% оплата",
    }

    # =====================================================
    # ✅ ЄДИНИЙ ШЛЯХ: РЕЄСТРУЄМО ЗАМОВЛЕННЯ ЯК САЙТ
    # =====================================================

    # формуємо itemsText (простий, стабільний)
    items_text_list = []
    for item in session["cart"].values():
        if item.get("type") == "discovery":
            items_text_list.append(
                item["name"] + ":\n" + "\n".join(item["aromas"])
            )
        else:
            qty = item.get("qty", 1)
            items_text_list.append(f'{item["name"]} × {qty}')
    items_text = "\n".join(items_text_list)

    # сертифікати як товар (для генерації)
    certificates = []
    for item in session["cart"].values():
        if item.get("label") == "Сертифікат":
            qty = item.get("qty", 1)
            for _ in range(qty):
                certificates.append({"nominal": item["price"]})

    if not MONO_BACKEND_URL:
        print("❌ MONO_BACKEND_URL missing — register-order skipped")
    else:
        try:
            requests.post(
                f"{MONO_BACKEND_URL}/register-order",
                json={
                    "orderId": invoice_ref,
                    "userId": uid,
                    "userEmail": session["checkout"].get("loyalty_email", ""),
                    "text": "🛒 Замовлення з Telegram-бота",
                    "source": "bot",
                    "certificates": certificates,
                    "usedCertificates": session["checkout"].get("usedCertificates", []),
                    "certificateType": session.get("certificates", {}).get(
                        "physical", False
                    ) and "фізичний" or "електронний",
                    "buyerName": session["checkout"].get("name", ""),
                    "buyerPhone": session["checkout"].get("phone", ""),
                    "delivery": session["checkout"].get("delivery", ""),
                    "itemsText": items_text,
                    "totalAmount": total,
                    "paidAmount": mono_amount,
                    "dueAmount": 0,
                    "paymentLabel": session["checkout"].get("payment"),
                },
                timeout=10,
            )
        except Exception as e:
            print("❌ REGISTER ORDER ERROR:", e)
    
    # =====================================================
    # 💳 MONO — ЯК БУЛО (СТАБІЛЬНО)
    # =====================================================
    payment_url = create_mono_invoice(
        amount=mono_amount,
        description="Оплата замовлення MONAL",
        invoice_ref=invoice_ref
    )

    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(
        InlineKeyboardButton(
            "💳 Оплатити через monobank",
            url=payment_url
        ),
        InlineKeyboardButton(
            "⬅️ Назад",
            callback_data="view_cart"
        ),
    )

    await call.message.edit_text(
        "💳 *Оплата 100%*\n\n"
        "Натисніть кнопку нижче для переходу до оплати:",
        reply_markup=kb,
        parse_mode="Markdown"
    )
    await call.answer()

@dp.callback_query_handler(lambda c: c.data == "pay_deposit")
async def pay_deposit(call: types.CallbackQuery):
    uid = call.from_user.id
    session = user_sessions[uid]

    # рахуємо повну суму замовлення
    total = 0
    for item in session["cart"].values():
        if item.get("type") == "discovery":
            total += item["price"]
        else:
            total += item["price"] * item.get("qty", 1)

    deposit = 150  # 🔴 для тесту можеш поставити 1
    invoice_ref = str(uuid.uuid4())

    session.setdefault("checkout", {})
    session["checkout"]["invoice_ref"] = invoice_ref
    session["checkout"]["payment"] = "Передплата 150 грн"
    session["checkout"]["paid"] = False

    # ⬇️ КЛЮЧОВЕ: суми
    session["checkout"]["total_amount"] = total
    session["checkout"]["paid_amount"] = deposit
    session["checkout"]["due_amount"] = total - deposit

    # ⬇️ ЗБЕРІГАЄМО ДЛЯ WEBHOOK
    pending_payments[invoice_ref] = {
        "user_id": uid,
        "cart": session["cart"],
        "checkout": session["checkout"],
        "payment_type": "Передплата 150 грн",
    }

    # ✅ РЕЄСТРУЄМО ЗАМОВЛЕННЯ НА БЕКЕНДІ ДЛЯ ПЕРЕДПЛАТИ
    items_text_list = []

    for item in session["cart"].values():
        if item.get("type") == "discovery":
            items_text_list.append(
                item["name"] + ":\n" + "\n".join(item["aromas"])
            )
        else:
            qty = item.get("qty", 1)
            items_text_list.append(f'{item["name"]} × {qty}')

    items_text = "\n".join(items_text_list)

    if not MONO_BACKEND_URL:
        print("❌ MONO_BACKEND_URL missing — register-order skipped")
    else:
        try:
            requests.post(
                f"{MONO_BACKEND_URL}/register-order",
                json={
                    "orderId": invoice_ref,
                    "userId": uid,
                    "userEmail": session["checkout"].get("loyalty_email", ""),
                    "text": "🛒 Замовлення з Telegram-бота",
                    "source": "bot",
                    "buyerName": session["checkout"].get("name", ""),
                    "buyerPhone": session["checkout"].get("phone", ""),
                    "delivery": session["checkout"].get("delivery", ""),
                    "itemsText": items_text,
                    "totalAmount": total,
                    "paidAmount": deposit,
                    "dueAmount": total - deposit,
                    "paymentLabel": session["checkout"].get("payment"),
                },
                timeout=10,
            )
        except Exception as e:
            print("❌ REGISTER ORDER DEPOSIT ERROR:", e)

    payment_url = create_mono_invoice(
        amount=deposit,
        description="Передплата 150 грн — MONAL",
        invoice_ref=invoice_ref
    )

    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(
        InlineKeyboardButton(
            "💳 Оплатити передплату",
            url=payment_url
        ),
        InlineKeyboardButton(
            "⬅️ Назад",
            callback_data="view_cart"
        ),
    )

    await call.message.edit_text(
        "💵 *Передплата 150 грн*\n\n"
        "Натисніть кнопку нижче для оплати:",
        reply_markup=kb,
        parse_mode="Markdown"
    )
    await call.answer()

# ================== CHECKOUT: ПІДТВЕРДЖЕННЯ ==================

@dp.callback_query_handler(lambda c: c.data == "confirm_order")
async def confirm_order(call: types.CallbackQuery):
    uid = call.from_user.id
    session = user_sessions[uid]
    cart = session.setdefault("cart", {})
    checkout = session.setdefault("checkout", {})

    # повідомлення адміну
    admin_text = "🔔 *НОВЕ ЗАМОВЛЕННЯ*\n\n"
    admin_text += f"👤 {checkout['name']}\n"
    admin_text += f"📞 {checkout['phone']}\n"
    admin_text += f"📦 {checkout['delivery']}\n"
    admin_text += f"💳 {checkout['payment']}\n\n"
    admin_text += "🛒 Товари:\n"

    total = 0
    for item in cart.values():
        if item.get("type") == "discovery":
            admin_text += (
                f"🎁 {item['name']} — {item['price']} грн\n"
                + "\n".join([f" • {a}" for a in item["aromas"]])
                + "\n\n"
            )
            total += item["price"]
        else:
            qty = item.get("qty", 1)
            admin_text += (
                f"{item['name']} × {qty} — "
                f"{item['price'] * qty} грн\n"
            )
            total += item["price"] * qty

    # суми з checkout (ВЖЕ ПОРАХОВАНІ)
    total_amount = checkout.get("total_amount", 0)
    paid_amount = checkout.get("paid_amount", 0)   # це mono
    due_amount = checkout.get("due_amount", 0)

    cert_nominal = checkout.get("certificate_nominal")

    admin_text += f"\n💰 Сума замовлення: {total_amount} грн"

    if cert_nominal:
        paid_by_cert, paid_by_mono = calculate_amounts_with_certificate(
            total_amount,
            cert_nominal
        )

        admin_text += (
            f"\n🎟 Сертифікатом: {paid_by_cert} грн"
            f"\n💳 Через mono: {paid_by_mono} грн"
        )
    else:
        admin_text += f"\n💳 Сплачено: {paid_amount} грн"

    admin_text += f"\n📦 До оплати: {due_amount} грн"

    await bot.send_message(
        ADMIN_ID,
        admin_text,
        parse_mode="Markdown"
    )

    await finalize_order(
        uid,
        "✅ Замовлення прийнято!\n\nМи зв’яжемось з вами для підтвердження 💛"
    )
    
    await call.answer()

# ================== CART CONTROL ==================

@dp.callback_query_handler(lambda c: c.data.startswith("cart_inc:"))
async def cart_inc(call: types.CallbackQuery):
    key = call.data.split(":")[1]
    cart = user_sessions[call.from_user.id]["cart"]

    if key in cart:
        cart[key]["qty"] += 1

    await call.answer()
    await view_cart(call)

@dp.callback_query_handler(lambda c: c.data.startswith("cart_dec:"))
async def cart_dec(call: types.CallbackQuery):
    key = call.data.split(":")[1]
    cart = user_sessions[call.from_user.id]["cart"]

    if key in cart:
        cart[key]["qty"] -= 1
        if cart[key]["qty"] <= 0:
            cart.pop(key)

    await call.answer()
    await view_cart(call)

@dp.callback_query_handler(lambda c: c.data.startswith("cart_del:"))
async def cart_del(call: types.CallbackQuery):
    key = call.data.split(":")[1]
    cart = user_sessions[call.from_user.id]["cart"]

    cart.pop(key, None)

    await call.answer("Видалено")
    await view_cart(call)

@dp.callback_query_handler(lambda c: c.data == "noop")
async def noop(call: types.CallbackQuery):
    await call.answer()

# ================== ОПЛАТА МОНО ==================

def create_mono_invoice(amount: int, description: str, invoice_ref: str):
    url = "https://api.monobank.ua/api/merchant/invoice/create"

    headers = {
        "X-Token": MONO_TOKEN,
        "Content-Type": "application/json",
    }

    payload = {
        "amount": int(amount * 100),
        "ccy": 980,
        "merchantPaymInfo": {
            "reference": invoice_ref,
            "destination": description,
        },
        "redirectUrl": "https://monal.com.ua/",
        "webHookUrl": "https://monal-mono-pay-production.up.railway.app/mono-webhook",
    }

    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()

    data = response.json()
    return data["pageUrl"]

# ================== BOT FINALIZE FROM SERVER ==================

async def bot_finalize(request: web.Request):
    data = await request.json()
    uid = data.get("userId")

    if uid and uid in user_sessions:
        await finalize_order(
            uid,
            "✅ Оплату отримано!\n\nДякуємо за замовлення 💛"
        )

    return web.Response(text="ok")

# ================== MONO WEBHOOK ==================

async def mono_webhook(request):
    data = await request.json()
    print("💰 MONO WEBHOOK DATA:", data)

    reference = data.get("reference")
    status = data.get("status")

    if not reference:
        print("❌ No reference in payload")
        return web.Response(text="no reference", status=400)

    if reference not in pending_payments:
        print("❌ Reference not found in pending_payments:", reference)
        return web.Response(text="unknown reference", status=200)

    # беремо збережене замовлення
    order = pending_payments[reference]
    user_id = order["user_id"]
    cart = order["cart"]
    checkout = order["checkout"]

    total_amount = checkout.get("total_amount", 0)
    paid_amount = checkout.get("paid_amount", 0)
    due_amount = checkout.get("due_amount", 0)
    payment_type = order["payment_type"]

    # --------- ТІЛЬКИ ТОВАРИ ДЛЯ ТАБЛИЦІ ---------
    items_text_list = []

    for item in cart.values():
        if item.get("type") == "discovery":
            items_text_list.append(
                item["name"] + ":\n" + "\n".join(item["aromas"])
            )
        else:
            qty = item.get("qty", 1)
            items_text_list.append(f'{item["name"]} × {qty}')

    items_text = "\n".join(items_text_list)

    # цікавить ТІЛЬКИ успішна оплата
    if status != "success":
        return web.Response(text="ok", status=200)

    # ✅ КРОК 8: якщо був застосований сертифікат — позначаємо його використаним
    cert_code = checkout.get("certificate_code")
    if cert_code:
        try:
            requests.post(
                f"{PAY_SERVER_URL}/send-free-order",
                json={
                    "orderId": reference,
                    "usedCertificates": [cert_code],
                },
                timeout=8,
            )
        except Exception as e:
            print("❌ CERT MARK USED ERROR:", e)

    # --------- формуємо повідомлення адміну ---------
    text = "✅ *ОПЛАТУ ОТРИМАНО*\n\n"
    text += f"👤 *{checkout.get('name', '—')}*\n"
    text += f"📞 {checkout.get('phone', '—')}\n"
    text += f"📦 {checkout.get('delivery', '—')}\n"
    text += f"💳 {payment_type}\n\n"

    total = 0
    text += "🛒 *Товари:*\n"

    for item in cart.values():
        if item.get("type") == "discovery":
            text += (
                f"🎁 {item['name']} — {item['price']} грн\n"
                + "\n".join([f" • {a}" for a in item["aromas"]])
                + "\n\n"
            )
            total += item["price"]
        else:
            qty = item.get("qty", 1)
            text += (
                f"{item['name']} × {qty} — "
                f"{item['price'] * qty} грн\n"
            )
            total += item["price"] * qty

    text += (
        f"\n💰 *Сума замовлення:* {total_amount} грн"
        f"\n💳 *Сплачено:* {paid_amount} грн"
        f"\n📦 *До оплати:* {due_amount} грн"
    )
    text += f"\n🧾 ref: {reference}"

    await bot.send_message(
        ADMIN_ID,
        text,
        parse_mode="Markdown"
    )

    # 🧾 ЛОГУЄМО ЗАМОВЛЕННЯ В ORDERS_LOG (через сервер)
    try:
        requests.post(
            "https://monal-mono-pay-production.up.railway.app/log-bot-order",
            json={
                "orderId": reference,
                "totalAmount": total_amount,
                "paidAmount": paid_amount,
                "dueAmount": due_amount,
                "paymentType": payment_type,
                "buyerName": checkout.get("name", ""),
                "buyerPhone": checkout.get("phone", ""),
                "delivery": checkout.get("delivery", ""),
                "itemsText": items_text,
            },
            timeout=5,
        )
    except Exception as e:
        print("❌ BOT → ORDERS_LOG ERROR:", e)

    await finalize_order(
        user_id,
        "✅ Оплату отримано!\n\nДякуємо за замовлення 💛"
    )

    # прибираємо з черги
    pending_payments.pop(reference, None)

    return web.Response(text="ok", status=200)

# =================== 👑 АДМІН: АКТИВНІ ЗАМОВЛЕННЯ ===================

@dp.message_handler(lambda m: m.text == "📦 Активні замовлення")
async def admin_active_orders(m: types.Message):
    if m.from_user.id != ADMIN_ID:
        return

    try:
        r = requests.get(
            "https://monal-mono-pay-production.up.railway.app/admin/active-orders",
            timeout=10,
        )
        orders = r.json()
    except Exception:
        await m.answer("❌ Не вдалося отримати замовлення")
        return

    if not orders:
        await m.answer("📭 Активних замовлень немає")
        return

    for o in orders:
        text = (
            f"🧾 Замовлення №{o.get('orderId', '—')}\n"
            f"👤 {o.get('buyerName', '—')}\n"
            f"📞 {o.get('buyerPhone', '—')}\n"
            f"📦 {o.get('delivery', '—')}\n\n"
            f"🛒 {o.get('itemsText', '—')}\n\n"
            f"💰 {o.get('totalAmount', '—')} грн"
        )

        kb = InlineKeyboardMarkup()
        kb.add(
            InlineKeyboardButton(
                "✅ Виконано",
                callback_data=f"order_done:{o.get('orderId')}",
            )
        )

        await m.answer(text, reply_markup=kb)

# =================== 👑 АДМІН: ПОМІТИТИ ЯК ВИКОНАНО ===================

@dp.callback_query_handler(lambda c: c.data and c.data.startswith("order_done:"))
async def admin_mark_done(call: types.CallbackQuery):
    try:
        await call.answer()
    except Exception:
        pass

    if call.from_user.id != ADMIN_ID:
        await call.answer("⛔️ Нема доступу", show_alert=True)
        return

    order_id = call.data.split("order_done:", 1)[1].strip()

    await call.message.answer(f"🟡 Mark done натиснуто для: {order_id}")

    try:
        r = requests.post(
            "https://monal-mono-pay-production.up.railway.app/admin/mark-done",
            json={"orderId": order_id},
            timeout=10,
        )
        await call.message.answer(
            f"🟢 mark-done статус: {r.status_code}\n{(r.text or '')[:200]}"
        )
    except Exception as e:
        await call.message.answer(f"🔴 mark-done помилка: {e}")
        return

    try:
        await call.message.edit_reply_markup(reply_markup=None)
    except Exception:
        pass


# =================== 👑 АДМІН: ВИКОНАНІ ЗАМОВЛЕННЯ ===================

@dp.message_handler(lambda m: m.text == "✅ Виконані замовлення")
async def admin_completed_orders(m: types.Message):
    if m.from_user.id != ADMIN_ID:
        return

    try:
        r = requests.get(
            "https://monal-mono-pay-production.up.railway.app/admin/completed-orders",
            timeout=10,
        )
        orders = r.json()
    except Exception:
        await m.answer("❌ Не вдалося отримати виконані замовлення")
        return

    if not orders:
        await m.answer("📭 Виконаних замовлень немає")
        return

    for o in orders:
        text = (
            f"🧾 Замовлення №{o.get('ID замовлення', '—')}\n"
            f"👤 {o.get('Імʼя клієнта', '—')}\n"
            f"📞 {o.get('Телефон', '—')}\n"
            f"📦 {o.get('Доставка', '—')}\n\n"
            f"🛒 {o.get('Склад замовлення', '—')}\n\n"
            f"💰 {o.get('Сума замовлення', '—')} грн\n"
            f"✅ Виконано"
        )

        await m.answer(text)


# ================== ЗАПУСК ==================

if __name__ == "__main__":
    app = web.Application()
    app.router.add_post("/webhook/telegram", telegram_webhook)
    app.router.add_post("/webhook/mono", mono_webhook)
    app.router.add_post("/bot-finalize", bot_finalize)
    app.on_startup.append(on_startup)

    web.run_app(
        app,
        host="0.0.0.0",
        port=int(os.getenv("PORT", "8080"))
    )

































