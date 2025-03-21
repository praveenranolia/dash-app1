import dash
import pandas as pd
from dash import html,dcc, Input, Output, State, callback, Patch
import plotly.express as px
import dash_bootstrap_components as dbc
import dash_ag_grid as dag
import plotly.graph_objects as go

dash.register_page(__name__, path="/page-2")
# importing the data
df2=pd.read_excel('https://docs.google.com/spreadsheets/d/1NbzklkOrIH4b4ayI-xu_tBN3mqYd0dDrS_Vz7hCmiAo/export?/format=xlsx')

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
        dcc.Graph(id='salespiechart',figure={},
                  style={'height':"400px",'width':'400px'})
    ])

)
# tab-selection for full and partial dispatched
tabs2 = dbc.Tabs([
    dbc.Tab(label="All Dispatched", tab_id="all_dispatched2"),
    dbc.Tab(label="Partial Dispatched", tab_id="partial_dispatched2"),
], id="tab_selection2", active_tab="all_dispatched2")
# this is the card for the selective blocks 
block_sales_card=dbc.Card(
    dbc.CardBody([
        html.P('TOTAL SALES INR :',style={"fontWeight": "bold",'font-size':'20px'}),
        html.Div(id='Total-block-sales',children='0',style={"marginBottom": "30px","fontWeight": "bold",'font-size':'20px'}),
        html.P('Total GST INR:',style={"fontWeight": "bold",'font-size':'20px'}),
        html.Div(id='block-gst',children='0',style={"marginBottom": "30px","fontWeight": "bold",'font-size':'20px'}),
        html.P('TRANSPORT INR:',style={"fontWeight": "bold",'font-size':'20px'}),
        html.Div(id='block-transport',children='0',style={"fontWeight": "bold",'font-size':'20px'}),

    ]),
    style={"width": "100%",'height':'100%'}
)
grid2=dag.AgGrid(
    id="table2",
    rowData=df2.to_dict("records"),
    columnDefs=[{"field": i,"cellDataType" : 'text'} for i in df2.columns[[1,2,29,30,31,32,33,34,35]]],
    # columnDefs=[{"field":'BLOCK NO',"cellDataType" : 'text' }],
    defaultColDef={"filter": True, "sortable": True, "resizable": True},
    className="ag-theme-alpine-dark",
    dashGridOptions={"pagination": True, "animateRows": False},
)
layout = dbc.Container(
    [dbc.Row(dcc.Dropdown(df2['COLOR NAME'].unique(),multi=True,value=df2['COLOR NAME'].unique()[0:2],id='dropdown1')),
     tabs2,
        dbc.Row(
            [ dbc.Col(card_sales,className="d-flex align-items-stretch" ,style={'margin-bottom': '20px'}),
            dbc.Col(card_pie_chart,style={'margin-bottom': '20px'}),  # Second card in its own row  # First card in its own row
    ]),
    dbc.Row([dbc.Col([
        dcc.Dropdown(id='blockselection2',placeholder='select the blocks',multi=True,value=df2['BLOCK NO'].unique()[0:3]),
        block_sales_card]

    ),
             dbc.Col(dcc.Graph(figure={},id='minigraph2'))]),
    

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
    Output(component_id='blockselection2',component_property='options'),
    Input(component_id='dropdown1',component_property='value'),
    Input(component_id='tab_selection2',component_property='active_tab')
)
def func(dropdown_value1,selected_tab):
    dff2=df2[df2['COLOR NAME'].isin(dropdown_value1)]
    if selected_tab == "all_dispatched2":
        dff2 = dff2[dff2['BALANCE SLABS'] == 0]  # all dispatched data
        # print('thiS is for all dispatched',dff2[['BALANCE SLABS','AMOUNT']])
    else:
        dff2=dff2[dff2['BALANCE SLABS'] != 0] 
        # print('this is for partial dispatched',dff2[['BALANCE SLABS','AMOUNT']])
    amount=round(sum(dff2['AMOUNT']),2)
    total_sales_amount=round(sum(dff2['TOTAL VALUE']),2)
    total_gst=round(sum(dff2['GST']),2)
    page2_blocks_value=dff2['BLOCK NO']
    total_transport=round(sum(dff2['ADJ TRANSPORT CHARGES PER BLOCK']))
    fig1=px.pie(values=[amount,total_gst,total_transport],labels=['AMOUNT','GST','TRANSPORT'],hole=0.4,names=['AMOUNT',"GST",'TRANSPORT']).update_layout(template="plotly_dark")
    histochart=px.histogram(dff2,x=dff2['BLOCK NO'],y=dff2['TOTAL VALUE']).update_layout(template="plotly_dark",xaxis=dict(type='category'))
    return fig1,total_sales_amount,total_gst,total_transport,histochart,page2_blocks_value

@callback(
    Output(component_id='Total-block-sales',component_property='children'),
    Output(component_id='block-gst',component_property='children'),
    Output(component_id='minigraph2',component_property='figure'),
    Output(component_id='block-transport',component_property='children'),
    Input(component_id='blockselection2',component_property='value')
)
def blockdropdown(block_value):
    if not block_value:
        return "", "", go.Figure(),""
    # print(block_value,[type(i) for i in block_value ])
    block_df2=df2[df2['BLOCK NO'].isin(block_value)]
    # print(block_df)
    total_sales_amount=round(sum(block_df2['TOTAL VALUE']),2)
    total_gst=round(sum(block_df2['GST']),2)
    block_transportation_amount=round(sum(block_df2['ADJ TRANSPORT CHARGES PER BLOCK']),2)
    page2fig2=px.histogram(block_df2,x=block_df2['BLOCK NO'],y=[block_df2['TOTAL VALUE'],block_df2['GST'],block_df2['ADJ TRANSPORT CHARGES PER BLOCK']])
    
    return total_sales_amount,total_gst,page2fig2,block_transportation_amount

