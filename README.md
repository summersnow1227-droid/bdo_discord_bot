# Discord Game & Utility Bot

本專案是一個整合多種功能的 Discord Bot，包含：
- 自動按 💩 模式
- 猜數字遊戲
- 英雄聯盟糾團系統（滿 5 人自動成團）
- 黑色沙漠活動查詢 / 夜晚時間 / 測試伺服器連結
- 內建 FastAPI Web Server 提供健康檢查

---

## 🛠️ 系統需求

- Python 3.10+
- Discord Bot Token
- 已啟用 Message Content Intent

---

## 📦 安裝方式

1. 建立並啟動虛擬環境（建議）

```bash
python -m venv venv
venv\Scripts\activate   # Windows
```
2.安裝依賴
```bash
pip install -r requirements.txt
```
3.設定環境變數

Bot 使用環境變數讀取 Token 和資訊，不會寫在程式內部。

Windows PowerShell
```PowerShell
setx BOT_TOKEN "你的 Bot Token"
setx GUILD_ID "你的伺服器 ID"
setx POOP_CHANNEL_IDS "啟用💩模式的頻道 ID，逗號分隔，如：12345,67890"
```

Linux / macOS
```bash
export BOT_TOKEN="你的 Bot Token"
export GUILD_ID="你的伺服器 ID"
export POOP_CHANNEL_IDS="12345,67890"
```

4.直接啟動：
```bash
python main.py
```
