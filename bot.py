# -*- coding: utf-8 -*-
import os
import requests
import uuid

from aiohttp import web

from aiogram import Bot, Dispatcher, types
from aiogram.types import (
    InlineKeyboardMarkup, InlineKeyboardButton,
    ReplyKeyboardMarkup, KeyboardButton
)

from aiogram.types import MenuButtonWebApp, WebAppInfo

# ================== НАЛАШТУВАННЯ ==================
API_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
MONO_TOKEN = os.getenv("MONO_TOKEN")

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
            web_app=WebAppInfo(
                url="https://monal.com.ua/"
            )
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
        {"id": "d1", "name": "VESPER 200мл", "price": 1},
        {"id": "d2", "name": "NOCTURNE 200мл", "price": 1590},
        {"id": "d3", "name": "ROSALYA 200мл", "price": 1590},
        {"id": "d4", "name": "DRIFT 200мл", "price": 1590},
        {"id": "d5", "name": "STONE & SALT 200мл", "price": 1590},
        {"id": "d6", "name": "FREEDOM 200мл", "price": 1590},
        {"id": "d7", "name": "CROWN OF OLIVE 200мл", "price": 1590},
        {"id": "d8", "name": "SHADOW OF FIG 200мл", "price": 1590},
        {"id": "d9", "name": "GOLDEN RUM 200мл", "price": 1590},
        {"id": "d10", "name": "GREEN HAVEN 200мл", "price": 1590},        
    ],
    "home": [
        {"id": "h1", "name": "VESPER 100мл", "price": 990},
        {"id": "h2", "name": "NOCTURNE 100мл", "price": 990},
        {"id": "h3", "name": "ROSALYA 100мл", "price": 990},
        {"id": "h4", "name": "DRIFT 100мл", "price": 990},
        {"id": "h5", "name": "STONE & SALT 100мл", "price": 990},
        {"id": "h6", "name": "FREEDOM 100мл", "price": 990},
        {"id": "h7", "name": "CROWN OF OLIVE 100мл", "price": 990},
        {"id": "h8", "name": "SHADOW OF FIG 100мл", "price": 990},
        {"id": "h9", "name": "GOLDEN RUM 100мл", "price": 990},
        {"id": "h10", "name": "GREEN HAVEN 100мл", "price": 990},        
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
        {"id": "c1000", "name": "Сертифікат 1000 грн", "price": 1000,
            "label": "Сертифікат"},
        {"id": "c2500", "name": "Сертифікат 2500 грн", "price": 2500,
            "label": "Сертифікат"},
        {"id": "c3500", "name": "Сертифікат 3500 грн", "price": 3500,
            "label": "Сертифікат"},
        {"id": "c5000", "name": "Сертифікат 5000 грн", "price": 5000,
            "label": "Сертифікат"},
    ],
    "gifts": [
        {"id": "g1", "name": "FAIRYTALE", "price": 3199},
        {"id": "g2", "name": "TEN MINI 10х3мл", "price": 949},
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
    kb.add(
        InlineKeyboardButton("🛒 Кошик", callback_data="view_cart")
    )

    kb.add(
        InlineKeyboardButton("⬅️ Назад", callback_data="back_categories")
    )

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

if cat == "certificates":
    uid = call.from_user.id

    kb = products_keyboard("certificates", uid)

    # ⬇️ ДОДАТКОВА ПРИМІТКА ДЛЯ ВСІХ СЕРТИФІКАТІВ
    checkout = user_sessions.setdefault(uid, {}).setdefault("checkout", {})
    is_physical = checkout.get("certificateType") == "фізичний"

    kb.add(
        InlineKeyboardButton(
            "☑️ Друкований сертифікат" if is_physical else "☐ Хочу друкований сертифікат",
            callback_data="toggle_physical_certificate"
        )
    )

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
    product = find_product(call.data.split(":")[1])

    if not product:
        await call.answer("Товар не знайдено", show_alert=True)
        return

    session = user_sessions.setdefault(uid, {"cart": {}})
    cart = session["cart"]
    cart[product["id"]] = cart.get(product["id"], {"name": product["name"], "price": product["price"], "qty": 0})
    cart[product["id"]]["qty"] += 1

    await call.answer("Додано в кошик ✅")

    try:
        await call.message.edit_reply_markup(
            reply_markup=products_keyboard(
                call.data.split(":")[0].replace("add", ""),  # category не міняємо
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
                f"🎁 {item['name']} — {item['price']} грн\n" +
                "\n".join([f"  • {a}" for a in item["aromas"]]) +
                "\n\n"
            )
            total += item["price"]

            # 1 рядок кнопок для сету (тільки видалити)
            kb.row(
                InlineKeyboardButton("Видалити сет 🗑", callback_data=f"cart_del:{key}")
            )

        # ЗВИЧАЙНИЙ ТОВАР
        else:
            qty = item.get("qty", 1)
            text += f"{item['name']} × {qty} — {item['price'] * qty} грн\n"
            total += item["price"] * qty

            # 1 рядок кнопок для товару: 1 / + / - / 🗑
            kb.row(
                InlineKeyboardButton("+", callback_data=f"cart_inc:{key}"),
                InlineKeyboardButton("-", callback_data=f"cart_dec:{key}"),
                InlineKeyboardButton("🗑", callback_data=f"cart_del:{key}")
            )

    text += f"\nСума: {total} грн"

    # Нижні кнопки (як ти хочеш)
    kb.row(
        InlineKeyboardButton("⬅️ Продовжити покупки", callback_data="back_categories")
    )
    kb.row(
        InlineKeyboardButton("✅ Оформити замовлення", callback_data="checkout_start")
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

# ================== DISCOVERY: вибір позицій у формуванні сету==================
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
            await call.answer("Можна обрати тільки 4 аромати", show_alert=True)
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
        await call.answer("Оберіть рівно 4 аромати", show_alert=True)
        return

    selected = builder["selected"]

    # формуємо один товар discovery
    discovery_item = {
        "type": "discovery",
        "name": "Discovery set (4 × 3 мл)",
        "aromas": selected.copy(),
        "price": DISCOVERY_PRICE
    }

    # додаємо в кошик як окрему позицію
    cart = session.setdefault("cart", {})
    key = f"discovery_{len([k for k in cart if k.startswith('discovery_')]) + 1}"
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

# ================== СЕРТИФІКАТИ==================
@dp.callback_query_handler(lambda c: c.data == "toggle_physical_certificate")
async def toggle_physical_certificate(call: types.CallbackQuery):
    uid = call.from_user.id
    session = user_sessions.setdefault(uid, {"cart": {}, "checkout": {}})
    checkout = session.setdefault("checkout", {})

    current = checkout.get("certificateType", "електронний")
    checkout["certificateType"] = "фізичний" if current == "електронний" else "електронний"

    # оновлюємо ТЕ Ж повідомлення з новою кнопкою
    try:
        await call.message.edit_reply_markup(
            reply_markup=certificates_keyboard(uid)
        )
    except Exception:
        pass

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
    lambda m: "checkout" in user_sessions.get(m.from_user.id, {})
    and "name" not in user_sessions[m.from_user.id]["checkout"]
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
        InlineKeyboardButton("✏️ Інший", callback_data="phone_other")
    )

    await m.answer(
        f"📞 Отримано номер:\n<b>{checkout['phone']}</b>\n\nЦе номер отримувача?",
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
    lambda m: "checkout" in user_sessions.get(m.from_user.id, {})
    and user_sessions[m.from_user.id]["checkout"].get("phone_mode") == "manual"
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

# ================== CHECKOUT: ОПЛАТА ==================
@dp.message_handler(
    lambda m: "checkout" in user_sessions.get(m.from_user.id, {})
    and "phone" in user_sessions[m.from_user.id]["checkout"]
    and "delivery" not in user_sessions[m.from_user.id]["checkout"]
)
async def checkout_payment(m: types.Message):
    uid = m.from_user.id
    user_sessions[uid]["checkout"]["delivery"] = m.text.strip()

    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(
        InlineKeyboardButton("💳 Оплата 100%", callback_data="pay_full"),
        InlineKeyboardButton("💵 Передплата 150 грн", callback_data="pay_deposit")
    )

    await m.answer("💳 Оберіть спосіб оплати:", reply_markup=kb)

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
                f"🎁 {item['name']} — {item['price']} грн\n" +
                "\n".join([f"  • {a}" for a in item["aromas"]]) +
                "\n\n"
            )
            total += item["price"]
        else:
            qty = item.get("qty", 1)
            text += f"{item['name']} × {qty} — {item['price'] * qty} грн\n"
            total += item["price"] * qty

    text += (
        f"\n📦 *Доставка:* {checkout.get('delivery', '—')}\n"
        f"📞 *Телефон:* {checkout.get('phone', '—')}\n"
        f"💳 *Оплата:* {checkout.get('payment', '—')}\n"
        f"\n*Сума:* {total} грн"
    )

    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(
        InlineKeyboardButton("✅ Підтвердити замовлення", callback_data="confirm_order"),
        InlineKeyboardButton("⬅️ Повернутись до покупок", callback_data="back_categories")
    )

    await bot.send_message(
        chat_id,
        text,
        reply_markup=kb,
        parse_mode="Markdown"
    )

# ================== CHECKOUT: ОПЛАТА_ВИБір ==================
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

    invoice_ref = str(uuid.uuid4())

    session.setdefault("checkout", {})
    session["checkout"]["invoice_ref"] = invoice_ref
    session["checkout"]["payment"] = "100% оплата"
    session["checkout"]["paid"] = False

    # ⬇️ КЛЮЧОВЕ: суми
    session["checkout"]["total_amount"] = total
    session["checkout"]["paid_amount"] = total
    session["checkout"]["due_amount"] = 0

    # ⬇️ ЗБЕРІГАЄМО ДЛЯ WEBHOOK
    pending_payments[invoice_ref] = {
        "user_id": uid,
        "cart": session["cart"],
        "checkout": session["checkout"],
        "payment_type": "100% оплата"
    }

    payment_url = create_mono_invoice(
        amount=total,
        description="Оплата замовлення MONAL",
        invoice_ref=invoice_ref
    )

    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(
        InlineKeyboardButton("💳 Оплатити через monobank", url=payment_url),
        InlineKeyboardButton("⬅️ Назад", callback_data="view_cart")
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
        "payment_type": "Передплата 150 грн"
    }

    payment_url = create_mono_invoice(
        amount=deposit,
        description="Передплата 150 грн — MONAL",
        invoice_ref=invoice_ref
    )

    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(
        InlineKeyboardButton("💳 Оплатити передплату", url=payment_url),
        InlineKeyboardButton("⬅️ Назад", callback_data="view_cart")
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

    cart = session["cart"]
    checkout = session["checkout"]

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
                f"🎁 {item['name']} — {item['price']} грн\n" +
                "\n".join([f"  • {a}" for a in item["aromas"]]) +
                "\n\n"
            )
            total += item["price"]
        else:
            qty = item.get("qty", 1)
            admin_text += f"{item['name']} × {qty} — {item['price'] * qty} грн\n"
            total += item["price"] * qty

    # суми з checkout (ВЖЕ ПОРАХОВАНІ)
    total_amount = checkout.get("total_amount", 0)
    paid_amount = checkout.get("paid_amount", 0)
    due_amount = checkout.get("due_amount", 0)

    admin_text += (
        f"\n💰 Сума замовлення: {total_amount} грн"
        f"\n💳 Сплачено: {paid_amount} грн"
        f"\n📦 До оплати: {due_amount} грн"
    )

    
    await bot.send_message(ADMIN_ID, admin_text, parse_mode="Markdown")

    await call.message.edit_text(
        "✅ *Замовлення прийнято!*\n\n"
        "Ми зв’яжемось з вами для підтвердження 💛",
        parse_mode="Markdown"
    )

    # очищаємо кошик і checkout після завершення
    user_sessions[uid]["cart"] = {}
    user_sessions[uid].pop("checkout", None)

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
        "Content-Type": "application/json"
    }

    payload = {
        "amount": int(amount * 100),
        "ccy": 980,
        "merchantPaymInfo": {
            "reference": invoice_ref,
            "destination": description
        },
        "redirectUrl": "https://monal.com.ua/",
        "webHookUrl": "https://web-production-9a49a.up.railway.app/webhook/mono"
    }

    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()

    data = response.json()
    return data["pageUrl"]

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

    # --------- формуємо повідомлення адміну ---------
    text = "✅ *ОПЛАТУ ОТРИМАНО*\n\n"

    text += f"👤 *{checkout.get('name','—')}*\n"
    text += f"📞 {checkout.get('phone','—')}\n"
    text += f"📦 {checkout.get('delivery','—')}\n"
    text += f"💳 {payment_type}\n\n"

    total = 0
    text += "🛒 *Товари:*\n"

    for item in cart.values():
        if item.get("type") == "discovery":
            text += (
                f"🎁 {item['name']} — {item['price']} грн\n" +
                "\n".join([f"  • {a}" for a in item["aromas"]]) +
                "\n\n"
            )
            total += item["price"]
        else:
            qty = item.get("qty", 1)
            text += f"{item['name']} × {qty} — {item['price'] * qty} грн\n"
            total += item["price"] * qty
    
    text += (
        f"\n💰 *Сума замовлення:* {total_amount} грн"
        f"\n💳 *Сплачено:* {paid_amount} грн"
        f"\n📦 *До оплати:* {due_amount} грн"
    )
    text += f"\n🧾 ref: `{reference}`"

    await bot.send_message(ADMIN_ID, text, parse_mode="Markdown")

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
                "itemsText": items_text
            },
            timeout=5
        )
    except Exception as e:
        print("❌ BOT → ORDERS_LOG ERROR:", e)

    # 🔽 ОЧИЩАЄМО КОШИК І CHECKOUT ПІСЛЯ УСПІШНОЇ ОПЛАТИ
    user_sessions[user_id]["cart"] = {}
    user_sessions[user_id].pop("checkout", None)

    # ✅ ПОВІДОМЛЕННЯ ПОКУПЦЮ: ОПЛАТУ ОТРИМАНО + СТАРТ ЗАНОВО
    await bot.send_message(
        user_id,
        "✅ Оплату отримано!\n\n"
        "Дякуємо за замовлення 💛\n"
        "Щоб оформити нове — оберіть категорію нижче 👇",
        reply_markup=persistent_keyboard()
    )

    # прибираємо з черги
    pending_payments.pop(reference, None)

    return web.Response(text="ok", status=200)

# =================== 👑 АДМІН: АКТИВНІ ЗАМОВЛЕННЯ ===========================
@dp.message_handler(lambda m: m.text == "📦 Активні замовлення")
async def admin_active_orders(m: types.Message):
    if m.from_user.id != ADMIN_ID:
        return

    try:
        r = requests.get(
            "https://monal-mono-pay-production.up.railway.app/admin/active-orders",
            timeout=10
        )
        orders = r.json()
    except Exception as e:
        await m.answer("❌ Не вдалося отримати замовлення")
        return

    if not orders:
        await m.answer("📭 Активних замовлень немає")
        return

    for o in orders:
        text = (
            f"🧾 Замовлення №{o.get('orderId','—')}\n"
            f"👤 {o.get('buyerName','—')}\n"
            f"📞 {o.get('buyerPhone','—')}\n"
            f"📦 {o.get('delivery','—')}\n\n"
            f"🛒 {o.get('itemsText','—')}\n\n"
            f"💰 {o.get('totalAmount','—')} грн"
        )

        kb = InlineKeyboardMarkup()
        kb.add(
            InlineKeyboardButton(
                "✅ Виконано",
                callback_data=f"order_done:{o.get('orderId')}"
            )
        )

        await m.answer(text, reply_markup=kb)

# =================== 👑 АДМІН: ПОМІТИТИ ЯК ВИКОНАНО ===================
@dp.callback_query_handler(lambda c: c.data and c.data.startswith("order_done:"))
async def admin_mark_done(call: types.CallbackQuery):
    # ✅ одразу закриваємо “крутилку”, щоб не було “не відповідає”
    try:
        await call.answer()
    except Exception:
        pass

    if call.from_user.id != ADMIN_ID:
        await call.answer("⛔️ Нема доступу", show_alert=True)
        return

    order_id = call.data.split("order_done:", 1)[1].strip()

    # ✅ покажемо в чаті, що хендлер ВЗАГАЛІ СПРАЦЮВАВ
    await call.message.answer(f"🟡 Mark done натиснуто для: {order_id}")

    try:
        r = requests.post(
            "https://monal-mono-pay-production.up.railway.app/admin/mark-done",
            json={"orderId": order_id},
            timeout=10
        )
        await call.message.answer(f"🟢 mark-done статус: {r.status_code}\n{(r.text or '')[:200]}")
    except Exception as e:
        await call.message.answer(f"🔴 mark-done помилка: {e}")
        return

    # ✅ пробуємо прибрати кнопку (не критично, якщо не вийде)
    try:
        await call.message.edit_reply_markup(reply_markup=None)
    except Exception:
        pass

# =================== 👑 АДМІН: ВИКОНАНІ ЗАМОВЛЕННЯ ===========================
@dp.message_handler(lambda m: m.text == "✅ Виконані замовлення")
async def admin_completed_orders(m: types.Message):
    if m.from_user.id != ADMIN_ID:
        return

    try:
        r = requests.get(
            "https://monal-mono-pay-production.up.railway.app/admin/completed-orders",
            timeout=10
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
            f"🧾 Замовлення №{o.get('ID замовлення','—')}\n"
            f"👤 {o.get('Імʼя клієнта','—')}\n"
            f"📞 {o.get('Телефон','—')}\n"
            f"📦 {o.get('Доставка','—')}\n\n"
            f"🛒 {o.get('Склад замовлення','—')}\n\n"
            f"💰 {o.get('Сума замовлення','—')} грн\n"
            f"✅ Виконано"
        )

        await m.answer(text)

# ================== ЗАПУСК ==================
if __name__ == "__main__":
    app = web.Application()

    app.router.add_post("/webhook/telegram", telegram_webhook)
    app.router.add_post("/webhook/mono", mono_webhook)

    app.on_startup.append(on_startup)

    web.run_app(app, host="0.0.0.0", port=int(os.getenv("PORT", "8080")))










