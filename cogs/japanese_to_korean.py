import discord
from discord import app_commands
from discord.ext import commands
import anthropic
import os
from dotenv import load_dotenv

load_dotenv()

class JapaneseToKoreanCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.client = anthropic.Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
        self.model = os.getenv('CLAUDE_MODEL')

    @app_commands.command(name="translate_jp_to_kr", description="日本語を韓国語に翻訳し、カタカナで発音を出力します。")
    @app_commands.describe(private="Whether to show the result only to you")
    async def translate(self, interaction: discord.Interaction, text: str, private: bool = False):
        translation = self.translate_japanese_to_korean(text)

        embed = discord.Embed(title="翻訳結果", color=discord.Color.blue())
        embed.add_field(name="原文", value=text, inline=False)
        embed.add_field(name="韓国語訳", value=translation["korean"], inline=False)
        embed.add_field(name="カタカナ読み", value=translation["katakana"], inline=False)

        await interaction.response.send_message(embed=embed, ephemeral=private)

    def translate_japanese_to_korean(self, text):
        response = self.client.messages.create(
            model=self.model,
            max_tokens=1024,
            messages=[
                {"role": "user", "content": f"""Translate the following Japanese text to Korean, including any internet slang or informal terms. Ensure that the translation faithfully captures any slang present and provides an equivalent Korean slang if available.
                Do not include any explanations, notes, or additional information. Only output the translations.
    
                Japanese: '{text}'
    
                Output format:
                Original Japanese text: {text}
                Korean translation: [Literal Korean translation, including any slang]
                Katakana: [Korean pronunciation in katakana]"""
                }
            ]
        )
    
        content = response.content[0].text
        korean, katakana = self.extract_korean_and_katakana(content)
        return {"korean": korean, "katakana": katakana}
    
    def extract_korean_and_katakana(self, content):
        korean_start = content.find("Korean translation:") + len("Korean translation:")
        katakana_start = content.find("Katakana:")
        
        korean = content[korean_start:katakana_start].strip()
        katakana = content[katakana_start + len("Katakana:"):].strip()

        return korean, katakana

async def setup(bot):
    await bot.add_cog(JapaneseToKoreanCog(bot))
