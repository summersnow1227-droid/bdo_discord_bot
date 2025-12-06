# cogs/bdo_dict.py

import discord
from discord.ext import commands

BDO_DICT_URL = "https://docs.google.com/spreadsheets/u/1/d/e/2PACX-1vS7Oy5AJBhqm5unk1YvQT9zw-7QF0VOXc-g1grRulydSGB9IIuJlfL1ufkeir-8YXvde8Cqhp9Gcjs0/pubhtml#gid=791448420"
BDO_DICT_SOURCE = "https://forum.gamer.com.tw/C.php?bsn=19017&snA=59877"


class BdoDictCog(commands.Cog):
    """
    黑色沙漠：配方大全指令

    指令：
    - !bdo_dict  → 顯示黑沙烹飪 / 工藝 / 煉金相關的整合配方表
    """

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="bdo_dict")
    async def bdo_dict(self, ctx: commands.Context):
        """顯示黑沙配方大全與資料來源"""
        embed = discord.Embed(
            title="📚 黑色沙漠配方大全",
            description="烹飪、煉金、工藝所有配方整合表",
            color=discord.Color.green(),
        )
        embed.add_field(
            name="配方總表",
            value=f"[點我查看]({BDO_DICT_URL})",
            inline=False
        )
        embed.add_field(
            name="資料來源",
            value=f"[PTT/巴哈姆特整理文]({BDO_DICT_SOURCE})",
            inline=False
        )
        embed.set_footer(text="更新速度依原作者為主，如有錯漏請依原帖為準。")

        await ctx.send(embed=embed)
