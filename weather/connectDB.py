import sqlite3, pandas as pd

#DBのtableからデータを取得するメソッド
def select_table():
    # 接続先となるDBの名前。'/home/user/database.db'といった表現方法も可能。
    dbname = 'weatherDatabase.db'

    # コネクタ作成。dbnameの名前を持つDBへ接続する。
    conn = sqlite3.connect(dbname)
    cur = conn.cursor()

    # ここから好きなだけクエリを打つ
    table = cur.execute('select * FROM yahooWeather;')
    data = table.fetchall()
        
    # 処理をコミット
    conn.commit()

    # 接続を切断
    conn.close()

    #select結果をリストからデータフレームにして返却
    data_list = []
    for i in data:
        data_list.append(list(i))
    return pd.DataFrame(data_list,
                        columns = ["rural", "municipality", "URL", "RSS"])

