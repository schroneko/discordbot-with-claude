import discord
import os
import anthropic
import dotenv
import requests
from bs4 import BeautifulSoup

# .envファイルから環境変数を読み込む
dotenv.load_dotenv()

# Discordクライアントの初期設定
intents = discord.Intents.default()
# メッセージ内容にアクセスするためのインテントを有効化
intents.message_content = True
client = discord.Client(intents=intents)

# Anthropic APIクライアントの初期化
anthropic_client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])


@client.event
async def on_ready():
    # ログイン完了時に実行される
    print(f"We have logged in as {client.user}")


@client.event
async def on_message(message):
    # メッセージ受信時に実行される
    # メッセージ送信者がbot自身または他のbotの場合は処理をスキップ
    if message.author.bot:
        return

    temp_message = await message.reply("ちょっとまってにゃ！")
    input_text = message.content
    answer = await fetch_response(input_text)

    if len(answer) > 2000:
        await temp_message.edit(content="ちょっと長すぎるにゃ！")
    else:
        await temp_message.edit(content=answer)


async def fetch_response(input_text):
    # URLかどうかを判断
    if input_text.startswith("http://") or input_text.startswith("https://"):
        # ページの内容をスクレイピング
        page_response = requests.get(input_text)
        page_content = BeautifulSoup(page_response.text, "html.parser")
        text = page_content.body.get_text(separator="\n", strip=True)
        prompt = f"与えられた文章から重要な要点を抽出し、それに続けて適切な解説を加えてください。フォーマットは Markdown で出力しなさい。余計な前置き、後書きは不要で、内容から出力を始めなさい。出力言語は日本語で。\n\n```\n{text}\n"
    else:
        prompt = input_text

    # ストリーミングモードでAnthropic APIを使用
    response_text = ""
    with anthropic_client.messages.stream(
        # model="claude-3-opus-20240229",
        model="claude-3-haiku-20240307",
        max_tokens=1000,
        temperature=0.2,
        system="あなたは優秀なAIアシスタントです。",
        messages=[{"role": "user", "content": prompt}],
    ) as stream:
        for text in stream.text_stream:
            response_text += text

    return response_text


# Discord Botを起動
client.run(os.environ["DISCORD_BOT_TOKEN"])
