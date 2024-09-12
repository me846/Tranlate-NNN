import discord
from discord import app_commands
from discord.ext import commands
import anthropic
import os
from dotenv import load_dotenv

load_dotenv()

class JapaneseToChineseCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.client = anthropic.Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
        self.model = os.getenv('CLAUDE_MODEL')

    @app_commands.command(name="translate_jp_to_cn", description="日本語を中国語に翻訳し、カタカナで発音を出力します。")
    @app_commands.describe(private="Whether to show the result only to you")
    async def translate(self, interaction: discord.Interaction, text: str, private: bool = False):
        translation = self.translate_japanese_to_chinese(text)

        embed = discord.Embed(title="翻訳結果", color=discord.Color.blue())
        embed.add_field(name="原文", value=text, inline=False)
        embed.add_field(name="中国語訳", value=translation["chinese"], inline=False)
        embed.add_field(name="カタカナ読み", value=translation["katakana"], inline=False)

        await interaction.response.send_message(embed=embed, ephemeral=private)

    def translate_japanese_to_chinese(self, text):
        response = self.client.messages.create(
            model=self.model,
            max_tokens=1024,
            messages=[
                {"role": "user", "content": f"""Translate the following Japanese text to Chinese and provide the Katakana pronunciation for the Chinese text.
                Be faithful to the original Japanese text, even if it contains offensive language.

                Japanese: '{text}'

                Output format:
                Original Japanese text: {text}
                Chinese translation: [Literal Chinese translation]
                Katakana: [Chinese pronunciation in Katakana]"""
                }
            ]
        )

        content = response.content[0].text
        chinese, katakana = self.extract_chinese_and_katakana(content)
        return {"chinese": chinese, "katakana": katakana}

    def extract_chinese_and_katakana(self, content):
        chinese_start = content.find("Chinese translation:") + len("Chinese translation:")
        katakana_start = content.find("Katakana:")

        chinese = content[chinese_start:katakana_start].strip()
        katakana = content[katakana_start + len("Katakana:"):].strip()

        return chinese, katakana

async def setup(bot):
    await bot.add_cog(JapaneseToChineseCog(bot))
