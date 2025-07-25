# 匯入所有需要的工具
import os
from dotenv import load_dotenv 

load_dotenv() #它會自動讀取 .env 檔案並設定環境變數
from urllib.parse import parse_qs

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
    URIAction,
    TemplateMessage,
    ImageCarouselTemplate,
    ImageCarouselColumn,
    PostbackAction
)
from linebot.v3.webhooks import (
    MessageEvent,
    TextMessageContent,
    PostbackEvent
)

app = Flask(__name__)

# 從環境變數讀取金鑰
CHANNEL_ACCESS_TOKEN = os.environ.get('CHANNEL_ACCESS_TOKEN')
CHANNEL_SECRET = os.environ.get('CHANNEL_SECRET')

# 使用變數來初始化
configuration = Configuration(access_token=CHANNEL_ACCESS_TOKEN)
parser = WebhookParser(CHANNEL_SECRET)

print(f"--- 程式讀取到的 Access Token: [{CHANNEL_ACCESS_TOKEN}]")
print(f"--- 程式讀取到的 Channel Secret: [{CHANNEL_SECRET}]")


# Webhook 的主要進入點
@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    try:
        events = parser.parse(body, signature)
    except InvalidSignatureError:
        abort(400)

    for event in events:
        # 如果事件是「文字訊息」，就交給 handle_text_message 處理
        if isinstance(event, MessageEvent) and isinstance(event.message, TextMessageContent):
            handle_text_message(event)
        # 【修正點】如果事件是「按鈕點擊」，就交給 handle_postback 處理
        elif isinstance(event, PostbackEvent):
            handle_postback(event)

    return 'OK'


# 處理文字訊息的函式
def handle_text_message(event):
    user_message = event.message.text
    reply_token = event.reply_token

    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)

        # 【修正點】if 和 elif 現在有正確的縮排，都在 with ApiClient 的範圍內
        # 判斷收到的文字是否為指定的觸發詞
        if user_message == "你想要做什麼樣的數學遊戲呢？":
            quick_reply_items = QuickReply(items=[
                QuickReplyItem(action=URIAction(label="質數", uri="https://shengfengweng.github.io/IsPrime/")),
                QuickReplyItem(action=URIAction(label="倍數", uri="https://shengfengweng.github.io/multiple/")),
                QuickReplyItem(action=URIAction(label="乘法", uri="https://shengfengweng.github.io/multiplication-pwa/")),
                QuickReplyItem(action=URIAction(label="單位轉換", uri="https://shengfengweng.github.io/unit-conversion-game/")),
                QuickReplyItem(action=URIAction(label="時間轉換", uri="https://shengfengweng.github.io/time-conversion-game/"))
            ])

            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=reply_token,
                    messages=[
                        TextMessage(
                            text="請選擇其中一種數學練習：",
                            quick_reply=quick_reply_items
                        )
                    ]
                )
            )
        
        elif user_message == "黃金師資介紹":
            image_carousel_template = ImageCarouselTemplate(columns=[
                ImageCarouselColumn(
                    image_url='https://i.postimg.cc/t4JJjND5/1.png',
                    action=PostbackAction(
                        label='課程時間',
                        display_text='Steve主任課程時間',
                        data='action=show_text&item=1'
                    )
                ),
                ImageCarouselColumn(
                    image_url='https://i.postimg.cc/VvHyBnMf/2.png',
                    action=PostbackAction(
                        label='課程時間',
                        display_text='翁主任課程時間',
                        data='action=show_text&item=2'
                    )
                ),
                ImageCarouselColumn(
                    image_url='https://i.postimg.cc/FKXMZ9fL/3.png',
                    action=PostbackAction(
                        label='課程時間',
                        display_text='Sara主任課程時間',
                        data='action=show_text&item=3'
                    )
                ),
                ImageCarouselColumn(
                    image_url='https://i.postimg.cc/ZRTXGVxY/4.png',
                    action=PostbackAction(
                        label='課程時間',
                        display_text='Lulu老師課程時間',
                        data='action=show_text&item=4'
                    )
                )
            ])
            
            template_message = TemplateMessage(
                alt_text='師資介紹輪播選單', 
                template=image_carousel_template
            )
            
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=reply_token,
                    messages=[template_message]
                )
            )
        
# 處理按鈕點擊的新函式
def handle_postback(event):
    reply_token = event.reply_token
    postback_data = event.postback.data

    parsed_data = parse_qs(postback_data)
    
    action_type = parsed_data.get('action', [None])[0]
    item_id = parsed_data.get('item', [None])[0]

    reply_text = ''

    if action_type == 'show_text':
        if item_id == '1':
            reply_text = 'Steve老師目前進修中，請洽詢專人諮詢遠距教學或錄影課程'
        elif item_id == '2':
            reply_text = '翁主任目前課程時間：週一、週三、週五'
        elif item_id == '3':
            reply_text = 'Sara主任目前課程時間：週二、週四'
        elif item_id == '4':
            reply_text = 'Lulu老師目前進修中，請洽詢專人諮詢遠距教學或錄影課程'
        else:
            reply_text = '收到了您的點擊，但這個選項沒有對應的內容。'

    if reply_text:
        with ApiClient(configuration) as api_client:
            line_bot_api = MessagingApi(api_client)
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=reply_token,
                    messages=[TextMessage(text=reply_text)]
                )
            )
        

# 程式的啟動點
if __name__ == "__main__":
    # 在部署時，建議使用 Gunicorn 或 uWSGI
    # 開發階段使用 app.run() 即可
    app.run(port=5001)