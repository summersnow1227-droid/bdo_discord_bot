# cogs/bdo_night.py

import datetime
import discord
from discord.ext import commands

# UTC+8 時區（台灣 / 黑色沙漠常用）
UTC_PLUS_8 = datetime.timezone(datetime.timedelta(hours=8))

# 黑色沙漠固定夜晚開始時間（24h制，UTC+8 現實時間）
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
      顯示遊戲夜晚的現實時間（UTC+8），以及下一次夜晚倒數
    """

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="bdo_night")
    async def bdo_night(self, ctx: commands.Context):
        # 取得目前 UTC+8 時間
        now = datetime.datetime.now(tz=UTC_PLUS_8)
        today = now.date()

        night_datetimes = []
        for t in BDO_NIGHT_TIMES:
            hour, minute = map(int, t.split(":"))
            night_time = datetime.datetime.combine(
                today,
                datetime.time(hour, minute, tzinfo=UTC_PLUS_8)
            )
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
            next_night = datetime.datetime.combine(
                today + datetime.timedelta(days=1),
                datetime.time(hour, minute, tzinfo=UTC_PLUS_8)
            )

        # 計算倒數
        delta = next_night - now
        total_minutes = delta.seconds // 60
        hours = total_minutes // 60
        mins = total_minutes % 60

        lines = [
            "🌙 **黑色沙漠 - 遊戲夜晚時間（UTC+8）**",
            "",
            "🕒 **每天固定夜晚時間（現實時間）**",
        ]
        lines += [f"• {t}" for t in BDO_NIGHT_TIMES]

        lines.append("")
        lines.append(f"⏭ **下一次夜晚：** {next_night.strftime('%Y-%m-%d %H:%M')} (UTC+8)")
        lines.append(f"⏳ **剩餘時間：** {hours} 小時 {mins} 分鐘")

        await ctx.send("\n".join(lines))
