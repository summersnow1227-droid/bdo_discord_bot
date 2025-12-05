# cogs/bdo_night.py

import datetime
import discord
from discord.ext import commands

# 黑色沙漠固定夜晚開始時間（24h制，現實時間）
BDO_NIGHT_TIMES = [
    "03:40",
    "07:40",
    "11:40",
    "15:40",
    "19:40",
    "23:40",
]


class BdoNightCog(commands.Cog):
    """
    黑色沙漠 ➤ 遊戲夜晚時間查詢

    指令：
    - !bdo_night
      顯示遊戲夜晚的現實時間，以及下一次夜晚倒數
    """

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="bdo_night")
    async def bdo_night(self, ctx: commands.Context):
        now = datetime.datetime.now()
        today = now.date()

        night_datetimes = []
        for t in BDO_NIGHT_TIMES:
            hour, minute = map(int, t.split(":"))
            night_time = datetime.datetime.combine(today, datetime.time(hour, minute))
            night_datetimes.append(night_time)

        # 找出下一次夜晚
        next_night = None
        for nt in night_datetimes:
            if nt > now:
                next_night = nt
                break

        # 若今天已過最後一個夜晚 → 下一次是明天最早的
        if next_night is None:
            hour, minute = map(int, BDO_NIGHT_TIMES[0].split(":"))
            next_night = datetime.datetime.combine(today + datetime.timedelta(days=1), datetime.time(hour, minute))

        # 計算倒數
        delta = next_night - now
        hours = delta.seconds // 3600
        mins = (delta.seconds % 3600) // 60

        lines = [
            "🌙 **黑色沙漠 - 遊戲夜晚時間**",
            "",
            "🕒 **每天固定夜晚時間（現實時間）**",
        ]
        lines += [f"• {t}" for t in BDO_NIGHT_TIMES]

        lines.append("")
        lines.append(f"⏭ **下一次夜晚：** {next_night.strftime('%Y-%m-%d %H:%M')}")
        lines.append(f"⏳ **剩餘時間：** {hours} 小時 {mins} 分鐘")

        await ctx.send("\n".join(lines))
