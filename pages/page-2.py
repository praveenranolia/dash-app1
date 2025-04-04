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

dash.register_page(__name__, path="/page-2")
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
# importing the recovery data
client=gspread.authorize(creds)
recovery_sheet_id="1lGNiK4_L2r8ZOE1slGfC0ZaPRBsVq8GwNW5N4zkRgj4"
sheet=client.open_by_key(recovery_sheet_id)
data=sheet.worksheet("MAIN").get_all_records()
recovery_df=pd.DataFrame(data)
recovery_df['BLOCK NO'] = recovery_df['BLOCK NO'].astype(str)
#importing the costing and production data 
production_sheet_id="1NvnuOaY8ZAZO_vgZhgessJO5-X6tUbEx0f_ybRJ-3U4"
cost_sheet_id="1iONtXc1AGdatKP9fQDBOKOhVZTUgDkw6Y7_uhNYCJcg"
production_sheet=client.open_by_key(production_sheet_id)
cost_sheet=client.open_by_key(cost_sheet_id)
costsft=cost_sheet.worksheet("COST PER UNIT").get_all_records()
cost_df_2=pd.DataFrame(costsft)
def fetch_sheet_data(sheet_name):
    data = production_sheet.worksheet(sheet_name).get_all_records()
    return pd.DataFrame(data)

dressing_df_2 = fetch_sheet_data("DRESSING")
print(dressing_df_2.head(5))
cutting_df_2 = fetch_sheet_data("CUTTING")
polishing_df_2 = fetch_sheet_data("POLISHING AND GRINDING")
epoxy_df_2 = fetch_sheet_data("EPOXY")
# fetching the purcahase and sales data
from Function import *
def recovery_info(df,block_no):
    pass


page2_grid=dag.AgGrid(
    id="page2grid1",
    rowData=[],
    columnDefs=[
        {
            "field": i,
            "width": 110,  # Adjusted width for better fit
            "cellStyle": {'padding': '0 5px'}  # Reduce internal padding
        } for i in ["BLOCK NO", "COLOUR", "CUTTING QTY","SLABS","BAL_SLABS","PURCHASE COST","TRANSPORT COST","PROCESS COST","TOTAL","SALES AMOUNT","MARGIN"]
            
        
    ],
    defaultColDef={"filter": True, "sortable": True, "resizable": True},
    className="ag-theme-alpine-dark",
    dashGridOptions={"pagination": True, "animateRows": False},)
layout = dbc.Container( [ dbc.Row(dcc.Dropdown(dressing_df_2['COLOUR'].unique(),placeholder="select the colour",multi=True,id="page2colourselect")),
    dbc.Row(dcc.Dropdown(id='block_selection_page2',placeholder="select the blocks",multi=True)),
    page2_grid,])

@callback(
    Output(component_id="block_selection_page2",component_property="options"),
    Input(component_id="page2colourselect",component_property="value"))
def updateblock2(colour_name):
    if not colour_name:
        return []
    blocks_no=dressing_df_2[dressing_df_2['COLOUR'].isin(colour_name)]["BLOCK NO"].unique()
    return blocks_no

@callback(
    Output(component_id="page2grid1",component_property="rowData"),
    Input(component_id="block_selection_page2",component_property="value"))
def update(blocknums):
    block_columns = ["BLOCK NO", "COLOUR", "CUTTING QTY","SLABS","BAL_SLABS","PURCHASE COST","TRANSPORT COST","PROCESS COST","TOTAL","SALES AMOUNT","MARGIN"]
    block_sales_df= pd.DataFrame(columns=block_columns)
    if not blocknums:
        return pd.DataFrame().to_dict("records")
    for block in blocknums:
        block_colour ,dress_price, month=dressing_value(block,dressing_df_2,cost_df_2)
        if month=="MARCH":
            month="FEBRUARY"
        block_cut_qty,block_cut_cost,block_misc_cost,=cutting_value(block,cutting_df_2,cost_df_2,month)
        block_polish_cost=polishing_value(block,polishing_df_2,cost_df_2,month)
        block_epoxy_cost=epoxy_value(block,epoxy_df_2,cost_df_2,month)
        inv_amount,slabs,sales_amount,transport,balance_slabs= purchase_cost(recovery_df,block)
        print("this is the transport cost showing at page2",transport)
        pc=dress_price+block_cut_cost+block_misc_cost+block_polish_cost+block_epoxy_cost
        
        total_cost=inv_amount+transport+pc
        if slabs!=0:
            sales_amount+=(balance_slabs/slabs)*total_cost
        new_row={
            "BLOCK NO":block,
            "COLOUR":block_colour,
            "CUTTING QTY":round(block_cut_qty,0),
            "SLABS":slabs,
            "BAL_SLABS":balance_slabs,
            "PURCHASE COST":round(inv_amount,0),
            "TRANSPORT COST":round(transport,0),
            "PROCESS COST":round(pc,0),
            "TOTAL":round(total_cost,0),
            "SALES AMOUNT":round(sales_amount,0),
            "MARGIN":round(sales_amount-total_cost,0)
        }
        block_sales_df=pd.concat([block_sales_df, pd.DataFrame([new_row])], ignore_index=True)
    return block_sales_df.to_dict('records')
        






