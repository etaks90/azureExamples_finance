import dash
import dash_bootstrap_components as dbc
from dash import html
from dash import dcc, dash_table
import plotly.express as px
from dash.dependencies import Input, Output
import pandas as pd
from lib import utils
import plotly.graph_objects as go

def get_engine():
    return utils.create_engine_object("SQLSERVER", my_host = "localhost", my_db = "master", my_odbc_driver = "ODBC Driver 17 for SQL Server")

def get_df_table(eng):
    sql = """select min(datetime) min_date, max(datetime) max_date, count(*) cnt, symbol, interval, 'CANDLE' as TYPE, null as DAYS_BACK_PLANNED, null as OPTIONAL
	from CANDLE_DATA
	group by symbol, interval
	union all
	select min(datetime) min_date, max(datetime) max_date, count(*) cnt, symbol, interval, 'CHANGE' as TYPE, null as DAYS_BACK_PLANNED, null as OPTIONAL
	from CANDLE_CHANGE
	group by symbol, interval
	union all
	select min(datetime) min_date, max(datetime) max_date, count(*) cnt, symbol, interval, 'CORRELATION' as TYPE, DAYS_BACK_PLANNED, null as OPTIONAL
	from CALCULATED_CORRELATION
	group by symbol, interval, DAYS_BACK_PLANNED
	union all
	select min(datetime) min_date, max(datetime) max_date, count(*) cnt, symbol, interval, VAR_TYPE as TYPE, DAYS_BACK_PLANNED, VAR_METHOD AS OPTIONAL
	from FINANCE_VAR
	group by symbol, interval, DAYS_BACK_PLANNED, VAR_TYPE, VAR_METHOD
	;"""
    df_table = pd.read_sql_query(sql, eng)
    df_table["min_date"] = df_table['min_date'].dt.date
    df_table["max_date"] = df_table['max_date'].dt.date

    return df_table

def get_symbol_choices(eng):
    sql = """select distinct symbol from CANDLE_DATA;"""
    df = pd.read_sql_query(sql, eng)

    return df