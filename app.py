# 匯入所有需要的工具
from flask import Flask, request, abort

from linebot.v3 import (
    WebhookParser
)
from linebot.v3.exceptions import (
    InvalidSignatureError
)
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    ReplyMessageRequest,
    TextMessage,
    QuickReply,
    QuickReplyItem,
    URIAction
)
from linebot.v3.webhooks import (
    MessageEvent,
    TextMessageContent
)

import os

app = Flask(__name__)

# --- 請確認這裡填入的是您自己的金鑰 ---
# 建議使用環境變數來儲存，但為了除錯先直接寫入
CHANNEL_ACCESS_TOKEN = '2blaTBBTTQgD5vINro0evqsfqIsD/0AuQgqBVDprdVHe7f5x2tQlsTygwB2ZdMXDb3g+iTcBczVclr4/beb6Cmm+WBJfURCsq0bfDHF3d12MZdQjteb5WXi9lZ/jIC7EdksecMiVv3QaJT3TQXD0WwdB04t89/1O/w1cDnyilFU='
CHANNEL_SECRET = 'e3743a3fbbc88522a78d672a6414138d'
# -----------------------------------------

# 使用變數來初始化
configuration = Configuration(access_token=CHANNEL_ACCESS_TOKEN)
parser = WebhookParser(CHANNEL_SECRET)

# ★★★★★ 除錯程式碼 ★★★★★
# 程式啟動時會印出金鑰，方便確認
print(f"--- 程式讀取到的 Access Token: [{configuration.access_token}]")
print(f"--- 程式讀取到的 Channel Secret: [{CHANNEL_SECRET}]")
# ★★★★★★★★★★★★★★★★★★★


# Webhook 的主要進入點
@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    try:
        # 使用 v3 的 parser 解析事件
        events = parser.parse(body, signature)
    except InvalidSignatureError:
        abort(400)

    # 迴圈處理每一個收到的事件
    for event in events:
        # 只處理文字訊息事件
        if isinstance(event, MessageEvent) and isinstance(event.message, TextMessageContent):
            # 直接呼叫處理函式
            handle_text_message(event)

    return 'OK'


# ★★★★★ 修改後的事件處理函式 ★★★★★
# 移除了 @line_handler.add(...) 裝飾器
def handle_text_message(event):
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        user_message = event.message.text

        # 判斷收到的文字是否為指定的觸發詞
        if user_message == "你想要做什麼樣的數學遊戲呢？":
            quick_reply_items = QuickReply(items=[
                QuickReplyItem(action=URIAction(label="質數", uri="https://shengfengweng.github.io/IsPrime/")),
                QuickReplyItem(action=URIAction(label="倍數", uri="https://shengfengweng.github.io/multiple/")),
                QuickReplyItem(action=URIAction(label="乘法", uri="https://shengfengweng.github.io/multiplication-pwa/")),
                QuickReplyItem(action=URIAction(label="單位轉換", uri="https://shengfengweng.github.io/unit-conversion-game/")),
                QuickReplyItem(action=URIAction(label="時間轉換", uri="https://shengfengweng.github.io/time-conversion-game/"))
            ])

            # 回覆帶有快速選單的訊息
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[
                        TextMessage(
                            text="請選擇其中一種數學練習：",
                            quick_reply=quick_reply_items
                        )
                    ]
                )
            )
        
        # 可以在這裡加入 else 來處理其他訊息，例如簡單的鸚鵡回覆
        # else:
        #     line_bot_api.reply_message(
        #         ReplyMessageRequest(
        #             reply_token=event.reply_token,
        #             messages=[TextMessage(text=f"收到訊息： {user_message}")]
        #         )
        #     )

# 程式的啟動點
if __name__ == "__main__":
    # 建議在部署時使用 Gunicorn 或 uWSGI
    # 開發階段使用 app.run() 即可
    app.run(port=5001)
