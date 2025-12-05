import asyncio
from datetime import datetime, timedelta, timezone

import discord
from discord.ext import commands

from config import GUILD_ID, POOP_CHANNEL_IDS


class PoopReactCog(commands.Cog):
    """
    使用 !poop 觸發：
    - !poop                → 對自己生效 1 分鐘
    - !poop 2              → 對自己生效 2 分鐘（最多 3）
    - !poop 2 @A @B @C     → 對 A/B/C 生效 2 分鐘
    - !poop @A @B          → 對 A/B 生效 1 分鐘（沒給時間就預設 1）
    """

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        # channel_id -> {"user_ids": set[int], "until": datetime, "task": asyncio.Task}
        self.sessions: dict[int, dict] = {}

    # -------- 指令部分 --------
    @commands.command(name="poop")
    async def poop(self, ctx: commands.Context, *args: str):
        """啟動在本頻道的『指定對象自動按 💩』一段時間"""

        # 只允許在指定伺服器 / 頻道使用
        if not ctx.guild or ctx.guild.id != GUILD_ID:
            return

        if ctx.channel.id not in POOP_CHANNEL_IDS:
            await ctx.send("❌ 這個頻道沒有開放 💩 模式（請先把頻道 ID 加進 CHANNEL_IDS）。")
            return

        # 解析 minutes（從參數中抓到第一個純數字）
        minutes = 1  # 預設 1 分鐘
        for arg in args:
            if arg.isdigit():
                minutes = int(arg)
                break

        # 限制 1~3 分鐘
        if minutes < 1:
            minutes = 1
        if minutes > 3:
            minutes = 3

        # 目標使用者：如果有 @ 人，就用 mentions；沒有就只對自己
        if ctx.message.mentions:
            target_users = list(ctx.message.mentions)
        else:
            target_users = [ctx.author]

        user_ids = {u.id for u in target_users}
        channel_id = ctx.channel.id

        # 如果這個頻道已有 session，先把舊的 timer 停掉
        old_session = self.sessions.get(channel_id)
        if old_session and (task := old_session.get("task")):
            task.cancel()

        now = datetime.now(timezone.utc)
        end_time = now + timedelta(minutes=minutes)

        # 建立新的 session
        self.sessions[channel_id] = {
            "user_ids": user_ids,
            "until": end_time,
            "task": asyncio.create_task(self._poop_timer(channel_id, end_time, minutes)),
        }

        mentions_text = "、".join(u.mention for u in target_users)
        await ctx.send(
            f"💩 已啟用 **{minutes} 分鐘**！\n"
            f"在這段時間，只要 {mentions_text} 在這個頻道發話，大便教主就會為您獻上 💩 祝福。"
        )

    async def _poop_timer(self, channel_id: int, end_time: datetime, minutes: int):
        """到時間後自動關閉該頻道的 💩 session"""
        try:
            await asyncio.sleep(minutes * 60)
        except asyncio.CancelledError:
            # 被新一輪 !poop 取代，直接結束即可
            return

        session = self.sessions.get(channel_id)
        # 確認沒有被新的 session 蓋掉
        if session and session.get("until") == end_time:
            self.sessions.pop(channel_id, None)

    # -------- 監聽訊息部分 --------
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        # 不處理 Bot 自己
        if message.author.bot:
            return

        # 必須在伺服器文字頻道
        if not message.guild:
            return

        if message.guild.id != GUILD_ID:
            return

        if message.channel.id not in POOP_CHANNEL_IDS:
            return

        channel_id = message.channel.id
        session = self.sessions.get(channel_id)

        if not session:
            return

        # 檢查是否已過期
        now = datetime.now(timezone.utc)
        if now >= session["until"]:
            # 超時就清掉 session
            self.sessions.pop(channel_id, None)
            return

        # 若發話者在目標名單內 → 按 💩
        if message.author.id in session["user_ids"]:
            try:
                await message.add_reaction("💩")
            except discord.Forbidden:
                print(f"[PoopReact] 權限不足，無法在頻道 {channel_id} 加表情。")
            except discord.HTTPException as e:
                print(f"[PoopReact] 加表情失敗：{e}")