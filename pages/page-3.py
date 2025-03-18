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
# fetching dressing data 

dressing=sheet.worksheet("DRESSING").get_all_records()
dressing_header = dressing[1]  # Second row (index 1)
dressing_rows = dressing[2:]   # Data starts from the third row (index 2)
dressing_df = pd.DataFrame(dressing_rows, columns=dressing_header)
# print(dressing_df.head(2))
# fetching cutting data
cutting=sheet.worksheet("CUTTING").get_all_records()
cutting_header=cutting[1]
cutting_rows=cutting[2:]
cutting_df=pd.DataFrame(cutting_rows,columns=cutting_header)
#fetching polishing data
polishing=sheet.worksheet("POLISHING AND GRINDING").get_all_records()
polishing_header=polishing[1]
polishing_rows=polishing[2:]
polishing_df=pd.DataFrame(polishing_rows,columns=polishing_header)
#fetching epoxy data
epoxy=sheet.worksheet("EPOXY").get_all_records()
epoxy_header=epoxy[1]
epoxy_rows=epoxy[2:]
epoxy_df=pd.DataFrame(epoxy_rows,columns=epoxy_header)
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


# funtion to filter the data based on date
def filter_data(start_date, end_date):
    # Function to filter data based on selected date range

    if start_date and end_date:
        start_date = pd.to_datetime(start_date)
        end_date = pd.to_datetime(end_date)
        filtered_data = data3[(data3['DATE'] >= start_date) & (data3['DATE'] <= end_date)]
        return filtered_data
    return data3  # Return full data if no date selected
#function to calculate the dressing 
def dressingvalue(block,dataframe1,dataframe2):
    qty=sum(dataframe1[dataframe1['BLOCK NO']==block]["TOTAL SQM"])
    price_per_unit=dataframe2['']




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
    dash.dash_table.DataTable(cost_df.to_dict('records'), [{"name": i, "id": i} for i in cost_df.columns]),

    ])
# print(data3)

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


