# data/products.py

PRODUCTS = {
    "privileges": [
        {
            "id": 1, 
            "name": "🛡 Флай", 
            "price_game": 5000, 
            "price_stars": 125, 
            "description": "Привилегия Флай"
        },
        {
            "id": 2, 
            "name": "🛡 VIP", 
            "price_game": 10000, 
            "price_stars": 250, 
            "description": "Привилегия VIP"
        },
        {
            "id": 3, 
            "name": "🛡 Креатив", 
            "price_game": 35000, 
            "price_stars": 875, 
            "description": "Привилегия Креатив"
        },
        {
            "id": 4, 
            "name": "🛡 Админ", 
            "price_game": 66000, 
            "price_stars": 1650, 
            "description": "Привилегия Админ"
        },
        {
            "id": 5, 
            "name": "🛡 Основатель", 
            "price_game": 111000, 
            "price_stars": 2775, 
            "description": "Привилегия Основатель"
        },
        {
            "id": 6, 
            "name": "🛡 Оператор", 
            "price_game": None,
            "price_stars": None,
            "description": "🔥 Предзаказ на один вайп"
        },
    ],
    "rubins": [
        {
            "id": 7, 
            "name": "💎 200 Рубинов", 
            "price_game": 40000, 
            "price_stars": 1000, 
            "description": "Пакет из 200 рубинов"
        },
        {
            "id": 8, 
            "name": "💎 500 Рубинов", 
            "price_game": 60000, 
            "price_stars": 1500, 
            "description": "Пакет из 500 рубинов"
        },
        {
            "id": 9, 
            "name": "💎 1000 Рубинов", 
            "price_game": 100000, 
            "price_stars": 2500, 
            "description": "Пакет из 1000 рубинов"
        },
        {
            "id": 10, 
            "name": "💎 3000 Рубинов", 
            "price_game": 300000, 
            "price_stars": 7500, 
            "description": "Пакет из 3000 рубинов"
        },
    ],
    "pets": [
        {
            "id": 11, 
            "name": "🐝 Пчела", 
            "price_game": 3000, 
            "price_stars": 75, 
            "description": "Питомец Пчела"
        },
        {
            "id": 12, 
            "name": "🦊 Лиса", 
            "price_game": 7000, 
            "price_stars": 175, 
            "description": "Питомец Лиса"
        },
        {
            "id": 13, 
            "name": "🐼 Панда", 
            "price_game": 40000, 
            "price_stars": 1000, 
            "description": "Питомец Панда"
        },
        {
            "id": 14, 
            "name": "🦈 Аксолотль", 
            "price_game": 100000, 
            "price_stars": 2500, 
            "description": "Питомец Аксолотль"
        },
        {
            "id": 15, 
            "name": "🍪 Тихоня", 
            "price_game": 180000, 
            "price_stars": 4500, 
            "description": "Питомец Тихоня"
        },
    ],
    "packs": [
        {
            "id": 16, 
            "name": "🎉 Новичок (Акция)", 
            "price_game": 10999, 
            "price_stars": 275, 
            "description": "Подарочный пак для новичка"
        },
        {
            "id": 17, 
            "name": "💼 Бомж", 
            "price_game": 7800, 
            "price_stars": 195, 
            "description": "Подарочный пак Бомж (от 7 800💵)"
        },
        {
            "id": 18, 
            "name": "🎁 Стандарт", 
            "price_game": 25000, 
            "price_stars": 625, 
            "description": "Подарочный пак Стандарт (от 25 000💵)"
        },
        {
            "id": 19, 
            "name": "💎 VIP", 
            "price_game": 80000, 
            "price_stars": 2000, 
            "description": "Подарочный пак VIP (от 80 000💵)"
        },
        {
            "id": 20, 
            "name": "👑 MAX VIP", 
            "price_game": 100000, 
            "price_stars": 2500, 
            "description": "Подарочный пак MAX VIP (от 100 000💵)"
        },
    ],
    "certificates": [
        {
            "id": 21, 
            "name": "🎟 Сертификат на 5000💵", 
            "price_game": 5000, 
            "price_stars": 125, 
            "description": "Подарочный сертификат на 5000💵"
        },
        {
            "id": 22, 
            "name": "🎟 Сертификат на 10000💵", 
            "price_game": 10000, 
            "price_stars": 250, 
            "description": "Подарочный сертификат на 10000💵"
        },
    ]
}

# Информация о категориях для дополнительного описания
CATEGORY_INFO = {
    "rubins": "\n\n📩 *Паки большего объёма обсуждаются индивидуально.*",
    "packs": (
        "\n\n🎁 *Подарочные паки*\n"
        "Подойдут для:\n"
        "🌈 Новичка • ❤️ Любимого человека • 😎 Друга • 🎂 Дня рождения • ⚔ PvP-игрока • 🎄 Нового года\n\n"
        "После покупки вы получите:\n"
        "✅ Бесплатную консультацию\n"
        "✅ Шаблон поздравления\n"
        "✅ Промокод\n\n"
        "🎁 Получатель отправляет промокод и свой ник — подарок активируется.\n"
        "⏳ Промокод действует 3 дня.\n\n"
        "Также доступны подарочные сертификаты."
    )
}

def get_product_by_id(product_id: int):
    """Получить товар по ID"""
    for category in PRODUCTS.values():
        for product in category:
            if product["id"] == product_id:
                return product
    return None

def get_products_by_category(category: str):
    """Получить товары по категории"""
    return PRODUCTS.get(category, [])

def get_category_info(category: str) -> str:
    """Получить дополнительную информацию о категории"""
    return CATEGORY_INFO.get(category, "")