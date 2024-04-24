import discord
import os
import anthropic
import dotenv
import requests
import re
import json
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

# def extract_json(response_text):
#     summary_pattern = r'<summary>(.*?)</summary>'
#     summary_match = re.search(summary_pattern, response_text, re.DOTALL)
#     if summary_match:
#         summary_json = summary_match.group(1).strip()
#         print(f"Extracted JSON: {summary_json}")  # デバッグ: 抽出されたJSONを表示
#         try:
#             return json.loads(summary_json)
#         except json.JSONDecodeError as e:
#             print(f"JSON decode error: {e}")  # デバッグ: JSONデコードエラーを表示
#             return None
#     else:
#         print("No summary found in the response")  # デバッグ: summaryが見つからない場合を表示
#         return None

def extract_json(response_text):
    point_pattern = r'<point>(.*?)</point>'
    point_matches = re.findall(point_pattern, response_text, re.DOTALL)
    if point_matches:
        summary_points = [match.strip() for match in point_matches]
        summary_json = json.dumps({"summary": summary_points})
        print(f"Extracted JSON: {summary_json}")  # デバッグ: 抽出されたJSONを表示
        try:
            return json.loads(summary_json)
        except json.JSONDecodeError as e:
            print(f"JSON decode error: {e}")  # デバッグ: JSONデコードエラーを表示
            return None
    else:
        print("No summary points found in the response")  # デバッグ: pointsが見つからない場合を表示
        return None

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

            prompt = "```text\n" + text + "\n```\n\n" + SUMMARY_PROMPT + "\nOutput the summary points inside <summary> tags.\n"
            response_text = await get_anthropic_response(prompt)
            print(f"Response text: {response_text}")  # デバッグ: レスポンステキストを表示
            result_json = extract_json(response_text)
            if result_json:
                summary_points = result_json.get("summary", [])
                formatted_points = "\n".join(f"- {point}" for point in summary_points)
                await temp_message.edit(content=formatted_points)
                print(f"要約ポイントの抽出に成功しました。\n要約ポイント: {formatted_points}")
            else:
                await temp_message.edit(content="要約ポイントの抽出に失敗しました。")
                print(f"要約ポイントの抽出に失敗しました。\nレスポンステキスト: {response_text}")
    else:
        temp_message = await message.reply(WAIT_MESSAGE)
        prompt = input_text
        response_text = await get_anthropic_response(prompt)
        if len(response_text) > MAX_MESSAGE_LENGTH:
            await temp_message.edit(content=TOO_LONG_MESSAGE)
            print(f"レスポンスが長すぎます。\nレスポンステキスト: {response_text}")
        else:
            await temp_message.edit(content=response_text)
            print(f"レスポンスを送信しました。\nレスポンステキスト: {response_text}")

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
