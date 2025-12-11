import asyncio
import discord
from discord.ext import commands

from fastapi import FastAPI
import uvicorn

from config import BOT_TOKEN
from cogs.poop_react import PoopReactCog
from cogs.guess_number import GuessNumberCog
from cogs.lol_group import LolGroupCog
from cogs.bdo_events import BdoEventsCog
from cogs.bdo_night import BdoNightCog
from cogs.bdo_test import BdoTestCog
from cogs.bdo_fish import BdoFishCog
from cogs.bdo_dict import BdoDictCog
from cogs.repeater import RepeaterCog

# ---------- Discord Bot 設定 ----------

intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True
intents.guilds = True

bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    print(f"✅ 已登入為：{bot.user} (ID: {bot.user.id})")
    print("功能：")
    print(" - !poop 啟動指定使用者自動 💩")
    print(" - !repeat / !repeat_stop 啟動指定使用者復讀訊息")
    print(" - !startnum / !endnum 猜數字遊戲")
    print(" - !lol / !lolend LoL 糾團（滿 5 人自動成團）")
    print(" - !bdo_event / !bdo_night / !bdo_test / !bdo_fish / !bdo_dict 黑色沙漠相關")
    print(" - !cmd 顯示可用指令說明")


@bot.command(name="cmd")
async def cmd_list(ctx: commands.Context):
    text = (
        "📜 **目前支援的指令：**\n"
        "```text\n"
        "[黑色沙漠 Black Desert]\n"
        "!bdo_event [數量]\n"
        "  抓取官網『有剩餘天數 / 長期』標記的活動列表。\n"
        "  例如：!bdo_event 5 → 顯示前 5 個活動（最多 20 個）\n"
        "\n"
        "!bdo_night\n"
        "  顯示遊戲夜晚時間與下一次夜晚倒數。\n"
        "\n"
        "!bdo_test\n"
        "  顯示黑色沙漠 Global Lab 測試伺服器公告連結。\n"
        "!bdo_fish\n"
        "  顯示 BDOLytics 黑色沙漠互動地圖（可查釣魚等）。\n"
        "!bdo_dict\n"
        "  顯示黑沙配方大全索引, 包含各類黑沙資訊。\n"
        "```\n"
        "```text\n"
        "[信奉無上的大便教主]\n"
        "!poop [分鐘] [@使用者...]\n"
        "  在指定頻道啟動自動按 💩 模式。\n"
        "  - 分鐘：1~3，沒填預設 1 分鐘\n"
        "  - @使用者：可以標記多位，被標記的人發話就會被按 💩\n"
        "  - 若沒標記任何人，則對下指令的人生效\n"
        "[指定復讀機]\n"
        "!repeat [分鐘] @使用者\n"
        "指定某位使用者成為復讀機，TA 說什麼我就複誦什麼。\n"
        "- 分鐘：1~5，沒填預設 1 分鐘\n"
        "- 只能指定 1 位對象\n"
        "- 在時間內該使用者每次發話都會被原樣複製\n"
        "- 重複使用 !repeat 會覆蓋舊設定並重新開始計時\n"
        "!repeat_stop\n"
        "手動停止復讀模式。\n"
        "- 輸入指令者 / 管理員皆可停止\n"
        "- 時間到也會自動停止\n"
        "\n"
        "[小遊戲]\n"
        "!startnum\n"
        "  在這個頻道開始一局 1~100 的猜數字遊戲，大家直接輸入數字來猜。\n"
        "\n"
        "!endnum\n"
        "  結束這個頻道目前進行中的猜數字遊戲（需管理訊息權限）。\n"
        "\n"
        "[英雄聯盟]\n"
        "!lol\n"
        "  在本頻道發起一則 League of Legends 糾團訊息，\n"
        "  發起人會自動加入，大家可以在該訊息按 ✅ 加入 / 取消。\n"
        "\n"
        "!lolend\n"
        "  結束目前頻道的 LoL 糾團（發起人或有管理權限者可用）。\n"
        "\n"
        "```\n"
        "💡 提醒：\n"
        "- !poop 只在設定於 POOP_CHANNEL_IDS 的頻道裡生效\n"
        "- 猜數字、LoL 糾團與 BDO 活動查詢，都是「每個頻道各自分開」互不干擾\n"
    )
    await ctx.send(text)


async def setup_bot():
    await bot.add_cog(PoopReactCog(bot))
    await bot.add_cog(GuessNumberCog(bot))
    await bot.add_cog(LolGroupCog(bot))
    await bot.add_cog(BdoEventsCog(bot))
    await bot.add_cog(BdoNightCog(bot))
    await bot.add_cog(BdoTestCog(bot))
    await bot.add_cog(BdoFishCog(bot))
    await bot.add_cog(BdoDictCog(bot))
    await bot.add_cog(RepeaterCog(bot))


# ---------- FastAPI Web Server 設定 ----------

app = FastAPI(title="Discord Bot Web Server")


@app.get("/")
async def root():
    """簡單健康檢查，用來確認 Bot Web Server 有在跑"""
    return {"status": "ok", "message": "Discord Bot 正常運行中"}


@app.get("/status")
async def status():
    """顯示一些簡單的 Bot 狀態"""
    if bot.user is None:
        return {"online": False, "guilds": 0}

    return {
        "online": True,
        "bot_name": str(bot.user),
        "bot_id": bot.user.id,
        "guilds": len(bot.guilds),
    }


async def start_discord_bot():
    """啟動 Discord Bot"""
    async with bot:
        await setup_bot()
        await bot.start(BOT_TOKEN)


async def start_web_server():
    """啟動 FastAPI Web Server"""
    config = uvicorn.Config(app, host="0.0.0.0", port=8000, log_level="info")
    server = uvicorn.Server(config)
    await server.serve()


async def main():
    # 同時啟動 Discord Bot + Web Server
    await asyncio.gather(
        start_discord_bot(),
        start_web_server(),
    )


if __name__ == "__main__":
    asyncio.run(main())
