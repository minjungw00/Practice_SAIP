import pandas as pd
from urllib import request as req
from bs4 import BeautifulSoup
import mplfinance as mpf

# 웹 브라우저 정보와 스크래핑할 url
headers = ("user-agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36")
url = 'https://finance.naver.com/item/sise_day.naver?code=005930'

# request 라이브러리를 이용해 페이지마다 헤더 정보 입력
opener = req.build_opener()
opener.addheaders = [headers]

# BeautifulSoup 라이브러리를 통해 페이지 파싱 및 해당 사이트의 맨 마지막 페이지 추출
response = opener.open(url)
doc = BeautifulSoup(response, 'lxml')
last_page = doc.find('td', class_='pgRR').a['href'].split('=')[-1]

# 데이터프레임 객체로 각 페이지의 정보 추출
df = pd.DataFrame()
for page in range(1, int(last_page) + 1):
    page_url = '{}&page={}'.format(url, page)
    response = opener.open(page_url)
    df = df.append(pd.read_html(response, header=0)[0])

# 차트 출력을 위해 데이터프레임 가공
df = df.dropna()
df = df.iloc[0:50]
df = df.rename(columns={'날짜':'Date', '시가':'Open', '고가':'High', '저가':'Low', '종가':'Close', '거래량':'Volume'})
df = df.sort_values(by='Date')
df.index = pd.to_datetime(df.Date)
df = df[['Open', 'High', 'Low', 'Close', 'Volume']]

# 차트 시각화
kwargs = dict(title='Samsung chart', type='candle', mav=(2, 4, 6), volume=True, ylabel='ohlc candles')
s = mpf.make_mpf_style(marketcolors=mpf.make_marketcolors(up='r', down='b', inherit=True))
mpf.plot(df, **kwargs, style=s)