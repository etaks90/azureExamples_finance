import dash
import dash_bootstrap_components as dbc
from dash import html
from dash import dcc, dash_table
import plotly.express as px
from dash.dependencies import Input, Output
import pandas as pd
from lib import utils, db, layout
import plotly.graph_objects as go


SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "16rem",
    "padding": "2rem 1rem",
    #"background-color": "#040404",
}

def get_content_sytle():
    CONTENT_STYLE = {
        "margin-left": "18rem",
        "margin-right": "2rem",
        "padding": "2rem 1rem",
        #"background-color": "#32EF26",
    }

    return CONTENT_STYLE

def get_main_sytle():
    MAIN_STYLE = {
    #"background-color": "#f8f9fa",
    }

    return MAIN_STYLE

def get_sidebar():
    sidebar = html.Div(
    [
        html.H2("", className="display-4"),
        html.Hr(),
        html.H2("Sidebar", className="display-4"),
        html.Hr(),
        html.P(
            "Number of students per education level", className="lead"
        ),
        dbc.Nav(
            [
                dbc.NavLink("Home", href="/", active="exact"),
                dbc.NavLink("Page 1", href="/page-1", active="exact"),
                dbc.NavLink("Page 2", href="/page-2", active="exact"),
            ],
            vertical=True,
            pills=True,
        ),
    ],
    style=SIDEBAR_STYLE,
    	)
    
    return sidebar
    

def get_navbar():
    navbar = dbc.NavbarSimple(
    children=[
        #dbc.NavItem(dbc.NavLink("Overview", href="/Overview")),
        #dbc.NavItem(dbc.NavLink("Compare Symbls", href="/Compare-Symbols")),
        #dbc.NavItem(dbc.NavLink("Correlation", href="/Correlation")),

        dbc.DropdownMenu(
        [
            dbc.DropdownMenuItem(page["name"], href=page["path"])
            for page in dash.page_registry.values()
            if page["module"] != "pages.not_found_404"
        ],
        nav=True,
        label="More Pages",
    ),
    ],
    brand="Financial Evaluation",
    brand_href="/",
    #color="#040404",
    #dark=True,
    )

    return navbar
