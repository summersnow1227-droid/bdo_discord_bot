# cogs/bdo_test.py

import discord
from discord.ext import commands

BDO_TEST_URL = "https://blackdesert.pearlabyss.com/GlobalLab/zh-TW/News/Notice"


class BdoTestCog(commands.Cog):
    """
    黑色沙漠測試伺服器公告查詢

    指令：
    - !bdo_test  → 顯示 Global Lab 測試伺服器公告網址
    """

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="bdo_test")
    async def bdo_test(self, ctx: commands.Context):
        """輸出黑色沙漠 Global Lab 測試公告網址"""
        await ctx.send(
            "🧪 **黑色沙漠測試伺服器公告頁面**\n"
            f"<{BDO_TEST_URL}>"
        )
