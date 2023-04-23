# Code source: https://dash-bootstrap-components.opensource.faculty.ai/examples/simple-sidebar/
from decimal import Decimal
import dash, itertools
import numpy as np
import dash_bootstrap_components as dbc
from dash import html
from dash import dcc, dash_table, ctx
import plotly.express as px
from dash.dependencies import Input, Output
import pandas as pd
from lib import utils, db, layout
import plotly.graph_objects as go
from dash_bootstrap_templates import load_figure_template
import datetime


app = dash.Dash(__name__, use_pages=True  # , external_stylesheets=[dbc.themes.BOOTSTRAP]
                , external_stylesheets=[dbc.themes.LUX]
                )
                
app.config.suppress_callback_exceptions = True
suppress_callback_exceptions = True
load_figure_template("LUX")


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
        brand_href="/",
        id="id-navbar"
    ),
    fluid=True,
    style={"padding-left": "200px"}
)

eng = db.get_engine()
sql = """select * from CANDLE_DATA;"""
df_candle_data = pd.read_sql_query(sql, eng)

sql = """select * from CANDLE_CHANGE;"""
df_candle_change = pd.read_sql_query(sql, eng)

sql = """select * from CALCULATED_CORRELATION;"""
df_correlation = pd.read_sql_query(sql, eng)

sql = """select distinct interval from CANDLE_DATA;"""
df = pd.read_sql_query(sql, eng)
list_intervals = df["interval"].to_list()

sql = """select distinct interval, DAYS_BACK_PLANNED from CALCULATED_CORRELATION;"""
df_correlation_intervals_days = pd.read_sql_query(sql, eng)


# callbacks overview
@app.callback(
    Output("id-main-div-overview", "children"),
    Output("id-main-div-change", "children"),
    Output("id-main-div-table", "children"),
    [Input("id-overview-choose-symbols", "value"),
     Input("id-overview-select-interval", "value")]
)
def create_divs_for_overview(list_symbols, interval):
    print(list_symbols)
    fig = []
    fig_change = []
    eng = db.get_engine()
    for s in list_symbols:

        # this method is used to always load from db, this might be slow
        if 1 == 2:
            sql = "select * from CANDLE_DATA WHERE interval = '" + interval + "' and symbol = '" + s + "'"
            print(sql)
            df1 = pd.read_sql_query(sql, eng)

        if 1 == 1:
            df1 = df_candle_data[(df_candle_data["symbol"] == s) & (
                df_candle_data["interval"] == interval)]

        # plots for dynamic candles
        f = go.Figure(go.Candlestick(x=df1['Datetime'], open=df1['Open'],
                                     high=df1['High'], low=df1['Low'], close=df1['Close']), layout={
            'title': s, 'title_x': 0.5
        })

        f.update_layout(
            xaxis=dict(
                rangeslider=dict(
                    visible=False
                )))

        f = dcc.Graph(id='id-f1', figure=f)
        fig.append(f)

    # plots for change
    df = df_candle_change
    df = df[df["symbol"].isin(list_symbols)]
    list_max = []
    for s in list_symbols:
        list_max.append(max(df[(df["symbol"] == s) & (df["interval"] == interval)]["Datetime"]))
    x_max = min(list_max)
    if interval == "1d":
        x_min = x_max - pd.Timedelta(60, "d")
    elif interval == "1m":
        x_min = x_max - pd.Timedelta(1, "h")
    else:
        x_min = x_max - pd.Timedelta(60, "d")
    f_scatter_dummy = px.scatter(df, x="Datetime", y="Open__change", color = "symbol",labels={
                        "Datetime": "Date",
                        "Open__change": "change (%)",
                        "symbol": "symbol"
                    },).update_traces(mode="lines+markers")
    fig_change = go.Figure(data=f_scatter_dummy)
    y_min = min(df[(df["interval"] == interval) & (df["symbol"].isin(list_symbols)) & (df["Datetime"] >= x_min) & (df["Datetime"] <= x_max)]["Open__change"])
    y_max = max(df[(df["interval"] == interval)& (df["symbol"].isin(list_symbols)) & (df["Datetime"] >= x_min) & (df["Datetime"] <= x_max)]["Open__change"])
    print(y_min, y_max)
    fig_change.update_layout(xaxis_range=[x_min,x_max])
    fig_change.update_layout(yaxis_range=[y_min,y_max])
    fig_change.update_layout(title="Relative Change (%)")
    fig_change.update_layout(title_x=0.5)
    fig_change = dcc.Graph(id='id-f1', figure=fig_change)

    # create table
    df = df_candle_change
    table_list_symbols = []
    table_list_entries = []
    table_list_min_dates = []
    table_list_max_dates = []
    table_list_mean = []
    table_list_median = []
    table_list_std = []
    for s in list_symbols:
        for i in list_intervals:
            table_list_symbols.append(s + " (" + i +")")
            dummy = df[(df["symbol"] == s) & (df["interval"] == i)]["Datetime"]
            open__change = df[(df["symbol"] == s) & (df["interval"] == i)]["Open__change"]
            if len(dummy) == 0:
                min_sym = "N/A"
                max_sym = "N/A"
                dummy_mean = "N/A"
                dummy_median = "N/A"
                dummy_std = "N/A"
            else:   
                min_sym = min(dummy)
                max_sym = max(dummy)
                dummy_mean = '%.2E' % Decimal(np.nanmean(open__change))
                dummy_median = '%.2E' % Decimal(np.nanmedian(open__change))
                dummy_std = '%.2E' % Decimal(np.nanstd(open__change))
            
            table_list_entries.append(len(dummy))
            table_list_min_dates.append(min_sym)
            table_list_max_dates.append(max_sym)
            table_list_mean.append(dummy_mean)
            table_list_median.append(dummy_median)
            table_list_std.append(dummy_std)

    df = pd.DataFrame(
        {
            "symbol": table_list_symbols,
            "# Entries": table_list_entries,
            "Min-Date": table_list_min_dates,
            "Max-Date": table_list_max_dates,
            "Mean": table_list_mean,
            "Median": table_list_median,
            "STD": table_list_std,
        }
    )


    table = dbc.Table.from_dataframe(df, striped=True, bordered=True, hover=True)

    return fig, fig_change, table


# callbacks correlation

def get_change_scatters(df_in, interval, list_symbols):
    list_scatters = {}
    for s in list_symbols:
        df = df_in[(df_in["symbol"] == s) & (df_in["interval"] == interval)]
        list_scatters[s] = go.Scatter(x=df["Datetime"], y=df["Open__change"], name = s, mode='lines+markers', yaxis='y2')
    return list_scatters

def get_correlation_scatters(df_in, interval, days_back, list_symbols):
    """Function to read the correlations from table.
    
    Args:
        list_symbols (pair): Possible pair of combinations, e.g. [('BBBY', 'AAPL'), ('BBBY', 'GME')]
    """

    list_dfs = []
    list_scatters = {}
    for s in list_symbols:
        # We do not know the order, for ('BBBY', 'AAPL') it could be either "BBBY____AAPL" or "AAPL____BBBY", therefore lets try both
        n = "____".join(s)
        df = df_in[(df_in["symbol"] == n) & (df_in["interval"] == interval) & (df_in["DAYS_BACK_PLANNED"] == int(days_back))]
        if len(df) == 0:
            n = "____".join(s[::-1])
            df = df_in[(df_in["symbol"] == n) & (df_in["interval"] == interval) & (df_in["DAYS_BACK_PLANNED"] == int(days_back))]

        # remove first and last entry as these entries are 1 and this looks stupid in visualization
        df = df.iloc[1:-1]
        list_dfs.append(df.copy())

        list_scatters[n] = go.Scatter(x=df["Datetime"], y=df["correlation"], name = n, mode='lines+markers', yaxis='y1')

    return list_scatters, list_dfs

def get_pair_combinations(stuff):
    l = []
    for L in range(len(stuff) + 1):
        for subset in itertools.combinations(stuff, L):
            if len(subset) == 2:
                l.append(subset)
    return l


@app.callback(
    Output("id-correlation-correlation", "children"),
    Output("id-correlation-change", "children"),
    Output("id-correlation-days-back", "options"),
    Output("id-correlation-days-back", "value"),
    [Input("id-correlation-choose-symbols", "value"),
     Input("id-correlation-interval", "value"),
     Input("id-correlation-days-back", "value"),
     ]
)
def create_divs_for_correlation(list_symbols, interval, days_back):
    """Visualizes correlation. Correlation is always presented for a certain day, no matter what index. Only the possible values for
    the history taken into account varies based on interval."""
    # examples
    #list_symbols = ['BBBY', 'AAPL', '^GSPC', 'GME']
    symbol_pairs =  get_pair_combinations(list_symbols)

    # the choice of days back is based on interval
    # set default value if not included
    possible_days_back = list(set(df_correlation_intervals_days[df_correlation_intervals_days["interval"] == interval]["DAYS_BACK_PLANNED"]))
    if not(days_back in possible_days_back):
        days_back = possible_days_back[0]

    # calculate the correlations
    dict_correlation_scatters, list_dfs_correlation = get_correlation_scatters(df_correlation.copy(), interval, days_back, symbol_pairs)
    dict_change_scatters = get_change_scatters(df_candle_change.copy(), interval, list_symbols)
    

    # pairwise change + correlation
    fig_pairs = []
    ct = 0
    for k in dict_correlation_scatters:
        s = k.split("____")
        scatter_change_0 = dict_change_scatters[s[0]]
        scatter_change_1 = dict_change_scatters[s[1]]
        scatter_correlation = dict_correlation_scatters[k]
        print(k)
        layout_change = go.Layout(title='Comparison ' + " - ".join(s), xaxis=dict(title='Date'), yaxis=dict(title='correlation'), yaxis2=dict(title='change (%)', overlaying='y', side='right'))
        fig_change = go.Figure(data=[scatter_change_0, scatter_change_1, scatter_correlation], layout=layout_change)
        fig_change.update_layout(yaxis_range=[-1,1])
        #fig_change[k].update_layout(yaxis2_range=[-1,1])
        f = dcc.Graph(id='id-pairwise-' + str(ct), figure=fig_change)
        ct = ct + 1
        fig_pairs.append(f)

    # needed as fig_correlation_dummy does not update for some reason
    list_complete = list_symbols + list_symbols[::-1]
    combs = list(set(get_pair_combinations(list_complete)))
    combs = ["____".join(e) for e in combs]
    ddf_correlation = pd.concat(list_dfs_correlation)
    f_scatter_dummy = px.scatter(ddf_correlation, x="Datetime", y="correlation", color = "symbol",labels={
                        "Datetime": "Date",
                        "Open__change": "change (%)",
                        "symbol": "symbol"
                    },).update_traces(mode="lines+markers")
    fig_correlation = go.Figure(data=f_scatter_dummy)
    fig_correlation.update_layout(title="Relative Change (%)")
    fig_correlation.update_layout(title_x=0.5)
    fig_correlation = dcc.Graph(id='id-f1', figure=fig_correlation)

    # usually here should be fig_correlation_dummy, but somehow this plot does not change. So we use fig_correlation
    return fig_correlation, fig_pairs, possible_days_back, days_back


# find closest point to mouse position: https://dash.plotly.com/interactive-graphing
@app.callback(
    Output("id-correlation-pair-timeevolution", "children"),
    Output("id-correlation-pair-xy", "children"),
    Output("id-correlation-pair-days-back", "options"),
    Output("id-correlation-pair-days-back", "value"),
    [
     Input("id-correlation-pair-symbol-1", "value"),
     Input("id-correlation-pair-symbol-2", "value"),
     Input("id-correlation-pair-interval", "value"),
     Input("id-correlation-pair-days-back", "value"),
     Input('id-cor-pair-time', 'hoverData'),
     Input('id-correlation-pair-checkbox', 'value'),
     ]
)
def create_divs_for_correlation_pairs(sym1, sym2, interval, days_back, hover_data, fix_axis_corr):
    list_symbols = [sym1, sym2]
    print("1")
    
    x_end = None
    if not(hover_data is None):
        x_end = hover_data["points"][0]["x"]
        format = '%Y-%m-%d'
        x_end = datetime.datetime.strptime(x_end, format)
        x_start = x_end - datetime.timedelta(days=days_back)

     # the choice of days back is based on interval
    possible_days_back = list(set(df_correlation_intervals_days[df_correlation_intervals_days["interval"] == interval]["DAYS_BACK_PLANNED"]))
    if not(days_back in possible_days_back):
        days_back = possible_days_back[0]


    # correlation
    symbol_pairs =  get_pair_combinations(list_symbols)
    dict_correlation_scatters, dummy = get_correlation_scatters(df_correlation.copy(), interval, days_back, symbol_pairs)
    list_correlation_scatters = list(dict_correlation_scatters.values())
    layout_correlation = go.Layout(title='Correlation', yaxis=dict(title='Crude and Model'), yaxis2=dict(title='Moddel Difference', overlaying='y', side='right'))
    fig_correlation = go.Figure(data=list_correlation_scatters, layout=layout_correlation)
    fig_correlation.update_layout(yaxis_range=[-1.02, 1.02])
    fig_correlation.update_layout(grid_yside="right")
    fig_correlation.update_layout(hovermode='closest')

    fig_timeevolution = dcc.Graph(id='id-cor-pair-time', figure=fig_correlation)

    # correlation - x - y
    change_0 = df_candle_change[(df_candle_change["symbol"] == list_symbols[0]) & (df_candle_change["interval"] == interval)][["Datetime", "Open__change"]]
    change_0.index = change_0["Datetime"]
    change_1 = df_candle_change[(df_candle_change["symbol"] == list_symbols[1]) & (df_candle_change["interval"] == interval)][["Datetime", "Open__change"]]
    change_1.index = change_1["Datetime"]



    df_change_0_1 = change_0.join(change_1, rsuffix='_right')
    l1 = df_change_0_1["Open__change"].to_list()
    l2 = df_change_0_1["Open__change_right"].to_list()

    df_change_0_1 = df_change_0_1[(~df_change_0_1["Open__change"].isnull()) & (~df_change_0_1["Open__change_right"].isnull())]


    # restrict times
    if not x_end is None:
        df_change_0_1 = df_change_0_1.loc[x_start.strftime('%Y-%m-%d'):x_end.strftime('%Y-%m-%d')]

    # if the value is one that means it is checked
    print(fix_axis_corr)
    if len(fix_axis_corr) == 1:
        xy_max = max(max(l1), max(l2))*1.02
    else:
        xy_max = max(df_change_0_1['Open__change'].abs().max(), df_change_0_1['Open__change_right'].abs().max())

    fig_px_scatter = px.scatter(df_change_0_1, x="Open__change", y="Open__change_right", labels={
                            "Open__change": list_symbols[0],
                            "Open__change_right": list_symbols[1],
                        }).update_traces(mode="markers")
    fig_go_Figure = go.Figure(data=fig_px_scatter)
    fig_go_Figure.update_layout(title="Relative Change (%)")
    fig_go_Figure.update_layout(title_x=0.5)
    fig_go_Figure.update_layout(xaxis_range=[-1*xy_max, xy_max])
    fig_go_Figure.update_layout(yaxis_range=[-1*xy_max, xy_max])

    fig_go_Figure.update_layout(
        autosize=False,
        width=800,
        height=800,)
    fig_xy = dcc.Graph(id='id-f1', figure=fig_go_Figure)
    return fig_timeevolution, fig_xy, possible_days_back, days_back


###############
# Landing page

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


# register app
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
