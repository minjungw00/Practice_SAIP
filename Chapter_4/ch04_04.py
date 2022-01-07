from bs4 import BeautifulSoup
from urllib import request as req
import pandas as pd

headers = ("user-agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36")
url = 'https://finance.naver.com/item/sise_day.naver?code=005930'

opener = req.build_opener()
opener.addheaders = [headers]
response = opener.open(url)
doc = BeautifulSoup(response, 'lxml')
last_page = doc.find('td', class_='pgRR').a['href'].split('=')[-1]

df = pd.DataFrame()
for page in range(1, int(last_page) + 1):
    page_url = '{}&page={}'.format(url, page)
    response = opener.open(page_url)
    df = df.append(pd.read_html(response, header=0)[0])
df = df.dropna()

print(df)