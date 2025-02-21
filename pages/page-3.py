import dash
import pandas as pd
from dash import html,dcc, Input, Output, State, callback, Patch
import plotly.express as px
import dash_bootstrap_components as dbc
import dash_ag_grid as dag
import plotly.graph_objects as go
from datetime import date
from sqlalchemy import create_engine

dash.register_page(__name__, path="/page-3")
# engine =create_engine('postgresql://postgres:4248@localhost:5432/postgres')
# data3 = pd.read_sql("SELECT * FROM shoolgiri_consumeables", engine)
data3=pd.read_excel('https://docs.google.com/spreadsheets/d/1LXlNqgl_Dy9nt9gocO8jMlrRl7_5hR1u5KTIcuqsUVw/export?/format=xlsx')
# print(data.head())
data3.fillna(0)
grid3=dag.AgGrid(
    id="table3",
    rowData=data3.to_dict("records"),
    columnDefs=[{"field": i,"cellDataType" : 'text'} for i in data3.columns],
    # columnDefs=[{"field":'BLOCK NO',"cellDataType" : 'text' }],
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

# funtion to filter the data based on date
def filter_data(start_date, end_date):
    # Function to filter data based on selected date range

    if start_date and end_date:
        start_date = pd.to_datetime(start_date)
        end_date = pd.to_datetime(end_date)
        filtered_data = data3[(data3['DATE'] >= start_date) & (data3['DATE'] <= end_date)]
        return filtered_data
    return data3  # Return full data if no date selected

layout = dbc.Container( [dcc.DatePickerRange(
        id='my-date-picker-range',
        min_date_allowed=data3['DATE'].min(),
        max_date_allowed=data3['DATE'].max(),
        initial_visible_month=data3['DATE'].min(),
        minimum_nights=0
        # # end_date=date(2017, 8, 25)
        # start_date=
    ),dbc.Row(
            [ dbc.Col(recipt_value,className="d-flex align-items-stretch" ,style={'margin-bottom': '20px'}),
            dbc.Col(issue_value,className="d-flex align-items-stretch",style={'margin-bottom': '20px'}),  # Second card in its own row  # First card in its own row
    ]),
    dbc.Row(dcc.Graph(figure={},id='page3graph1'),style={
        # "width": "2000px",  # Set a large width for the graph container
        "overflow-x": "auto",  # Enable horizontal scrolling
        "white-space": "nowrap"  # Prevent graph from wrapping
    }),

    grid3])
print(data3)

@callback(
    Output(component_id='TOTAL RECEIPT VALUE',component_property='children'),
    Output(component_id='TOTAL ISSUE VALUE',component_property='children'),
    Output(component_id='page3graph1',component_property='figure'),
    Input(component_id='my-date-picker-range',component_property='start_date'),
    Input(component_id='my-date-picker-range',component_property='end_date'),
    prevent_initial_call=True

)
def update(start_date,end_date):
    filtered_data=filter_data(start_date,end_date)
    recipt_val=sum(filtered_data['RECEIPT\n VALUE'])
    issue_val=sum(filtered_data['ISSUE\n VALUE'])
    figpage3=px.histogram(filtered_data,x=filtered_data['DATE'],y=filtered_data['ISSUE\n VALUE']).update_layout(template="plotly_dark",xaxis=dict(type='category'))
    return recipt_val,issue_val,figpage3


