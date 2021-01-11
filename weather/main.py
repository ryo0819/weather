######LINEBot用インポート
from flask import Flask, request, abort
import os

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,QuickReplyButton, MessageAction, QuickReply
)

######

######自作メソッドファイル
import connectDB, weatherMethod
from richmenu import RichMenu, RichMenuManager
######

app = Flask(__name__)

#環境変数取得
YOUR_CHANNEL_ACCESS_TOKEN = os.environ["YOUR_CHANNEL_ACCESS_TOKEN"]
YOUR_CHANNEL_SECRET = os.environ["YOUR_CHANNEL_SECRET"]

line_bot_api = LineBotApi(YOUR_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(YOUR_CHANNEL_SECRET)

@app.route("/")
def hello_world():
    return "hello world!"

@app.route("/callback", methods=['POST'])
def callback():
    #変数宣言
    global rural
    global municipality
    
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    
    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    #天気情報を送信した後の処理
    if rural and municipality:
        rural = ""
        municipality = ""
        
    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    global rural
    global municipality
    global data_frame
    
    
    if not rural:
        #メッセージ内容を格納
        rural = event.message.text
        municipality_list = data_frame.query('rural == \"' + rural + '\"')["municipality"].values.tolist()
        items = [QuickReplyButton(action=MessageAction(label=f"{muni}", text=f"{muni}")) for muni in municipality_list]
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text = "現在の地方：" + rural + "\n市区町村を入力してください",
            quick_reply = QuickReply(items=items))
            
        )

    elif not municipality:
        #メッセージ内容を格納
        municipality = event.message.text
        # ruralとmunicipalityに一致した天気情報を送信
        targetDataDF = data_frame.query('municipality == \"' + municipality + '\"')
        targetIndex  = targetDataDF.index[0]
        targetURL    = targetDataDF.at[targetIndex, "URL"]
        targetRSS    = targetDataDF.at[targetIndex, "RSS"]
        # ruralとmunicipalityに一致した天気情報を送信
        line_bot_api.reply_message(
            event.reply_token,
            [TextSendMessage(text = weatherMethod.Parser(targetRSS) + "\n" + weatherMethod.rainProbability(targetURL)),
             TextSendMessage(text = targetURL)
            ]
        )

if __name__ == "__main__":

    #リッチメニューの登録
    # Setup RichMenu to register
    rmm = RichMenuManager(YOUR_CHANNEL_ACCESS_TOKEN)
    rm = RichMenu(name="Test menu", chat_bar_text="tap here")
    rm.add_area(0, 0, 1250, 843, "message", "天気情報")
    rm.add_area(1250, 0, 1250, 843, "uri", "乗り換え案内")
    
    res = rmm.register(rm, os.path.joim(os.path.dirname(__file__), "乗り換えメニュー画像.jpg"))
    richmenu_id = res["richMenuId"]
    print("Registered as " + richmenu_id)
    
    #DB読み込み
    data_frame = connectDB.select_table()
    #各データのリストを用意
    rural_list = []
    for i in data_frame:
        if not i[0] in rural_list:
            rural_list.append(i[0])

    #各変数設定
    rural = ""
    municipality = ""
    
    port = int(os.getenv("PORT"))
    app.run(host="0.0.0.0", port=port)
