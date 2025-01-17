import dash
import pandas as pd
from dash import html,dcc, Input, Output, State, callback, Patch
import plotly.express as px
import dash_bootstrap_components as dbc
import dash_ag_grid as dag
import plotly.graph_objects as go

dash.register_page(__name__, path="/page-1")
# importing the data
df=pd.read_excel('https://docs.google.com/spreadsheets/d/1fJ_8PMI9BLrZaLinmL9pwWxL-yLiixXZ/export?format=xlsx')
# )
# df=pd.read_excel('/Users/praveen/Desktop/APO_DASH/Data_dash_recovery.xlsx')
# df=pd.read_csv('/Users/praveen/Desktop/APO_DASH/Data_dash_recovery.csv')
# filling the NaN value to zero just for instance
df=df.fillna(0)
# layout of the page
# card 1 'Recovery'

card_recovery = dbc.Card(
    dbc.CardBody([
        html.H3('RECOVERY'),
        html.P('Recovery of the blocks cutting QTY SQF/CBM'),
        html.Div(id='recovery', children=0,style={'font-size':'50px'}),
    ]),
    style={"width": "100%",'height':'100%'}  # Ensure card uses full width of its column
)
# card2 for the quantity
card_quantity = dbc.Card(
    dbc.CardBody([
        html.H3('QUANTITY'),
        html.P('Dispatched: ', style={"fontWeight": "bold"}),
        html.Div(id='dispatched', children='0', style={"marginBottom": "10px"}),
        html.P('In Stocks: ', style={"fontWeight": "bold"}),
        html.Div(id='in_stocks', children='0'),
    ]),
    style={"width": "100%",'height':'100%'}
)
grid=dag.AgGrid(
    id="table",
    rowData=df.to_dict("records"),
    columnDefs=[{"field": i} for i in df.columns],
    defaultColDef={"filter": True, "sortable": True, "resizable": True},
    className="ag-theme-alpine-dark",
)
# dynamic chart for APO recovery



layout = dbc.Container(
    [dbc.Row(dcc.Dropdown(df['COLOR NAME'].unique(),multi=True,value=df['COLOR NAME'].unique()[0:2],id='dropdown')),
        dbc.Row(
            [ dbc.Col(card_recovery,className="d-flex align-items-stretch" ,style={'margin-bottom': '20px'}),
            dbc.Col(card_quantity,className="d-flex align-items-stretch",style={'margin-bottom': '20px'}),  # Second card in its own row  # First card in its own row
    ]),
        
    
        dbc.Row(dcc.Graph(figure={},id='graph1'),style={'margin-bottom': '20px'}),
        grid
    ],
    fluid=True
)
@callback(
    Output(component_id='graph1',component_property='figure'),
    Output(component_id='recovery',component_property='children'),
    Output(component_id='dispatched',component_property='children'),
    Output(component_id='in_stocks',component_property='children'),
    Input(component_id='dropdown',component_property='value')
)
def update(dropdown_value):
    dff=df[df['COLOR NAME'].isin(dropdown_value)]
    fig=px.histogram(dff,x=dff['APO NO'],y=dff['TOTAL  RECOVERY CBM FOR BLOCK']).update_layout(template="plotly_dark",xaxis=dict(type='category'))
    rec=int(sum(dff['CUTTING QTY'])/sum(dff['CBM']))
    dispactchqty=dff['DISPATCHED QTY'].sum()
    instockqty=dff['CUTTING QTY'].sum()-dispactchqty
    print(rec)
    return fig,rec,dispactchqty,instockqty