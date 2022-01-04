from pandas_datareader import data as pdr
import yfinance as yf
import matplotlib.pyplot as plt

# yfinance ��Ű���� ���� ���� ���̳������� �����ϴ� �Ｚ���ڿ� ����ũ�μ���Ʈ �ֽ� �ü��� ���������������� �Է�
yf.pdr_override()

# �Ｚ���� �����������ӿ��� �ϰ� ������ ������ ����
sec = pdr.get_data_yahoo('005930.KS', start='2020-01-01')
sec_dpc = (sec['Close'] / sec['Close'].shift(1) - 1) * 100
sec_dpc.iloc[0] = 0
sec_dpc_cs = sec_dpc.cumsum()

# ����ũ�μ���Ʈ �����������ӿ��� �ϰ� ������ ������ ����
msft = pdr.get_data_yahoo('MSFT', start='2020-01-01')
msft_dpc = (msft['Close'] / msft['Close'].shift(1) - 1) * 100
msft_dpc.iloc[0] = 0
msft_dpc_cs = msft_dpc.cumsum()

# matplotlib ��Ű���� ���� �ֽ� ���ͷ� ���
plt.plot(sec.index, sec_dpc_cs, 'b', label='Samsung Electronics')
plt.plot(msft.index, msft_dpc_cs, 'r--', label='Microsoft')
plt.ylabel('Change %')
plt.grid(True)
plt.legend(loc='best')
plt.show()