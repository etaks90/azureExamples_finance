import dash
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import load_figure_template


app = dash.Dash(__name__, use_pages=True, external_stylesheets=[dbc.themes.LUX]
                )
                
load_figure_template("LUX")


navbar = dbc.NavbarSimple(
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
    brand="- - - - Financial Evaluation",
    brand_href="/overview",
    id = "id-navbar"
)

dash.register_page("home", layout="We're home!", path="/")

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
