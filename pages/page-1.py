import dash
import pandas as pd
from dash import html,dcc, Input, Output, State, callback, Patch
import plotly.express as px
import dash_bootstrap_components as dbc
import dash_ag_grid as dag
import plotly.graph_objects as go

dash.register_page(__name__, path="/page-1")
# importing the data
df=pd.read_excel('https://docs.google.com/spreadsheets/d/1qSho2LLqIBMhKDCcGC_7vLkUc7rNa012o8Tvh37MkwU/export?format=xlsx')

# )
# df=pd.read_excel('/Users/praveen/Desktop/APO_DASH/Data_dash_recovery.xlsx')
# df=pd.read_excel('/Users/praveen/Desktop/APO_DASH/RECOVERY.xlsx')
# df=pd.read_csv('/Users/praveen/Desktop/APO_DASH/RECOVERY.csv')
# filling the NaN value to zero just for instance
df=df.fillna(0)
# layout of the page
# card 1 'Recovery'
card_recovery = dbc.Card(
    dbc.CardBody([
        html.H3('AVG. RECOVERY'),
        html.P('Recovery of the blocks cutting QTY SQF/CBM'),
        html.Div(id='recovery', children=0,style={'font-size':'50px'}),
    ]),
    style={"width": "100%",'height':'100%'}  # Ensure card uses full width of its column
)
# card2 for the quantity
card_quantity = dbc.Card(
    dbc.CardBody([
        html.H3('QUANTITY'),
        html.P('Dispatched SQF: ', style={"fontWeight": "bold"}),
        html.Div(id='dispatched', children='0', style={"marginBottom": "10px",'font-size':'40px'}),
        html.P('In Stocks SQF: ', style={"fontWeight": "bold"}),
        html.Div(id='in_stocks', children='0',style={'font-size':'40px'}),
    ]),
    style={"width": "100%",'height':'100%'}
)
grid=dag.AgGrid(
    id="table",
    rowData=df.to_dict("records"),
    columnDefs=[{"field": i,"cellDataType" : 'text'} for i in df.columns],
    # columnDefs=[{"field":'BLOCK NO',"cellDataType" : 'text' }],
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
        
    
        dbc.Row(dcc.Graph(figure={},id='graph1'),style={
                # "width": "2000px",  # Set a large width for the graph container
                "overflow-x": "auto",  # Enable horizontal scrolling
                "white-space": "nowrap"  # Prevent graph from wrapping
            }),
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
    fig=px.histogram(dff,x=dff['BLOCK NO'],y=dff['Recovery']).update_layout(template="plotly_dark",xaxis=dict(type='category'))
    rec=round(sum(dff['DISPATCHED QTY']+dff['SFT FOR BAL SLABS'])/sum(dff['CBM']),2)
    
    dispactchqty=round(dff['DISPATCHED QTY'].sum(),2)
    instockqty=round(dff['CUTTING QTY'].sum()-dispactchqty,2)
    return fig,rec,dispactchqty,instockqty