from bs4 import BeautifulSoup
from urllib import request as req
import pandas as pd

# 웹 브라우저 정보 및 웹 스크랩핑할 url
headers = ("user-agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36")
url = 'https://finance.naver.com/item/sise_day.naver?code=005930'

# request 라이브러리를 통해 url을 열 때마다 웹 브라우저 정보 제공
opener = req.build_opener()
opener.addheaders = [headers]
response = opener.open(url)

# BeautifulSoup 라이브러리로 페이지 파싱 후 해당 사이트의 맨 뒤 페이지 숫자 추출
doc = BeautifulSoup(response, 'lxml')
last_page = doc.find('td', class_='pgRR').a['href'].split('=')[-1]

# 데이터프레임으로 각 페이지 정보 저장
df = pd.DataFrame()
for page in range(1, int(last_page) + 1):
    page_url = '{}&page={}'.format(url, page)
    response = opener.open(page_url)
    df = df.append(pd.read_html(response, header=0)[0])
df = df.dropna()

print(df)