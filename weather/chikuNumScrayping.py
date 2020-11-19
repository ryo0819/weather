import requests
from bs4 import BeautifulSoup
import re, csv

#初回のみ
#取得したページ
#http://www.tt.rim.or.jp/~ishato/tiri/code/code.htm
target_url = "http://www.tt.rim.or.jp/~ishato/tiri/code/kyusyu.htm"
#Requestsを使って、webから取得
res = requests.get(target_url)
res.encoding = res.apparent_encoding
#要素を抽出
soup = BeautifulSoup(res.text, 'lxml')
#print(soup)

#soup.find_allを用いてリンク先が「news.yahoo.co.jp/pickup」の項目を全て取得
elems = soup.find_all("tr")
with open("chikuNumber.csv", "a", encoding="cp932") as chikuNumber:
    writer = csv.writer(chikuNumber)
    for e in elems:
        row = []
        line = e.getText()
        line = line.replace("\xa0", "")
        row.append(line)
        writer.writerow(row)

import csv, re

writeChiku = []

with open("chikuNumber.csv") as number:
    reader = csv.reader(number)
    for row in reader:
        if not row:
            continue
        if re.search("(\d|\*)+", row[0]):
            #地区番号の取得
            chikuNumber = re.search("(\d|\*)+", row[0]).group()
            row = row[0].replace(chikuNumber, "")
            chikuKanji = re.search("[一-龥]+", row).group()
            row = row.replace("[一-龥]+", "")
            chikuHiragana = re.search("[ぁ-ん]+", row).group()
            writeChiku.append([chikuNumber, chikuKanji, chikuHiragana])
            
with open("ReChiku.csv", "w") as reWrite:
    writer = csv.writer(reWrite)
    writer.writerow(["地区番号", "地区名", "ふりがな"])
    writer.writerows(writeChiku)
