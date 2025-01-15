import dash
import pandas as pd
from dash import Dash, html, dcc, Input, Output, State, callback, Patch
import dash_bootstrap_components as dbc
import dash_ag_grid as dag
import plotly.graph_objects as go
app = Dash(external_stylesheets=[dbc.themes.CYBORG],use_pages=True)
server=app.server
# creating the object for side bar
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
    "padding": "20px",
    'overflow':"auto"
}
app.layout = dbc.Container(
    [
   
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
                            dbc.NavLink("Consumeables", href="/page-3", className="mb-2", active="exact"),
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
if __name__ == "__main__":
    app.run_server(debug=True)

