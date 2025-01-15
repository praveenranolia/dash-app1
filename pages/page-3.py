import dash
from dash import html

dash.register_page(__name__, path="/page-3")

layout = html.Div(
    [
        html.H2("Welcome to the Third Page"),
        html.P("This is the content of the third page."),
    ]
)