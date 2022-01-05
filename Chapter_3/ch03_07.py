import pandas as pd
from pandas_datareader import data as pdr
import yfinance as yf
from scipy import stats
import matplotlib.pyplot as plt

# yfinance ��Ű���� ���� ���� ���̳������� �����ϴ� �ٿ����� ������ �ڽ��� ���� ������ �ٿ�ε�
yf.pdr_override()

dow = pdr.get_data_yahoo('^DJI', '2000-01-04')
kospi = pdr.get_data_yahoo('^KS11', '2000-01-04')

# �� ������ ���� Į������ �������������� ������ �� NaN ����
df = pd.DataFrame({'X': dow['Close'], 'Y': kospi['Close']})
df = df.fillna(method='bfill')
df = df.fillna(method='ffill')

# scipy ��Ű���� ���� �ٿ����� ���� X���� �ڽ��� ���� Y���� ����ȸ�� �� ��ü ����
regr = stats.linregress(df.X, df.Y)
regr_line = f'Y = {regr.slope:.2f} * X + {regr.intercept:.2f}'

# ȸ�� �м� �� �ð�ȭ
plt.figure(figsize=(7, 7))
plt.plot(df.X, df.Y, '.') # ������ ���
plt.plot(df.X, regr.slope * df.X + regr.intercept, 'r') # ȸ�ͼ� ���
plt.legend(['DOW x KOSPI', regr_line])
plt.title(f'DOW x KOSPI (R = {regr.rvalue:.2f})')
plt.xlabel('Dow Jones Industrial Average')
plt.ylabel('KOSPI')
plt.show()