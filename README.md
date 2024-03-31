# Discord Bot with Anthropic API

注：本 README は Claude により生成しております。基本的に間違ってはいないですが、Rye により環境構築しておりますので、もし利用される際は Rye を導入することを推奨します。

このプロジェクトは、Anthropic API を使用して Discord 上で動作するボットを実装したものです。ユーザーからのメッセージに対して、Anthropic API を使用して適切な応答を生成し、返信します。

## 主な機能

- ユーザーからのメッセージを受信し、Anthropic API を使用して応答を生成
- URL が送信された場合、ページの内容をスクレイピングし、要点の抽出と解説を行う
- 生成された応答が 2000 文字を超える場合、長すぎるという旨のメッセージを返す

## 使用している主なライブラリ

- discord-py: Discord API とのインタラクションを行うためのライブラリ
- anthropic: Anthropic API を使用するためのライブラリ
- python-dotenv: 環境変数を管理するためのライブラリ
- requests: HTTP リクエストを送信するためのライブラリ
- beautifulsoup4: HTML のパースとスクレイピングを行うためのライブラリ

## セットアップ

1. リポジトリをクローンまたはダウンロードします。
2. 必要なライブラリをインストールします: `pip install -r requirements.lock`
3. `.env` ファイルを作成し、以下の環境変数を設定します:
   - `DISCORD_BOT_TOKEN`: Discord Bot のトークン
   - `ANTHROPIC_API_KEY`: Anthropic API の API キー
4. `main.py` を実行してボットを起動します。

## 使用方法

1. Discord サーバーにボットを招待します。
2. ボットにメッセージを送信すると、Anthropic API を使用して生成された応答が返ってきます。
3. URL を送信すると、ページの内容から要点の抽出と解説が行われます。

## 注意点

- Anthropic API の使用には、API キーが必要です。
- ボットの応答が 2000 文字を超える場合、長すぎるというメッセージが返されます。

## 貢献

プルリクエストや改善案は歓迎します。バグ報告や機能リクエストがある場合は、Issue を作成してください。

## ライセンス

このプロジェクトは MIT ライセンスの下で公開されています。詳細については、`LICENSE`ファイルを参照してください。

