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

dash.register_page(__name__, name="01 - Overview")

# get data
list_symbols = ["a", "b", "c"]

eng = db.get_engine()

sql = """select distinct symbol from CANDLE_DATA;"""
df = pd.read_sql_query(sql, eng)
list_symbols = df["symbol"].to_list()

sql = """select distinct interval from CANDLE_DATA;"""
df = pd.read_sql_query(sql, eng)
list_intervals = df["interval"].to_list()

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

sidebar = html.Div(
    [
        html.H2("Filter"),
        html.Hr(),
        html.P(
            "Select symbols", className="lead"
        ),
        dcc.Dropdown(
            list_symbols,
            [list_symbols[0]],
            multi=True,
            id="id-overview-choose-symbols"),
        html.Hr(),
        html.P(
            "Select interval", className="lead"
        ),
        dcc.RadioItems(
            list_intervals,
            "1d",
            id='id-overview-select-interval',
            labelStyle={'display': 'inline-block', 'marginTop': '5px'}
        )

    ],
    style=SIDEBAR_STYLE,
)

content = html.Div(id="page-content", style=CONTENT_STYLE)

content = html.Div(
    [
        html.Div(id="id-main-div-table"),
        html.Div(id="id-main-div-change"),
        html.Div(id="id-main-div-overview"),
        # dcc.Graph(id='id-f1', figure=f1),
    ]
)


layout = dbc.Row(
    [
        dbc.Col(sidebar, width=2),
        dbc.Col(content, width=9),
    ],
    className="g-0",
)
