# cogs/repeater.py

import asyncio
from datetime import datetime, timedelta, timezone

import discord
from discord.ext import commands


class RepeaterCog(commands.Cog):
    """
    指定某位使用者變成「復讀機」
    用法：
    - !repeat @使用者          → 預設 1 分鐘
    - !repeat 3 @使用者        → 3 分鐘
    - !repeat_stop             → 手動停止
    """

    def __init__(self, bot: commands.Bot):
        self.bot = bot

        # 每頻道一個復讀 session
        # channel_id -> {"user_id": int, "until": datetime, "task": asyncio.Task}
        self.repeat_sessions = {}

    # --------------------
    #    !repeat 指令
    # --------------------
    @commands.command(name="repeat")
    async def repeat(self, ctx: commands.Context, *args):
        """
        設定指定使用者成為復讀機，時間為 1~5 分鐘
        用法：
        !repeat 2 @人
        !repeat @人      → 預設 1 分鐘
        """

        if not ctx.guild:
            return

        # -------- 解析分鐘數 --------
        minutes = 1
        target_users = []

        for arg in args:
            if arg.isdigit():
                minutes = int(arg)
            # 非數字部分會交由 mentions 解決

        # 限制分鐘範圍
        if minutes < 1:
            minutes = 1
        if minutes > 5:
            minutes = 5

        # -------- 確定復讀對象 --------
        if ctx.message.mentions:
            target_users = ctx.message.mentions
        else:
            await ctx.send("❌ 請使用 `!repeat [分鐘] @使用者`。")
            return

        # 我們只處理第一個標記的人
        target = target_users[0]
        channel_id = ctx.channel.id

        # 若已有舊 session → 停掉
        old = self.repeat_sessions.get(channel_id)
        if old and old.get("task"):
            old["task"].cancel()

        now = datetime.now(timezone.utc)
        end_time = now + timedelta(minutes=minutes)

        # 啟動新 session
        task = asyncio.create_task(self._repeat_timer(channel_id, end_time))
        self.repeat_sessions[channel_id] = {
            "user_id": target.id,
            "until": end_time,
            "task": task
        }

        await ctx.send(
            f"🔁 復讀機啟動！時間：**{minutes} 分鐘**\n"
            f"📣 對象：{target.mention}\n"
            f"在這段期間，{target.mention} 說什麼，我就會複誦一次。"
        )

    # --------------------
    #  自動結束復讀 session
    # --------------------
    async def _repeat_timer(self, channel_id: int, end_time: datetime):
        try:
            now = datetime.now(timezone.utc)
            remain = (end_time - now).total_seconds()
            await asyncio.sleep(max(remain, 0))
        except asyncio.CancelledError:
            return

        session = self.repeat_sessions.get(channel_id)
        if session and session["until"] == end_time:
            self.repeat_sessions.pop(channel_id, None)

    # --------------------
    #  !repeat_stop 指令
    # --------------------
    @commands.command(name="repeat_stop")
    async def repeat_stop(self, ctx: commands.Context):
        """手動停止復讀機"""

        ch_id = ctx.channel.id
        session = self.repeat_sessions.get(ch_id)

        if not session:
            await ctx.send("❌ 目前沒有正在復讀的對象。")
            return

        task = session.get("task")
        if task:
            task.cancel()

        self.repeat_sessions.pop(ch_id, None)
        await ctx.send("🛑 復讀機已停止。")

    # --------------------
    #  監聽訊息：復讀邏輯
    # --------------------
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        # 不處理 Bot 自己
        if message.author.bot:
            return

        if not message.guild:
            return

        ch_id = message.channel.id
        session = self.repeat_sessions.get(ch_id)

        if not session:
            return

        # 檢查是否過期
        now = datetime.now(timezone.utc)
        if now >= session["until"]:
            self.repeat_sessions.pop(ch_id, None)
            return

        # 不是指定對象就不復讀
        if message.author.id != session["user_id"]:
            return

        # 不復讀指令（避免洗屏）—— 如需復讀指令可刪除此段
        if message.content.startswith("!"):
            return

        try:
            await message.channel.send(message.content)
        except discord.Forbidden:
            print(f"[Repeater] 沒權限發送訊息於 {ch_id}")
        except Exception as e:
            print(f"[Repeater] Unexpected error: {e}")
