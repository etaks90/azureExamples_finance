import dash
import dash_bootstrap_components as dbc
from dash import html
dash.register_page(__name__)
SIDEBAR_STYLE = {"position": "fixed","top": 0,"left": 0,"bottom": 0,"width": "16rem","background-color": "#f8f9fa",}
sidebar = html.Div(
    [
        html.H2("Filter"),
    ],
    style=SIDEBAR_STYLE,
)

content = html.Div([])

layout = dbc.Row(
    [
        dbc.Col(sidebar, width=2),
        dbc.Col(content, width=9),
    ],
    className="g-0",
)
