import random
import discord
from discord.ext import commands


class GuessNumberCog(commands.Cog):
    """猜數字遊戲：!startnum / !endnum + 直接輸入數字"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        # channel_id -> {"number": int, "attempts": int, "active": bool}
        self.games: dict[int, dict] = {}

    @commands.command(name="startnum")
    async def startnum(self, ctx: commands.Context):
        """開始一局新的猜數字（1~100）"""
        ch_id = ctx.channel.id

        if self.games.get(ch_id, {}).get("active"):
            await ctx.send("❗ 這個頻道已經有一局在進行中了，先把它玩完吧！")
            return

        number = random.randint(1, 100)
        self.games[ch_id] = {
            "number": number,
            "attempts": 0,
            "active": True,
        }

        await ctx.send("🎮 猜數字開始！我想了一個 **1~100** 的整數，直接輸入數字來猜～")

    @commands.command(name="endnum")
    @commands.has_permissions(manage_messages=True)
    async def endnum(self, ctx: commands.Context):
        """強制結束目前這個頻道的猜數字"""
        ch_id = ctx.channel.id
        game = self.games.get(ch_id)

        if not game or not game.get("active"):
            await ctx.send("❌ 這個頻道目前沒有正在進行的猜數字遊戲。")
            return

        game["active"] = False
        await ctx.send(f"🛑 遊戲已結束！答案是 **{game['number']}**")

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        """
        只處理「正在遊戲中的頻道」中的「純數字訊息」。
        這裡 **不要** 呼叫 bot.process_commands，避免所有指令跑兩次。
        """
        if message.author.bot:
            return

        # 只處理文字頻道（避免 DM 或別的類型）
        if not isinstance(message.channel, discord.TextChannel):
            return

        ch_id = message.channel.id
        game = self.games.get(ch_id)

        if not game or not game.get("active"):
            return

        content = message.content.strip()
        if not content.isdigit():
            return

        guess = int(content)
        game["attempts"] += 1
        answer = game["number"]

        if guess < answer:
            await message.channel.send("🔼 太小了，再大一點！")
        elif guess > answer:
            await message.channel.send("🔽 太大了，再小一點！")
        else:
            game["active"] = False
            await message.channel.send(
                f"🎉 恭喜 <@{message.author.id}> 猜對了！答案就是 **{answer}** 🎯\n"
                f"一共猜了 **{game['attempts']} 次**！\n"
                "想再玩一局可以輸入 `!startnum` ～"
            )