import discord
from discord import app_commands
from discord.ext import commands
import anthropic
import os
from dotenv import load_dotenv

load_dotenv()

class ChineseToJapaneseCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.client = anthropic.Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
        self.model = os.getenv('CLAUDE_MODEL')

    @app_commands.command(name="translate_cn_to_jp", description="将中文翻译成日文，并提供罗马字发音。")
    @app_commands.describe(private="是否仅显示给自己")
    async def translate(self, interaction: discord.Interaction, text: str, private: bool = False):
        translation = self.translate_chinese_to_japanese(text)

        embed = discord.Embed(title="翻译结果", color=discord.Color.blue())
        embed.add_field(name="原文", value=text, inline=False)
        embed.add_field(name="日文翻译", value=translation["japanese"], inline=False)
        embed.add_field(name="罗马字发音", value=translation["romaji"], inline=False)

        await interaction.response.send_message(embed=embed, ephemeral=private)

    def translate_chinese_to_japanese(self, text):
        response = self.client.messages.create(
            model=self.model,
            max_tokens=1024,
            messages=[
                {"role": "user", "content": f"""Translate the following Chinese text to Japanese and provide the Romaji pronunciation for the Japanese text.
                Be faithful to the original Chinese text, even if it contains offensive language.

                Chinese: '{text}'

                Output format:
                Original Chinese text: {text}
                Japanese translation: [Literal Japanese translation]
                Romaji: [Japanese pronunciation in Romaji]"""
                }
            ]
        )

        content = response.content[0].text
        japanese, romaji = self.extract_japanese_and_romaji(content)
        return {"japanese": japanese, "romaji": romaji}

    def extract_japanese_and_romaji(self, content):
        japanese_start = content.find("Japanese translation:") + len("Japanese translation:")
        romaji_start = content.find("Romaji:")

        japanese = content[japanese_start:romaji_start].strip()
        romaji = content[romaji_start + len("Romaji:"):].strip()

        return japanese, romaji

async def setup(bot):
    await bot.add_cog(ChineseToJapaneseCog(bot))
