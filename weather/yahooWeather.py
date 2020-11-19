import requests, urllib
from bs4 import BeautifulSoup
import re, csv, pandas as pd

#全国＞都道府県のURLを取得（１度のみ）
target_url= "https://weather.yahoo.co.jp/weather/"
res       = requests.get(target_url)
soup      = BeautifulSoup(res.text, 'lxml')
elems     = soup.find_all("a")

with open("yahooChiku.csv", "w", encoding="utf-8", newline ="") as ychiku:
    writer = csv.writer(ychiku)
    for e in elems:
        chikuNumList = []
        if re.search(r'<a data-ylk="', str(e)):
            if re.search(r'"//weather.yahoo.co.jp/weather/jp/\d.*/"', str(e)):
                row = re.search(r'"//weather.yahoo.co.jp/weather/jp/\d.*/"', str(e)).group().strip('"')
                row = "https:" + row
                chikuNumList.append(row)
                writer.writerow(chikuNumList)


#都道府県＞詳細地区のURLを取得（１度のみ）
with open("yahooChiku.csv", "r", encoding="utf-8") as readChikuNum:
    reader     = csv.reader(readChikuNum)
    with open("shosaiChiku.csv", "w", encoding="cp932", newline="") as schiku:
        writer = csv.writer(schiku)
        column = ["地方", "市区町村", "URL"]
        writer.writerow(column)
        for target_url in reader:
            res           = requests.get(target_url[0])
            soup         = BeautifulSoup(res.text, 'lxml')
            chiku        = re.search(r".*の", str(soup.find("title").text)).group().strip("の")
            elems         = soup.find_all("a")
            chikuList, shosaiNumList = [], []
            chikuNameList = [chikuName.get_text() for chikuName in soup.find_all(class_= "name")]
            for e in elems:
                if re.search(r'data-ylk="slk:prefctr', str(e)):
                    if re.search(r'"https://.*html"', str(e)):
                        row = re.search(r'"https://.*html"', str(e)).group().strip('"')
                        chikuList.append(chiku)
                        shosaiNumList.append(row)

            for p, e, c in zip(chikuList, chikuNameList, shosaiNumList):
                writeList = [p, e, c]
                writer.writerow(writeList)

#詳細地区のRSSをURLを利用して取得
#詳細地区のURLを読み込み
df = pd.read_csv("shosaiChiku.csv", encoding="cp932")
with open("dataBase.csv", "w", encoding="cp932", newline="") as DBcsv:
    writer  = csv.writer(DBcsv)
    #ヘッダ書き込み
    columns = ["地方", "市区町村", "URL", "RSS"]
    writer.writerow(columns)

    #データ（地区名、市区町村、URL、RSS）を一行ずつ書きこみ
    for place, city, url in zip(df["地方"], df["市区町村"], df["URL"]):
        row    = [place, city, url]
        rssURL = "https://rss-weather.yahoo.co.jp/rss/days/"
        #URLから「数字.html」を取得＞「数字.rss」に成形
        url_pattern = re.search(r"\d*\.html", url).group()
        url_pattern = url_pattern.replace("html", "xml")
        rssURL = rssURL + url_pattern
        row.append(rssURL)
        writer.writerow(row)    


#天気情報WebページのHTMLタグから天気情報を抽出メソッド
def Parser(rssurl):
   with urllib.request.urlopen(rssurl) as res:
      xml  = res.read()
      soup = BeautifulSoup(xml, "html.parser")
      for item in soup.find_all("item"):
         title       = item.find("title").string
         if title.find("[ PR ]") == -1:
            tenki.append(title)
            
#詳細地区URLから当日の降水確率を取得メソッド
def rainProbability(URL):
   res       = requests.get(URL)
   soup      = BeautifulSoup(res.text, 'lxml')
   rain_time = []
   for rt in soup.find_all(class_ = "time")[0].find_all("td"):
      tempList = re.findall(r"\d{1,2}", rt.text)
      rain_time.append(tempList[0]+"時~"+tempList[1]+"時")
   rain_probability = ["0%"if pb.text == "---" else pb.text for pb in soup.find_all(class_ = "precip")[0].find_all("td")]
   returnTextList = "降水確率\n"\
                         "{0:>7} | {4:>4}\n"\
                         "{1:>7} | {5:>4}\n"\
                         "{2:>7} | {6:>4}\n"\
                         "{3:>7} | {7:>4}".format(rain_time[0], rain_time[1], rain_time[2], rain_time[3],
              rain_probability[0].rjust(4, " "), rain_probability[1].rjust(4, " "), rain_probability[2].rjust(4, " "), rain_probability[3].rjust(4, " "))
   return returnTextList


#DB読み込み
print("どこの天気が知りたいですか？")
weatherDF = pd.read_csv("./database.csv", encoding="cp932")

#地方一覧の表示
chihouList = []
for chihou in weatherDF["地方"]:
   if not chihou in chihouList:
      chihouList.append(chihou)

###例外値チェックすること
while True:
   for i, chihou in enumerate(chihouList):
      print(chihou + "・・・" + str(i))
   chihouNum = int(input())
   print(chihouList[chihouNum] + "でよろしいですか？")
   decision =  input("Yes・・・9 / No・・・0" + "\n")
   if decision == "9":
      shikuList = weatherDF.query('地方 == \"' + chihouList[chihouNum] + '\"')["市区町村"].values.tolist()
      for i, sikuchou in enumerate(shikuList):
         print(sikuchou + "・・・" + str(i))
      shikuNum = int(input())
      print(shikuList[shikuNum] + "でよろしいですか？")
      decision =  input("Yes・・・9 / No・・・0" + "\n")
      if decision == "9":
         #indexが振られるため列名だけを指定しても要素取得不可＞リストにする
         targetDataDF = weatherDF.query('市区町村 == \"' + shikuList[shikuNum] + '\"')
         targetIndex = targetDataDF.index[0]
         rssurl = targetDataDF.at[targetIndex, "RSS"]
         targetURL = targetDataDF.at[targetIndex, "URL"]
         break
      
tenki = []
#line_notify_tokenには自身で登録したトークンを指定
line_notify_token = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
line_notify_api = 'https://notify-api.line.me/api/notify'
Parser(rssurl) # 天気予報サイトのHTMLタグから天気情報を抽出
rain = rainProbability(targetURL)#降水確率を取得


#メッセージ内容(見出しと降水確率)
message = tenki[0] + "\n" + rain
payload = {'message': "\n" + message}
headers = {'Authorization': 'Bearer ' + line_notify_token}
#lineにメッセージ送信
line_notify = requests.post(line_notify_api, data=payload, headers=headers)

#メッセージ内容(当日の天気予報のURL)
message = targetURL
payload = {'message': "\n" + message}
headers = {'Authorization': 'Bearer ' + line_notify_token}
#lineにメッセージ送信
line_notify = requests.post(line_notify_api, data=payload, headers=headers)
