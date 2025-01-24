import dash
import pandas as pd
from dash import html,dcc, Input, Output, State, callback, Patch
import plotly.express as px
import dash_bootstrap_components as dbc
import dash_ag_grid as dag
import plotly.graph_objects as go

dash.register_page(__name__, path="/page-2")
# importing the data
df2=pd.read_excel('https://docs.google.com/spreadsheets/d/1qSho2LLqIBMhKDCcGC_7vLkUc7rNa012o8Tvh37MkwU/export?format=xlsx')

# )
# df2=pd.read_excel('/Users/praveen/Desktop/APO_DASH/Data_dash_recovery.xlsx')
# df2=pd.read_excel('/Users/praveen/Desktop/APO_DASH/RECOVERY.xlsx')
# df2=pd.read_csv('/Users/praveen/Desktop/APO_DASH/RECOVERY.csv')
# filling the NaN value to zero just for instance
df2=df2.fillna(0)
card_sales= dbc.Card(
    dbc.CardBody([
        html.H3('Sales'),
        html.P('TOTAL AMOUNT INR: ', style={"fontWeight": "bold"}),
        html.Div(id='totalamount', children='0', style={"marginBottom": "10px",'font-size':'40px'}),
        html.P('TOTAL GST INR: ', style={"fontWeight": "bold"}),
        html.Div(id='gstamount', children='0',style={'font-size':'40px'}),
        html.P('TRANSPORT INR',style={"fontWeight": "bold"}),
        html.Div(id='transportamount', children='0', style={"marginBottom": "10px",'font-size':'40px'})
    ]),
    style={"width": "100%",'height':'100%'})
card_pie_chart=dbc.Card(
    dbc.CardBody([
        html.H3('SALES'),
        dcc.Graph(id='salespiechart',figure={})
    ])

)
grid2=dag.AgGrid(
    id="table2",
    rowData=df2.to_dict("records"),
    columnDefs=[{"field": i,"cellDataType" : 'text'} for i in df2.columns[[1,2,13,14,15,16,17,18]]],
    # columnDefs=[{"field":'BLOCK NO',"cellDataType" : 'text' }],
    defaultColDef={"filter": True, "sortable": True, "resizable": True},
    className="ag-theme-alpine-dark",
    dashGridOptions={"pagination": True, "animateRows": False},
)
layout = dbc.Container(
    [dbc.Row(dcc.Dropdown(df2['COLOR NAME'].unique(),multi=True,value=df2['COLOR NAME'].unique()[0:2],id='dropdown1')),
        dbc.Row(
            [ dbc.Col(card_sales,className="d-flex align-items-stretch" ,style={'margin-bottom': '20px'}),
            dbc.Col(card_pie_chart,style={'margin-bottom': '20px'}),  # Second card in its own row  # First card in its own row
    ]),
    dbc.Row(dcc.Graph(figure={},id='page2chart'),style={
        # "width": "2000px",  # Set a large width for the graph container
        "overflow-x": "auto",  # Enable horizontal scrolling
        "white-space": "nowrap"  # Prevent graph from wrapping
    }),
    grid2
    ],
    fluid=True
)
@callback(
    Output(component_id='salespiechart',component_property='figure'),
    Output(component_id='totalamount',component_property='children'),
    Output(component_id='gstamount',component_property='children'),
    Output(component_id='transportamount',component_property='children'),
    Output(component_id='page2chart',component_property='figure'),
    Input(component_id='dropdown1',component_property='value')
)
def func(dropdown_value1):
    dff2=df2[df2['COLOR NAME'].isin(dropdown_value1)]
    amount=sum(dff2['AMOUNT'])
    total_sales_amount=sum(dff2['TOTAL VALUE'])
    total_gst=sum(dff2['GST'])
    # total_transport=sum(dff2['TRANSPORT CHARGES PER BLOCK'])
    total_transport=0
    fig1=px.pie(values=[amount,total_gst,total_transport],labels=['AMOUNT','GST','TRANSPORT'],hole=0.4,names=['AMOUNT',"GST",'TRANSPORT']).update_layout(template="plotly_dark")
    histochart=px.histogram(dff2,x=dff2['BLOCK NO'],y=dff2['TOTAL VALUE']).update_layout(template="plotly_dark",xaxis=dict(type='category'))
    return fig1,total_sales_amount,total_gst,total_transport,histochart
