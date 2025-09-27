import discord
from discord.ext import commands
from discord import app_commands
import aiohttp
import asyncio
import json
import os
import logging
import config

MEMORY_FILE = "memory.json"
LOG_FOLDER = "logs"

# ------------------- 日誌系統 -------------------
os.makedirs(LOG_FOLDER, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(f"{LOG_FOLDER}/bot.log", encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("BotLogger")

# ------------------- 內建函數 -------------------
def load_memory():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_memory(memory):
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(memory, f, ensure_ascii=False, indent=2)

# ------------------- Bot 初始化 -------------------
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# ------------------- GPT 聊天 Cog -------------------
class GPTChat(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # /chat 指令
    @app_commands.command(name="chat", description="與 AI 聊天")
    async def chat(self, interaction: discord.Interaction, message: str):
        await interaction.response.defer()
        logger.info(f"/chat 收到訊息: {message} 來自 {interaction.user}")
        reply = await self.generate_reply(interaction.user.id, message)
        await interaction.followup.send(reply)

    # /del 指令
    @app_commands.command(name="del", description="刪除你的聊天記憶")
    async def delete_memory(self, interaction: discord.Interaction):
        memory = load_memory()
        user_id = str(interaction.user.id)
        if user_id in memory:
            del memory[user_id]
            save_memory(memory)
            await interaction.response.send_message("✅ 已刪除你的聊天記憶")
            logger.info(f"使用者 {user_id} 刪除記憶")
        else:
            await interaction.response.send_message("⚠️ 你沒有任何記憶可刪除")

    # 生成 GPT 回覆
    async def generate_reply(self, user_id, user_msg):
        memory = load_memory()
        user_id = str(user_id)
        if user_id not in memory:
            memory[user_id] = []

        memory[user_id].append({"role": "user", "content": user_msg})

        # 讀取角色設定
        role_text = getattr(config, "AI_ROLE", "你是一個有禮貌的聊天助理。")

        payload = {
            "model": config.MODEL_NAME,  # ✅ 改成從 config 讀取
            "messages": [{"role": "system", "content": role_text}] + memory[user_id]
        }

        url = config.API_BASE_URL  # ✅ 改成直接使用 config 的 endpoint

        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=15)) as session:
                headers = {"Authorization": f"Bearer {config.API_KEY}"}
                async with session.post(url, json=payload, headers=headers) as resp:
                    logger.info(f"HTTP 狀態碼: {resp.status}, URL: {resp.url}")
                    data = await resp.json()
                    logger.info(f"GPT API 回傳原始資料: {data}")
                    reply = data.get("choices", [{}])[0].get("message", {}).get("content", "（沒有回覆）")
        except Exception as e:
            logger.error(f"GPT API 請求失敗: {e}")
            reply = "⚠️ GPT API 請求失敗"

        memory[user_id].append({"role": "assistant", "content": reply})
        save_memory(memory)
        logger.info(f"GPT 回覆給使用者 {user_id}: {reply[:50]}...")
        return reply

async def setup_gpt():
    await bot.add_cog(GPTChat(bot))
    logger.info("[GPTChat] 模組已載入，斜線指令: /chat, /del")

# ------------------- @機器人聊天事件 -------------------
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if bot.user.mentioned_in(message):
        user_msg = message.content.replace(f"<@{bot.user.id}>", "").strip()
        if not user_msg:
            await message.channel.send("請輸入想對我說的話")
            return

        cog = bot.get_cog("GPTChat")
        reply = await cog.generate_reply(message.author.id, user_msg)
        await message.channel.send(reply)
        logger.info(f"@bot 收到訊息: {user_msg} 來自 {message.author}")

    await bot.process_commands(message)

# ------------------- Bot Ready 事件 -------------------
@bot.event
async def on_ready():
    logger.info(f"🎉 Bot 已登入: {bot.user}")
    try:
        synced = await bot.tree.sync()
        logger.info(f"📌 已同步 {len(synced)} 條斜線指令")
    except Exception as e:
        logger.error(f"同步斜線指令失敗: {e}")

    # 列出已註冊的斜線指令
    logger.info("📝 已註冊的斜線指令：")
    for cmd in bot.tree.walk_commands():
        logger.info(f" - {cmd.name}")

# ------------------- 主函數 -------------------
async def main():
    # 載入其他 cog（例如 ping、setu）
    if os.path.exists("./commands"):
        for filename in os.listdir("./commands"):
            if filename.endswith(".py"):
                cog_path = f"commands.{filename[:-3]}"
                try:
                    await bot.load_extension(cog_path)
                    logger.info(f"✅ 已載入模組: {cog_path}")
                except Exception as e:
                    logger.error(f"❌ 載入模組失敗: {cog_path} -> {e}")

    await setup_gpt()
    await bot.start(config.TOKEN)

if __name__ == "__main__":
    asyncio.run(main())
