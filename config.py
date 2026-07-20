import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN не задан — создай .env по примеру .env.example")

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

BANNER_PATH = "sakura_banner.jpg"
BOT_USERNAME = "Sakura_Store67_bot"
ADMIN_IDS = [int(x) for x in os.getenv("ADMIN_IDS", "").split(",") if x.strip()]
MANAGER_IDS = []
MODER_IDS = []
SHOP_SETTINGS = {
    "name": "SAKURA STORE",
    "shop_open": True,
    "discount_3plus_percent": 5,
    "coins_rate": 10,
    "referral_percent": 2,
    "manager_username": "@Mik55554",
    "mortal_nickname": "MortalKhan95290",
}