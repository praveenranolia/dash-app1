
# Import packages
from dash import Dash, html, dash_table, dcc, callback, Output, Input
import pandas as pd
import plotly.express as px
import dash_ag_grid as dag

# Incorporate data
df = pd.read_csv('/Users/praveen/Desktop/APO_DASH/2011_us_ag_exports.csv')

# Plotly graphs
# fig = px.scatter(df, x='V', y='S')

# Initialize the app
app = Dash(__name__)

app.layout = html.Div([
  html.Div(id="my-title", children="Us Agricultural Exports in 2011"),
  dcc.Dropdown(id="state-dropdown", options=df.state.unique(), value=["Alabama","Arkansas"], multi=True),
  dcc.Graph(id="graph1"),
  html.Div(id='table-here')
])

@callback(
  Output(component_id='graph1', component_property='figure'),
  Input(component_id='state-dropdown', component_property='value')
)
def update_graph(states_selected):
  df_country = df[df.state.isin(states_selected)]
  fig1 = px.bar(data_frame=df_country, x='state', y=['beef','pork','fruits fresh'])
  return fig1


@callback(
  Output(component_id='table-here', component_property='children'),
    Input(component_id='graph1', component_property='hoverData'),
  prevent_initial_call=True
)

if __name__ == '__main__':
    app.run(debug=True)