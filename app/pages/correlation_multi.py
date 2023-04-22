import dash
import dash_bootstrap_components as dbc
from dash import html
from dash import dcc, dash_table, ctx
import plotly.express as px
from dash.dependencies import Input, Output
import pandas as pd
from lib import utils, db, layout
import plotly.graph_objects as go

"""
Example of the register_page defaults
"""


from dash import html

import dash

dash.register_page(__name__)

# get data
list_symbols = ["a", "b", "c"]

eng = db.get_engine()

sql = """select distinct symbol from CANDLE_DATA;"""
df = pd.read_sql_query(sql, eng)
list_symbols = df["symbol"].to_list()

sql = """select distinct interval, DAYS_BACK_PLANNED from CALCULATED_CORRELATION;"""
df_correlation_intervals_days = pd.read_sql_query(sql, eng)


sql = """select distinct concat(VAR_TYPE, ' (', VAR_METHOD, ')') as var_method
from FINANCE_VAR
order by 1 asc;"""
df = pd.read_sql_query(sql, eng)
list_quantities = df["var_method"].to_list()
list_quantities = ["correlation"] + list_quantities

##


# the style arguments for the sidebar. We use position:fixed and a fixed width
SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "16rem",
    # "padding": "2rem 1rem",
    "background-color": "#f8f9fa",
}

# the styles for the main content position it to the right of the sidebar and
# add some padding.
CONTENT_STYLE = {
    # "margin-left": "2rem",
    # "margin-right": "2rem",
    # "padding": "2rem 1rem",
}

dd = dcc.Dropdown(
    list_symbols,
    [list_symbols[0], list_symbols[1]],
    multi=True,
    id="id-correlation-choose-symbols")

# the choice of days back is based on interval
val_interval = df_correlation_intervals_days.iloc[-1]["interval"]
list_possible_days_back = list(set(df_correlation_intervals_days[df_correlation_intervals_days["interval"] == val_interval]["DAYS_BACK_PLANNED"]))
ri_interval = dcc.RadioItems(
    list(set(df_correlation_intervals_days["interval"])),
    val_interval,
    id='id-correlation-interval',
    labelStyle={'display': 'inline-block', 'marginTop': '5px'}
)

ri_days_back = dcc.Dropdown(
    list_possible_days_back,
    list_possible_days_back[0],
    id='id-correlation-days-back',
    #labelStyle={'display': 'inline-block', 'marginTop': '5px'}
)


sidebar = html.Div(
    [
        html.H2("Filter"),
        html.Hr(),
        html.P(
            "Select symbols", className="lead"
        ),
        dd,
        html.Hr(),
        html.P(
            "Select interval", className="lead"
        ),
        ri_interval,
        html.Hr(),
        html.P(
            "Select number days for correlation calculation", className="lead"
        ),
        ri_days_back,
    ],
    style=SIDEBAR_STYLE,
)


content = html.Div(
    [
        html.Div(id="id-correlation-correlation"),
        html.Div(id="id-correlation-change"),
        
    ]
)


layout = dbc.Row(
    [
        dbc.Col(sidebar, width=2),
        dbc.Col(content, width=9),
    ],
    className="g-0",
)
