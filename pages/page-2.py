import dash
from dash import html

dash.register_page(__name__, path="/page-2")

layout = html.Div(
    [
        html.H2("Welcome to the Second Page"),
        html.P("This is the content of the second page."),
    ]
)