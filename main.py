import discord
import os
import anthropic
import dotenv
import requests
import re
from bs4 import BeautifulSoup
from constants import (
    MODEL,
    MAX_TOKENS,
    TEMPERATURE,
    SYSTEM_PROMPT,
    SUMMARY_PROMPT,
    MAX_MESSAGE_LENGTH,
    WAIT_MESSAGE,
    TOO_LONG_MESSAGE,
    URL_CONTENT_ERROR_MESSAGE,
)


import chardet
dotenv.load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

anthropic_client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

allowed_channels = list(map(int, os.getenv("ALLOWED_CHANNELS", "").split(",")))


@client.event
async def on_ready():
    print(f"{client.user}としてログインしました")

def extract_backquote_text(response_text):
    backquote_content = response_text.split('```')
    if len(backquote_content) >= 3:
        return backquote_content[1]


@client.event
async def on_message(message):
    if message.author.bot or message.channel.id not in allowed_channels:
        return

    input_text = message.content
    url_pattern = r"https?://[^\s]+"
    urls = re.findall(url_pattern, input_text)

    if urls:
        for url in urls:
            temp_message = await message.reply(WAIT_MESSAGE)
            text = await fetch_url_content(url)
            if text is None:
                await temp_message.edit(content=URL_CONTENT_ERROR_MESSAGE)
                continue

            prompt = "```text\n" + text + "\n```\n\n" + SUMMARY_PROMPT + "\n"
            response_text = await get_anthropic_response(prompt)
            extracted_text = extract_backquote_text(response_text)
            if len(response_text) > MAX_MESSAGE_LENGTH:
                await temp_message.edit(content=TOO_LONG_MESSAGE)
            else:
                await temp_message.edit(content=extracted_text)
    else:
        temp_message = await message.reply(WAIT_MESSAGE)
        prompt = input_text
        response_text = await get_anthropic_response(prompt)
        if len(response_text) > MAX_MESSAGE_LENGTH:
            await temp_message.edit(content=TOO_LONG_MESSAGE)
        else:
            await temp_message.edit(content=response_text)

async def fetch_url_content(url):
    try:
        page_response = requests.get(url)
        page_content = BeautifulSoup(page_response.text, "html.parser")
        if page_content.body is None:
            return None
        return page_content.body.get_text(separator="\n", strip=True)
    except Exception as e:
        print(f"URLのコンテンツ取得エラー: {e}")
        return None

async def get_anthropic_response(prompt):
    response_text = ""
    with anthropic_client.messages.stream(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        temperature=TEMPERATURE,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": prompt}],
    ) as stream:
        for text in stream.text_stream:
            response_text += text
    return response_text

client.run(os.environ["DISCORD_BOT_TOKEN"])
