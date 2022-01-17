import matplotlib.pyplot as plt
from Chapter_5 import Analyzer

# 시세 반환
mk = Analyzer.MarketDB()
df = mk.get_daily_price('NAVER', '2019-01-02')

# 20개 종가의 이동평균(중간 볼린저 밴드), 표준편차, 상단 볼린저 밴드, 하단 볼린저 밴드, %B, 중심 가격
df['MA20'] = df['close'].rolling(window=20).mean()
df['stddev'] = df['close'].rolling(window=20).std()
df['upper'] = df['MA20'] + (df['stddev'] * 2)
df['lower'] = df['MA20'] - (df['stddev'] * 2)
df['PB'] = (df['close'] - df['lower']) / (df['upper'] - df['lower'])
df['TP'] = (df['high'] + df['low'] + df['close']) / 3
# 긍정적 현금 흐름, 부정적 현금 흐름 계산 후 이를 바탕으로 현금 흐름 비율과 현금 흐름 지수 저장
df['PMF'] = 0
df['NMF'] = 0
for i in range(len(df.close) - 1):
    if df.TP.values[i] < df.TP.values[i + 1]:
        df.PMF.values[i + 1] = df.TP.values[i + 1] * df.volume.values[i + 1]
        df.NMF.values[i + 1] = 0
    else:
        df.NMF.values[i + 1] = df.TP.values[i + 1] * df.volume.values[i + 1]
        df.PMF.values[i + 1] = 0
df['MFR'] = df.PMF.rolling(window=10).sum() / df.NMF.rolling(window=10).sum()
df['MFI10'] = 100 - 100 / (1 + df['MFR'])
# NaN이 들어있는 앞 19개의 데이터 제외
df = df[19:]

# 볼린저 밴드 시각화
plt.figure(figsize=(9, 8))
plt.subplot(2, 1, 1)
plt.title('NAVER Bollinger Band (20 day, 2 std) - Trend Following')
plt.plot(df.index, df['close'], color='#0000ff', label='Close')
plt.plot(df.index, df['upper'], 'r--', label='Uppder band')
plt.plot(df.index, df['MA20'], 'k--', label='Moving average 20')
plt.plot(df.index, df['lower'], 'c--', label='Lower band')
plt.fill_between(df.index, df['upper'], df['lower'], color='0.9')
# 매수 매도시점 시각화. %B와 MFI10으로 매도 매수 결정
for i in range(len(df.close)):
    if df.PB.values[i] > 0.8 and df.MFI10.values[i] > 80:
        plt.plot(df.index.values[i], df.close.values[i], 'r^')
    elif df.PB.values[i] < 0.2 and df.MFI10.values[i] < 20:
        plt.plot(df.index.values[i], df.close.values[i], 'bv')
plt.legend(loc='best')

# %B, MFI10 시각화
plt.subplot(2, 1, 2)
plt.plot(df.index, df['PB'] * 100, color='b', label='%B x 100')
plt.plot(df.index, df['MFI10'], 'g--', label='MFI(10 days)')
plt.yticks([-20, 0, 20, 40, 60, 80, 100, 120])
# 매수 매도시점 시각화. %B와 MFI10으로 매도 매수 결정
for i in range(len(df.close)):
    if df.PB.values[i] > 0.8 and df.MFI10.values[i] > 80:
        plt.plot(df.index.values[i], 0, 'r^')
    elif df.PB.values[i] < 0.2 and df.MFI10.values[i] < 20:
        plt.plot(df.index.values[i], 0, 'bv')
plt.grid(True)
plt.legend(loc='best')
plt.show()