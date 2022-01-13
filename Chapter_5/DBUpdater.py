import pandas as pd
from bs4 import BeautifulSoup
import pymysql, calendar, json, requests
from datetime import datetime
from threading import Timer

class DBUpdater:
    def __init__(self):
        # 생성자: MariaDB 연결 및 종목코드 딕셔너리 생성

        # pymysql 라이브러리를 통해 데이터베이스 연결
        self.conn = pymysql.connect(host='localhost', user='root',
                                 password='password', db='INVESTAR', charset='utf8')
        
        # company_info 테이블과 daily_price 테이블 생성
        with self.conn.cursor() as curs:
            sql = """
            CREATE TABLE IF NOT EXISTS company_info(
                code VARCHAR(20),
                company VARCHAR(40),
                last_update DATE,
                PRIMARY KEY(CODE)
            );
            """
            curs.execute(sql)
            sql = """
            CREATE TABLE IF NOT EXISTS daily_price(
                code VARCHAR(20),
                date DATE,
                open BIGINT(20),
                high BIGINT(20),
                low BIGINT(20),
                close BIGINT(20),
                diff BIGINT(20),
                volume BIGINT(20),
                PRIMARY KEY(code, date)
            );
            """
            curs.execute(sql)

        # 변경 반영
        self.conn.commit()

        # codes 딕셔너리 생성
        self.codes = dict()


    def __del__(self):
        # 소멸자: MariaDB 연결 해제
        self.conn.close()

    def read_krx_code(self):
        # KRX로부터 상장법인목록 파일을 읽어와서 데이터프레임으로 반환

        # 상장법인목록.xls 파일 읽기
        url = 'http://kind.krx.co.kr/corpgeneral/corpList.do?method=download&searchType=13'
        krx = pd.read_html(url, header=0)[0]

        # 파일에서 종목코드와 회사명 칼럼만 남긴 후 두 칼럼명을 영문으로 변환 후 종목코드는 6자리 문자열로 저장
        krx = krx[['종목코드', '회사명']]
        krx = krx.rename(columns={'종목코드':'code', '회사명':'company'})
        krx.code = krx.code.map('{:06d}'.format)
        return krx

    def update_comp_info(self):
        # 종목코드를 company_info 테이블에 업데이트한 후 딕셔너리에 저장

        # company_info 테이블 읽기
        sql = "SELECT * FROM company_info"
        df = pd.read_sql(sql, self.conn)

        # 종목코드와 회사명으로 딕셔너리 초기화
        for idx in range(len(df)):
            self.codes[df['code'].values[idx]] = df['company'].values[idx]

        
        with self.conn.cursor() as curs:
            # DB의 최근 업데이트 날짜와 현재 날짜 호출
            sql = "SELECT max(last_update) FROM company_info"
            curs.execute(sql)
            rs = curs.fetchone()
            today = datetime.today().strftime('%Y-%m-%d')

            # DB 업데이트 날짜가 없거나 현재일보다 오래된 경우 상장법인목록 파일에서 데이터 업데이트
            if rs[0] == None or rs[0].strftime('%Y-%m-%d') < today:
                krx = self.read_krx_code()
                for idx in range(len(krx)):
                    code = krx.code.values[idx]
                    company = krx.company.values[idx]
                    sql = f"REPLACE INTO company_info(code, company, last_update) values('{code}', '{company}', '{today}')"
                    curs.execute(sql)
                    self.codes[code] = company
                    tmnow = datetime.now().strftime('%Y-%m-%d %H:%M')
                    print(f"[{tmnow}] {idx:04d} REPLACE INTO company_info VALUES({code}, {company}, {today})")
                self.conn.commit()
                print('')

    def read_naver(self, code, company, pages_to_fetch):
        # 네이버 금융에서 주식 시세를 읽어서 데이터프레임으로 반환
        try:
            url = f"http://finance.naver.com/item/sise_day.nhn?code={code}"
            html = BeautifulSoup(requests.get(url, headers={"user-agent": "Mozilla/5.0"}).text, "lxml")

            # 일별 시세의 마지막 페이지 탐색
            pgrr = html.find("td", class_="pgRR")
            if pgrr is None:
                return None
            s = str(pgrr.a["href"]).split('=')
            lastpage = s[-1]

            # 기존에 설정된 값과 위에서 얻은 마지막 페이지 수 중 작은 값 선택
            pages = min(int(lastpage), pages_to_fetch)

            df = pd.DataFrame()
            for page in range(1, pages + 1):
                # 일별 시세 페이지를 읽고 데이터프레임에 추가
                pg_url = '{}&page={}'.format(url, page)
                df = df.append(pd.read_html(requests.get(pg_url,
                    headers={'User-agent': 'Mozilla/5.0'}).text)[0])                                          
                tmnow = datetime.now().strftime('%Y-%m-%d %H:%M')
                print('[{}] {} ({}) : {:04d}/{:04d} pages are downloading...'.
                    format(tmnow, company, code, page, pages), end="\r")
                    
            # 칼럼명과 일자 형식, 빈 데이터 등을 가공
            df = df.rename(columns={'날짜':'date','종가':'close','전일비':'diff'
                ,'시가':'open','고가':'high','저가':'low','거래량':'volume'})
            df['date'] = df['date'].replace('.', '-')
            df = df.dropna()

            # DB에서 BIGINT로 지정된 칼럼들을 int 데이터형으로 변환 후 순서 변경
            df[['close', 'diff', 'open', 'high', 'low', 'volume']] = df[['close',
                'diff', 'open', 'high', 'low', 'volume']].astype(int)
            df = df[['date', 'open', 'high', 'low', 'close', 'diff', 'volume']]
        except Exception as e:
            print('Exception occured :', str(e))
            return None
        return df

    def replace_into_db(self, df, num, code, company):
        # 네이버 금융에서 읽어온 주식 시세를 DB에 REPLACE
        with self.conn.cursor() as curs:
            # 인수로 받은 데이터프레임을 튜플로 순회해 daily_price 테이블 업데이트
            for r in df.itertuples():
                sql = f"REPLACE INTO daily_price VALUES ('{code}', '{r.date}', '{r.open}', '{r.high}', '{r.low}', '{r.close}', '{r.diff}', '{r.volume}')"
                curs.execute(sql)
            self.conn.commit()
            print('[{}] #{:04d} {} ({}) : {} rows > REPLACE INTO daily_price [OK]'.
                format(datetime.now().strftime('%Y-%m-%d %H:%M'), num+1, company, code, len(df)))

    def update_daily_price(self, pages_to_fetch):
        # KRX 상장법인의 주식 시세를 네이버로부터 읽어서 DB에 업데이트

        # self.codes 딕셔너리에 저장된 모든 종목코드에 대해 순회해 데이터를 구하고 DB에 저장
        for idx, code in enumerate(self.codes):
            df = self.read_naver(code, self.codes[code], pages_to_fetch)
            if df is None:
                continue
            self.replace_into_db(df, idx, code, self.codes[code])

    def execute_daily(self):
        # 실행 즉시 및 매일 오후 다섯시에 daily_price 테이블 업데이트

        # 종목 코드 저장
        self.update_comp_info()

        # config.json을 열어 pages_to_fetch값을 얻고 파일이 없으면 새로 생성
        try:
            with open('config.json', 'r') as in_file:
                config = json.load(in_file)
                pages_to_fetch = config['pages_to_fetch']
        except FileNotFoundError:
            with open('config.json', 'w') as out_file:
                pages_to_fetch = 100
                config = {'pages_to_fetch': 1}
                json.dump(config, out_file)

        # 일별 시세 업데이트
        self.update_daily_price(pages_to_fetch)

        # 다음날 오후 5시까지의 차이 계산
        tmnow = datetime.now()
        lastday = calendar.monthrange(tmnow.year, tmnow.month)[1]
        if tmnow.month == 12 and tmnow.day == lastday:
            tmnext = tmnow.replace(year=tmnow.year+1, month=1, day=1, hour=17, minute=0, second=0)
        elif tmnow.day == lastday:
            tmnext = tmnow.replace(month=tmnow.month+1, day=1, hour=17, minute=0, second=0)
        else:
            tmnext = tmnow.replace(day=tmnow.day+1, hour=17, minute=0, second=0)
        tmdiff = tmnext - tmnow
        secs = tmdiff.seconds
        
        # 타이머 객체 생성
        t = Timer(secs, self.execute_daily)
        print("Waiting for next update({}) ... ".format(tmnext.strftime('%Y-%m-%d %H:%M')))
        t.start()

if __name__ == '__main__':
    try:
        dbu = DBUpdater()
        dbu.execute_daily()
    except Exception as ex:
        print(ex)
        a = input()