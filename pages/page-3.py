import dash
import pandas as pd
import os
import tempfile
import json
from dash import html,dcc, Input, Output, State, callback, Patch
import plotly.express as px
import dash_bootstrap_components as dbc
import dash_ag_grid as dag
import plotly.graph_objects as go
from datetime import date
import gspread
from google.oauth2.service_account import Credentials
dash.register_page(__name__, path="/page-3")
data3=pd.read_excel('https://docs.google.com/spreadsheets/d/1LXlNqgl_Dy9nt9gocO8jMlrRl7_5hR1u5KTIcuqsUVw/export?/format=xlsx')
# fetching the costing data using google sheets APIs
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
sheet_id="1NvnuOaY8ZAZO_vgZhgessJO5-X6tUbEx0f_ybRJ-3U4"
cost_sheet_id="1iONtXc1AGdatKP9fQDBOKOhVZTUgDkw6Y7_uhNYCJcg"
sheet=client.open_by_key(sheet_id)
cost_sheet=client.open_by_key(cost_sheet_id)
costsft=cost_sheet.worksheet("COST PER UNIT").get_all_records()
cost_df=pd.DataFrame(costsft)
def fetch_sheet_data(sheet_name):
    data = sheet.worksheet(sheet_name).get_all_records()
    return pd.DataFrame(data)

dressing_df = fetch_sheet_data("DRESSING")
cutting_df = fetch_sheet_data("CUTTING")
polishing_df = fetch_sheet_data("POLISHING AND GRINDING")
epoxy_df = fetch_sheet_data("EPOXY")
data3.fillna(0)
grid3=dag.AgGrid(
    id="table3",
    rowData=cost_df.to_dict("records"),
    columnDefs=[{"field": i,"cellDataType" : 'text'} for i in cost_df.columns],
    # columnDefs=[{"field":'BLOCK NO',"cellDataType" : 'text' }],
    defaultColDef={"filter": True, "sortable": True, "resizable": True},
    className="ag-theme-alpine-dark",
    dashGridOptions={"pagination": True, "animateRows": False},
)
#cost table
grid4=dag.AgGrid(

    id="page3grid1",
    rowData=[],
    columnDefs=[
        {
            "field": i,
            "width": 110,  # Adjusted width for better fit
            "cellStyle": {'padding': '0 5px'}  # Reduce internal padding
        } for i in [
            "COLOUR", "BLOCK NO", "CUTTING QTY",
            "CUTTING COST", "POLISHING COST", "EPOXY COST", "MISC COST", "TOTAL COST"
        ]
    ],
    defaultColDef={"filter": True, "sortable": True, "resizable": True},
    className="ag-theme-alpine-dark",
    dashGridOptions={"pagination": True, "animateRows": False},

)

recipt_value=dbc.Card([
    dbc.CardHeader('TOTAL RECEIPT VALUE'),
    dbc.CardBody(html.Div(id='TOTAL RECEIPT VALUE', children='0', style={"marginBottom": "10px",'font-size':'40px'}))
])
issue_value=dbc.Card([
    dbc.CardHeader('TOTAL ISSUE VALUE'),
    dbc.CardBody(html.Div(id='TOTAL ISSUE VALUE', children='0', style={"marginBottom": "10px",'font-size':'40px'}))
])
# block_no=input("give the block no.")
# print(block_no)
# print(epoxy_df[epoxy_df['BLOCK NO']==block_no])
# print("this is the cutting df",cutting_df)


# funtion to filter the data based on date
def filter_data(start_date, end_date):
    # Function to filter data based on selected date range

    if start_date and end_date:
        start_date = pd.to_datetime(start_date)
        end_date = pd.to_datetime(end_date)
        filtered_data = data3[(data3['DATE'] >= start_date) & (data3['DATE'] <= end_date)]
        return filtered_data
    return data3  # Return full data if no date selected
#function to calculate the dressing cost
from Function import *

layout = dbc.Container( [ dbc.Row(dcc.Dropdown(dressing_df['COLOUR'].unique(),placeholder="select the colour",multi=True,id="page3colourselect")),
    dbc.Row(dcc.Dropdown(id='block_selection',placeholder="select the blocks",multi=True)),
    # dbc.Row(dcc.Graph(figure={},id='page3graph2'),style={
    #     # "width": "2000px",  # Set a large width for the graph container
    #     "overflow-x": "auto",  # Enable horizontal scrolling
    #     "white-space": "nowrap"  # Prevent graph from wrapping
    # }),
    grid4,
    dcc.DatePickerRange(
        id='my-date-picker-range',
        min_date_allowed=data3['DATE'].min(),
        max_date_allowed=data3['DATE'].max(),
        initial_visible_month=data3['DATE'].min(),
        minimum_nights=0
        # # end_date=date(2017, 8, 25)
        # start_date=
    ),dbc.Row(dcc.Dropdown(data3['CATEGORY'].unique(),placeholder='select the category',multi=True,id='page3dropdown')),
    dbc.Row(
            [ dbc.Col(recipt_value,className="d-flex align-items-stretch" ,style={'margin-bottom': '20px'}),
            dbc.Col(issue_value,className="d-flex align-items-stretch",style={'margin-bottom': '20px'}),  # Second card in its own row  # First card in its own row
    ]),
    dbc.Row(dcc.Graph(figure={},id='page3graph1'),style={
        # "width": "2000px",  # Set a large width for the graph container
        "overflow-x": "auto",  # Enable horizontal scrolling
        "white-space": "nowrap"  # Prevent graph from wrapping
    }),
    dbc.Row(dcc.Dropdown(cost_df['MONTH'].unique(),placeholder='select the month',multi=True,id="page3dropdown2")),
    grid3,
])


@callback(
    Output(component_id='TOTAL RECEIPT VALUE',component_property='children'),
    Output(component_id='TOTAL ISSUE VALUE',component_property='children'),
    Output(component_id='page3graph1',component_property='figure'),
    Input(component_id='my-date-picker-range',component_property='start_date'),
    Input(component_id='my-date-picker-range',component_property='end_date'),
    Input(component_id='page3dropdown',component_property='value'),
    prevent_initial_call=True

)
def update(start_date,end_date,category):
    filtered_data=filter_data(start_date,end_date)
    if category:
        filtered_data = filtered_data[filtered_data['CATEGORY'].isin(category)]
    
    recipt_val=sum(filtered_data['RECEIPT\n VALUE'])
    issue_val=sum(filtered_data['ISSUE\n VALUE'])
    figpage3=px.histogram(filtered_data,x=filtered_data['DATE'],y=filtered_data['ISSUE\n VALUE']).update_layout(template="plotly_dark",xaxis=dict(type='category'))
    return recipt_val,issue_val,figpage3


@callback(
    Output(component_id="block_selection",component_property="options"),
    Input(component_id="page3colourselect",component_property="value")
)
def updateblock(colour_name):
    if not colour_name:
        return []
    blocks_no=dressing_df[dressing_df['COLOUR'].isin(colour_name)]["BLOCK NO"].unique()
    return blocks_no

@callback(
    # Output(component_id="page3graph2",component_property="figure"),
    Output(component_id="page3grid1",component_property="rowData"),
    Input(component_id="block_selection",component_property="value"),
    prevent_initial_call= True

)
def update_values(block_no):
    block_columns = ["BLOCK NO", "COLOUR", "CUTTING QTY", "CUTTING COST", "POLISHING COST", "EPOXY COST", "MISC COST"]
    block_cost_df = pd.DataFrame(columns=block_columns)
    if not block_no:
        return pd.DataFrame()
    for block in block_no:
        block_colour ,dress_price, month=dressing_value(block,dressing_df,cost_df)
        if month=="MARCH":
            month="FEBRUARY"
        block_cut_qty,block_cut_cost,block_misc_cost,=cutting_value(block,cutting_df,cost_df,month)
        block_polish_cost=polishing_value(block,polishing_df,cost_df,month)
        block_epoxy_cost=epoxy_value(block,epoxy_df,cost_df,month)
        # print("THESE ARE SERIAL WISE VALUES",block,block_cut_qty,"\n",block_colour,"\n",block_cut_cost,"\n",block_polish_cost,"\n",block_epoxy_cost,"\n",block_misc_cost)
        new_row = {
            "BLOCK NO": block,
            "COLOUR": block_colour,
            "CUTTING QTY": block_cut_qty,
            "DRESSING COST": dress_price,
            "CUTTING COST": block_cut_cost,  # Convert Series to a single value
            "POLISHING COST": block_polish_cost,
            "EPOXY COST": block_epoxy_cost,
            "MISC COST": block_misc_cost
        }
        block_cost_df = pd.concat([block_cost_df, pd.DataFrame([new_row])], ignore_index=True)
        
    block_cost_df["TOTAL COST"] = block_cost_df.iloc[:, 3:].sum(axis=1)
    
    return block_cost_df.to_dict("records")







        





