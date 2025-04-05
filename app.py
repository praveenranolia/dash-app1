import dash
import pandas as pd
import os
import tempfile
import json
from dash import Dash, html, dcc, Input, Output, State, callback, Patch
import dash_bootstrap_components as dbc
import dash_ag_grid as dag
import plotly.graph_objects as go
import gspread
from google.oauth2.service_account import Credentials

app = Dash(external_stylesheets=[dbc.themes.CYBORG],use_pages=True,suppress_callback_exceptions=True)
server=app.server

SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "25%",
    "padding": "20px 10px",
    "background-color": "#f8f9fa",
}
# padding for page content
CONTENT_STYLE = {
    "margin-left": "25%",
    "margin-right": "2rem",
    "padding": "10px",
    'overflow':"auto"
}
app.layout = dbc.Container(
    [ dcc.Location(id='url'),
   
        # Sidebar with buttons
        dbc.Row(
            [
                dbc.Col([
                    html.Div(children='APO DASHBOARD',className="text mt-4 mb-4",style= {"font-size":"30px",
                                                                                         "color":'white'}),

                    dbc.Nav(
                        [
                            dbc.NavLink("Recovery", href="/page-1", className="mb-2", active="exact"),
                            dbc.NavLink("Sales", href="/page-2", className="mb-2", active="exact"),
                            dbc.NavLink("Costing", href="/page-3", className="mb-2", active="exact"),
                        ],
                        vertical=True,
                        pills=True,
                    )],
                    width=3,
                    className="bg-light p-3",
                    style=SIDEBAR_STYLE,
                ),
                
                # Space for pages
                dbc.Col(dash.page_container,width=12,md=9,style=CONTENT_STYLE),
            ],
            className="g-0",
        ),
    ],
    # fluid=False,

)
@app.callback(
    Output("url", "pathname"),
    Input("url", "pathname"),
    prevent_initial_call=True
)
def redirect_to_page_1(pathname):
    if pathname == "/":
        return "/page-1"
    return pathname

if __name__ == "__main__":
    app.run_server(debug=True)