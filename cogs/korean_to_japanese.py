import discord
from discord import app_commands
from discord.ext import commands
import anthropic
import os
from dotenv import load_dotenv

load_dotenv()

class KoreanToJapaneseCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.client = anthropic.Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
        self.model = os.getenv('CLAUDE_MODEL')

    @app_commands.command(name="translate_kr_to_jp", description="한국어를 일본어로 번역하고 로마자로 발음을 출력합니다.")
    @app_commands.describe(private="결과를 개인적으로만 표시할지 여부")
    async def translate(self, interaction: discord.Interaction, text: str, private: bool = False):
        await interaction.response.defer(ephemeral=private)

        translation, token_usage = self.translate_korean_to_japanese(text)

        embed = discord.Embed(title="번역 결과", color=discord.Color.blue())
        embed.add_field(name="원문", value=text, inline=False)
        embed.add_field(name="일본어 번역", value=translation["japanese"], inline=False)
        embed.add_field(name="로마자 발음", value=translation["romaji"], inline=False)

        print(f"Input tokens: {token_usage['input_tokens']}, Output tokens: {token_usage['output_tokens']}")
        await interaction.followup.send(embed=embed)

    def translate_korean_to_japanese(self, text):
        response = self.client.messages.create(
            model=self.model,
            max_tokens=1024,
            messages=[
                {"role": "user", "content": f"""Translate the following Korean text to Japanese, including internet slang or informal terms. For example, use these translations for common internet slang:

    - 앙기모찌 → 気持ちいい
    - ㅋㅋㅋ → ｗｗｗ
    - 뇌절 → 頭おかしい

    If no direct equivalent exists, retain the Korean term. Do not include any explanations or notes.

    Korean: '{text}'

    Output format:
    Original Korean text: {text}
    Japanese translation: [Literal Japanese translation, including slang adaptations]
    Romaji: [Japanese pronunciation in Romaji]"""
                }
            ]
        )
        content = response.content[0].text
        japanese, romaji = self.extract_japanese_and_romaji(content)
        token_usage = {
            'input_tokens': response.usage.input_tokens,
            'output_tokens': response.usage.output_tokens
        }
        return {"japanese": japanese, "romaji": romaji}, token_usage

    def extract_japanese_and_romaji(self, content):
        japanese_start = content.find("Japanese translation:") + len("Japanese translation:")
        romaji_start = content.find("Romaji:")
        japanese = content[japanese_start:romaji_start].strip()
        romaji = content[romaji_start + len("Romaji:"):].strip()

        return japanese, romaji

async def setup(bot):
    await bot.add_cog(KoreanToJapaneseCog(bot))
