# 爬蟲相關套件
import requests
from requests_html import HTML
from bs4 import BeautifulSoup
# 計時器相關套件
import time
import datetime as dt

# ===== 參數 =====
URL = 'https://www.ptt.cc/bbs/TaichungBun/index.html' # 目標看板網址
KEYWORD = '今網' # 搜尋關鍵字
SLEEPTIME = 60 # 每輪搜尋休眠時間
# ===== 參數 =====
flog = False # 判斷是否已尋找到目標用的
t = dt.datetime # 顯示時間用的

def fetch(url):
    '傳入網址，向 PTT 回答已經滿 18 歲，回傳網頁內容'
    response = requests.get(url)
    response = requests.get(url, cookies={'over18':'1'})
    return response

def parse_article_entries(doc):
    '傳入網頁內容，利用 requests_html 取出 div.r-ent 的元素內容並回傳'
    html = HTML( html = doc )
    post_entries = html.find('div.r-ent')
    return post_entries

def parse_article_meta(entry):
    '將 r-ent 元素的內容格式化成 dict 再回傳'
    meta = {
        'title': entry.find('div.title', first=True).text,
        'push': entry.find('div.nrec', first=True).text,
        'date': entry.find('div.date', first=True).text
    }
    try:
        # 正常的文章可以取得作者和連結
        meta['author'] = entry.find('div.author', first=True).text
        meta['link'] = entry.find('div.title > a', first=True).attrs['href']
    except AttributeError:
        # 被刪除的文章我們就不要了
        meta['author'] = '[Deleted]'
        meta['link'] = '[Deleted]'
    return meta


def print_meta(meta):
    '列印文章資料，看起來整齊一點'
    print('{push:<3s}{date:<5s}{author:<15s}{title:<40s}'\
        .format(push = meta['push'], date = meta['date'], author = meta['author'], title = meta['title']))


def lineNotifyMessage(meta):
    headers = {
        "Authorization": "Bearer " + "BtRhYQNRtjtWXLjlAoHIZMncfjyjhe1rF61U92st9RO", 
        "Content-Type" : "application/x-www-form-urlencoded"
    }
    
    payload = {'message':  ' https://www.ptt.cc' + meta['link'] }
    r = requests.post("https://notify-api.line.me/api/notify", headers = headers, params = payload)
    return r.status_code


# 程式本體
def ptt_alert(url, keyword):
    url = url # 團購版
    resp = fetch(url) # 取得網頁內容
    post_entries = parse_article_entries(resp.text) # 取得各列標題

    print('[%s] 連線成功，開始搜尋目標「%s」\n' %(t.now(), KEYWORD))

    for entry in post_entries:
        meta = parse_article_meta(entry)
        # 如果找到關鍵字，寄信通知我
        if keyword in meta['title'].lower() and not "截止" in meta['title']:
            print_meta(meta)
            # send_mail_for_me(meta)
            lineNotifyMessage(meta)
            print('[%s] 已發現監聽目標！通知信已寄出' %t.now())
            flog = True
            break
        # 沒找到的時候就正常顯示
        else:
            print_meta(meta)
    else:
        print('\n[%s] 搜尋完畢，並未發現目標。正在休眠 %s 毫秒並等待下一輪搜尋……' %(t.now(), SLEEPTIME))
    
# 主流程部分
def main():
    try:
        while True:
            print('[%s] 開始執行監聽' %t.now())

            ptt_alert(URL, KEYWORD) # 開始執行主流程

            if  flog:
                print('[%s] 已發現目標，停止監聽' %t.now())
                break
            else:
                time.sleep(SLEEPTIME)
                
    except Exception as e:
        print('[%s] 執行期間錯誤：%s' %(t.now(), e))
    
if __name__ == '__main__':
    main()
