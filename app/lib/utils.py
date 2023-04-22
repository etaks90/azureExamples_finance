from typing import List
from var import VaR
import numpy as np
import sys, json
from itertools import product
import datetime, logging, sqlite3, pyodbc
import yfinance as yf
from sqlalchemy import create_engine
import pandas as pd
from sqlalchemy.engine import URL

# https://stackoverflow.com/questions/26055556/writing-python-pandas-data-frame-to-sql-database-error
def create_engine_object(connection_type, my_host, my_db, my_odbc_driver):
    """Function to create engine.

    Args:
        connection_type (str): connection_type
        my_host (str): my_host

    Returns:
        create_engine (create_engine): create_engine
    """
    connection_url = URL.create(
    "mssql+pyodbc",
    #username=my_uid,
    #password=my_pwd,
    host=my_host,
    database=my_db,  # required; not an empty string
    query={"driver": my_odbc_driver},
)

    if connection_type.upper() == "SQLITE":
        return sqlite3.connect(connection_url)
    elif connection_type.upper() == "SQLSERVER":
        return create_engine(connection_url)


def exec_merge_statement(eng, table_name):
    if table_name == "CANDLE_DATA":
        sql = """merge
CANDLE_DATA as target
using
CANDLE_DATA_STG as source
on (source.Datetime = target.Datetime and source.symbol = target.symbol and source.interval = target.interval)
WHEN NOT MATCHED
THEN
INSERT
VALUES (source.[Datetime], source.[Open], source.[High], source.[Low], source.[Close], source.[Adj Close], source.[Volume], source.[symbol], source.[interval])
;"""
    elif table_name == "CANDLE_CHANGE":
        sql = """merge
CANDLE_CHANGE as target
using
CANDLE_CHANGE_STG as source
on (source.Datetime = target.Datetime and source.symbol = target.symbol and source.interval = target.interval)
WHEN NOT MATCHED
THEN
INSERT
VALUES (source.[Datetime], source.[Open__change], source.[High__change], source.[Low__change], source.[Close__change], source.[symbol], source.[interval])
;"""
    elif table_name == "CALCULATED_CORRELATION":
        sql = """merge
CALCULATED_CORRELATION as target
using
CALCULATED_CORRELATION_STG as source
on (source.Datetime = target.Datetime and source.symbol = target.symbol and source.interval = target.interval and source.DAYS_BACK_PLANNED = target.DAYS_BACK_PLANNED)
WHEN NOT MATCHED
THEN
INSERT
VALUES (source.[Datetime], source.[symbol], source.[corr_information], source.[correlation], source.[interval], source.[DAYS_BACK_PLANNED], source.[DAYS_BACK_REAL])
;"""
    elif table_name == "FINANCE_VAR":
        sql = """merge
FINANCE_VAR as target
using
FINANCE_VAR_STG as source
on (source.Datetime = target.Datetime and source.symbol = target.symbol and source.var_method = target.var_method and source.var_type = target.var_type and source.interval = target.interval and source.DAYS_BACK_PLANNED = target.DAYS_BACK_PLANNED)
WHEN NOT MATCHED
THEN
INSERT
VALUES (source.[Datetime], source.[VAR_TYPE], source.[VAR_METHOD], source.[CARDINALITY], source.[symbol], source.[VALUE], source.[interval], source.[DAYS_BACK_PLANNED], source.[DAYS_BACK_REAL])
;"""
    connection = eng.raw_connection()
    cursor = connection.cursor()
    cursor.execute(sql)
    cursor.commit()
    cursor.close()
    return 1

def str_to_datetime(input,format = '%Y-%m-%d'):
    return datetime.datetime.strptime(input, format)

def extract_until_end_date(symbol: str, start_date: datetime, final_end_date: datetime, interval: str, break_first_iteration: bool = False):
    if interval == "1m":
        jump_days_based_on_interval = 5
    elif interval == "1d":
        jump_days_based_on_interval = 1000
    


    end_date = start_date + datetime.timedelta(days=jump_days_based_on_interval)
    df_list = []
    ct = 0
    while True:
        if start_date.strftime("%Y-%m-%d")==final_end_date.strftime("%Y-%m-%d"):
            print("Escape 1")
            break
        ct = ct + 1
        if ct > 10:
            break
        str_start = start_date.strftime("%Y-%m-%d")
        str_end = (end_date - datetime.timedelta(minutes=1)).strftime("%Y-%m-%d")
        print("---------")
        print(str_start, str_end)
        df = yf.download(tickers = symbol, interval = interval,start=str_start, end=str_end)
        df_list.append(df)
        start_date = max(df.index)
        print(start_date)
        end_date_old = end_date
        end_date = start_date + datetime.timedelta(days=jump_days_based_on_interval)
        if end_date_old == end_date:
            print("Escape 2")
            break
        if break_first_iteration:
            break
    
    return pd.concat(df_list)

def write_to_db(eng, df, table_name):

    if not(eng.has_table(table_name)):
        if table_name == "CANDLE_DATA":
            sql = """CREATE TABLE CANDLE_DATA (
    [Datetime] datetime,
    [Open] float,
    [High] float,
    [Low] float,
    [Close] float,
    [Adj Close] float,
    [Volume] float,
    [symbol] varchar(20),
    [interval] varchar(20),
    PRIMARY KEY (Datetime, symbol, interval)
);"""
        elif table_name == "CANDLE_CHANGE":
            sql = """CREATE TABLE CANDLE_CHANGE (
    [Datetime] datetime,
    [Open__change] float,
    [High__change] float,
    [Low__change] float,
    [Close__change] float,
    [symbol] varchar(20),
    [interval] varchar(20),
    PRIMARY KEY (Datetime, symbol, interval)
);"""
        elif table_name == "CALCULATED_CORRELATION":
            sql = """CREATE TABLE CALCULATED_CORRELATION (
    [Datetime] datetime,
    [symbol] varchar(20),
    [corr_information] varchar(20),
    [correlation] float,
    [interval] varchar(20),
    [DAYS_BACK_PLANNED] int,
    [DAYS_BACK_REAL] int,
    PRIMARY KEY (Datetime, symbol, interval, DAYS_BACK_PLANNED)
);"""
        elif table_name == "FINANCE_VAR":
            sql = """CREATE TABLE FINANCE_VAR (
    [Datetime] datetime,
    [VAR_TYPE] varchar(20),
    [VAR_METHOD] varchar(20),
    [CARDINALITY] int,
    [symbol] varchar(1000),
    [VALUE] float,
    [interval] varchar(20),
    [DAYS_BACK_PLANNED] int,
    [DAYS_BACK_REAL] int,
    PRIMARY KEY (Datetime, symbol, var_method, var_type, interval, DAYS_BACK_PLANNED)
	);"""
        eng.execute(sql)

    if not(eng.has_table(table_name + "_STG")):
        if table_name == "CANDLE_DATA":
            sql = """CREATE TABLE CANDLE_DATA_STG (
    [Datetime] datetime,
    [Open] float,
    [High] float,
    [Low] float,
    [Close] float,
    [Adj Close] float,
    [Volume] float,
    [symbol] varchar(20),
    [interval] varchar(20),
    PRIMARY KEY (Datetime, symbol, interval)
);"""
        elif table_name == "CANDLE_CHANGE":
            sql = """CREATE TABLE CANDLE_CHANGE_STG (
    [Datetime] datetime,
    [Open__change] float,
    [High__change] float,
    [Low__change] float,
    [Close__change] float,
    [symbol] varchar(20),
    [interval] varchar(20),
    PRIMARY KEY (Datetime, symbol, interval)
);"""
        elif table_name == "CALCULATED_CORRELATION":
            sql = """CREATE TABLE CALCULATED_CORRELATION_STG (
    [Datetime] datetime,
    [symbol] varchar(20),
    [corr_information] varchar(20),
    [correlation] float,
    [interval] varchar(20),
    [DAYS_BACK_PLANNED] int,
    [DAYS_BACK_REAL] int,
    PRIMARY KEY (Datetime, symbol, interval, DAYS_BACK_PLANNED)
);"""
        elif table_name == "FINANCE_VAR":
            sql = """CREATE TABLE FINANCE_VAR_STG (
    [Datetime] datetime,
    [VAR_TYPE] varchar(20),
    [VAR_METHOD] varchar(20),
    [CARDINALITY] int,
    [symbol] varchar(1000),
    [VALUE] float,
    [interval] varchar(20),
    [DAYS_BACK_PLANNED] int,
    [DAYS_BACK_REAL] int,
    PRIMARY KEY (Datetime, symbol, var_method, var_type, interval, DAYS_BACK_PLANNED)
	);"""
        eng.execute(sql)
    

    df['Datetime'] = df.index
    #df = df.drop('Datetime', axis=1)
    

    # data quality for the volume is not that good, value can vary. Therefore we have to restrict the duplicates on "datetime" and "symbol", e.g.:
    # 2022-11-15 00:01:00.000	16617.484375	16617.484375	16617.484375	16617.484375	16617.484375	0	BTC-USD
    # 2022-11-15 00:01:00.000	16617.484375	16617.484375	16617.484375	16617.484375	16617.484375	6844416	BTC-USD



    if table_name in ("CANDLE_DATA","CANDLE_CHANGE"):
        df = df.drop_duplicates(subset= ["Datetime", "symbol", "interval"])
    if table_name in ("CALCULATED_CORRELATION"):
        df = df.drop_duplicates(subset= ["Datetime", "symbol", "interval", "DAYS_BACK_PLANNED"])
    elif table_name in ("FINANCE_VAR"):
        df = df.drop_duplicates(subset= ["Datetime", "symbol", "VAR_METHOD", "VAR_TYPE", "interval", "DAYS_BACK_PLANNED"])

    df.to_sql(name=table_name + "_STG",if_exists='replace',con = eng, index = False)

    exec_merge_statement(eng, table_name)


    return 1

def get_data_in_timeinterval(sql, eng):
    df = pd.read_sql_query(sql, eng)
    df['Datetime'] =  pd.to_datetime(df['Datetime'], format='%Y-%m-%d')

    return df

def calculate_change_for_df(df, symbol, interval):
    if interval == "1m":
        freq = "min"
    elif interval == "1d":
        freq = "B"
    df_full = pd.DataFrame({'Datetime': pd.date_range(min(df["Datetime"]), max(df["Datetime"]), freq = freq)})

    df = df_full.merge(df, on='Datetime', how='left')
    df.index = df["Datetime"]

    # we have to drop the non-float columns as otehrwise there is an error in teh change calculation
    #df = df.drop('Datetime', axis=1)
    #df = df.drop('symbol', axis=1)
    df = df[["Open","High","Low","Close"]]
    df_change = df.pct_change()

    df = df.join(df_change, rsuffix = "__change")
    df_change = df.copy()
    df_change = df_change[["Open__change","High__change","Low__change","Close__change"]]
    df_change = df_change.dropna(how='any',axis=0) 
    df_change = df_change.round(5)
    df_change["symbol"] = symbol

    return df_change

def calculate_correlation_for_df(df_1, df_2, symbol_1, symbol_2):

    df_1.index = df_1["Datetime"]
    df_2.index = df_2["Datetime"]

    df = df_1.join(df_2, lsuffix = "__" + symbol_1, rsuffix = "__" + symbol_2)

    corr_open = df['Open__change' +  "__" + symbol_1].corr(df['Open__change'+  "__" + symbol_2])

    return corr_open

# change this method to calculate multi-correlatons
# https://stats.stackexchange.com/questions/284861/do-the-determinants-of-covariance-and-correlation-matrices-and-or-their-inverses#:~:text=%22The%20determinant%20of%20the%20correlation,scores%20on%20the%20measures%20involved.
"""
import pandas as pd
from numpy import linalg

df = pd.DataFrame([(.2, .3, .1), (.0, .6, .2), (.6, .0, .1), (.2, .1, .1)], columns=['dogs', 'cats', 'dummy'])

                  
#df = pd.DataFrame([(.2, .3), (.0, .6), (.6, .0), (.2, .1)], columns=['dogs', 'cats'])
print(df.corr())
print(df["dogs"].corr(df["cats"]))
#print(df["dogs"].corr(df["dummy"]))

print(linalg.det(df.corr()))
"""

    

def unique_list_combinations(l):
    l = list(product(l, l))
    l = [sorted(e) for e in l]
    l = [list(x) for x in set(tuple(x) for x in l)]
    l = [e for e in l if not(e[0] == e[1])]

    return l

def calculate_change(dates, symbol, eng, interval, length_interval_in_daays):
    for d in dates:
        sql = "SELECT * FROM CANDLE_DATA WHERE symbol = '" + symbol + "' AND '"+d.strftime("%Y-%m-%d")+"' <= datetime and datetime <= '" + (d + datetime.timedelta(days = length_interval_in_daays)).strftime("%Y-%m-%d") + "' AND interval = '" + interval + "'"
        df__candle_data = get_data_in_timeinterval(sql, eng)
        print(sql)
        print(df__candle_data)
        if len(df__candle_data) == 0:
            continue
        df__candle_change = calculate_change_for_df(df__candle_data, symbol, interval)
        df__candle_change["interval"] = interval
        write_to_db(eng, df__candle_change, "CANDLE_CHANGE")

    return 1


def calculate_correlation(d1, symbols, eng, interval, days_back):
    d2 = d1 +datetime.timedelta(days = days_back)
    df__candle_change = {}
    for symbol in symbols:
        sql = "SELECT Datetime, Open__change FROM CANDLE_CHANGE WHERE symbol = '" + symbol + "' AND '"+d1.strftime("%Y-%m-%d")+"' <= datetime and datetime <= '" + d2.strftime("%Y-%m-%d") + "' AND interval = '" + interval + "'"
        df__candle_change[symbol] = get_data_in_timeinterval(sql, eng)
        if len(df__candle_change[symbol]) == 0:
            return 0

    dict__calculated_correlation = []
    corr_open = calculate_correlation_for_df(df__candle_change[symbols[0]], df__candle_change[symbols[1]], symbols[0], symbols[1])
    dummy = {}
    dummy["Datetime"] = d2
    dummy["symbol"] = "____".join(symbols)
    dummy["corr_information"] = "on_open"
    dummy["correlation"] = corr_open
    dummy["interval"] = interval
    dummy["DAYS_BACK_PLANNED"] = days_back
    dummy["DAYS_BACK_REAL"] = (min(max(df__candle_change[symbols[0]]["Datetime"]), max(df__candle_change[symbols[1]]["Datetime"])) - max(min(df__candle_change[symbols[0]]["Datetime"]), min(df__candle_change[symbols[1]]["Datetime"]))).days+1
    dict__calculated_correlation.append(dummy.copy())
    
    df__calculated_correlation = pd.json_normalize(dict__calculated_correlation)
    df__calculated_correlation.index = df__calculated_correlation["Datetime"]
    df__calculated_correlation = df__calculated_correlation.drop('Datetime', axis=1)
    write_to_db(eng, df__calculated_correlation, "CALCULATED_CORRELATION")

    return 1

def calculate_var(d1: datetime.datetime, symbols: list[str], eng: create_engine, interval: str, alpha: list[float], days_back: int) -> int:
    """Calculates the (conditional) Value-at-Risk based on the method from https://github.com/ibaris/VaR.
    
    Args:
        d1 (datetime.datetime): The end-date for which teh calculation is executed.
        symbols (list[str]): List of teh symbols in the portfolio.
        eng (create_engine): The engine connectiong to the db.
        interval (str): The interval of the timesteps.
        alpha (list[float]) Confidence interval.
        days_back (int): amount of days we go back in history.

    Returns:
        Returns 1 if data successfully written to db.

    Examples:
        >>> calculate_var(d1, symbols, eng, interval, alpha, p)
        1
    """
    df = None
    d2 = d1 +datetime.timedelta(days = days_back)
    for symbol in symbols:
        sql = "SELECT Datetime, Open__change FROM CANDLE_CHANGE WHERE symbol = '" + symbol + "' AND '"+d1.strftime("%Y-%m-%d")+"' <= datetime and datetime <= '" + d2.strftime("%Y-%m-%d") + "' AND interval = '" + interval + "'"
        df_dummy = get_data_in_timeinterval(sql, eng)
        if len(df_dummy) == 0:
            return 0
        df_dummy.index = df_dummy["Datetime"]
        df_dummy = df_dummy[["Open__change"]]
        if df is None:
            df = df_dummy
        else:
            df = df.join(df_dummy, rsuffix = "_")

    weights = np.ones(len(df.columns))/len(df.columns)

    var = VaR(df, weights)
    var = VaR(df, weights, alpha)
    var_calc = var.summary()
    var_json = json.loads(var_calc.to_json())
    j = []
    for e in var_json:
        for ee in var_json[e]:
            j_dummy = {}
            j_dummy["Datetime"] = d2.strftime("%Y-%m-%d")
            j_dummy["VAR_TYPE"] = e
            j_dummy["VAR_METHOD"] = ee
            j_dummy["CARDINALITY"] = len(weights)
            j_dummy["symbol"] = "##" + "##".join(symbols) + "##"
            j_dummy["VALUE"] = var_json[e][ee]
            j_dummy["interval"] = interval
            j_dummy["DAYS_BACK_PLANNED"] = days_back
            j_dummy["DAYS_BACK_REAL"] = (max(df.index) - min(df.index)).days
            j.append(j_dummy)

        
    df__var = pd.json_normalize(j)
    df__var.index = df__var["Datetime"]
    df__var = df__var.drop('Datetime', axis=1)
    write_to_db(eng, df__var, "FINANCE_VAR")

    return 1