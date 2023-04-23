import dash
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import load_figure_template
from flask import redirect, url_for
from dash import html


app = dash.Dash(__name__, use_pages=True, external_stylesheets=[dbc.themes.LUX]
                )
                
load_figure_template("LUX")


import dash_bootstrap_components as dbc

navbar = dbc.Container(
    dbc.NavbarSimple(
        children=[
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
        brand_href="/overview",
        id="id-navbar"
    ),
    fluid=True,
    style={"padding-left": "200px"}
)

## define layout landing page

SIDEBAR_STYLE = {
    "position": "fixed","top": 0
    ,"left": 0,"bottom": 0,"width": "16rem","background-color": "#f8f9fa",
    }
sidebar = html.Div(
    [
    ],
    style=SIDEBAR_STYLE,
)


layout_landing = dbc.Row(
    [
        dbc.Col(sidebar, width=2),
        dbc.Col("EXAMPLES", width=2),
    ],
    className="g-0",
)


dash.register_page("home", layout=layout_landing, path="/")

app.layout = dbc.Container(
    [
        navbar,
        dash.page_container,
    ],
    className="dbc",
    fluid=True,
)


if __name__ == "__main__":
    app.run_server(debug=True)
