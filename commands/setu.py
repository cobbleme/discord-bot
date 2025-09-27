import discord
from discord.ext import commands
from discord import app_commands
import aiohttp
import config

API_URL = "https://api.lolicon.app/setu/v2"

class Setu(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="setu",
        description="隨機獲取圖片 (0=普通, 1=R18)"
    )
    @app_commands.describe(r18="0=普通, 1=R18")
    async def setu(self, interaction: discord.Interaction, r18: int = 0):
        # 如果是 R18，檢查權限
        if r18 == 1:
            user_roles = [role.id for role in interaction.user.roles]
            if interaction.user.id != config.ADMIN_ID and not any(role in config.R18_ROLE_IDS for role in user_roles):
                await interaction.response.send_message(
                    "❌ 你沒有權限請求 R18 圖片（需管理員或 R18 角色）",
                    ephemeral=True
                )
                return

        # 請求 API
        async with aiohttp.ClientSession() as session:
            async with session.get(API_URL, params={"r18": r18}) as resp:
                try:
                    data = await resp.json()
                except Exception:
                    await interaction.response.send_message("⚠️ API 回傳非 JSON", ephemeral=True)
                    return

                if "data" not in data or len(data["data"]) == 0:
                    await interaction.response.send_message("沒有找到圖片。", ephemeral=True)
                    return

                img_info = data["data"][0]

                # 優先選取 HTTPS 圖片
                img_url = None
                for key in ["original", "regular", "medium", "small"]:
                    url = img_info.get("urls", {}).get(key, "")
                    if url.startswith("https://"):
                        img_url = url
                        break

                if not img_url:
                    await interaction.response.send_message("⚠️ 沒有可內嵌的圖片 URL", ephemeral=True)
                    return

                author = img_info.get("author", "Unknown")

                # 建立 Embed，只顯示作者
                embed = discord.Embed(description=f"作者: {author}")
                embed.set_image(url=img_url)

                await interaction.response.send_message(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(Setu(bot))
