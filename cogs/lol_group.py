# cogs/lol_group.py

import discord
from discord.ext import commands


MAX_LOL_PLAYERS = 5  # ← 這裡設定最大人數（你要改 3、10 都可以）


class LolGroupCog(commands.Cog):
    """
    League of Legends 糾團系統
    - !lol      → 發起糾團，用 ✅ 加入 / 取消
    - !lolend   → 提前結束糾團（發起人或管理員）
    - 自動滿 5 人結束糾團
    """

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        # message_id -> {"channel_id": int, "owner_id": int, "players": set[int]}
        self.sessions: dict[int, dict] = {}

    @commands.command(name="lol")
    async def lol_start(self, ctx: commands.Context):
        for session in self.sessions.values():
            if session["channel_id"] == ctx.channel.id:
                await ctx.send("❗ 這個頻道已經有一團 LoL 在糾了，請先 !lolend")
                return

        owner_id = ctx.author.id
        players = {owner_id}
        content = self._build_lol_message(owner_id, players)
        msg = await ctx.send(content)

        # 加上反應
        try:
            await msg.add_reaction("✅")
        except:
            pass

        self.sessions[msg.id] = {
            "channel_id": ctx.channel.id,
            "owner_id": owner_id,
            "players": players,
        }

    @commands.command(name="lolend")
    async def lol_end(self, ctx: commands.Context):
        message_id, session = self._find_session(ctx.channel.id)
        if not session:
            await ctx.send("❌ 目前沒有糾團")
            return

        if ctx.author.id != session["owner_id"] and not ctx.author.guild_permissions.manage_messages:
            await ctx.send("🚫 只有發起人或管理員能結束糾團")
            return

        await self._finish_group(message_id, session)

    # ---- 反應事件 ----

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction: discord.Reaction, user: discord.abc.User):
        if user.bot or str(reaction.emoji) != "✅":
            return

        session = self.sessions.get(reaction.message.id)
        if not session:
            return

        session["players"].add(user.id)
        await self._update_lol_message(reaction.message.id)

        # 👇 NEW：滿團自動結束
        if len(session["players"]) >= MAX_LOL_PLAYERS:
            await self._finish_group(reaction.message.id, session, auto=True)

    @commands.Cog.listener()
    async def on_reaction_remove(self, reaction: discord.Reaction, user: discord.abc.User):
        if user.bot or str(reaction.emoji) != "✅":
            return

        session = self.sessions.get(reaction.message.id)
        if not session:
            return

        if user.id in session["players"]:
            session["players"].remove(user.id)

        await self._update_lol_message(reaction.message.id)

    # ---- 工具方法 ----

    def _find_session(self, channel_id: int):
        for mid, session in self.sessions.items():
            if session["channel_id"] == channel_id:
                return mid, session
        return None, None

    def _build_lol_message(self, owner_id: int, players: set[int]) -> str:
        members = "、".join(f"<@{uid}>" for uid in players)
        return (
            "🎮 **League of Legends 糾團中！**\n"
            f"發起人：<@{owner_id}>\n"
            f"目前人數：**{len(players)} / {MAX_LOL_PLAYERS}**\n"
            f"成員：{members}\n\n"
            "按下底下的 ✅ 加入 / 再按一次取消"
        )

    async def _update_lol_message(self, message_id: int):
        session = self.sessions.get(message_id)
        if not session:
            return

        channel = self.bot.get_channel(session["channel_id"])
        msg = await channel.fetch_message(message_id)

        new_content = self._build_lol_message(session["owner_id"], session["players"])
        await msg.edit(content=new_content)

    async def _finish_group(self, message_id: int, session: dict, auto: bool = False):
        """結束糾團（auto=True 表示滿團自動結束）"""
        players = session["players"]
        members = "、".join(f"<@{uid}>" for uid in players)

        # 刪除 session
        self.sessions.pop(message_id, None)

        channel = self.bot.get_channel(session["channel_id"])

        if auto:
            await channel.send(
                f"🎉 **LoL 糾團已滿 {MAX_LOL_PLAYERS} 人，團已成形！**\n"
                f"本次隊伍成員：{members}\n"
                "🔥 祝大家順利吃雞、不要再撞隊友啦！"
            )
        else:
            await channel.send(f"❌ 糾團已被結束。\n成員：{members}")
