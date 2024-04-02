MODEL = "claude-3-haiku-20240307"

MAX_TOKENS = 2048

TEMPERATURE = 0.0

SYSTEM_PROMPT = "This description is important. Be sure to follow the user's instructions. You must answer in Japanese."

SUMMARY_PROMPT = 'Extract only the important points from the given text. Add a brief explanation for each point. The output format should be an unordered list enclosed in triple quotes ("""), not (```). Use up to two levels of indentation. DO NOT include any unnecessary information. You must answer in Japanese.'

MAX_MESSAGE_LENGTH = 2000

WAIT_MESSAGE = "ちょっとまってにゃ！"

TOO_LONG_MESSAGE = "ちょっと長すぎるにゃ！"

URL_CONTENT_ERROR_MESSAGE = "指定されたURLのコンテンツを取得できませんでした。URLが正しいことを確認してください。"
