import requests, urllib
from bs4 import BeautifulSoup


## Parser : 天気情報WebページのHTMLタグから天気情報を抽出してパースするメソッド ##########################
def Parser(rssurl):
   with urllib.request.urlopen(rssurl) as res:
      xml = res.read()
      soup = BeautifulSoup(xml, "html.parser")
      for item in soup.find_all("item"):
         title = item.find("title").string
         description = item.find("description").string
         if title.find("[ PR ]") == -1:
            tenki.append(title)
            detail.append(description)

tenki = []
detail = []
rssurl = "https://rss-weather.yahoo.co.jp/rss/days/1100.xml"

#line_notify_tokenには自身でlineに登録したトークンを指定
line_notify_token = 'xxxxxxxxxxxxx'
line_notify_api = 'https://notify-api.line.me/api/notify'
Parser(rssurl) # 天気予報サイトのHTMLタグから天気情報を抽出

#メッセージ内容
message = tenki[0]
payload = {'message': "\n" + message}
headers = {'Authorization': 'Bearer ' + line_notify_token}
#lineにメッセージ送信
line_notify = requests.post(line_notify_api, data=payload, headers=headers)

#ck_Weather(0, detail) # 天気情報とそれに応じた天気アイコンを出力(アイコン表示しないためコメントアウト)

message = URL
payload = {'message': message}
headers = {'Authorization': 'Bearer ' + line_notify_token}  #yahoo天気のURLを送信
line_notify = requests.post(line_notify_api, data=payload, headers=headers)
