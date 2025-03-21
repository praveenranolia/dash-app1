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
# from sqlalchemy import create_engine

dash.register_page(__name__, path="/page-3")
# engine =create_engine('postgresql://postgres:4248@localhost:5432/postgres')
# data3 = pd.read_sql("SELECT * FROM shoolgiri_consumeables", engine)
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
def dressing_value(block, df1, df2):
    # Fetch block color and month safely
    block_data = df1[df1['BLOCK NO'] == block]
    # print("this is the block_data",block_data)
    
    if block_data.empty:
        return None, 0, None  # Return defaults if no data found

    block_colour = block_data['COLOUR'].iloc[0]
    month = block_data['MONTH'].iloc[0]
    
    # Compute total square meters
    qty = block_data["TOTAL SQM"].sum()

    def get_cost(item):
        """Fetches cost per SFT safely, returns 0 if not found."""
        cost_series = df2[(df2['MONTH'] == month) & (df2['ITEM'] == item)]['COST PER SFT']
        return cost_series.iloc[0] if not cost_series.empty else 0

    # Calculate costs
    price = round(qty * get_cost("MONOWIRE SAW"),0)

    return block_colour, price, month
#function to calculate the cutting qty and cutting cost and misc cost
def cutting_value(block, df1, df2, month):
    dff1 = df1[df1['BLOCK NO'].str.contains(fr'^{block}\s*[A-Z]?$', na=False, regex=True)]
    # print("cutting_valuedfff",dff1)

    mws_qty = dff1[dff1['MACHINE'] == "MWS"]['AREA IN SQFT'].sum()
    no_mws_qty = dff1[dff1['MACHINE'] != "MWS"]['AREA IN SQFT'].sum()

    def get_cost(item_name, process_name=None):
        """Fetches cost per SFT safely, returns 0 if not found."""
        if process_name:
            cost_series = df2[(df2['MONTH'] == month) & (df2['PROCESS'] == process_name)]['COST PER SFT']
        else:
            cost_series = df2[(df2['MONTH'] == month) & (df2['ITEM'] == item_name)]['COST PER SFT']
        return cost_series.iloc[0] if not cost_series.empty else 0

    misc_cost = round((mws_qty + no_mws_qty) * get_cost(None, "MISC"),0)
    mws_price = mws_qty * get_cost("MULTI WIRE SAW")
    no_mws_price = no_mws_qty * get_cost("CUTTER")
    salary = (mws_qty + no_mws_qty) * get_cost("SALARY")

    total_cost = round(mws_price + no_mws_price + salary,0)
    total_area = mws_qty + no_mws_qty

    # print("cutting_value", total_area, total_cost, misc_cost)
    
    return total_area, total_cost, misc_cost

def polishing_value(block, df1, df2, month):
    dff1 = df1[df1['BLOCK NO'].str.contains(fr'^{block}\s*[A-Z]?$', na=False, regex=True)]
    # print("this ths the polishing dataframe have the regex dff1",dff1)
    grinding_qty = dff1[dff1['PROCESS CATEGORY'] == "GRINDING"]['SFT'].sum()
    polishing_qty = dff1[dff1['PROCESS CATEGORY'] == "POLISHING"]['SFT'].sum()
    leather_honed_qty = dff1[dff1['PROCESS CATEGORY'] == "LEATHER ADN HONED"]['SFT'].sum()
    # print("polishing aty",grinding_qty,polishing_qty,leather_honed_qty)

    def get_cost(process_name):
        """Fetches cost per SFT safely, returns 0 if not found."""
        cost_series = df2[(df2['MONTH'] == month) & (df2['PROCESS'] == process_name)]['COST PER SFT']
        return cost_series.iloc[0] if not cost_series.empty else 0

    polish_price = polishing_qty * get_cost("POLISHING")
    grinding_price = grinding_qty * get_cost("GRINDING")
    leather_honed_price = leather_honed_qty * get_cost("LEATHER AND HONED")
    # print("polishing_price",polish_price,grinding_price,leather_honed_price)

    return round(polish_price + grinding_price + leather_honed_price,0)
def epoxy_value(block, df1, df2, month):
    dff1 = df1[df1['BLOCK NO'].str.contains(fr'^{block}\s*[A-Z]?$', na=False, regex=True)]
    epoxy_cost = dff1["COST"].sum()
    
    nettingqty = dff1[dff1["TYPE OF EPOXY"] == 1204]['SLAB SFT'].sum()  # Ensure sum() for scalar value
    netting_price_series = df2[(df2['MONTH'] == month) & (df2['PROCESS'] == "NETTING")]['COST PER SFT']
    # print(netting_price_series)
    
    if not netting_price_series.empty:
        netting_price = nettingqty * netting_price_series.values[0]  # Extract scalar value before multiplication
    else:
        netting_price = 0  # Default to zero if no cost found
    # print("this is the epoxy value",nettingqty,netting_price,epoxy_cost)
    
    return round(epoxy_cost + netting_price,0)
block_columns = ["BLOCK NO", "COLOUR", "CUTTING QTY", "CUTTING COST", "POLISHING COST", "EPOXY COST", "MISC COST"]
block_cost_df = pd.DataFrame(columns=block_columns)

layout = dbc.Container( [dcc.DatePickerRange(
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
    dbc.Row(dcc.Dropdown(dressing_df['COLOUR'].unique(),placeholder="select the colour",multi=True,id="page3colourselect")),
    dbc.Row(dcc.Dropdown(id='block_selection',placeholder="select the blocks",multi=True)),
    dbc.Row(dcc.Graph(figure={},id='page3graph2'),style={
        # "width": "2000px",  # Set a large width for the graph container
        "overflow-x": "auto",  # Enable horizontal scrolling
        "white-space": "nowrap"  # Prevent graph from wrapping
    })])


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
    Output(component_id="page3graph2",component_property="figure"),
    Input(component_id="block_selection",component_property="value"),
    prevent_initial_call= True

)
def update_values(block_no):
    block_columns = ["BLOCK NO", "COLOUR", "CUTTING QTY", "CUTTING COST", "POLISHING COST", "EPOXY COST", "MISC COST"]
    block_cost_df = pd.DataFrame(columns=block_columns)
    if not block_no:
        return go.Figure()
    for block in block_no:
        block_colour ,dress_price, month=dressing_value(block,dressing_df,cost_df)
        if month=="MARCH":
            month="FEBURARY"
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
    # print(block_cost_df)
    # page3fig2=px.histogram(block_cost_df,x='BLOCK NO',y=block_cost_df.columns[2:-1].to_list()).update_layout(template="plotly_dark",xaxis=dict(type='category'))
    # return page3fig2
    chart_df = block_cost_df[["BLOCK NO", "CUTTING QTY", "TOTAL COST"]].melt(
    id_vars=["BLOCK NO"], 
    value_vars=["CUTTING QTY", "TOTAL COST"],
    var_name="Category", 
    value_name="Value"
)

# Add custom hover text for "TOTAL COST"
    block_cost_df["HOVER_TEXT"] = (
        "DRESSING COST: "+ block_cost_df["DRESSING COST"].astype(str) + "<br>" +
        "CUTTING COST: " + block_cost_df["CUTTING COST"].astype(str) + "<br>" +
        "POLISHING COST: " + block_cost_df["POLISHING COST"].astype(str) + "<br>" +
        "EPOXY COST: " + block_cost_df["EPOXY COST"].astype(str) + "<br>" +
        "MISC COST: " + block_cost_df["MISC COST"].astype(str)
    )

# Merge hover text into the chart DataFrame
    chart_df = chart_df.merge(block_cost_df[["BLOCK NO", "HOVER_TEXT"]], on="BLOCK NO", how="left")

# Create a grouped bar chart
    page3fig2 = px.bar(chart_df, 
                   x="BLOCK NO", 
                   y="Value", 
                   color="Category", 
                   barmode="group",  # Grouped bars
                   template="plotly_dark",
                   custom_data=["HOVER_TEXT"])  # Add custom hover data

# Update hover template to show custom text for "TOTAL COST"
    page3fig2.update_traces(
        hovertemplate="<b>%{x}</b><br>" +  # BLOCK NO
                    "Category: %{customdata[0]}<br>" +  # Custom hover text
                    "Value: %{y}<extra></extra>"  # Value of the bar
    )

    # Update x-axis to categorical
    page3fig2.update_layout(xaxis=dict(type='category'))
    
    return page3fig2







        





