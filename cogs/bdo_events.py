# cogs/bdo_events.py

import asyncio
from typing import List, Dict

import discord
from discord.ext import commands

import requests
from bs4 import BeautifulSoup

# 黑色沙漠台服活動列表（boardType=3 = 活動）
BDO_EVENT_URL = "https://www.tw.playblackdesert.com/zh-TW/News/Notice?boardType=3"
BDO_BASE_URL = "https://www.tw.playblackdesert.com"


class BdoEventsCog(commands.Cog):
    """
    黑色沙漠活動查詢（只顯示「剩餘天數」或「長期」的活動）

    指令：
    - !bdo          → 顯示目前有「剩餘天數 / 長期」標記的活動（最多 10 筆）
    - !bdo 5        → 顯示前 5 筆（最多 10）
    """

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="bdo_event")
    async def bdo_events(self, ctx: commands.Context, limit: int = 10):
        """爬黑色沙漠官網，顯示剩餘天數 / 長期活動"""

        # 限制數量範圍
        if limit < 1:
            limit = 1
        if limit > 20:
            limit = 20

        msg = await ctx.send("⏳ 正在幫你查詢黑色沙漠活動中（剩餘天數 / 長期）…")

        try:
            # 把阻塞的 requests 丟到背景 thread，不要卡住 Discord 主線程
            events = await asyncio.to_thread(self._fetch_events_with_remaining, limit)
        except Exception as e:
            print(f"[BDO] 抓活動發生錯誤: {e}")
            await msg.edit(content="⚠ 抓取黑色沙漠活動時發生錯誤，可能是官網暫時無法連線或網頁結構改版。")
            return

        if not events:
            await msg.edit(content="😢 沒有抓到任何『有剩餘天數 / 長期』標記的活動。")
            return

        lines = ["📢 **黑色沙漠 - 目前有剩餘天數 / 長期的活動**"]
        for i, ev in enumerate(events, start=1):
            title = ev["title"]
            remain = ev.get("remaining", "")
            url = ev["url"]

            if remain:
                lines.append(f"{i}. [{title}]({url})  `({remain})`")
            else:
                lines.append(f"{i}. [{title}]({url})")

        await msg.edit(content="\n".join(lines))

    # -------- 內部：實際爬網頁邏輯 --------

    def _fetch_events_with_remaining(self, limit: int) -> List[Dict[str, str]]:
        """
        從活動列表頁面中，搜尋文字內同時滿足：
        - 含「活動」關鍵字
        - 並且含「剩下」或「長期」字樣

        然後切出：
        - title   = 活動名稱
        - remaining = 剩餘天數 / 長期
        - url     = 活動詳細頁連結
        """
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        }
        resp = requests.get(BDO_EVENT_URL, headers=headers, timeout=10)
        resp.raise_for_status()

        soup = BeautifulSoup(resp.text, "html.parser")

        events: List[Dict[str, str]] = []

        # 掃所有 <a>，找出同時有「活動」與「剩下 / 長期」的文字
        for a in soup.find_all("a", href=True):
            text = " ".join(a.stripped_strings)

            # 先確定是活動相關
            if "活動" not in text:
                continue

            # 再確定有剩餘天數或長期
            if ("剩下" not in text) and ("長期" not in text):
                continue

            # 切出標題與剩餘資訊
            title = text
            remaining = ""

            if "剩下" in text:
                idx = text.find("剩下")
                remaining = text[idx:].strip()    # e.g. "剩下 14 天"
                title = text[:idx].strip()
            elif "長期" in text:
                idx = text.find("長期")
                remaining = text[idx:].strip()    # e.g. "長期"
                title = text[:idx].strip()

            href = a["href"]
            # 補成完整 URL
            if href.startswith("http"):
                url = href
            else:
                if not href.startswith("/"):
                    href = "/" + href
                url = BDO_BASE_URL + href

            events.append(
                {
                    "title": title,
                    "remaining": remaining,
                    "url": url,
                }
            )

        # 以 title+url 去重，避免重複
        unique: List[Dict[str, str]] = []
        seen = set()
        for ev in events:
            key = (ev["title"], ev["url"])
            if key in seen:
                continue
            seen.add(key)
            unique.append(ev)

        return unique[:limit]
