import dash
import os
import tempfile
import json
import pandas as pd
from dash import html,dcc, Input, Output, State, callback, Patch
import plotly.express as px
import dash_bootstrap_components as dbc
import dash_ag_grid as dag
import plotly.graph_objects as go
import gspread
from google.oauth2.service_account import Credentials

dash.register_page(__name__, path="/page-1")
# importing the data
scopes=[
    "https://www.googleapis.com/auth/spreadsheets"
]
# creds=Credentials.from_service_account_file("credentials.json",scopes=scopes) 
google_creds = os.getenv("GOOGLE_CREDENTIALS")
if google_creds:
    creds_dict = json.loads(google_creds)  # Convert JSON string to dictionary

    # Create a temporary file to store the credentials
    with tempfile.NamedTemporaryFile(mode="w", delete=False) as temp:
        json.dump(creds_dict, temp)
        temp.flush()
        credentials_path = temp.name  # Store temp file path

    # Use the temporary file instead of a local credentials.json file
    creds = Credentials.from_service_account_file(credentials_path, scopes=scopes)
else:
    raise ValueError("GOOGLE_CREDENTIALS environment variable is not set.")
client=gspread.authorize(creds)
sheet_id="1lGNiK4_L2r8ZOE1slGfC0ZaPRBsVq8GwNW5N4zkRgj4"
sheet=client.open_by_key(sheet_id)
data=sheet.worksheet("MAIN").get_all_records()
df=pd.DataFrame(data)
# df=pd.read_excel('https://docs.google.com/spreadsheets/d/1NbzklkOrIH4b4ayI-xu_tBN3mqYd0dDrS_Vz7hCmiAo/export?/format=xlsx')
# df=pd.read_excel('https://docs.google.com/spreadsheets/d/1qSho2LLqIBMhKDCcGC_7vLkUc7rNa012o8Tvh37MkwU/export?format=xlsx')
# filling the NaN value to zero just for instance
df.replace('',0,inplace=True)
# layout of the page
# card 1 'Recovery'
# Tabs for selection of FULL OR PARTIAL DISPATCHED 
tabs = dbc.Tabs([
    dbc.Tab(label="Partial  Dispatched", tab_id="all_dispatched"),
    dbc.Tab(label="NOT DISPATCHED", tab_id="partial_dispatched"),
], id="tab_selection", active_tab="all_dispatched")
card_recovery = dbc.Card(
    dbc.CardBody([
        html.H3('AVG. RECOVERY'),
        html.P('(dispatched +instock)inSQF/CBM of block'),
        html.Div(id='recovery', children=0,style={'font-size':'50px'}),
        html.P('Cutting QTY SFT: ', style={"fontWeight": "bold"}),
        html.Div(id='cuttingqty', children='0', style={"marginBottom": "10px",'font-size':'40px'}),

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
        html.P('Block Count',style={"fontWeight": "bold"}),
        html.Div(id="blockcount",children='0', style={"marginBottom": "10px",'font-size':'40px'})

    ]),
    style={"width": "100%",'height':'100%'}
)
# this is the card for the selective blocks 
block_card=dbc.Card(
    dbc.CardBody([
        html.P('Avg RECOVERY:',style={"fontWeight": "bold",'font-size':'20px'}),
        html.Div(id='block-recovery',children='0',style={"marginBottom": "30px","fontWeight": "bold",'font-size':'20px'}),
        html.P('Dispatched QTY (SQF):',style={"fontWeight": "bold",'font-size':'20px'}),
        html.Div(id='block-dispatched',children='0',style={"marginBottom": "30px","fontWeight": "bold",'font-size':'20px'}),
        html.P('In STOCKS QTY (SQF):',style={"fontWeight": "bold",'font-size':'20px'}),
        html.Div(id='block-instocks',children='0',style={"fontWeight": "bold",'font-size':'20px'}),

    ]),
    style={"width": "100%",'height':'100%'}
)
grid=dag.AgGrid(
    id="table",
    rowData=df.to_dict("records"),
    columnDefs=[{"field": i,"cellDataType" : 'text'} for i in df.columns[:26]],
    # columnDefs=[{"field":'BLOCK NO',"cellDataType" : 'text' }],
    defaultColDef={"filter": True, "sortable": True, "resizable": True},
    className="ag-theme-alpine-dark",
    dashGridOptions={"pagination": True, "animateRows": False,"filterModel":"server",
    "sortingMode":"server"},
)
# dynamic chart for APO recovery
layout = dbc.Container(
    [dbc.Row(dcc.Dropdown(df['COLOR NAME'].unique(),placeholder='select the colors',multi=True,id='dropdown')),
     dbc.Row(dcc.Dropdown(id='cutterselection',placeholder='select the size')),
     tabs,
        dbc.Row(
            [ dbc.Col(card_recovery,className="d-flex align-items-stretch" ,style={'margin-bottom': '20px'}),
            dbc.Col(card_quantity,className="d-flex align-items-stretch",style={'margin-bottom': '20px'}),  # Second card in its own row  # First card in its own row
    ]),
    dbc.Row([dbc.Col([
        dcc.Dropdown(id='blockselection',placeholder='select the blocks',multi=True,value=df['BLOCK NO'].unique()[0:3]),
        block_card]

    ),
             dbc.Col(dcc.Graph(figure={},id='minigraph'))]),
        grid
    ],
    fluid=True
)
@callback(
    # Output(component_id='graph1',component_property='figure'),
    # Output(component_id='recovery',component_property='children'),
    # Output(component_id='dispatched',component_property='children'),
    # Output(component_id='in_stocks',component_property='children'),
    # Output(component_id='blockselection',component_property='options'),
    Output(component_id='cutterselection',component_property='options'),
    Input(component_id='dropdown',component_property='value'),
    prevent_initial_call= True
    
)
def update(dropdown_value):
    if not dropdown_value:
        return []
    dff=df[df['COLOR NAME'].isin(dropdown_value)]
    cutter_methods=dff['SIZE'].unique()
    # fig=px.histogram(dff,x=dff['BLOCK NO'],y=dff['RECOVERY']).update_layout(template="plotly_dark",xaxis=dict(type='category'))
    # rec=round(sum(dff['DISPATCHED QTY']+dff['SFT FOR BAL SLABS'])/sum(dff['NEW CBM']),2)
    # values=dff['BLOCK NO']
    # dispactchqty=round(dff['DISPATCHED QTY'].sum(),2)
    # instockqty=round(dff['CUTTING QTY'].sum()-dispactchqty,2)
    return cutter_methods

@callback(
    # Output(component_id='graph1',component_property='figure'),
    Output(component_id='recovery',component_property='children'),
    Output(component_id='dispatched',component_property='children'),
    Output(component_id='in_stocks',component_property='children'),
    Output(component_id='blockselection',component_property='options'),
    Output(component_id='blockcount',component_property='children'),
    Output(component_id="cuttingqty",component_property="children"),
    Input(component_id='dropdown',component_property='value'),
    Input(component_id='cutterselection',component_property='value'),
    Input(component_id='tab_selection',component_property='active_tab'),
    prevent_initial_call=True  
)
def func2(colors,cutters,selected_tab):
    if not colors or not cutters:
        return  "", "", "", [],"",""
    # print(colors,cutters)
     
    dff2=df[(df['COLOR NAME'].isin(colors)) & (df['SIZE']==cutters)]
    values=dff2['BLOCK NO']
    cutting_qty=round(dff2['CUTTING QTY'].sum(),2)
    fig=px.histogram(dff2,x=dff2['BLOCK NO'],y=dff2['RECOVERY']).update_layout(template="plotly_dark",xaxis=dict(type='category'))

    if selected_tab == "all_dispatched":
        dff2 = dff2[dff2['DISPATCHED SLABS'] > 0]  # all dispatched data
        rec=round(sum(dff2['DISPATCHED QTY']+dff2['SFT FOR BAL SLABS'])/sum(dff2['ADJ CBM']),2)
        block_count=dff2['BLOCK NO'].nunique()
        # print(block_count)
        # print('this is for all dipatched page1 ',dff2)
    else:
        dff2 = dff2[(dff2['DISPATCHED SLABS'] == 0) & (dff2['CUTTING QTY']>0)]
        # print("dataset for the not dispatched slabs",dff2[['ADJ CBM',"CUTTING QTY"]])
        rec=round(sum(dff2['CUTTING QTY'])*.85/sum(dff2['ADJ CBM']),2)
        block_count=dff2['BLOCK NO'].nunique()
        # print(block_count)
        # print(dff2)  # partial dispatched data
    # rec=round(sum(dff2['DISPATCHED QTY']+dff2['SFT FOR BAL SLABS'])/sum(dff2['ADJ CBM']),2)
    dispactchqty=round(dff2['DISPATCHED QTY'].sum(),2)
    # instockqty=round(dff2['CUTTING QTY'].sum()-dispactchqty,2)
    instockqty=round(dff2['SFT FOR BAL SLABS'].sum(),2)
    return rec,dispactchqty,instockqty,values,block_count, cutting_qty



@callback(
    Output(component_id='block-recovery',component_property='children'),
    Output(component_id='block-dispatched',component_property='children'),
    Output(component_id='block-instocks',component_property='children'),
    Output(component_id='minigraph',component_property='figure'),
    Input(component_id='blockselection',component_property='value'),
    
    prevent_initial_call=True
)
def blockdropdown(block_value):
    if not block_value:
        return "", "", "", go.Figure()
    # print(block_value,[type(i) for i in block_value ])
    block_df=df[df['BLOCK NO'].isin(block_value) & df['CUTTING QTY']>0]
    if block_df.empty:
        return "block not yet cutted", "", "", go.Figure()
    condition=(block_df['DISPATCHED QTY']==0)
    block_df.loc[condition,'SFT FOR BAL SLABS']=block_df.loc[condition,'CUTTING QTY']*.85
    block_df.loc[condition,'RECOVERY']=block_df.loc[condition,'SFT FOR BAL SLABS']/block_df.loc[condition,'ADJ CBM']
    
    block_rec=round((block_df['SFT FOR BAL SLABS'].sum() + block_df['DISPATCHED QTY'].sum()) / block_df['ADJ CBM'].sum(),2)
    block_dispatch=round(block_df['DISPATCHED QTY'].sum(),2)
    block_instocks=round(block_df['SFT FOR BAL SLABS'].sum(),2)
    # print(block_df)

    fig2=px.histogram(block_df,x=block_df['BLOCK NO'],y=block_df['RECOVERY']).update_layout(template="plotly_dark",xaxis=dict(type='category'))
    return block_rec,block_dispatch,block_instocks,fig2




    
