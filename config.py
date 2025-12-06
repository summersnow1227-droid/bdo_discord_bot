# config.py
import os

# ----------------------------------------
# BOT TOKEN
# ----------------------------------------
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError("❌ BOT_TOKEN 未設定，請先設定環境變數 BOT_TOKEN")

# ----------------------------------------
# 伺服器 ID (Guild ID)
# ----------------------------------------
_guild = os.getenv("GUILD_ID")
if not _guild:
    raise RuntimeError("❌ GUILD_ID 未設定，請先設定環境變數 GUILD_ID\n"
                       "➡ 伺服器中右鍵 → 複製 ID")

try:
    GUILD_ID = int(_guild)
except ValueError:
    raise RuntimeError(f"❌ GUILD_ID 必須是純數字，你提供的是：{_guild}")

# ----------------------------------------
# 💩 POOP 模式啟用頻道 IDs
# 支援多個頻道以逗號分隔
# 例：POOP_CHANNEL_IDS="123,456,789"
# ----------------------------------------
_raw_channels = os.getenv("POOP_CHANNEL_IDS", "")
if not _raw_channels:
    POOP_CHANNEL_IDS = set()
else:
    try:
        POOP_CHANNEL_IDS = {
            int(cid.strip()) for cid in _raw_channels.split(",") if cid.strip()
        }
    except ValueError:
        raise RuntimeError(
            f"❌ POOP_CHANNEL_IDS 必須是純數字列表，例如：123,456，但你給的是：{_raw_channels}"
        )
