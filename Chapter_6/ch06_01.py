import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from Chapter_5 import Analyzer

# Analyzer.py 모듈을 통해 4개 기업의 종가를 데이터프레임으로 추출
mk = Analyzer.MarketDB()
stocks = ['삼성전자', 'SK하이닉스', '현대자동차', 'NAVER']
df = pd.DataFrame()
for s in stocks:
    df[s] = mk.get_daily_price(s, '2021-09-01', '2021-01-14')['close']

# 일간 변동룰, 연간 수익률, 일간 리스크(일간 변동률의 공분산), 연간 리스크, 252는 미국의 1년 평균 개장일
daily_ret = df.pct_change()
annual_ret = daily_ret.mean() * 252
daily_cov = daily_ret.cov()
annual_cov = daily_cov * 252

# 포트폴리오 수익률, 리스크, 종목 비중 리스트
port_ret = []
port_risk = []
port_weights = []

# 몬테카를로 시뮬레이션으로 포트폴리오 20000개 생성
for _ in range(20000):
    # 4개 종목의 비중을 랜덤 생성
    weights = np.random.random(len(stocks))
    weights /= np.sum(weights)

    # 생성된 비중에 대한 수익률과 리스크
    returns = np.dot(weights, annual_ret)
    risk = np.sqrt(np.dot(weights.T, np.dot(annual_cov, weights)))

    # 포트폴리오 추가
    port_ret.append(returns)
    port_risk.append(risk)
    port_weights.append(weights)

# portfolio 딕셔너리에 4개 종목과 4개의 리턴 리스크 저장
portfolio = {'Returns':port_ret, 'Risk':port_risk}
for i, s, in enumerate(stocks):
    portfolio[s] = [weights[i] for weight in port_weights]

# 위 딕셔너리와 리턴 리스크를 데이터프레임에 저장
df = pd.DataFrame(portfolio)
df = df[['Returns', 'Risk'] + [s for s in stocks]]

# 효율적 투자선 출력
df.plot.scatter(x='Risk', y='Returns', figsize=(10, 7), grid=True)
plt.title('Efficient Frontier')
plt.xlabel('Risk')
plt.ylabel('Expected Returns')
plt.show()