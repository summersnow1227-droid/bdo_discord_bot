# cogs/bdo_fish.py

import discord
from discord.ext import commands


BDO_FISH_URL = "https://bdolytics.com/tw/TW/map"


class BdoFishCog(commands.Cog):
    """
    黑色沙漠釣魚／地圖導引

    指令：
    - !bdo_fish  → 顯示 BDOLytics 地圖連結
    """

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="bdo_fish")
    async def bdo_fish(self, ctx: commands.Context):
        """顯示 BDOLytics 地圖連結（可查釣魚 / 採集 / 怪物等資訊）"""
        await ctx.send(
            "🎣 **黑色沙漠釣魚 / 地圖查詢**\n"
            "BDOLytics 互動地圖：\n"
            f"<{BDO_FISH_URL}>"
        )
