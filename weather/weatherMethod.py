import requests, urllib, re
from bs4 import BeautifulSoup

#天気情報WebページのHTMLタグから天気情報を抽出メソッド
def Parser(rssurl):
   with urllib.request.urlopen(rssurl) as res:
      xml  = res.read()
      soup = BeautifulSoup(xml, "html.parser")
      for item in soup.find_all("item"):
         title       = item.find("title").string
         if title.find("[ PR ]") == -1:
            return title

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
