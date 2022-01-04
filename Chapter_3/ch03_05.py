from pandas_datareader import data as pdr
import yfinance as yf
import matplotlib.pyplot as plt

# yfinance ��Ű���� ���� ���� ���̳������� �����ϴ� KOSPI ���� ������ �ٿ�ε�
yf.pdr_override()

kospi = pdr.get_data_yahoo('^KS11', '2004-01-04')

window = 252 # ���� �Ⱓ, 1�� ������ �������� ���� 252�Ϸ� ����
peak = kospi['Adj Close'].rolling(window, min_periods=1).max() # ���� �Ⱓ �� �ְ�ġ
drawdown = kospi['Adj Close']/peak - 1.0 # �ְ�ġ ��� �϶���
max_dd = drawdown.rolling(window, min_periods=1).min() # ���� �Ⱓ �� ����ġ

# matplotlib ��Ű���� ���� MDD ���
plt.figure(figsize=(9, 7))
plt.subplot(211)
kospi['Close'].plot(label='KOSPI', title='KOSPI MDD', grid=True, legend=True)
plt.subplot(212)
drawdown.plot(c='blue', label='KOSPI DD', grid=True, legend=True)
max_dd.plot(c='red', label='KOSPI MDD', grid=True, legend=True)
plt.show()