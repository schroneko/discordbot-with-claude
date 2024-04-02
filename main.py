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


dotenv.load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

anthropic_client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])


@client.event
async def on_ready():
    print(f"We have logged in as {client.user}")


@client.event
async def on_message(message):
    allowed_channels = [1223899218893082670, 1224538937536675913]
    if message.author.bot or message.channel.id not in allowed_channels:
        return

    temp_message = await message.reply(WAIT_MESSAGE)
    input_text = message.content
    answer = await fetch_response(input_text)
    print("Answer: ", answer)

    if len(answer) > MAX_MESSAGE_LENGTH:
        print("In case of too long message", len(answer), answer)
        await temp_message.edit(content=TOO_LONG_MESSAGE)
    else:
        await temp_message.edit(content=answer)


async def fetch_response(input_text):
    url_pattern = r'https?://[^\s]+'
    urls = re.findall(url_pattern, input_text)
    
    if urls:  # URLが一つでも見つかった場合
        first_url = urls[0]  # 最初のURLを取得
        page_response = requests.get(first_url)
        page_content = BeautifulSoup(page_response.text, "html.parser")
        if page_content.body is None:
            return URL_CONTENT_ERROR_MESSAGE
        text = page_content.body.get_text(separator="\n", strip=True)
        prompt = "```text\n" + text + "\n```\n\n" + SUMMARY_PROMPT
    else:
        prompt = input_text

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

    triple_quote_content = response_text.split('"""')
    if len(triple_quote_content) >= 3:
        return triple_quote_content[1]
    else:
        return response_text


client.run(os.environ["DISCORD_BOT_TOKEN"])
