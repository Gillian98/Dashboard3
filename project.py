
# -*- coding: utf-8 -*-
"""
Created on Fri Jun 18 12:37:33 2021

@author: user
"""

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input,Output
import plotly.graph_objs as go
import pandas as pd
import numpy as np
import datetime
import plotly.express as px
import geojson
import plotly as plt

# import geopandas as gpd

df = pd.read_csv(r'fire_claims.csv')
loss_date=df['LOSSDATE']
# report_date=df['REPORTDATE']
df['LOSSDATE']=pd.to_datetime(loss_date,dayfirst=True)
# df['REPORTDATE']=pd.to_datetime(report_date,dayfirst=True)
df['LOSSYEAR']=df['LOSSYEAR'].astype(int)
df['LOSSQUARTER']=df['LOSSQUARTER'].astype(int)
df['LOSSMONTH']=df['LOSSMONTH'].astype(int)

df['LOB']=df['LOB'].astype(str)
df['BASE RATE']=df['BASE RATE'].astype(str)
df['RISK']=df['RISK'].astype(str)
df['CONSTN']=df['CONSTN'].astype(str)
df['PRODUCT']=df['PRODUCT'].astype(str)
df['PERILS']=df['PERILS'].astype(str)
df['DCHNL']=df['DCHNL'].astype(str)
df['ACCIDENT_OCCUR_GROUP']=df['ACCIDENT_OCCUR_GROUP'].astype(str)


def conditions4(df):
    if df['BUILDING_TYPE'] != ' ' :
        return 1
    else:
        return 0
df['BUILDING_TYPE_CNT']=df.apply(conditions4, axis=1)
    

df=df.fillna(0)
df_bydate_sum=df.groupby(['LOSSYEAR','LOSSQUARTER'])[['PAIDLS','BALOS','INCTOT','INCCNT']].sum().reset_index()
df_bydate_count=df.groupby(['LOSSYEAR','LOSSQUARTER'])[['PAIDLS','BALOS','INCTOT','INCCNT']].count().reset_index()


latest_quarter=(df_bydate_sum['LOSSQUARTER'].iloc[-1])
latest_year=(df_bydate_sum['LOSSYEAR'].iloc[-1])

if latest_quarter == 1:
    latest_month = 3
elif latest_quarter == 2:
    latest_month = 6
elif latest_quarter == 3:
    latest_month = 9    
elif latest_quarter == 4:
    latest_month = 12
    

df_map = pd.read_csv(r'fire_claims.csv', dtype=object)
df_map['LAT'] = df_map['LAT'].astype(float)
df_map['LOT'] = df_map['LOT'].astype(float)
df_map['LOSSYEAR'] = df_map['LOSSYEAR'].astype(int)
df_map['PAIDLS'] = df_map['PAIDLS'].astype(float)
df_map['BALOS'] = df_map['BALOS'].astype(float)
df_map['INCTOT'] = df_map['INCTOT'].astype(float)
df_map['INCCNT'] = df_map['INCCNT'].astype(float)
df_map.drop(df_map.index[df_map['LOT'] == 0], inplace = True)
df_map.drop(df_map.index[df_map['LAT'] == 0], inplace = True)
df_map=df_map.reset_index(drop=True)
          
import json
with open(r"map4.geojson") as f:
    geojson = geojson.load(f)
for feature in geojson['features']:
    print(feature['properties'])
    

app = dash.Dash(__name__, suppress_callback_exceptions=True, 
                meta_tags=[{"name": "viewport", "content": "width=device-width"}],
                include_assets_files=True,
                title='ISM Location Analytics')

server = app.server


app.layout = html.Div([
    html.Div([
        html.Div([
            html.Img(src=app.get_asset_url('logo.png'),
                      style={
                          'height':'100px',
                          'width':'auto',
                          'margin-bottom':'25px',
                          },
                      )
        ],className='one-third column',
        ),
        
        html.Div([
            html.Div([
                html.Div('Location Analytics',style={'font-size':50,'textAlign':'center','margin-bottom':'8px','color':'white'}),
                ])
            ],className='one-half column',
            ),
        
        html.Div([
            html.Div([
                html.H3('Fire Insurance',style={'font-size':50,'textAlign':'center','margin-top':'8px','color':'white'}),
                ])
            ],className='one-third column',
            ),
        
        ],id='header',className='row flex-display',style={'margin-bottom':'25px'}),
     
    
    dcc.Tabs(
        id="tabs-with-classes",
        value='Overview',
        parent_className='custom-tabs',
        className='custom-tabs-container',
        children=[
            dcc.Tab(
                label='Overview',
                value='Overview',
                className='custom-tab',
                selected_className='custom-tab--selected',
                style={'font-size': '150%','height': '50%'},
            ),           
            dcc.Tab(
                label='Map',
                value='Map',
                className='custom-tab',
                selected_className='custom-tab--selected',
                style={'font-size': '150%','height': '50%'},
            ),       
            dcc.Tab(
                label='Statistics',
                value='Statistics',
                className='custom-tab',
                selected_className='custom-tab--selected',
                style={'font-size': '150%','height': '50%'},
            ),
            dcc.Tab(
                label='Breakdown',
                value='Breakdown',
                className='custom-tab',
                selected_className='custom-tab--selected',
                style={'font-size': '150%','height': '50%'},
            ), 
            dcc.Tab(
                label='Interactive Analysis',
                value='Interactive Analysis',
                className='custom-tab',
                selected_className='custom-tab--selected',
                style={'font-size': '150%','height': '50%'},
            ),               

        ]),
    html.Div(id='tabs-content-classes')
])


#########################################################################################################


@app.callback(Output('tabs-content-classes', 'children'),
              Input('tabs-with-classes', 'value'))

def render_content(tab):
    
    def sum_value(month,year,data_type):
        latest_value=round(df_bydate_sum[(df_bydate_sum['LOSSQUARTER']==latest_quarter)&(df_bydate_sum['LOSSYEAR']==latest_year)][data_type].iloc[-1])
        previous_quarter_value=round(df_bydate_sum[(df_bydate_sum['LOSSQUARTER']==(latest_quarter-1))&(df_bydate_sum['LOSSYEAR']==latest_year)][data_type].iloc[-1])
        previous_year_value=round(df_bydate_sum[(df_bydate_sum['LOSSQUARTER']==latest_quarter)&(df_bydate_sum['LOSSYEAR']==(latest_year-1))][data_type].iloc[-1])   
        quarter_diff=round(latest_value-previous_quarter_value)
        year_diff=round(latest_value-previous_year_value)    
        quarter_rate=round(quarter_diff/previous_quarter_value*100,2)
        year_rate=round(year_diff/previous_year_value*100,2)
        return latest_value,quarter_diff,quarter_rate,year_diff,year_rate   
    
    if tab == 'Overview':  
        
        return html.Div([
            
            html.Div([
                html.H1(''),                
            ],className='row flex-display'),   
            
            html.Div([
                html.H1(''),                
            ],className='row flex-display'),   
            
           ########## First Row ###########            
            html.Div([
                html.Div([
                    html.Div([
                        html.H2('Fire Insurance in Malaysia (2016-2020)',style={'color':'white'}),
                        ]),
                    html.Div([
                        html.H4('Last Updated: ' + datetime.date(1900, latest_month, 1).strftime('%B') + ' ' + str(latest_year),
                                style={'color':'white'}),
                        ]),
                    html.Div([
                        html.H4('Claims - Accident Year',
                                style={'color':'white'}),
                            ]),
                    ]),
                        
            ],className='row flex-display'), 

           ########## Second Row ###########            
            # html.Div([
            #     html.H3('Location analytics is the process or the ability to gain insight from the location or geographic component of business data. In this webpage, the presentation and interpretation of the claims data will be focus on the analysis by states and districts in Malaysia. Here, the claims data used is based on Accident Year basis.'
            #         ,style={'color':'orange'}),
            #     # ],className='one-third column',id='title1'), 
            # ],className='row flex-display'),           
            
            html.Div([
                html.H1(''),                
            ],className='row flex-display'),   
            
            
           ########## Third Row ###########            
            html.Div([
                html.Div([
                    html.H6(children='Total Incurred Claims Count',
                            style={'textAlign':'center',
                                   'color':'white',
                                   'fontSize':30}
                            ),
                    html.P(format(sum_value(latest_quarter,latest_year,'INCCNT')[0],','),
                           style={'textAlign':'center',
                                  'color':'orange',
                                  'fontSize':50}
                            ),
                    html.P('QoQ: ' + format(sum_value(latest_quarter,latest_year,'INCCNT')[1],',')
                           + ' (' + format(sum_value(latest_quarter,latest_year,'INCCNT')[2],',') + '%)',
                           style={'textAlign':'center',
                                  'color':'white',
                                  'fontSize':20,
                                  'margin-top':'-10px'} 
                           ),
                    html.P('YoY: ' + format(sum_value(latest_quarter,latest_year,'INCCNT')[3],',')
                           + ' (' + format(sum_value(latest_quarter,latest_year,'INCCNT')[4],',') + '%)',
                           style={'textAlign':'center',
                                  'color':'white',
                                  'fontSize':20,
                                  'margin-top':'-10px'} 
                           )],className='card_container four columns',
                    ),
                
                html.Div([
                    html.H6(children='Total Claims Paid',
                            style={'textAlign':'center',
                                   'color':'white',
                                   'fontSize':30}
                            ),
                    html.P(format(sum_value(latest_quarter,latest_year,'PAIDLS')[0],','),
                           style={'textAlign':'center',
                                  'color':'orange',
                                  'fontSize':50}
                           ),
                    html.P('QoQ: ' + format(sum_value(latest_quarter,latest_year,'PAIDLS')[1],',')
                           + ' (' + format(sum_value(latest_quarter,latest_year,'PAIDLS')[2],',') + '%)',                  
                           style={'textAlign':'center',
                                  'color':'white',
                                  'fontSize':20,
                                  'margin-top':'-10px'} 
                           ),                    
                    html.P('YoY: ' + format(sum_value(latest_quarter,latest_year,'PAIDLS')[3],',')
                           + ' (' + format(sum_value(latest_quarter,latest_year,'PAIDLS')[4],',') + '%)',
                           style={'textAlign':'center',
                                  'color':'white',
                                  'fontSize':20,
                                  'margin-top':'-10px'}         
                        )],className='card_container four columns',
                    ),                
            
                html.Div([
                    html.H6(children='Total Claims Incurred',
                            style={'textAlign':'center',
                                   'color':'white',
                                   'fontSize':30}
                            ),
                    html.P(format(sum_value(latest_quarter,latest_year,'INCTOT')[0],','),
                           style={'textAlign':'center',
                                  'color':'orange',
                                  'fontSize':50}
                           ),
                    html.P('QoQ: ' + format(sum_value(latest_quarter,latest_year,'INCTOT')[1],',')
                           + ' (' + format(sum_value(latest_quarter,latest_year,'INCTOT')[2],',') + '%)',
                           style={'textAlign':'center',
                                  'color':'white',
                                  'fontSize':20,
                                  'margin-top':'-10px'} 
                           ),
                    html.P('YoY: ' + format(sum_value(latest_quarter,latest_year,'INCTOT')[3],',')
                           + ' (' + format(sum_value(latest_quarter,latest_year,'INCTOT')[4],',') + '%)',
                           style={'textAlign':'center',
                                  'color':'white',
                                  'fontSize':20,
                                  'margin-top':'-10px'}         
                        )],className='card_container four columns',
                    ),                   
    
                html.Div([
                    html.H6(children='Total Claims Outstanding',
                            style={'textAlign':'center',
                                   'color':'white',
                                   'fontSize':30}
                            ),
                    html.P(format(sum_value(latest_quarter,latest_year,'BALOS')[0],','),
                           style={'textAlign':'center',
                                  'color':'orange',
                                  'fontSize':50}
                           ),
                    html.P('QoQ: ' + format(sum_value(latest_quarter,latest_year,'INCTOT')[1],',')
                           + ' (' + format(sum_value(latest_quarter,latest_year,'INCTOT')[2],',') + '%)',
                           style={'textAlign':'center',
                                  'color':'white',
                                  'fontSize':20,
                                  'margin-top':'-10px'} 
                           ),
                    html.P('YoY: ' + format(sum_value(latest_quarter,latest_year,'INCTOT')[3],',')
                           + ' (' + format(sum_value(latest_quarter,latest_year,'INCTOT')[4],',') + '%)',
                           style={'textAlign':'center',
                                  'color':'white',
                                  'fontSize':20,
                                  'margin-top':'-10px'}                 
                    )],className='card_container four columns',
                    ) 
               ],className='row flex-display'),            
            
            
           ########## Forth Row ###########            
           html.Div([
                html.Div([
                    html.Video(src=app.get_asset_url('PAIDLS.mp4'),
                               autoPlay=True,
                               controls=True,
                               poster='',
                               style={
                               'height':'500px',
                               'width':'100%',
                               # 'margin-bottom':'25px',
                               },
                               )
                    ],className='create_container six columns'),
                
                html.Div([                    
                    html.Video(src=app.get_asset_url('BALOS.mp4'),
                               autoPlay=True,
                               controls=True,
                               poster='',
                               style={
                               'height':'500px',
                               'width':'100%',
                               # 'margin-bottom':'25px',
                               },
                               )                    
                    ],className='create_container six columns'),
                ],className='row flex-display'),               


            ############### Fifth Row  #################                            
            html.Div([
                html.Div([
                    html.Video(src=app.get_asset_url('INCCNT.mp4'),
                               autoPlay=True,
                               controls=True,
                               poster='',
                               style={
                               'height':'500px',
                               'width':'100%',
                               # 'margin-bottom':'25px',
                               },
                               )
                    ],className='create_container six columns'),
                
                html.Div([                    
                    html.Video(src=app.get_asset_url('INCTOT.mp4'),
                               autoPlay=True,
                               controls=True,
                               poster='',
                               style={
                               'height':'500px',
                               'width':'100%',
                               # 'margin-bottom':'25px',
                               },
                               )                    
                    ],className='create_container six columns'),
                ],className='row flex-display'),             

            ])
    
    elif tab == 'Interactive Analysis':  
        return html.Div([
            ########## First Row ###########
            html.Div([                                               
                html.Div([            
                    html.P('Select Data Type:',className='fix_label',
                            style={'color':'white'}
                            ),
                    dcc.Dropdown(id='w_data_type',
                                  multi=False,
                                  clearable=True,
                                  value='PAIDLS',
                                  placeholder='Select Data Type',
                                  options=[{'label':'Total Claims Paid','value':'PAIDLS'},
                                            {'label':'Total Claims Count','value':'INCCNT'},
                                            {'label':'Total Claims Outstanding','value':'BALOS'},
                                            {'label':'Total Claims Incurred','value':'INCTOT'}
                                      ],className='dcc_compon'),  
                    ],className='create_container three columns'),

                html.Div([                    
                    html.P('Select Independent Variable:',className='fix_label',
                            style={'color':'white'}
                            ),
                    dcc.Dropdown(id='w_ind_var_type',
                                 multi=False,
                                 clearable=True,
                                 value='STATES',
                                 placeholder='Select Data Type',
                                 options=[{'label':'State','value':'STATES'},
                                          {'label':'Line of Business','value':'LOB'},
                                          {'label':'Base Rate','value':'BASE RATE'},
                                          {'label':'Contruction','value':'CONSTN'},
                                          {'label':'Fire Product','value':'PRODUCT'},
                                          {'label':'Distribution Channel','value':'DCHNL'}                                          
                                          ],className='dcc_compon'), 
                    ],className='create_container three columns'),   
                
                html.Div([                    
                    html.P('Select Dependent Variable:',className='fix_label',
                            style={'color':'white'}
                            ),
                    dcc.Dropdown(id='w_dep_var_type',
                                 multi=False,
                                 clearable=True,
                                 value='LOB',
                                 placeholder='Select Data Type',                               
                                 className='dcc_compon'), 
                    ],className='create_container three columns'),                   
                                                                             
                html.Div([            
                    html.P('Select Comparison Variable 1: ',className='fix_label',
                            style={'color':'white'}
                            ),
                    dcc.Dropdown(id='w_breakdown1',
                                  multi=False,
                                  clearable=True,
                                  placeholder='Select Breakdown',
                                  className='dcc_compon'),
                    ],className='create_container three columns'),

                html.Div([            
                    html.P('Select Comparison Variable 2: ',className='fix_label',
                            style={'color':'white'}
                            ),
                    dcc.Dropdown(id='w_breakdown2',
                                  multi=False,
                                  clearable=True,
                                  placeholder='Select Breakdown',
                                 className='dcc_compon'),
                    ],className='create_container three columns'),
                                          
                ],className='row flex-display'),    


            ########## Second Row ###########
            html.Div([                                               
                html.Div([
                    dcc.Graph(id='butterfly',
                              config={'displayModeBar':'hover'}),
                    ],className='create_container twelve columns'), 
                
                ],className='row flex-display'), 
            ]),              
                           
            
#########################################################################################################
        
    elif tab == 'Statistics':
        return html.Div([
            ############### First Row  #################                
            html.Div([                                               
                html.Div([
                    html.P('Select Data Type:',className='fix_label',
                            style={'color':'white'}
                            ),
                    dcc.Dropdown(id='w_data_type',
                                  multi=False,
                                  clearable=True,
                                  value='PAIDLS',
                                  placeholder='Select Data Type',
                                  options=[{'label':'Total Claims Paid','value':'PAIDLS'},
                                           {'label':'Total Claims Count','value':'INCCNT'},
                                           {'label':'Total Claims Outstanding','value':'BALOS'},
                                           {'label':'Total Claims Incurred','value':'INCTOT'}
                                      ],className='dcc_compon'),  
                    ],className='create_container six columns',id='cross-filter-options'),

                html.Div([
                    html.P('Select Year:',className='fix_label',
                            style={'color':'white'}
                            ),
                    dcc.Dropdown(id='radio_items',
                                  multi=False,
                                  clearable=True,
                                  value='2020',
                                  placeholder='Select Year',
                                  options=[{'label': '2016', 'value': '2016'},
                                          {'label': '2017', 'value': '2017'},
                                          {'label': '2018', 'value': '2018'},
                                          {'label': '2019', 'value': '2019'},
                                          {'label': '2020', 'value': '2020'},
                                      ],className='dcc_compon'),  
                    ],className='create_container six columns'),
            ],className='row flex-display'),
                
            ############### Second Row  #################                                
            html.Div([
                html.Div([
                    dcc.Graph(id='treemap',
                              config={'displayModeBar':'hover'}),
                    ],className='create_container twelve columns'),
                
                ],className='row flex-display'),
                

            ############### Third Row  #################                                
            html.Div([
                html.Div([
                    dcc.Dropdown(id='w_state',
                                  multi=False,
                                  clearable=True,
                                  value='Malaysia',
                                  placeholder='Select Data Type',
                                  options=[{'label':'Malaysia','value':'Malaysia'},
                                            {'label':'Johor','value':'Johor'},
                                            {'label':'Kedah','value':'Kedah'},
                                            {'label':'Kelantan','value':'Kelantan'},
                                            {'label':'Melaka','value':'Melaka'},
                                            {'label':'Negeri Sembilan','value':'Negeri Sembilan'},
                                            {'label':'Pahang','value':'Pahang'},
                                            {'label':'Perak','value':'Perak'},
                                            {'label':'Perlis','value':'Perlis'},
                                            {'label':'Pulau Pinang','value':'Pulau Pinang'},
                                            {'label':'Sabah','value':'Sabah'},
                                            {'label':'Sarawak','value':'Sarawak'},
                                            {'label':'Selangor','value':'Selangor'},
                                            {'label':'Terengganu','value':'Terengganu'},
                                            {'label':'WP Kuala Lumpur','value':'WP Kuala Lumpur'},
                                            {'label':'WP Labuan','value':'WP Labuan'},
                                            {'label':'WP Putrajaya','value':'WP Putrajaya'}
                                      ],className='dcc_compon'), 
                    ],className='create_container twelve columns'),
                
                ],className='row flex-display'), 
                
                
            ############### Forth Row  #################                                
            html.Div([                
                html.Div([
                    dcc.Graph(id='quarterly_chart',
                              config={'displayModeBar':'hover'}),
                    ],className='create_container six columns'),
                    
                
                html.Div([  
                    dcc.Graph(id='monthly_chart',
                              config={'displayModeBar':'hover'}),
                    ],className='create_container six columns'),

                ],className='row flex-display'),   
                
                
            ############### Fifth Row  #################                                
            html.Div([  
                html.Div([
                    dcc.Graph(id='RC_pie_chart',
                              config={'displayModeBar':'hover'}),
                    ],className='create_container six columns'),
                 
                html.Div([
                    dcc.Graph(id='RC_bar_chart',
                              config={'displayModeBar':'hover'}),
                    ],className='create_container six columns'),
                
                ],className='row flex-display'),                    

                
            ############### Sixth Row  #################                                
            html.Div([  
                html.Div([
                    dcc.Graph(id='report_claims_area_chart',
                              config={'displayModeBar':'hover'}),
                    ],className='create_container six columns'),                 
                
                html.Div([
                    dcc.Graph(id='report_claims_bar_chart',
                              config={'displayModeBar':'hover'}),
                    ],className='create_container six columns'),                   
            
                ],className='row flex-display'),                    
                          

            ############### Seventh Row  #################                                
            html.Div([  
                html.Div([
                    dcc.Graph(id='accident_happen_area_chart',
                              config={'displayModeBar':'hover'}),
                    ],className='create_container six columns'),                 
                
                html.Div([
                    dcc.Graph(id='accident_happen_bar_chart',
                              config={'displayModeBar':'hover'}),
                    ],className='create_container six columns'),                   
            
                ],className='row flex-display'), 
            
            
            ############### Eighth Row  #################                                
            html.Div([  
                html.Div([
                    dcc.Graph(id='CY_pie_chart',
                              config={'displayModeBar':'hover'}),
                    ],className='create_container six columns'),
                 
                html.Div([
                    dcc.Graph(id='CY_bar_chart',
                              config={'displayModeBar':'hover'}),
                    ],className='create_container six columns'),
                
                ],className='row flex-display'),            


            ############### Nineth Row  #################                                
            html.Div([  
                html.Div([
                    dcc.Graph(id='BH_pie_chart',
                              config={'displayModeBar':'hover'}),
                    ],className='create_container six columns'),
                 
                html.Div([
                    dcc.Graph(id='BH_bar_chart',
                              config={'displayModeBar':'hover'}),
                    ],className='create_container six columns'),
                
                ],className='row flex-display'), 

            
            ],id='mainContainer',
            style={'display':'flex',
                    'flex-direction':'column'})   

#########################################################################################################
    
    elif tab == 'Breakdown':
        return html.Div([
            ########## First Row ###########
            html.Div([                                                                                            
                html.Div([            
                    html.P('Select Data Type:',className='fix_label',
                            style={'color':'white'}
                            ),
                    dcc.Dropdown(id='w_data_type',
                                  multi=False,
                                  clearable=True,
                                  value='PAIDLS',
                                  placeholder='Select Data Type',
                                  options=[{'label':'Total Claims Paid','value':'PAIDLS'},
                                            {'label':'Total Claims Count','value':'INCCNT'},
                                            {'label':'Total Claims Outstanding','value':'BALOS'},
                                            {'label':'Total Claims Incurred','value':'INCTOT'}
                                      ],className='dcc_compon'),  
                    ],className='create_container four columns'),
                
                html.Div([            
                    html.P('Select Year:',className='fix_label',
                            style={'color':'white'}
                            ),
                    dcc.Dropdown(id='radio_items',
                                  multi=False,
                                  clearable=True,
                                  value='2020',
                                  placeholder='Select Year',
                                  options=[{'label': '2016', 'value': '2016'},
                                          {'label': '2017', 'value': '2017'},
                                          {'label': '2018', 'value': '2018'},
                                          {'label': '2019', 'value': '2019'},
                                          {'label': '2020', 'value': '2020'},
                                      ],className='dcc_compon'),  
                    ],className='create_container four columns'),   

                html.Div([
                    html.P('Select Variable Type:',className='fix_label',
                            style={'color':'white'}
                            ),
                    dcc.Dropdown(id='w_var_type',
                                 multi=False,
                                 clearable=True,
                                 value='LOB',
                                 placeholder='Select Data Type',
                                 options=[{'label':'Line of Business','value':'LOB'},
                                          {'label':'Risk Code','value':'RISK'},
                                          {'label':'Base Rate','value':'BASE RATE'},
                                          {'label':'Contruction','value':'CONSTN'},
                                          {'label':'Fire Product','value':'PRODUCT'},
                                          # {'label':'Perils','value':'PERILS'},
                                          {'label':'Distribution Channel','value':'DCHNL'}                                          
                                          ],className='dcc_compon'), 
                    ],className='create_container four columns'),                 
                
                html.Div([            
                    html.P('Select Breakdown: ',className='fix_label',
                            style={'color':'white'}
                            ),
                    dcc.Dropdown(id='w_breakdown',
                                  multi=False,
                                  clearable=True,
                                  placeholder='Select Breakdown',
                                className='dcc_compon'),
                    ],className='create_container four columns'),                
                                          
                ],className='row flex-display'), 
            
            
            ############### Second Row  #################                                
            html.Div([
                html.Div([
                    dcc.Graph(id='var_treemap',
                              config={'displayModeBar':'hover'}),
                    ],className='create_container twelve columns'),

                ],className='row flex-display'),
                

            ############### Third Row  #################                                
            html.Div([
                html.Div([
                    dcc.Dropdown(id='w_state',
                                  multi=False,
                                  clearable=True,
                                  value='Malaysia',
                                  placeholder='Select Data Type',
                                  options=[{'label':'Malaysia','value':'Malaysia'},
                                            {'label':'Johor','value':'Johor'},
                                            {'label':'Kedah','value':'Kedah'},
                                            {'label':'Kelantan','value':'Kelantan'},
                                            {'label':'Melaka','value':'Melaka'},
                                            {'label':'Negeri Sembilan','value':'Negeri Sembilan'},
                                            {'label':'Pahang','value':'Pahang'},
                                            {'label':'Perak','value':'Perak'},
                                            {'label':'Perlis','value':'Perlis'},
                                            {'label':'Pulau Pinang','value':'Pulau Pinang'},
                                            {'label':'Sabah','value':'Sabah'},
                                            {'label':'Sarawak','value':'Sarawak'},
                                            {'label':'Selangor','value':'Selangor'},
                                            {'label':'Terengganu','value':'Terengganu'},
                                            {'label':'WP Kuala Lumpur','value':'WP Kuala Lumpur'},
                                            {'label':'WP Labuan','value':'WP Labuan'},
                                            {'label':'WP Putrajaya','value':'WP Putrajaya'}
                                      ],className='dcc_compon'), 
                    ],className='create_container twelve columns'),
                
                ],className='row flex-display'), 
                
                
            ############### Forth Row  #################                                
            html.Div([                
                html.Div([
                    dcc.Graph(id='var_quarterly_chart',
                              config={'displayModeBar':'hover'}),
                    ],className='create_container six columns'),
                    
                
                html.Div([  
                    dcc.Graph(id='var_monthly_chart',
                              config={'displayModeBar':'hover'}),
                    ],className='create_container six columns'),

                ],className='row flex-display'),   
                
                
            ############### Fifth Row  #################                                
            html.Div([  
                html.Div([
                    dcc.Graph(id='var_RC_pie_chart',
                              config={'displayModeBar':'hover'}),
                    ],className='create_container six columns'),
                 
                html.Div([
                    dcc.Graph(id='var_RC_bar_chart',
                              config={'displayModeBar':'hover'}),
                    ],className='create_container six columns'),
                
                ],className='row flex-display'),                    

                
            ############### Sixth Row  #################                                
            html.Div([  
                html.Div([
                    dcc.Graph(id='var_report_claims_area_chart',
                              config={'displayModeBar':'hover'}),
                    ],className='create_container six columns'),                 
                
                html.Div([
                    dcc.Graph(id='var_report_claims_bar_chart',
                              config={'displayModeBar':'hover'}),
                    ],className='create_container six columns'),                   
            
                ],className='row flex-display'),                    
                          

            ############### Seventh Row  #################                                
            html.Div([  
                html.Div([
                    dcc.Graph(id='var_accident_happen_area_chart',
                              config={'displayModeBar':'hover'}),
                    ],className='create_container six columns'),                 
                
                html.Div([
                    dcc.Graph(id='var_accident_happen_bar_chart',
                              config={'displayModeBar':'hover'}),
                    ],className='create_container six columns'),                   
            
                ],className='row flex-display'), 


            ############### Eighth Row  #################                                
            html.Div([  
                html.Div([
                    dcc.Graph(id='var_CY_pie_chart',
                              config={'displayModeBar':'hover'}),
                    ],className='create_container six columns'),
                 
                html.Div([
                    dcc.Graph(id='var_CY_bar_chart',
                              config={'displayModeBar':'hover'}),
                    ],className='create_container six columns'),
                
                ],className='row flex-display'), 
            
            
            ############### Eighth Row  #################                                
            html.Div([  
                html.Div([
                    dcc.Graph(id='var_BH_pie_chart',
                              config={'displayModeBar':'hover'}),
                    ],className='create_container six columns'),
                 
                html.Div([
                    dcc.Graph(id='var_BH_bar_chart',
                              config={'displayModeBar':'hover'}),
                    ],className='create_container six columns'),
                
                ],className='row flex-display'), 
            
            
            ],id='mainContainer',
            style={'display':'flex',
                    'flex-direction':'column'})                       
    
#########################################################################################################
     
    elif tab == 'Map':
        return html.Div([
            # html.H3(),
            html.Div([
                html.Div([            
                    html.P('Select Data Type:',className='fix_label',
                            style={'color':'white'}
                            ),
                    dcc.Dropdown(id='w_data_type',
                                  multi=False,
                                  clearable=True,
                                  value='PAIDLS',
                                  placeholder='Select Data Type',
                                  options=[{'label':'Total Claims Paid','value':'PAIDLS'},
                                            {'label':'Total Claims Count','value':'INCCNT'},
                                            {'label':'Total Claims Outstanding','value':'BALOS'},
                                            {'label':'Total Claims Incurred','value':'INCTOT'}
                                      ],className='dcc_compon'),  
                    ],className='create_container six columns'),
                
                # html.Div([            
                #     html.P('Select Year:',className='fix_label',
                #             style={'color':'white'}
                #             ),                
                #     dcc.Dropdown(id='radio_items',
                #                   multi=False,
                #                   clearable=True,
                #                   value='2020',
                #                   placeholder='Select Year',
                #                   options=[{'label': '2016', 'value': '2016'},
                #                           {'label': '2017', 'value': '2017'},
                #                           {'label': '2018', 'value': '2018'},
                #                           {'label': '2019', 'value': '2019'},
                #                           {'label': '2020', 'value': '2020'},
                #                       ],className='dcc_compon'),  
                #     ],className='create_container four columns'),                
        
                 
                html.Div([            
                    html.P('Select Map Type:',className='fix_label',
                            style={'color':'white'}
                            ),                
                    dcc.Dropdown(id='map_type',
                                  multi=False,
                                  clearable=True,
                                  value='choropleth',
                                  placeholder='Select Map Type',
                                  options=[{'label': 'Choropleth', 'value': 'choropleth'},
                                          {'label': 'Bubble', 'value': 'bubble'},
                                      ],className='dcc_compon'),  
                    ],className='create_container six columns'),                
                
                ],className='row flex-display'),              


            ############### Second Row  #################                                
            html.Div([    
                html.Div([
                    dcc.Graph(id='map',
                               style={
                               'height':'800px',
                               'width':'100%'}) ,
                    ],className='create_container twelve columns'),

                ],className='row flex-display'),  
            
            ############### Third Row  #################                                
            html.Div([
                html.Div([
                    dcc.Dropdown(id='w_state',
                                  multi=False,
                                  clearable=True,
                                  value='Malaysia',
                                  placeholder='Select Data Type',
                                  options=[{'label':'Malaysia','value':'Malaysia'},
                                            {'label':'Johor','value':'Johor'},
                                            {'label':'Kedah','value':'Kedah'},
                                            {'label':'Kelantan','value':'Kelantan'},
                                            {'label':'Melaka','value':'Melaka'},
                                            {'label':'Negeri Sembilan','value':'Negeri Sembilan'},
                                            {'label':'Pahang','value':'Pahang'},
                                            {'label':'Perak','value':'Perak'},
                                            {'label':'Perlis','value':'Perlis'},
                                            {'label':'Pulau Pinang','value':'Pulau Pinang'},
                                            {'label':'Sabah','value':'Sabah'},
                                            {'label':'Sarawak','value':'Sarawak'},
                                            {'label':'Selangor','value':'Selangor'},
                                            {'label':'Terengganu','value':'Terengganu'},
                                            {'label':'WP Kuala Lumpur','value':'WP Kuala Lumpur'},
                                            {'label':'WP Labuan','value':'WP Labuan'},
                                            {'label':'WP Putrajaya','value':'WP Putrajaya'}
                                      ],className='dcc_compon'), 
                    ],className='create_container twelve columns'),
                
                ],className='row flex-display'), 


            ############### Forth Row  #################                                
            html.Div([    
                html.Div([
                    dcc.Graph(id='line_chart',
                              style={
                               'height':'800px',
                               'width':'100%'},
                              animate=True
                               ) ,

                    # dcc.Interval(
                    #     id = 'graph-update',
                    #     interval = 1*1000,
                    #     n_intervals = 0,
                    #     )
                    
                    ],className='create_container twelve columns'),

                ],className='row flex-display'), 
          
            
            
            ],id='mainContainer',
            style={'display':'flex',
                    'flex-direction':'column'})      
                    
#########################################################################################################

@app.callback(
    Output('w_dep_var_type', 'options'),
    [Input('w_ind_var_type', 'value')])    
def set_options(w_ind_var_type):
    if w_ind_var_type == 'STATES':
        return [
                {'label':'Line of Business','value':'LOB'},
                {'label':'Risk Code','value':'RISK'},                                          
                {'label':'Base Rate','value':'BASE RATE'},
                {'label':'Contruction','value':'CONSTN'},
                {'label':'Fire Product','value':'PRODUCT'},
                {'label':'Distribution Channel','value':'DCHNL'},
            ]

    elif w_ind_var_type == 'LOB':
        return [
                {'label':'State','value':'STATES'}  ,
                {'label':'Risk Code','value':'RISK'},                                          
                {'label':'Base Rate','value':'BASE RATE'},
                {'label':'Contruction','value':'CONSTN'},
                {'label':'Fire Product','value':'PRODUCT'},
                {'label':'Distribution Channel','value':'DCHNL'}
            ]

    elif w_ind_var_type == 'BASE RATE':
        return [
                {'label':'Line of Business','value':'LOB'},
                {'label':'Risk Code','value':'RISK'},                                          
                {'label':'Contruction','value':'CONSTN'},
                {'label':'Fire Product','value':'PRODUCT'},
                {'label':'Distribution Channel','value':'DCHNL'},
                {'label':'State','value':'STATES'}  
            ]

    elif w_ind_var_type == 'CONSTN':
        return [
                {'label':'Line of Business','value':'LOB'},
                {'label':'Risk Code','value':'RISK'},                                          
                {'label':'Base Rate','value':'BASE RATE'},
                {'label':'Fire Product','value':'PRODUCT'},
                {'label':'Distribution Channel','value':'DCHNL'},
                {'label':'State','value':'STATES'}  
            ]
    
    elif w_ind_var_type == 'PRODUCT':
        return [
                {'label':'Line of Business','value':'LOB'},
                {'label':'Risk Code','value':'RISK'},                                          
                {'label':'Base Rate','value':'BASE RATE'},
                {'label':'Contruction','value':'CONSTN'},
                {'label':'Distribution Channel','value':'DCHNL'},
                {'label':'State','value':'STATES'}  
            ]
    
    elif w_ind_var_type == 'DCHNL':
        return [
                {'label':'Line of Business','value':'LOB'},
                {'label':'Risk Code','value':'RISK'},                                          
                {'label':'Base Rate','value':'BASE RATE'},
                {'label':'Contruction','value':'CONSTN'},
                {'label':'Fire Product','value':'PRODUCT'},
                {'label':'State','value':'STATES'}  
            ]    
    
@app.callback(
    Output('w_dep_var_type', 'value'),
    [Input('w_dep_var_type', 'options')])
def set_options_value(w_dep_var_type):
    return w_dep_var_type[5]['value']               
                
#########################################################################################################
 

@app.callback(
    Output('w_breakdown1', 'options'),
    [Input('w_dep_var_type', 'value')])
def set_options(w_dep_var_type):
    if w_dep_var_type == 'LOB':
        return [{'label': 'Fire-Material Damage', 'value': '1'},
                {'label': 'Fire-Consequential Damage', 'value': '2'},
                {'label': 'Houseowner', 'value': '3'},
                {'label': 'Householder', 'value': '4'},
                {'label': 'Plantations', 'value': '5'},
                {'label': 'Industrial All Risks - Section 1', 'value': '6'},
                {'label': 'Industrial All Risks - Section 2', 'value': '7'},
                {'label': 'Fire-Consequential Loss (Standalone)', 'value': '8'},
                # {'label': 'Error', 'value': '-1'}
                ]
    
    elif w_dep_var_type == 'RISK':   
        return [{'label': 'Residential', 'value': '10'},
                {'label': 'Retail', 'value': '11'},
                {'label': 'Hotel, Office', 'value': '12'},
                {'label': 'Mining', 'value': '13'},
                {'label': 'Construction', 'value': '14'},
                {'label': 'Food Processing', 'value': '15'},
                {'label': 'Beverage', 'value': '16'},
                {'label': 'Tobacco', 'value': '17'},
                {'label': 'Textiles', 'value': '18'},
                {'label': 'Leather & Fibre', 'value': '19'},
                {'label': 'Timber', 'value': '20'},
                {'label': 'Paper & Printing', 'value': '21'},
                {'label': 'Chemicals', 'value': '22'},
                {'label': 'Petroleum', 'value': '23'},
                {'label': 'Rubber', 'value': '24'},
                {'label': 'Plastics', 'value': '25'},
                {'label': 'Non-metalic minerals', 'value': '26'},
                {'label': 'Metal Working, Engineering', 'value': '27'},
                {'label': 'Motor Trade and Related Risks', 'value': '28'},
                {'label': 'Restaurants, Places of recreation', 'value': '29'},
                {'label': 'Utilities', 'value': '30'},
                {'label': 'Transport', 'value': '31'},
                {'label': 'Cinemas, studios & exhibition halls', 'value': '33'},
                {'label': 'General Storage', 'value': '34'},
                {'label': 'Oil Mill', 'value': '35'},
                {'label': 'Rice & Flour Mills', 'value': '36'},
                {'label': 'Sugar Factory', 'value': '37'},
                {'label': 'Cocoa, Coffee & Tea Factories', 'value': '38'},
                {'label': 'Cold stores', 'value': '39'},
                {'label': 'Houseowners & Householders', 'value': '40'},
                {'label': 'Plantations', 'value': '50'},
                # {'label': 'Error', 'value': '-1'}
                               
                ]

    elif w_dep_var_type == 'BASE RATE':
        return [{'label': 'Tariff', 'value': '0'},
                {'label': 'Self-Rating', 'value': '1'},
                {'label': 'Special Rating', 'value': '2'},
                {'label': 'Large & Specialized Risk', 'value': '3'},
                {'label': 'Industrial All Risks', 'value': '4'},
                {'label': 'Non-Tariff', 'value': '5'},
                # {'label': 'Error', 'value': '-1'}
                ]

    elif w_dep_var_type == 'CONSTN':
        return [{'label': 'Class 1A', 'value': '1'},
                {'label': 'Class 1B', 'value': '2'},
                {'label': 'Class 2', 'value': '3'},
                {'label': 'Class 3', 'value': '4'},
                # {'label': 'Error', 'value': '-1'}
                ]

    elif w_dep_var_type == 'PRODUCT':
        return [{'label': 'Tariff Rated/ Self-Rated/ Special Rated/ LSR/ IAR', 'value': '1'},
                {'label': 'Non-Tariff Rated', 'value': '2'},
                {'label': 'Enhanced Houseowner', 'value': '3'},
                {'label': 'Enhanced Householder', 'value': '4'},    
                {'label': 'Enhanced Fire-Long Term Contract', 'value': '5'},           
                {'label': 'Enhanced Fire-Long Term Agreement', 'value': '6'},           
                {'label': 'Enhanced Fire-Others', 'value': '7'},
                # {'label': 'Error', 'value': '-1'} 
                ]

    elif w_dep_var_type == 'PERILS':   
        return [{'label': 'All', 'value': 'All'},                             
                ]
       
    elif w_dep_var_type == 'DCHNL':           
        return [{'label': 'Agent', 'value': '0'},
                {'label': 'Broker', 'value': '1'},
                {'label': 'Banca Assurance', 'value': '2'},
                {'label': 'Direct-Internet', 'value': '3'},
                {'label': 'Direct-Mail', 'value': '4'},
                {'label': 'Direct-Corporate Client', 'value': '5'},
                {'label': 'Direct-Walk In', 'value': '6'},
                {'label': 'Direct-Phone', 'value': '7'},
                {'label': 'Others', 'value': '9'},  
                # {'label': 'Error', 'value': '-1'},                           
                ]   
    
    elif w_dep_var_type == 'STATES':
        return [{'label':'Johor','value':'Johor'},
                {'label':'Kedah','value':'Kedah'},
                {'label':'Kelantan','value':'Kelantan'},
                {'label':'Melaka','value':'Melaka'},
                {'label':'Negeri Sembilan','value':'Negeri Sembilan'},
                {'label':'Pahang','value':'Pahang'},
                {'label':'Perak','value':'Perak'},
                {'label':'Perlis','value':'Perlis'},
                {'label':'Pulau Pinang','value':'Pulau Pinang'},
                {'label':'Sabah','value':'Sabah'},
                {'label':'Sarawak','value':'Sarawak'},
                {'label':'Selangor','value':'Selangor'},
                {'label':'Terengganu','value':'Terengganu'},
                {'label':'WP Kuala Lumpur','value':'WP Kuala Lumpur'},
                {'label':'WP Labuan','value':'WP Labuan'},
                {'label':'WP Putrajaya','value':'WP Putrajaya'},
                # {'label':'Error','value':'Error'}  
                ]
    
    elif w_dep_var_type == 'VAR':
        return [{'label':'Select Variable','value':'VAR'}]
        
@app.callback(
    Output('w_breakdown1', 'value'),
    [Input('w_breakdown1', 'options')])
def set_options_value(w_dep_var_type):
    return w_dep_var_type[0]['value']                
                

#########################################################################################################


@app.callback(
    Output('w_breakdown2', 'options'),
    [Input('w_dep_var_type', 'value')])
def set_options(w_dep_var_type):
    if w_dep_var_type == 'LOB':
        return [{'label': 'Fire-Material Damage', 'value': '1'},
                {'label': 'Fire-Consequential Damage', 'value': '2'},
                {'label': 'Houseowner', 'value': '3'},
                {'label': 'Householder', 'value': '4'},
                {'label': 'Plantations', 'value': '5'},
                {'label': 'Industrial All Risks - Section 1', 'value': '6'},
                {'label': 'Industrial All Risks - Section 2', 'value': '7'},
                {'label': 'Fire-Consequential Loss (Standalone)', 'value': '8'},
                # {'label': 'Error', 'value': '-1'}
                ]
    
    elif w_dep_var_type == 'RISK':   
        return [{'label': 'Residential', 'value': '10'},
                {'label': 'Retail', 'value': '11'},
                {'label': 'Hotel, Office', 'value': '12'},
                {'label': 'Mining', 'value': '13'},
                {'label': 'Construction', 'value': '14'},
                {'label': 'Food Processing', 'value': '15'},
                {'label': 'Beverage', 'value': '16'},
                {'label': 'Tobacco', 'value': '17'},
                {'label': 'Textiles', 'value': '18'},
                {'label': 'Leather & Fibre', 'value': '19'},
                {'label': 'Timber', 'value': '20'},
                {'label': 'Paper & Printing', 'value': '21'},
                {'label': 'Chemicals', 'value': '22'},
                {'label': 'Petroleum', 'value': '23'},
                {'label': 'Rubber', 'value': '24'},
                {'label': 'Plastics', 'value': '25'},
                {'label': 'Non-metalic minerals', 'value': '26'},
                {'label': 'Metal Working, Engineering', 'value': '27'},
                {'label': 'Motor Trade and Related Risks', 'value': '28'},
                {'label': 'Restaurants, Places of recreation', 'value': '29'},
                {'label': 'Utilities', 'value': '30'},
                {'label': 'Transport', 'value': '31'},
                {'label': 'Cinemas, studios & exhibition halls', 'value': '33'},
                {'label': 'General Storage', 'value': '34'},
                {'label': 'Oil Mill', 'value': '35'},
                {'label': 'Rice & Flour Mills', 'value': '36'},
                {'label': 'Sugar Factory', 'value': '37'},
                {'label': 'Cocoa, Coffee & Tea Factories', 'value': '38'},
                {'label': 'Cold stores', 'value': '39'},
                {'label': 'Houseowners & Householders', 'value': '40'},
                {'label': 'Plantations', 'value': '50'},
                # {'label': 'Error', 'value': '-1'}               
                ]
    if w_dep_var_type == 'BASE RATE':
        return [{'label': 'Tariff', 'value': '0'},
                {'label': 'Self-Rating', 'value': '1'},
                {'label': 'Special Rating', 'value': '2'},
                {'label': 'Large & Specialized Risk', 'value': '3'},
                {'label': 'Industrial All Risks', 'value': '4'},
                {'label': 'Non-Tariff', 'value': '5'},
                # {'label': 'Error', 'value': '-1'}
                ]

    elif w_dep_var_type == 'CONSTN':
        return [{'label': 'Class 1A', 'value': '1'},
                {'label': 'Class 1B', 'value': '2'},
                {'label': 'Class 2', 'value': '3'},
                {'label': 'Class 3', 'value': '4'},
                # {'label': 'Error', 'value': '-1'}
                ]

    elif w_dep_var_type == 'PRODUCT':
        return [{'label': 'Tariff Rated/ Self-Rated/ Special Rated/ LSR/ IAR', 'value': '1'},
                {'label': 'Non-Tariff Rated', 'value': '2'},
                {'label': 'Enhanced Houseowner', 'value': '3'},
                {'label': 'Enhanced Householder', 'value': '4'},    
                {'label': 'Enhanced Fire-Long Term Contract', 'value': '5'},           
                {'label': 'Enhanced Fire-Long Term Agreement', 'value': '6'},           
                {'label': 'Enhanced Fire-Others', 'value': '7'},
                # {'label': 'Error', 'value': '-1'}
                ]

    elif w_dep_var_type == 'PERILS':   
        return [{'label': 'All', 'value': 'All'},                             
                ]
       
    elif w_dep_var_type == 'DCHNL':   
        return [{'label': 'Agent', 'value': '0'},
                {'label': 'Broker', 'value': '1'},
                {'label': 'Banca Assurance', 'value': '2'},
                {'label': 'Direct-Internet', 'value': '3'},
                {'label': 'Direct-Mail', 'value': '4'},
                {'label': 'Direct-Corporate Client', 'value': '5'},
                {'label': 'Direct-Walk In', 'value': '6'},
                {'label': 'Direct-Phone', 'value': '7'},
                {'label': 'Others', 'value': '9'},
                # {'label': 'Error', 'value': '-1'},                             
                ]     
    
    elif w_dep_var_type == 'STATES':
        return [{'label':'Johor','value':'Johor'},
                {'label':'Kedah','value':'Kedah'},
                {'label':'Kelantan','value':'Kelantan'},
                {'label':'Melaka','value':'Melaka'},
                {'label':'Negeri Sembilan','value':'Negeri Sembilan'},
                {'label':'Pahang','value':'Pahang'},
                {'label':'Perak','value':'Perak'},
                {'label':'Perlis','value':'Perlis'},
                {'label':'Pulau Pinang','value':'Pulau Pinang'},
                {'label':'Sabah','value':'Sabah'},
                {'label':'Sarawak','value':'Sarawak'},
                {'label':'Selangor','value':'Selangor'},
                {'label':'Terengganu','value':'Terengganu'},
                {'label':'WP Kuala Lumpur','value':'WP Kuala Lumpur'},
                {'label':'WP Labuan','value':'WP Labuan'},
                {'label':'WP Putrajaya','value':'WP Putrajaya'},
                # {'label':'Error','value':'-1'}
                ]  
    
    elif w_dep_var_type == 'VAR':
        return [{'label':'Select Variable','value':'VAR'}]
        
@app.callback(
    Output('w_breakdown2', 'value'),
    [Input('w_breakdown2', 'options')])
def set_options_value(w_dep_var_type):
    return w_dep_var_type[1]['value']                
                
#########################################################################################################


@app.callback(
    Output('w_breakdown', 'options'),
    [Input('w_var_type', 'value')])

def set_options(w_var_type):
    if w_var_type == 'LOB':
        return [{'label': 'Fire-Material Damage', 'value': '1'},
                {'label': 'Fire-Consequential Damage', 'value': '2'},
                {'label': 'Houseowner', 'value': '3'},
                {'label': 'Householder', 'value': '4'},
                {'label': 'Plantations', 'value': '5'},
                {'label': 'Industrial All Risks - Section 1', 'value': '6'},
                {'label': 'Industrial All Risks - Section 2', 'value': '7'},
                {'label': 'Fire-Consequential Loss (Standalone)', 'value': '8'},
                # {'label': 'Error', 'value': '-1'}
                ]
    
    elif w_var_type == 'RISK':   
        return [{'label': 'Residential', 'value': '10'},
                {'label': 'Retail', 'value': '11'},
                {'label': 'Hotel, Office', 'value': '12'},
                {'label': 'Mining', 'value': '13'},
                {'label': 'Construction', 'value': '14'},
                {'label': 'Food Processing', 'value': '15'},
                {'label': 'Beverage', 'value': '16'},
                {'label': 'Tobacco', 'value': '17'},
                {'label': 'Textiles', 'value': '18'},
                {'label': 'Leather & Fibre', 'value': '19'},
                {'label': 'Timber', 'value': '20'},
                {'label': 'Paper & Printing', 'value': '21'},
                {'label': 'Chemicals', 'value': '22'},
                {'label': 'Petroleum', 'value': '23'},
                {'label': 'Rubber', 'value': '24'},
                {'label': 'Plastics', 'value': '25'},
                {'label': 'Non-metalic minerals', 'value': '26'},
                {'label': 'Metal Working, Engineering', 'value': '27'},
                {'label': 'Motor Trade and Related Risks', 'value': '28'},
                {'label': 'Restaurants, Places of recreation', 'value': '29'},
                {'label': 'Utilities', 'value': '30'},
                {'label': 'Transport', 'value': '31'},
                {'label': 'Cinemas, studios & exhibition halls', 'value': '33'},
                {'label': 'General Storage', 'value': '34'},
                {'label': 'Oil Mill', 'value': '35'},
                {'label': 'Rice & Flour Mills', 'value': '36'},
                {'label': 'Sugar Factory', 'value': '37'},
                {'label': 'Cocoa, Coffee & Tea Factories', 'value': '38'},
                {'label': 'Cold stores', 'value': '39'},
                {'label': 'Houseowners & Householders', 'value': '40'},
                {'label': 'Plantations', 'value': '50'},
                # {'label': 'Error', 'value': '-1'}               
                ]

    elif w_var_type == 'BASE RATE':
        return [{'label': 'Tariff', 'value': '0'},
                {'label': 'Self-Rating', 'value': '1'},
                {'label': 'Special Rating', 'value': '2'},
                {'label': 'Large & Specialized Risk', 'value': '3'},
                {'label': 'Industrial All Risks', 'value': '4'},
                {'label': 'Non-Tariff', 'value': '5'},
                # {'label': 'Error', 'value': '-1'}
                ]

    elif w_var_type == 'CONSTN':
        return [{'label': 'Class 1A', 'value': '1'},
                {'label': 'Class 1B', 'value': '2'},
                {'label': 'Class 2', 'value': '3'},
                {'label': 'Class 3', 'value': '4'},
                # {'label': 'Error', 'value': '-1'}
                ]

    elif w_var_type == 'PRODUCT':
        return [{'label': 'Tariff Rated/ Self-Rated/ Special Rated/ LSR/ IAR', 'value': '1'},
                {'label': 'Non-Tariff Rated', 'value': '2'},
                {'label': 'Enhanced Houseowner', 'value': '3'},
                {'label': 'Enhanced Householder', 'value': '4'},    
                {'label': 'Enhanced Fire-Long Term Contract', 'value': '5'},           
                {'label': 'Enhanced Fire-Long Term Agreement', 'value': '6'},           
                {'label': 'Enhanced Fire-Others', 'value': '7'},
                # {'label': 'Error', 'value': '-1'}
                ]

    elif w_var_type == 'PERILS':   
        return [{'label': 'All', 'value': 'All'},                             
                ]
       
    elif w_var_type == 'DCHNL':   
        return [{'label': 'Agent', 'value': '0'},
                {'label': 'Broker', 'value': '1'},
                {'label': 'Banca Assurance', 'value': '2'},
                {'label': 'Direct-Internet', 'value': '3'},
                {'label': 'Direct-Mail', 'value': '4'},
                {'label': 'Direct-Corporate Client', 'value': '5'},
                {'label': 'Direct-Walk In', 'value': '6'},
                {'label': 'Direct-Phone', 'value': '7'},
                {'label': 'Others', 'value': '9'},
                # {'label': 'Error', 'value': '-1'}             
                ]            

@app.callback(
    Output('w_breakdown', 'value'),
    [Input('w_breakdown', 'options')])
def set_options_value(w_var_type):
    return w_var_type[0]['value']                
                

#########################################################################################################

@app.callback(
    Output('butterfly','figure'),
    [Input('w_data_type','value')],
    [Input('w_ind_var_type','value')],
    [Input('w_dep_var_type','value')],
    [Input('w_breakdown1','value')],
    [Input('w_breakdown2','value')])

def updated_graph(w_data_type,w_ind_var_type,w_dep_var_type,w_breakdown1,w_breakdown2):
    # radio_items=2020
    # w_data_type='PAIDLS'
    # w_ind_var_type='BASE RATE'
    # w_dep_var_type='LOB'
    # w_breakdown1='1'
    # w_breakdown2='2'
    
    x=latest_year-5
    
    df_bys=df.groupby(['LOSSYEAR',w_ind_var_type,w_dep_var_type])[w_data_type].sum().reset_index()
    selection1=df_bys[(df_bys['LOSSYEAR']>x)&((df_bys[w_dep_var_type]==w_breakdown1)|(df_bys[w_dep_var_type]==w_breakdown2))]    
    
    selection1=selection1.sort_values(by=[w_dep_var_type,'LOSSYEAR',w_ind_var_type])
    selection2=pd.DataFrame(columns = ['LOSSYEAR', w_ind_var_type, w_dep_var_type, w_data_type])

    if w_ind_var_type == 'STATES':
        list2=['Johor','Kedah','Kelantan','Melaka','Negeri Sembilan','Pahang','Perak', 'Perlis','Pulau Pinang','Sabah','Sarawak','Selangor','Terengganu','WP Kuala Lumpur','WP Labuan','WP Putrajaya','Error']
    
    elif w_ind_var_type == 'LOB':
        list2=['1','2','3','4','5','6','7','8','-1']
    
    elif w_ind_var_type == 'RISK':
        list2=['10','11','12','13','14','15','16','17','18','19',
               '20','21','22','23','24','25','26','27','28','29',
               '30','31','33','34','35','36','37','38','39',
               '40','50','-1']
    elif w_ind_var_type == 'BASE RATE':
        list2=['0','1','2','3','4','5','-1']
        
    elif w_ind_var_type == 'CONSTN':
        list2=['1','2','3','4','-1']
        
    elif w_ind_var_type == 'PRODUCT':
        list2=['1','2','3','4','5','6','7','-1']
        
    elif w_ind_var_type == 'DCHNL':
        list2=['0','1','2','3','4','5','6','7','9','-1']
        


    for i in selection1[w_dep_var_type].unique():
        for year in selection1['LOSSYEAR'].unique():
            list1=selection1[(selection1['LOSSYEAR']==year)&(selection1[w_dep_var_type]==i)][w_ind_var_type].tolist()
            list2=list2
            missing=set(list2).difference(set(list1))
                 
            for j in missing:
                data = [{'LOSSYEAR':year, w_ind_var_type:j, w_dep_var_type:i, w_data_type :0}]           
                selection2 = selection2.append(data, ignore_index=True)
    
    selection=pd.concat([selection1,selection2])
    selection=selection.sort_values(by=[w_dep_var_type,'LOSSYEAR',w_ind_var_type]).reset_index()
    
    
    if w_ind_var_type == 'LOB':
        conditions=[selection['LOB']=='1', selection['LOB']=='2', selection['LOB']=='3', selection['LOB']=='4',
                    selection['LOB']=='5', selection['LOB']=='6', selection['LOB']=='7', selection['LOB']=='8',
                    selection['LOB']=='-1'
                    ]
        
        values=['Fire-Material Damage','Fire-Consequential Damage','Houseowner','Householder', 
                'Plantations','Industrial All Risks-Section 1','Industrial All Risks-Section 2','Fire-Consequential Loss (Standalone)',
                'Error'
                ]
                
         
    elif  w_ind_var_type == 'BASE RATE':
        conditions=[selection['BASE RATE']=='0',selection['BASE RATE']=='1',selection['BASE RATE']=='2',
                   selection['BASE RATE']=='3',selection['BASE RATE']=='4',selection['BASE RATE']=='5',
                    selection['BASE RATE']=='-1'
                   ]
        values=['Tariff','Self-Rating','Special Rating',
               'Large & Specialized Risk','Industrial All Risks','Non-Tariff',
                'Error'
               ]
       
    elif w_ind_var_type == 'RISK':
        conditions=[selection['RISK']=='10',selection['RISK']=='11',selection['RISK']=='12',selection['RISK']=='13',
                    selection['RISK']=='14',selection['RISK']=='15',selection['RISK']=='16',selection['RISK']=='17',
                    selection['RISK']=='18',selection['RISK']=='19',selection['RISK']=='20',selection['RISK']=='21',
                    selection['RISK']=='22',selection['RISK']=='23',selection['RISK']=='24',selection['RISK']=='25',
                    selection['RISK']=='26',selection['RISK']=='27',selection['RISK']=='28',selection['RISK']=='29',
                    selection['RISK']=='30',selection['RISK']=='31',selection['RISK']=='33',selection['RISK']=='34',
                    selection['RISK']=='35',selection['RISK']=='36',selection['RISK']=='37',selection['RISK']=='38',
                    selection['RISK']=='39',selection['RISK']=='40',selection['RISK']=='50',
                    selection['RISK']=='-1'                    
                    ]
        values=['Residential','Retail','Hotel, Office','Mining',
                'Construction','Food Processing', 'Beverage', 'Tobacco',
                'Textiles','Leather & Fibre','Timber','Paper & Printing',
                'Chemicals','Petroleum','Rubber','Plastics',
                'Non-metalic minerals','Metal Working, Engineering','Motor Trade and Related Risks','Restaurants, Places of recreation',
                'Utilities','Transport','Cinemas, studios & exhibition halls','General Storage',
                'Oil Mill','Rice & Flour Mills','Sugar Factory','Cocoa, Coffee & Tea Factories',
                'Cold stores','Houseowners & Householders','Plantations',
                'Error'
                ]
        
    elif w_ind_var_type == 'CONSTN':
        conditions=[selection['CONSTN']=='1',selection['CONSTN']=='2',
                    selection['CONSTN']=='3',selection['CONSTN']=='4',
                    selection['CONSTN']=='-1'
                    ]
        values=['Class 1A','Class 1B',
                'Class 2','Class 3',
                'Error'
                ]
        
    elif w_ind_var_type == 'PRODUCT':
        conditions=[selection['PRODUCT']=='1',selection['PRODUCT']=='2',selection['PRODUCT']=='3',
                    selection['PRODUCT']=='4',selection['PRODUCT']=='5',selection['PRODUCT']=='6',
                    selection['PRODUCT']=='7',
                    selection['PRODUCT']=='-1'
                    ]
        values=['Tariff Rated/ Self-Rated/ Special Rated/ LSR/ IAR','Non-Tariff Rated','Enhanced Houseowner',
                'Enhanced Householder','Enhanced Fire-Long Term Contract','Enhanced Fire-Long Term Agreement',
                'Enhanced Fire-Others', 
                'Error'
                ]
        
    elif w_ind_var_type == 'PERILS':
        conditions=[selection['PERILS']=='1',selection['PERILS']=='2',selection['PERILS']=='3',selection['PERILS']=='4',
                    selection['PERILS']=='5',selection['PERILS']=='6',selection['PERILS']=='8',selection['PERILS']=='9',
                    selection['PERILS']=='10',selection['PERILS']=='11',selection['PERILS']=='12',selection['PERILS']=='13',
                    selection['PERILS']=='14',selection['PERILS']=='15',selection['PERILS']=='16',selection['PERILS']=='17',
                    selection['PERILS']=='18',selection['PERILS']=='19',selection['PERILS']=='20',selection['PERILS']=='21',
                    selection['PERILS']=='22',selection['PERILS']=='23',selection['PERILS']=='24',selection['PERILS']=='25',
                    selection['PERILS']=='26',selection['PERILS']=='27',selection['PERILS']=='28',selection['PERILS']=='29',
                    selection['PERILS']=='30',selection['PERILS']=='31',
                    selection['PERILS']=='-1'
                    ]
        values=['Fire & Lightning','Riot Strike & Malicious Damage','Explosion','Flood',
                'Aircraft','Earthquake & Volcanic Eruption','Storm Tempest','Impact Damage',
                'Bursting of Pipes, Water Tanks','Electrical Installations','Theft/ Burglary','Subsidence & Landslip',
                'Spontaneous Combustion','Falling Trees','Bush/ Lalang Fire','Sprinkler Leakage',
                'All Warranty that involve premiums','All Clauses & Endorsement that involve premiums','Loading','Discount',
                'Animal Damage','Goods and stocks undergoing any drying/ heating process','Smoke Damage','Cold Storage/ Incubator Clause B',
                'Lost Adjustment Fee/ Legal Charges','Salvage','Extended theft cover (i) excluding theft by domestic servants','Extended theft cover (ii) including theft by domestic servants',
                'Terrorism','Non-Fire Related Covers',
                'Error'
                ]
        
    elif w_ind_var_type == 'DCHNL':
        conditions=[selection['DCHNL']=='0',selection['DCHNL']=='1',selection['DCHNL']=='2',selection['DCHNL']=='3',
                    selection['DCHNL']=='4',selection['DCHNL']=='5',selection['DCHNL']=='6',selection['DCHNL']=='7',
                    selection['DCHNL']=='9',
                    selection['DCHNL']=='-1'
                    ]
        values=['Agent','Broker','Banca Assurance','Direct-Internet',
                'Direct-Mail','Direct-Corporate Client','Direct-Walk In','Direct-Phone',
                'Others',
                'Error'
                ]
                
    elif w_ind_var_type=='STATES':
        conditions=[selection['STATES']=='Johor',selection['STATES']=='Kedah',selection['STATES']=='Kelantan',
                    selection['STATES']=='Melaka',selection['STATES']=='Negeri Sembilan',selection['STATES']=='Pahang',
                    selection['STATES']=='Perak',selection['STATES']=='Perlis',selection['STATES']=='Pulau Pinang',
                    selection['STATES']=='Sabah',selection['STATES']=='Sarawak',selection['STATES']=='Selangor',
                    selection['STATES']=='Terengganu',selection['STATES']=='WP Kuala Lumpur',selection['STATES']=='WP Labuan',
                    selection['STATES']=='WP Putrajaya',
                    selection['STATES']=='Error'
                    ]
        
        values=['Johor','Kedah','Kelantan',
                'Melaka','Negeri Sembilan','Pahang',
                'Perak','Perlis','Pulau Pinang',
                'Sabah','Sarawak','Selangor',
                'Terengganu','WP Kuala Lumpur','WP Labuan',
                'WP Putrajaya',
                'Error'
                ]
       
        
         
    selection['w_ind_var_desc']=np.select(conditions,values)
    selection['LOSSYEAR']=selection['LOSSYEAR'].astype(int)
    selection[w_data_type]=selection[w_data_type].astype(np.int64)
    selection=selection.sort_values(by=['LOSSYEAR','w_ind_var_desc',w_dep_var_type])
    selection.reset_index(drop=True, inplace=True)    

    # selection[w_data_type]=np.where(selection[w_dep_var_type]==w_breakdown1,selection[w_data_type]*-1,selection[w_data_type])
    # selection['color'] = np.where(selection[w_data_type]<0, 'teal', 'lightseagreen')
    # hover = selection.columns.tolist(),
    color_discrete_map = {w_breakdown1: 'teal', 
                          w_breakdown2: 'lightseagreen'}

    fig = px.bar(selection,
                  x=w_data_type, 
                  y="w_ind_var_desc",
                  color=w_dep_var_type,
                  animation_frame="LOSSYEAR",
                  barmode='group',
                  color_discrete_map=color_discrete_map,
                #   facet_col=selection[w_dep_var_type]                  
                  )
    
    max_range=max(-min(selection[w_data_type]),max(selection[w_data_type]))
    
    fig.update_layout(
                      xaxis_range=[0,max_range+2000000],
                      paper_bgcolor='#1f2c56',
                      font_color="white",
                      height=700,
                      font_size=18,
                        # margin = dict(t=80, l=1, r=1, b=1),
                      showlegend=False,
                      title={
                          # 'text':w_breakdown1+' vs '+w_breakdown2,
                          'y':0.95,
                          'x':0.5,
                          'xanchor':'center',
                          'yanchor':'top'},
                      titlefont={
                          'color':'white',
                          'size':20},
                    #   hovermode='y unified',
                      hoverlabel=dict(
                              font_size=20),
                      xaxis={'title': None,
                              'color':'white',
                              'zeroline': True,
                              'showgrid': True,
                              'visible': True,
                              'showticklabels': True},
                      yaxis={'title': None,
                              'color':'white',
                              'showgrid': True,
                              'showline': True,
                              'zeroline': True,
                              'autorange': 'reversed',
                              'scaleratio': 0.5},   
                         )
    
    fig.update_traces(
             # texttemplate='%{text:.2s}', 
             # textposition='outside',
             # textfont=dict(
             # size=20,
             # color='black'),
             hovertemplate='%{y}<br>%{x:,.0f}<extra></extra>',
             hoverinfo='y+x',
             )   

    fig.layout.updatemenus[0].buttons[0].args[1]["frame"]["duration"] = 1500

    return fig

#########################################################################################################


@app.callback(Output('treemap','figure'),
              
            [Input('radio_items','value')],
            [Input('w_data_type','value')])

def updated_graph(radio_items,w_data_type):
    radio_items=int(radio_items)
    
    if w_data_type=='PAIDLS': w_data_type_desc='Total Claims Paid'      
    if w_data_type=='BALOS': w_data_type_desc='Total Claims Outstanding'      
    if w_data_type=='INCTOT': w_data_type_desc='Total Claims Incurred'      
    if w_data_type=='INCCNT': w_data_type_desc='Total Claims Count'
    
    df_bys=df.groupby(['LOSSYEAR','STATES','DISTRICT'])[['PAIDLS','BALOS','INCTOT','INCCNT']].sum().reset_index()
    selection=df_bys[(df_bys['LOSSYEAR']==radio_items)]      

    fig = px.treemap(selection, path=[selection['STATES'],selection['DISTRICT']], 
                 values=selection[w_data_type],
                 )
    
    fig.data[0].textinfo = 'label+value+percent entry'
    fig.data[0].hovertemplate = '%{label}<br>%{value}'

    
    fig.update_layout(height=650,
                      hovermode='closest',
                      paper_bgcolor='#1f2c56',
                      autosize=True,
                      margin = dict(t=80, l=1, r=1, b=1),
                      title={ 'text':'{} by State and District ('.format(w_data_type_desc) + str(radio_items) + ')',
                              'y':0.93,
                              'x':0.5,
                              'xanchor':'center',
                              'yanchor':'top'},
                      titlefont={'color':'white',
                                 'size':25},
                      hoverlabel=dict(font_size=20),
                      font=dict(size=20,color='white')
                          )   
    return fig


    
@app.callback(Output('quarterly_chart','figure'),
              [Input('radio_items','value')],              
              [Input('w_state','value')],
              [Input('w_data_type','value')])

def updated_graph(radio_items,w_state,w_data_type):
    radio_items=int(radio_items)
    x=latest_year-5
    x1=x+1
    
    if w_data_type=='PAIDLS': w_data_type_desc='Total Claims Paid'      
    if w_data_type=='BALOS': w_data_type_desc='Total Claims Outstanding'      
    if w_data_type=='INCTOT': w_data_type_desc='Total Claims Incurred'      
    if w_data_type=='INCCNT': w_data_type_desc='Total Claims Count'    
    
    if w_state=='Malaysia':
        df_bys=df.groupby(['LOSSYEAR','LOSSQUARTER'])[w_data_type].sum().reset_index()
        df_bys=df_bys[(df_bys['LOSSYEAR']>x)]
        
        fig = go.Figure()
        fig.update_layout(height=500,
                          barmode='stack',    
                          paper_bgcolor='#1f2c56',
                          font_color="white",
                          margin = dict(t=80, l=1, r=1, b=145),
                          title={
                              'text':'{} by Quarter: {} ('.format(w_data_type_desc,w_state) + str(x1) + ' - '+ str(latest_year) + ')',
                              'y':0.99,
                              'x':0.5,
                              'xanchor':'center',
                              'yanchor':'top'},
                          titlefont={
                              'color':'white',
                              'size':25},
                          xaxis_title="Quarter",
                          hoverlabel=dict(font_size=20),
                          font=dict(size=18,color='white'))
        fig.update_yaxes(ticksuffix = "  ")
        fig.update_xaxes(ticksuffix = "  ")

        
        # for r in ( df_bys['STATES'].unique()):
        #     plot_df = df_bys[df_bys['STATES'] == r]
        fig.add_trace(
            go.Bar(x=[df_bys['LOSSQUARTER'],df_bys['LOSSYEAR']], y=df_bys[w_data_type],marker_color='cornflowerblue',
                   hovertemplate = '%{y:,.0f}<extra></extra>'),
        )
        return fig
    
    else:
        df_bys=df.groupby(['LOSSYEAR','LOSSQUARTER','STATES'])[w_data_type].sum().reset_index()
        df_bys=df_bys[(df_bys['LOSSYEAR']>x)&(df_bys['STATES']==w_state)]
        
        fig = go.Figure()
        fig.update_layout(height=500,
                          barmode='stack',    
                          paper_bgcolor='#1f2c56',
                          font_color="white",
                          margin = dict(t=80, l=1, r=1, b=145),
                          title={
                              'text':'{} by Quarter: {} ('.format(w_data_type_desc,w_state) + str(x1) + ' - '+ str(latest_year) + ')',
                              'y':0.99,
                              'x':0.5,
                              'xanchor':'center',
                              'yanchor':'top'},
                          titlefont={
                              'color':'white',
                              'size':25},
                          xaxis_title="Quarter",
                          hoverlabel=dict(font_size=20),
                          font=dict(size=18,color='white'))
        fig.update_yaxes(ticksuffix = "  ")
        fig.update_xaxes(ticksuffix = "  ")        
        
        
        for r in ( df_bys['STATES'].unique()):
            plot_df = df_bys[df_bys['STATES'] == r]
            fig.add_trace(
                go.Bar(x=[plot_df['LOSSQUARTER'],plot_df['LOSSYEAR']], y=plot_df[w_data_type], name=r,marker_color='cornflowerblue',
                       hovertemplate = '%{y:,.0f}<extra></extra>'),
            )
        return fig  
    


@app.callback(Output('monthly_chart','figure'),
              [Input('radio_items','value')],
              [Input('w_state','value')],              
              [Input('w_data_type','value')])

def updated_graph(radio_items,w_state,w_data_type):
    radio_items=int(radio_items)
    if w_data_type=='PAIDLS': w_data_type_desc='Total Claims Paid'      
    if w_data_type=='BALOS': w_data_type_desc='Total Claims Outstanding'      
    if w_data_type=='INCTOT': w_data_type_desc='Total Claims Incurred'      
    if w_data_type=='INCCNT': w_data_type_desc='Total Claims Count'      

    
    if w_state=='Malaysia':
        df_bys=df.groupby(['LOSSYEAR','LOSSMONTH'])[w_data_type].sum().reset_index() 
        selection=df_bys[(df_bys['LOSSYEAR']==radio_items)]
        # df_bys[w_data_type] = df_bys[w_data_type].apply(lambda x : "{:,.0f}".format(x))
    
    else:
        df_bys=df.groupby(['LOSSYEAR','LOSSMONTH','STATES'])[w_data_type].sum().reset_index() 
        selection=df_bys[(df_bys['LOSSYEAR']==radio_items)&(df_bys['STATES']==w_state)]           
    
    
    fig = go.Figure(data=[            
        go.Bar(x=selection['LOSSMONTH'], y=selection[w_data_type],marker_color='cornflowerblue',
                 hovertemplate = '%{y:,.0f}<extra></extra>')])
        
    fig.update_layout(height=500,
                      barmode='stack',  
                      hovermode='closest',
                      paper_bgcolor='#1f2c56',
                      margin = dict(t=80, l=1, r=1, b=1),
                      title={
                          'text':'{} by Month: {} ('.format(w_data_type_desc,w_state) + str(radio_items) + ')',
                          'y':0.99,
                          'x':0.5,
                          'xanchor':'center',
                          'yanchor':'top'},
                      titlefont={
                          'color':'white',
                          'size':25},
                      hoverlabel=dict(font_size=20),
                      font=dict(size=18,color='white'),
                      xaxis=dict(title='Month',tickvals=['1','2','3','4','5','6','7','8','9','10','11','12']))
    fig.update_yaxes(ticksuffix = "  ")
    fig.update_xaxes(ticksuffix = "  ")    
        
    return fig



@app.callback(Output('RC_pie_chart','figure'),
              [Input('radio_items','value')],
              [Input('w_data_type','value')])

def updated_graph(radio_items,w_data_type):
    radio_items=int(radio_items)
    if w_data_type=='PAIDLS': w_data_type_desc='Total Claims Paid'      
    if w_data_type=='BALOS': w_data_type_desc='Total Claims Outstanding'      
    if w_data_type=='INCTOT': w_data_type_desc='Total Claims Incurred'      
    if w_data_type=='INCCNT': w_data_type_desc='Total Claims Count'   
    
    df_bys=df.groupby(['LOSSYEAR','BUILDING_TYPE'])[['PAIDLS','BALOS','INCTOT','INCCNT','BUILDING_TYPE_CNT']].sum().reset_index()
    selection=df_bys[(df_bys['LOSSYEAR']==radio_items)][[w_data_type,'BUILDING_TYPE','BUILDING_TYPE_CNT']]      

    conditions=[selection['BUILDING_TYPE']=='Residential',
                selection['BUILDING_TYPE']=='Commercial',
                selection['BUILDING_TYPE']=='Error'
                ]
    values=['lightgreen',
            'limegreen',
            'grey'
            ]
    selection['colors']=np.select(conditions,values)              
 
    fig=go.Figure()
    fig=go.Figure(data=[go.Pie(labels=selection['BUILDING_TYPE'],
               values=selection[w_data_type],
               marker_colors=selection['colors'],
               hoverinfo='label+value+percent',
               textinfo='value+percent',
               textfont=dict(size=18),
               hole=0,
               # marker=dict(colors=colors),
               )])
    
    fig.update_layout(height=500,
                      showlegend=True,
                      plot_bgcolor='#1f2c56',
                      paper_bgcolor='#1f2c56',
                      hovermode='closest',
                      autosize=True,
                      margin = dict(t=100, l=0, r=0, b=20),
                      title={
                          'text':'{} by Property Type ('.format(w_data_type_desc) + str(radio_items) + ')',
                          'y':0.99,
                          'x':0.5,
                          'xanchor':'center',
                          'yanchor':'top'},
                      titlefont={
                          'color':'white',
                          'size':25},
                      font=dict(
                          # family='sans-serif',
                          size=18,
                          color='white'),
                      legend={
                          'y':0.5,
                          'x':0.8,
                          'font':dict(size = 20, color = "white")
                          },
                      hoverlabel=dict(
                          font_size=20)
                      )
    fig.update_yaxes(ticksuffix = "  ")
    fig.update_xaxes(ticksuffix = "  ")       
        
    return fig


@app.callback(Output('RC_bar_chart','figure'),
              [Input('radio_items','value')],
              [Input('w_data_type','value')])

def updated_graph(radio_items,w_data_type):
    radio_items=int(radio_items)
    if w_data_type=='PAIDLS': w_data_type_desc='Total Claims Paid'      
    if w_data_type=='BALOS': w_data_type_desc='Total Claims Outstanding'      
    if w_data_type=='INCTOT': w_data_type_desc='Total Claims Incurred'      
    if w_data_type=='INCCNT': w_data_type_desc='Total Claims Count'    
    
    df_bys=df.groupby(['LOSSYEAR','STATES','BUILDING_TYPE'])[['PAIDLS','BALOS','INCTOT','INCCNT','BUILDING_TYPE_CNT']].sum().reset_index()
    selection=df_bys[(df_bys['LOSSYEAR']==radio_items)][['STATES',w_data_type,'BUILDING_TYPE','BUILDING_TYPE_CNT']]      
        
    fig = go.Figure()  
    fig = go.Figure(data=[
        go.Bar(name='Commercial', x=selection[(selection['BUILDING_TYPE']=='Commercial')]['STATES'], y=selection[(selection['BUILDING_TYPE']=='Commercial')][w_data_type],marker_color='limegreen',
               hovertemplate = 'Commercial <br>%{x} <br>%{y:,.0f}<extra></extra>'),        
        go.Bar(name='Residential', x=selection[(selection['BUILDING_TYPE']=='Residential')]['STATES'], y=selection[(selection['BUILDING_TYPE']=='Residential')][w_data_type],marker_color='lightgreen',
               hovertemplate = 'Residential <br>%{x} <br>%{y:,.0f}<extra></extra>'),
        go.Bar(name='Error', x=selection[(selection['BUILDING_TYPE']=='Error')]['STATES'], y=selection[(selection['BUILDING_TYPE']=='Error')][w_data_type],marker_color='grey',
               hovertemplate = 'Error <br>%{x} <br>%{y:,.0f}<extra></extra>'),
        ])            
        
    fig.update_layout(height=500,
                      barmode='stack',
                      paper_bgcolor='#1f2c56',
                      font_color="white",
                      margin = dict(t=80, l=1, r=1, b=1),
                      showlegend=False,
                      font=dict(size=18,
                                color='white'),                      
                      title={
                          'text':'{} by Property Type & State ('.format(w_data_type_desc) + str(radio_items) + ')',
                          'y':0.99,
                          'x':0.5,
                          'xanchor':'center',
                          'yanchor':'top'},
                      titlefont={
                          'color':'white',
                          'size':25},
                      hoverlabel=dict(
                              font_size=20),
                      )
    fig.update_yaxes(ticksuffix = "  ")
    fig.update_xaxes(ticksuffix = "  ")
        
    return fig



@app.callback(Output('report_claims_area_chart','figure'),
              [Input('radio_items','value')],
              [Input('w_data_type','value')])

def updated_graph(radio_items,w_data_type):
    radio_items=int(radio_items)
    df_bys=df.groupby(['LOSSYEAR','LOSSMONTH','CLAIMS_FILING_GROUP'])[['PAIDLS','BALOS','INCTOT','INCCNT']].sum().reset_index()
    selection=df_bys[(df_bys['LOSSYEAR']==radio_items)][['LOSSMONTH',w_data_type,'CLAIMS_FILING_GROUP']]      

    fig = go.Figure()  
    
    
    fig.add_trace(go.Scatter(name='0-7 days', x=selection[(selection['CLAIMS_FILING_GROUP']=='0-7 days')]['LOSSMONTH'], y=selection[(selection['CLAIMS_FILING_GROUP']=='0-7 days')][w_data_type],fillcolor='rebeccapurple',line=dict(color='rebeccapurple'),stackgroup='one',
                  hovertemplate = '0-7 days: %{y:,.0f}<extra></extra>')),
    fig.add_trace(go.Scatter(name='8-30 days', x=selection[(selection['CLAIMS_FILING_GROUP']=='8-30 days')]['LOSSMONTH'], y=selection[(selection['CLAIMS_FILING_GROUP']=='8-30 days')][w_data_type],fillcolor='darkviolet',line=dict(color='darkviolet'),stackgroup='one',
                  hovertemplate = '8-30 days: %{y:,.0f}<extra></extra>')) ,          
    fig.add_trace(go.Scatter(name='1-2 months', x=selection[(selection['CLAIMS_FILING_GROUP']=='1-2 months')]['LOSSMONTH'], y=selection[(selection['CLAIMS_FILING_GROUP']=='1-2 months')][w_data_type],fillcolor='mediumorchid',line=dict(color='mediumorchid'),stackgroup='one',
                  hovertemplate = '1-2 months: %{y:,.0f}<extra></extra>')),           
    fig.add_trace(go.Scatter(name='2-3 months', x=selection[(selection['CLAIMS_FILING_GROUP']=='2-3 months')]['LOSSMONTH'], y=selection[(selection['CLAIMS_FILING_GROUP']=='2-3 months')][w_data_type],fillcolor='orchid',line=dict(color='orchid'),stackgroup='one',
                  hovertemplate = '2-3 months: %{y:,.0f}<extra></extra>')),
    fig.add_trace(go.Scatter(name='3-6 months', x=selection[(selection['CLAIMS_FILING_GROUP']=='3-6 months')]['LOSSMONTH'], y=selection[(selection['CLAIMS_FILING_GROUP']=='3-6 months')][w_data_type],fillcolor='plum',line=dict(color='plum'),stackgroup='one',
                  hovertemplate = '3-6 months: %{y:,.0f}<extra></extra>')),
    fig.add_trace(go.Scatter(name='6-12 months', x=selection[(selection['CLAIMS_FILING_GROUP']=='6-12 months')]['LOSSMONTH'], y=selection[(selection['CLAIMS_FILING_GROUP']=='6-12 months')][w_data_type],fillcolor='lavender',line=dict(color='lavender'),stackgroup='one',
                  hovertemplate = '6-12 months: %{y:,.0f}<extra></extra>')),
    # fig.add_trace(go.Scatter(name='1-2 years', x=selection[(selection['CLAIMS_FILING_GROUP']=='1-2 years')]['LOSSMONTH'], y=selection[(selection['CLAIMS_FILING_GROUP']=='1-2 years')][w_data_type],fillcolor='lightsteelblue',line=dict(color='lightsteelblue'),stackgroup='one',
    #               hovertemplate = '1-2 years: %{y:,.0f}<extra></extra>')),
    # fig.add_trace(go.Scatter(name='>2 years', x=selection[(selection['CLAIMS_FILING_GROUP']=='>2 years')]['LOSSMONTH'], y=selection[(selection['CLAIMS_FILING_GROUP']=='>2 years')][w_data_type],fillcolor='steelblue',line=dict(color='steelblue'),stackgroup='one',
    #               hovertemplate = '>2 years: %{y:,.0f}<extra></extra>')),
    fig.add_trace(go.Scatter(name='Error', x=selection[(selection['CLAIMS_FILING_GROUP']=='Error')]['LOSSMONTH'], y=selection[(selection['CLAIMS_FILING_GROUP']=='Error')][w_data_type],fillcolor='grey',line=dict(color='grey'),stackgroup='one',
                  hovertemplate = 'Error: %{y:,.0f}<extra></extra>')),    
           
    fig.update_layout(height=550,
                      showlegend=True,
                      xaxis_type='category',
                      paper_bgcolor='#1f2c56',
                      font_color="white",
                      margin = dict(t=80, l=1, r=1, b=1),
                      font=dict(size=18,
                                color='white'),                      
                      title={
                          'text':'Gap between Loss Date and Reported Date by Month (' + str(radio_items) + ')',
                          'y':0.99,
                          'x':0.5,
                          'xanchor':'center',
                          'yanchor':'top'},
                      titlefont={
                          'color':'white',
                          'size':25},
                      legend_y=0.5,
                      hoverlabel=dict(
                              font_size=20),
                      xaxis=dict(
                        title='Month',
                        tickmode='linear')
                      # xaxis_title="Month",
                      )
    fig.update_yaxes(ticksuffix = "  ")
    fig.update_xaxes(ticksuffix = "  ")
    
    return fig



@app.callback(Output('report_claims_bar_chart','figure'),
              [Input('radio_items','value')],
              [Input('w_data_type','value')])

def updated_graph(radio_items,w_data_type):
    radio_items=int(radio_items)
    df_bys=df.groupby(['LOSSYEAR','STATES','CLAIMS_FILING_GROUP'])[['PAIDLS','BALOS','INCTOT','INCCNT']].sum().reset_index()
    selection=df_bys[(df_bys['LOSSYEAR']==radio_items)][['STATES',w_data_type,'CLAIMS_FILING_GROUP']]      

    fig = go.Figure(data=[
        go.Bar(name='0-7 days', x=selection[(selection['CLAIMS_FILING_GROUP']=='0-7 days')]['STATES'], y=selection[(selection['CLAIMS_FILING_GROUP']=='0-7 days')][w_data_type],marker_color='rebeccapurple',
               hovertemplate = '0-7 days <br>%{x} <br>%{y:,.0f}<extra></extra>'),
        go.Bar(name='8-30 days', x=selection[(selection['CLAIMS_FILING_GROUP']=='8-30 days')]['STATES'], y=selection[(selection['CLAIMS_FILING_GROUP']=='8-30 days')][w_data_type],marker_color='darkviolet',
               hovertemplate = '8-30 days <br>%{x} <br>%{y:,.0f}<extra></extra>'),
        go.Bar(name='1-2 months', x=selection[(selection['CLAIMS_FILING_GROUP']=='1-2 months')]['STATES'], y=selection[(selection['CLAIMS_FILING_GROUP']=='1-2 months')][w_data_type],marker_color='mediumorchid',
               hovertemplate = '1-2 months <br>%{x} <br>%{y:,.0f}<extra></extra>'),
        go.Bar(name='2-3 months', x=selection[(selection['CLAIMS_FILING_GROUP']=='2-3 months')]['STATES'], y=selection[(selection['CLAIMS_FILING_GROUP']=='2-3 months')][w_data_type],marker_color='orchid',
               hovertemplate = '2-3 months <br>%{x} <br>%{y:,.0f}<extra></extra>'),
        go.Bar(name='3-6 months', x=selection[(selection['CLAIMS_FILING_GROUP']=='3-6 months')]['STATES'], y=selection[(selection['CLAIMS_FILING_GROUP']=='3-6 months')][w_data_type],marker_color='plum',
               hovertemplate = '3-6 months <br>%{x} <br>%{y:,.0f}<extra></extra>'),
        go.Bar(name='6-12 months', x=selection[(selection['CLAIMS_FILING_GROUP']=='6-12 months')]['STATES'], y=selection[(selection['CLAIMS_FILING_GROUP']=='6-12 months')][w_data_type],marker_color='lavender',
               hovertemplate = '6-12 months <br>%{x} <br>%{y:,.0f}<extra></extra>'),
        go.Bar(name='1-2 years', x=selection[(selection['CLAIMS_FILING_GROUP']=='1-2 years')]['STATES'], y=selection[(selection['CLAIMS_FILING_GROUP']=='1-2 years')][w_data_type],marker_color='lightsteelblue',
               hovertemplate = '1-2 years <br>%{x} <br>%{y:,.0f}<extra></extra>'),
        go.Bar(name='>2 years', x=selection[(selection['CLAIMS_FILING_GROUP']=='>2 years')]['STATES'], y=selection[(selection['CLAIMS_FILING_GROUP']=='>2 years')][w_data_type],marker_color='steelblue',
               hovertemplate = '>2 years <br>%{x} <br>%{y:,.0f}<extra></extra>'),
        go.Bar(name='Error', x=selection[(selection['CLAIMS_FILING_GROUP']=='Error')]['STATES'], y=selection[(selection['CLAIMS_FILING_GROUP']=='Error')][w_data_type],marker_color='grey',
               hovertemplate = 'Error <br>%{x} <br>%{y:,.0f}<extra></extra>'),        
        ])            
        
    fig.update_layout(height=550,
                      barmode='stack',
                      paper_bgcolor='#1f2c56',
                      font_color="white",
                      margin = dict(t=80, l=1, r=1, b=1),
                      showlegend=False,
                      font=dict(size=18,
                                color='white'),                      
                      title={
                          'text':'Gap between Loss Date and Reported Date by States (' + str(radio_items) + ')',
                          'y':0.99,
                          'x':0.5,
                          'xanchor':'center',
                          'yanchor':'top'},
                      titlefont={
                          'color':'white',
                          'size':25},
                      hoverlabel=dict(
                              font_size=20),
                      )
    fig.update_yaxes(ticksuffix = "  ")
    fig.update_xaxes(ticksuffix = "  ")
        
    return fig
        


@app.callback(Output('accident_happen_area_chart','figure'),
              [Input('radio_items','value')],
              [Input('w_data_type','value')])

def updated_graph(radio_items,w_data_type):
    radio_items=int(radio_items)
    df_bys=df.groupby(['LOSSYEAR','ACCIDENT_OCCUR_GROUP'])[['PAIDLS','BALOS','INCTOT','INCCNT']].sum().reset_index()
    selection=df_bys[(df_bys['LOSSYEAR']==radio_items)][[w_data_type,'ACCIDENT_OCCUR_GROUP']]      

    # fig = go.Figure()  
    # fig.add_trace(go.Scatter(name='1-3 months', x=selection[(selection['ACCIDENT_OCCUR_GROUP']=='1-3 months')]['LOSSMONTH'], y=selection[(selection['ACCIDENT_OCCUR_GROUP']=='1-3 months')][w_data_type],fillcolor='mediumvioletred',line=dict(color='mediumvioletred'),stackgroup='one',
    #                           hovertemplate = '1-3 months: %{y:,.0f}<extra></extra>'))
    # fig.add_trace(go.Scatter(name='4-6 months', x=selection[(selection['ACCIDENT_OCCUR_GROUP']=='4-6 months')]['LOSSMONTH'], y=selection[(selection['ACCIDENT_OCCUR_GROUP']=='4-6 months')][w_data_type],fillcolor='palevioletred',line=dict(color='palevioletred'),stackgroup='one',
    #                           hovertemplate = '4-6 months: %{y:,.0f}<extra></extra>'))
    # fig.add_trace(go.Scatter(name='7-9 months', x=selection[(selection['ACCIDENT_OCCUR_GROUP']=='7-9 months')]['LOSSMONTH'], y=selection[(selection['ACCIDENT_OCCUR_GROUP']=='7-9 months')][w_data_type],fillcolor='lightpink',line=dict(color='lightpink'),stackgroup='one',
    #                           hovertemplate = '7-9 months: %{y:,.0f}<extra></extra>'))
    # fig.add_trace(go.Scatter(name='10-12 months', x=selection[(selection['ACCIDENT_OCCUR_GROUP']=='10-12 months')]['LOSSMONTH'], y=selection[(selection['ACCIDENT_OCCUR_GROUP']=='10-12 months')][w_data_type],fillcolor='mistyrose',line=dict(color='mistyrose'),stackgroup='one',
    #                           hovertemplate = '10-12 months: %{y:,.0f}<extra></extra>'))
    # fig.add_trace(go.Scatter(name='>12 months', x=selection[(selection['ACCIDENT_OCCUR_GROUP']=='>12 months')]['LOSSMONTH'], y=selection[(selection['ACCIDENT_OCCUR_GROUP']=='>12 months')][w_data_type],fillcolor='grey',line=dict(color='grey'),stackgroup='one',
    #                           hovertemplate = '>12 months: %{y:,.0f}<extra></extra>'))
    # fig.add_trace(go.Scatter(name='Error', x=selection[(selection['ACCIDENT_OCCUR_GROUP']=='Error')]['LOSSMONTH'], y=selection[(selection['ACCIDENT_OCCUR_GROUP']=='Error')][w_data_type],fillcolor='grey',line=dict(color='grey'),stackgroup='one',
    #                           hovertemplate = 'Error: %{y:,.0f}<extra></extra>'))


    selection['ACCIDENT_OCCUR_GROUP'] = pd.Categorical(selection['ACCIDENT_OCCUR_GROUP'], 
                                    ['<1 month','1-3 months',
                                      '3-6 months','6-9 months','9-12 months','>12 months',
                                    ],ordered=True)
    selection.sort_values('ACCIDENT_OCCUR_GROUP')
    selection=selection.sort_values(by=['ACCIDENT_OCCUR_GROUP'])
    
    conditions=[selection['ACCIDENT_OCCUR_GROUP']=='<1 month',
                selection['ACCIDENT_OCCUR_GROUP']=='1-3 months',
                selection['ACCIDENT_OCCUR_GROUP']=='3-6 months',
                selection['ACCIDENT_OCCUR_GROUP']=='6-9 months',
                selection['ACCIDENT_OCCUR_GROUP']=='9-12 months',
                selection['ACCIDENT_OCCUR_GROUP']=='>12 months',
                ]
    values=['mediumvioletred',
            'palevioletred',
            'lightpink',
            'mistyrose',
            'peachpuff',          
            'darksalmon',         
        ]
    selection['colors']=np.select(conditions,values)
      
    fig=go.Figure()
    fig=go.Figure(data=[go.Pie(labels=selection['ACCIDENT_OCCUR_GROUP'],
               values=selection[w_data_type],
               hoverinfo='label+value+percent',
               # textinfo='value+percent',
               textfont=dict(size=18),
               hole=0.3,
               sort=False,
               marker_colors=selection['colors']
               # marker=dict(colors=colors),
               )])


    fig.update_layout(height=550,
                      showlegend=True,
                      # xaxis_type='category',
                      paper_bgcolor='#1f2c56',
                      font_color="white",
                      margin = dict(t=80, l=1, r=1, b=20),
                      font=dict(size=18,
                                color='white'),                      
                      title={
                          'text':'Gap between Policy Inception Date and Loss Date (' + str(radio_items) + ')',
                          'y':0.99,
                          'x':0.5,
                          'xanchor':'center',
                          'yanchor':'top'},
                      titlefont={
                          'color':'white',
                          'size':25},
                      # legend_y=0.5,
                      legend={
                          'y':0.5,
                          'x':0.8,
                          'font':dict(size=20,color='white')
                          },
                      hoverlabel=dict(
                              font_size=20),
                      # xaxis_title="Month",
                      )
    fig.update_yaxes(ticksuffix = "  ")
    fig.update_xaxes(ticksuffix = "  ")    
    
    return fig



@app.callback(Output('accident_happen_bar_chart','figure'),
              [Input('radio_items','value')],
              [Input('w_data_type','value')])

def updated_graph(radio_items,w_data_type):
    radio_items=int(radio_items)
    df_bys=df.groupby(['LOSSYEAR','STATES','ACCIDENT_OCCUR_GROUP'])[['PAIDLS','BALOS','INCTOT','INCCNT']].sum().reset_index()
    selection=df_bys[(df_bys['LOSSYEAR']==radio_items)][['STATES',w_data_type,'ACCIDENT_OCCUR_GROUP']]      

    fig = go.Figure(data=[
        go.Bar(name='<1 month', x=selection[(selection['ACCIDENT_OCCUR_GROUP']=='<1 month')]['STATES'], y=selection[(selection['ACCIDENT_OCCUR_GROUP']=='<1 month')][w_data_type],marker_color='mediumvioletred',
               hovertemplate = '<1 month <br>%{x} <br>%{y:,.0f}<extra></extra>'),          
        go.Bar(name='1-3 months', x=selection[(selection['ACCIDENT_OCCUR_GROUP']=='1-3 months')]['STATES'], y=selection[(selection['ACCIDENT_OCCUR_GROUP']=='1-3 months')][w_data_type],marker_color='palevioletred',
               hovertemplate = '1-3 months <br>%{x} <br>%{y:,.0f}<extra></extra>'),        
        go.Bar(name='3-6 months', x=selection[(selection['ACCIDENT_OCCUR_GROUP']=='3-6 months')]['STATES'], y=selection[(selection['ACCIDENT_OCCUR_GROUP']=='3-6 months')][w_data_type],marker_color='lightpink',
               hovertemplate = '3-6 months <br>%{x} <br>%{y:,.0f}<extra></extra>'),        
        go.Bar(name='6-9 months', x=selection[(selection['ACCIDENT_OCCUR_GROUP']=='6-9 months')]['STATES'], y=selection[(selection['ACCIDENT_OCCUR_GROUP']=='6-9 months')][w_data_type],marker_color='mistyrose',
               hovertemplate = '6-9 months <br>%{x} <br>%{y:,.0f}<extra></extra>'),        
        go.Bar(name='9-12 months', x=selection[(selection['ACCIDENT_OCCUR_GROUP']=='9-12 months')]['STATES'], y=selection[(selection['ACCIDENT_OCCUR_GROUP']=='9-12 months')][w_data_type],marker_color='peachpuff',
               hovertemplate = '9-12 months <br>%{x} <br>%{y:,.0f}<extra></extra>'),        
        go.Bar(name='>12 months', x=selection[(selection['ACCIDENT_OCCUR_GROUP']=='>12 months')]['STATES'], y=selection[(selection['ACCIDENT_OCCUR_GROUP']=='>12 months')][w_data_type],marker_color='lightcoral',
               hovertemplate = '>12 months <br>%{x} <br>%{y:,.0f}<extra></extra>'),  
        ])            
        
    fig.update_layout(height=550,
                      barmode='stack',
                      paper_bgcolor='#1f2c56',
                      font_color="white",
                      margin = dict(t=80, l=1, r=1, b=1),
                      showlegend=False,
                      font=dict(size=18,
                                color='white'),                      
                      title={
                          'text':'Gap between Policy Inception Date and Loss Date by States (' + str(radio_items) + ')',
                          'y':0.99,
                          'x':0.5,
                          'xanchor':'center',
                          'yanchor':'top'},
                      titlefont={
                          'color':'white',
                          'size':25},
                      hoverlabel=dict(
                              font_size=20),
                      )
    fig.update_yaxes(ticksuffix = "  ")
    fig.update_xaxes(ticksuffix = "  ")
        
    return fig


@app.callback(Output('CY_pie_chart','figure'),
              [Input('radio_items','value')],
              [Input('w_data_type','value')])

def updated_graph(radio_items,w_data_type):
    radio_items=int(radio_items)
    if w_data_type=='PAIDLS': w_data_type_desc='Total Claims Paid'      
    if w_data_type=='BALOS': w_data_type_desc='Total Claims Outstanding'      
    if w_data_type=='INCTOT': w_data_type_desc='Total Claims Incurred'      
    if w_data_type=='INCCNT': w_data_type_desc='Total Claims Count'    
    
    df_bys=df.groupby(['LOSSYEAR','CONSTNYR_GROUP'])[w_data_type].sum().reset_index()
    selection=df_bys[(df_bys['LOSSYEAR']==radio_items)] 
    selection['CONSTNYR_GROUP'] = pd.Categorical(selection['CONSTNYR_GROUP'], 
                                    ['Before 1990','1990-1999',
                                     '2000-2004','2005-2009','2010-2014','2015-2019',
                                     '2020','Error'
                                    ],ordered=True)
    selection.sort_values('CONSTNYR_GROUP')
    selection=selection.sort_values(by=['CONSTNYR_GROUP'])

    # selection['colors'] = np.where(selection['CONSTNYR_GROUP']!= 'Residential', 'limegreen', 'palegreen')
      
    fig=go.Figure()
    fig=go.Figure(data=[go.Pie(labels=selection['CONSTNYR_GROUP'],
               values=selection[w_data_type],
               hoverinfo='label+value+percent',
               # textinfo='value+percent',
               textfont=dict(size=18),
               hole=0.3,
               sort=False,
               marker=dict(colors=px.colors.sequential.Tealgrn_r)
               # marker=dict(colors=colors),
               )])
    
    fig.update_layout(height=550,
                      showlegend=True,
                      plot_bgcolor='#1f2c56',
                      paper_bgcolor='#1f2c56',
                      hovermode='closest',
                      autosize=True,
                      margin = dict(t=100, l=0, r=0, b=20),
                      title={
                          'text':' {} by Construction Year ('.format(w_data_type_desc) + str(radio_items) + ')',
                          'y':0.99,
                          'x':0.5,
                          'xanchor':'center',
                          'yanchor':'top'},
                      titlefont={
                          'color':'white',
                          'size':25},
                      font=dict(
                          # family='sans-serif',
                          size=18,
                          color='white'),
                      legend={
                          'y':0.5,
                          'x':0.8,
                          'font':dict(size = 20, color = "white")
                          },
                      hoverlabel=dict(
                          font_size=20)
                      )
    fig.update_yaxes(ticksuffix = "  ")
    fig.update_xaxes(ticksuffix = "  ")       
        
    return fig


@app.callback(Output('CY_bar_chart','figure'),
              [Input('radio_items','value')],
              [Input('w_data_type','value')])

def updated_graph(radio_items,w_data_type):
    radio_items=int(radio_items)
    if w_data_type=='PAIDLS': w_data_type_desc='Total Claims Paid'      
    if w_data_type=='BALOS': w_data_type_desc='Total Claims Outstanding'      
    if w_data_type=='INCTOT': w_data_type_desc='Total Claims Incurred'      
    if w_data_type=='INCCNT': w_data_type_desc='Total Claims Count'    
    
    df_bys=df.groupby(['LOSSYEAR','STATES','CONSTNYR_GROUP'])[w_data_type].sum().reset_index()
    selection=df_bys[(df_bys['LOSSYEAR']==radio_items)]   
        
    fig = go.Figure()  
    fig = go.Figure(data=[
        go.Bar(name='Before 1980', x=selection[(selection['CONSTNYR_GROUP']=='Before 1990')]['STATES'], y=selection[(selection['CONSTNYR_GROUP']=='Before 1990')][w_data_type],marker_color=px.colors.sequential.Tealgrn[6],
               hovertemplate = 'Before 1990 <br>%{x} <br>%{y:,.0f}<extra></extra>'),        
        # go.Bar(name='1980-1989', x=selection[(selection['CONSTNYR_GROUP']=='1980-1989')]['STATES'], y=selection[(selection['CONSTNYR_GROUP']=='1980-1989')][w_data_type],marker_color=px.colors.sequential.haline[1],
        #        hovertemplate = '1980-1989 <br>%{x} <br>%{y:,.0f}<extra></extra>'),
        go.Bar(name='1990-1994', x=selection[(selection['CONSTNYR_GROUP']=='1990-1999')]['STATES'], y=selection[(selection['CONSTNYR_GROUP']=='1990-1999')][w_data_type],marker_color=px.colors.sequential.Tealgrn[5],
               hovertemplate = '1990-1999 <br>%{x} <br>%{y:,.0f}<extra></extra>'),
        # go.Bar(name='1995-1999', x=selection[(selection['CONSTNYR_GROUP']=='1995-1999')]['STATES'], y=selection[(selection['CONSTNYR_GROUP']=='1995-1999')][w_data_type],marker_color=px.colors.sequential.haline[3],
        #        hovertemplate = '1995-1999 <br>%{x} <br>%{y:,.0f}<extra></extra>'),
        go.Bar(name='2000-2004', x=selection[(selection['CONSTNYR_GROUP']=='2000-2004')]['STATES'], y=selection[(selection['CONSTNYR_GROUP']=='2000-2004')][w_data_type],marker_color=px.colors.sequential.Tealgrn[4],
               hovertemplate = '2000-2004 <br>%{x} <br>%{y:,.0f}<extra></extra>'),
        go.Bar(name='2005-2009', x=selection[(selection['CONSTNYR_GROUP']=='2005-2009')]['STATES'], y=selection[(selection['CONSTNYR_GROUP']=='2005-2009')][w_data_type],marker_color=px.colors.sequential.Tealgrn[3],
               hovertemplate = '2005-2009 <br>%{x} <br>%{y:,.0f}<extra></extra>'),
        go.Bar(name='2010-2014', x=selection[(selection['CONSTNYR_GROUP']=='2010-2014')]['STATES'], y=selection[(selection['CONSTNYR_GROUP']=='2010-2014')][w_data_type],marker_color=px.colors.sequential.Tealgrn[2],
               hovertemplate = '2010-2014 <br>%{x} <br>%{y:,.0f}<extra></extra>'),
        go.Bar(name='2015-2019', x=selection[(selection['CONSTNYR_GROUP']=='2015-2019')]['STATES'], y=selection[(selection['CONSTNYR_GROUP']=='2015-2019')][w_data_type],marker_color=px.colors.sequential.Tealgrn[1],
               hovertemplate = '2015-2019 <br>%{x} <br>%{y:,.0f}<extra></extra>'),
        go.Bar(name='2020-2024', x=selection[(selection['CONSTNYR_GROUP']=='2020')]['STATES'], y=selection[(selection['CONSTNYR_GROUP']=='2020')][w_data_type],marker_color=px.colors.sequential.Tealgrn[0],
               hovertemplate = '2020 <br>%{x} <br>%{y:,.0f}<extra></extra>'),
        go.Bar(name='Error', x=selection[(selection['CONSTNYR_GROUP']=='Error')]['STATES'], y=selection[(selection['CONSTNYR_GROUP']=='Error')][w_data_type],marker_color='blue',
               hovertemplate = 'Error <br>%{x} <br>%{y:,.0f}<extra></extra>'),       
        ])            
        
    fig.update_layout(height=550,
                      barmode='stack',
                      paper_bgcolor='#1f2c56',
                      font_color="white",
                      margin = dict(t=80, l=1, r=1, b=1),
                      showlegend=False,
                      font=dict(size=18,
                                color='white'),                      
                      title={
                          'text':'{} by Construction Year & State ('.format(w_data_type_desc) + str(radio_items) + ')',
                          'y':0.99,
                          'x':0.5,
                          'xanchor':'center',
                          'yanchor':'top'},
                      titlefont={
                          'color':'white',
                          'size':25},
                      hoverlabel=dict(
                              font_size=20),
                      )
    fig.update_yaxes(ticksuffix = "  ")
    fig.update_xaxes(ticksuffix = "  ")
        
    return fig



@app.callback(Output('BH_pie_chart','figure'),
              [Input('radio_items','value')],
              [Input('w_data_type','value')])

def updated_graph(radio_items,w_data_type):
    radio_items=int(radio_items)
    if w_data_type=='PAIDLS': w_data_type_desc='Total Claims Paid'      
    if w_data_type=='BALOS': w_data_type_desc='Total Claims Outstanding'      
    if w_data_type=='INCTOT': w_data_type_desc='Total Claims Incurred'      
    if w_data_type=='INCCNT': w_data_type_desc='Total Claims Count'    
    
    df_bys=df.groupby(['LOSSYEAR','BHEIGHT_GROUP'])[w_data_type].sum().reset_index()
    selection=df_bys[(df_bys['LOSSYEAR']==radio_items)] 
    selection['BHEIGHT_GROUP'] = pd.Categorical(selection['BHEIGHT_GROUP'], 
                                    ['One Storey Building','Two Storey Building','Three Storey Building','Three and Above','Error'
                                    ],ordered=True)
    # selection.sort_values('BHEIGHT_GROUP')
    selection=selection.sort_values(by=['BHEIGHT_GROUP'])

    # selection['colors'] = np.where(selection['BHEIGHT_GROUP']!= 'Residential', 'limegreen', 'palegreen')
      
    fig=go.Figure()
    fig=go.Figure(data=[go.Pie(labels=selection['BHEIGHT_GROUP'],
               values=selection[w_data_type],
               hoverinfo='label+value+percent',
               # textinfo='value+percent',
               textfont=dict(size=18),
               hole=0.3,
               sort=False,
               marker=dict(colors=px.colors.sequential.Oryel_r)
               # marker=dict(colors=colors),
               )])
    
    fig.update_layout(height=550,
                      showlegend=True,
                      plot_bgcolor='#1f2c56',
                      paper_bgcolor='#1f2c56',
                      hovermode='closest',
                      autosize=True,
                      margin = dict(t=100, l=0, r=0, b=20),
                      title={
                          'text':'{} by Building Height ('.format(w_data_type_desc) + str(radio_items) + ')',
                          'y':0.99,
                          'x':0.5,
                          'xanchor':'center',
                          'yanchor':'top'},
                      titlefont={
                          'color':'white',
                          'size':25},
                      font=dict(
                          # family='sans-serif',
                          size=18,
                          color='white'),
                      legend={
                          'y':0.5,
                          'x':0.8,
                          'font':dict(size = 20, color = "white")
                          },
                      hoverlabel=dict(
                          font_size=20)
                      )
    fig.update_yaxes(ticksuffix = "  ")
    fig.update_xaxes(ticksuffix = "  ")       
        
    return fig



@app.callback(Output('BH_bar_chart','figure'),
              [Input('radio_items','value')],
              [Input('w_data_type','value')])

def updated_graph(radio_items,w_data_type):
    radio_items=int(radio_items)
    if w_data_type=='PAIDLS': w_data_type_desc='Total Claims Paid'      
    if w_data_type=='BALOS': w_data_type_desc='Total Claims Outstanding'      
    if w_data_type=='INCTOT': w_data_type_desc='Total Claims Incurred'      
    if w_data_type=='INCCNT': w_data_type_desc='Total Claims Count'    
    
    df_bys=df.groupby(['LOSSYEAR','STATES','BHEIGHT_GROUP'])[w_data_type].sum().reset_index()
    selection=df_bys[(df_bys['LOSSYEAR']==radio_items)]   
        
    fig = go.Figure()  
    fig = go.Figure(data=[
        go.Bar(name='One Storey Building', x=selection[(selection['BHEIGHT_GROUP']=='One Storey Building')]['STATES'], y=selection[(selection['BHEIGHT_GROUP']=='One Storey Building')][w_data_type],marker_color=px.colors.sequential.Oryel[4],
               hovertemplate = 'One Storey Building <br>%{x} <br>%{y:,.0f}<extra></extra>'),        
        go.Bar(name='Two Storey Building', x=selection[(selection['BHEIGHT_GROUP']=='Two Storey Building')]['STATES'], y=selection[(selection['BHEIGHT_GROUP']=='Two Storey Building')][w_data_type],marker_color=px.colors.sequential.Oryel[3],
               hovertemplate = 'Two Storey Building <br>%{x} <br>%{y:,.0f}<extra></extra>'),
        go.Bar(name='Three Storey Building', x=selection[(selection['BHEIGHT_GROUP']=='Three Storey Building')]['STATES'], y=selection[(selection['BHEIGHT_GROUP']=='Three Storey Building')][w_data_type],marker_color=px.colors.sequential.Oryel[2],
               hovertemplate = 'Three Storey Building <br>%{x} <br>%{y:,.0f}<extra></extra>'),
        go.Bar(name='Three and Above', x=selection[(selection['BHEIGHT_GROUP']=='Three and Above')]['STATES'], y=selection[(selection['BHEIGHT_GROUP']=='Three and Above')][w_data_type],marker_color=px.colors.sequential.Oryel[1],
               hovertemplate = 'Three and Above <br>%{x} <br>%{y:,.0f}<extra></extra>'),
        go.Bar(name='Error', x=selection[(selection['BHEIGHT_GROUP']=='Error')]['STATES'], y=selection[(selection['BHEIGHT_GROUP']=='Error')][w_data_type],marker_color=px.colors.sequential.Oryel[0],
               hovertemplate = 'Error <br>%{x} <br>%{y:,.0f}<extra></extra>'),
        ])            
        
    fig.update_layout(height=550,
                      barmode='stack',
                      paper_bgcolor='#1f2c56',
                      font_color="white",
                      margin = dict(t=80, l=1, r=1, b=1),
                      showlegend=False,
                      font=dict(size=18,
                                color='white'),                      
                      title={
                          'text':'{} by Construction Year & State ('.format(w_data_type_desc) + str(radio_items) + ')',
                          'y':0.99,
                          'x':0.5,
                          'xanchor':'center',
                          'yanchor':'top'},
                      titlefont={
                          'color':'white',
                          'size':25},
                      hoverlabel=dict(
                              font_size=20),
                      )
    fig.update_yaxes(ticksuffix = "  ")
    fig.update_xaxes(ticksuffix = "  ")
        
    return fig



#########################################################################################################

@app.callback(
    Output('var_treemap','figure'),
    [Input('radio_items','value')],
    [Input('w_var_type','value')],    
    [Input('w_data_type','value')])
def updated_graph(radio_items,w_var_type,w_data_type):
    
    radio_items=int(radio_items)
    df_bys=df.groupby(['LOSSYEAR',w_var_type])[['PAIDLS','BALOS','INCTOT','INCCNT']].sum().reset_index()
    selection=df_bys[(df_bys['LOSSYEAR']==radio_items)][['LOSSYEAR',w_var_type,w_data_type]]      
    
    if w_var_type=='LOB':    
        w_var_type_desc = []        
        for row in selection['LOB']:
            if row == '1' :   w_var_type_desc.append('Fire-Material Damage')
            elif row == '2':  w_var_type_desc.append('Fire-Consequential Damage')
            elif row == '3':  w_var_type_desc.append('Houseowner')
            elif row == '4':  w_var_type_desc.append('Householder')
            elif row == '5':  w_var_type_desc.append('Plantations')
            elif row == '6':  w_var_type_desc.append('Industrial All Risks-Section 1')
            elif row == '7':  w_var_type_desc.append('Industrial All Risks-Section 2')
            elif row == '8':  w_var_type_desc.append('Fire-Consequential Loss (Standalone)')
            elif row == '-1':  w_var_type_desc.append('Error')
            
            
    elif w_var_type=='RISK':  
        w_var_type_desc = []                
        for row in selection['RISK']:
            if row == '10' :   w_var_type_desc.append('Residential')
            elif row == '11':  w_var_type_desc.append('Retail')
            elif row == '12':  w_var_type_desc.append('Hotel, Office')
            elif row == '13':  w_var_type_desc.append('Mining')
            elif row == '14':  w_var_type_desc.append('Construction')
            elif row == '15':  w_var_type_desc.append('Food Processing')            
            elif row == '16':  w_var_type_desc.append('Beverage')
            elif row == '17':  w_var_type_desc.append('Tobacco')
            elif row == '18':  w_var_type_desc.append('Textiles')
            elif row == '19':  w_var_type_desc.append('Leather & Fibre')
            elif row == '20':  w_var_type_desc.append('Timber')
            elif row == '21':  w_var_type_desc.append('Paper & Printing')
            elif row == '22':  w_var_type_desc.append('Chemicals')
            elif row == '23':  w_var_type_desc.append('Petroleum')
            elif row == '24':  w_var_type_desc.append('Rubber')
            elif row == '25':  w_var_type_desc.append('Plastics')
            elif row == '26':  w_var_type_desc.append('Non-metalic minerals')
            elif row == '27':  w_var_type_desc.append('Metal Working, Engineering')
            elif row == '28':  w_var_type_desc.append('Motor Trade and Related Risks')
            elif row == '29':  w_var_type_desc.append('Restaurants, Places of recreation')
            elif row == '30':  w_var_type_desc.append('Utilities')
            elif row == '31':  w_var_type_desc.append('Transport')
            elif row == '33':  w_var_type_desc.append('Cinemas, studios & exhibition halls')
            elif row == '34':  w_var_type_desc.append('General Storage')
            elif row == '35':  w_var_type_desc.append('Oil Mill')
            elif row == '36':  w_var_type_desc.append('Rice & Flour Mills')
            elif row == '37':  w_var_type_desc.append('Sugar Factory')
            elif row == '38':  w_var_type_desc.append('Cocoa, Coffee & Tea Factories')
            elif row == '39':  w_var_type_desc.append('Cold stores')
            elif row == '40':  w_var_type_desc.append('Houseowners & Householders')
            elif row == '50':  w_var_type_desc.append('Plantations')   
            elif row == '-1':  w_var_type_desc.append('Error')             
            
    elif w_var_type=='BASE RATE':  
        w_var_type_desc = []                
        for row in selection['BASE RATE']:
            if row == '0' :   w_var_type_desc.append('Tariff')
            elif row == '1':  w_var_type_desc.append('Self-Rating')
            elif row == '2':  w_var_type_desc.append('Special Rating')
            elif row == '3':  w_var_type_desc.append('Large & Specialized Risk')
            elif row == '4':  w_var_type_desc.append('Industrial All Risks')
            elif row == '5':  w_var_type_desc.append('Non-Tariff')
            elif row == '-1':  w_var_type_desc.append('Error')

    elif w_var_type=='CONSTN':  
        w_var_type_desc = []                
        for row in selection['CONSTN']:
            if row == '1' :   w_var_type_desc.append('Class 1A')
            elif row == '2':  w_var_type_desc.append('Class 1B')
            elif row == '3':  w_var_type_desc.append('Class 2')
            elif row == '4':  w_var_type_desc.append('Class 3')
            elif row == '-1':  w_var_type_desc.append('Error')

    elif w_var_type=='PRODUCT':  
        w_var_type_desc = []                
        for row in selection['PRODUCT']:
            if row == '1' :   w_var_type_desc.append('Tariff Rated/ Self-Rated/ Special Rated/ LSR/ IAR')
            elif row == '2':  w_var_type_desc.append('Non-Tariff Rated')
            elif row == '3':  w_var_type_desc.append('Enhanced Houseowner')
            elif row == '4':  w_var_type_desc.append('Enhanced Householder')
            elif row == '5':  w_var_type_desc.append('Enhanced Fire-Long Term Contract')
            elif row == '6':  w_var_type_desc.append('Enhanced Fire-Long Term Agreement')   
            elif row == '7':  w_var_type_desc.append('Enhanced Fire-Others') 
            elif row == '-1':  w_var_type_desc.append('Error')

    elif w_var_type=='PERILS':  
        w_var_type_desc = []                
        for row in selection['PERILS']:
            if row == '1' :   w_var_type_desc.append('Fire & Lightning')
            elif row == '2':  w_var_type_desc.append('Riot Strike & Malicious Damage')
            elif row == '3':  w_var_type_desc.append('Explosion')
            elif row == '4':  w_var_type_desc.append('Flood')
            elif row == '5':  w_var_type_desc.append('Aircraft')
            elif row == '6':  w_var_type_desc.append('Earthquake & Volcanic Eruption')            
            elif row == '8':  w_var_type_desc.append('Storm Tempest')
            elif row == '9':  w_var_type_desc.append('Impact Damage')
            elif row == '10':  w_var_type_desc.append('Bursting of Pipes, Water Tanks')
            elif row == '11':  w_var_type_desc.append('Electrical Installations')
            elif row == '12':  w_var_type_desc.append('Theft/ Burglary')
            elif row == '13':  w_var_type_desc.append('Subsidence & Landslip')        
            elif row == '14':  w_var_type_desc.append('Spontaneous Combustion')
            elif row == '15':  w_var_type_desc.append('Falling Trees')
            elif row == '16':  w_var_type_desc.append('Bush/ Lalang Fire')
            elif row == '17':  w_var_type_desc.append('Sprinkler Leakage')
            elif row == '18':  w_var_type_desc.append('All Warranty that involve premiums')
            elif row == '19':  w_var_type_desc.append('All Clauses & Endorsement that involve premiums')
            elif row == '20':  w_var_type_desc.append('Loading')
            elif row == '21':  w_var_type_desc.append('Discount')
            elif row == '22':  w_var_type_desc.append('Animal Damage')
            elif row == '23':  w_var_type_desc.append('Goods and stocks undergoing any drying/ heating process')
            elif row == '24':  w_var_type_desc.append('Smoke Damage')
            elif row == '25':  w_var_type_desc.append('Cold Storage/ Incubator Clause B')
            elif row == '26':  w_var_type_desc.append('Lost Adjustment Fee/ Legal Charges')
            elif row == '27':  w_var_type_desc.append('Salvage')
            elif row == '28':  w_var_type_desc.append('Extended theft cover (i) excluding theft by domestic servants')
            elif row == '29':  w_var_type_desc.append('Extended theft cover (ii) including theft by domestic servants')
            elif row == '30':  w_var_type_desc.append('Terrorism')
            elif row == '31':  w_var_type_desc.append('Non-Fire Related Covers') 
            elif row == '-1':  w_var_type_desc.append('Error')
            
    elif w_var_type=='DCHNL':  
        w_var_type_desc = []                
        for row in selection['DCHNL']:
            if row == '0' :   w_var_type_desc.append('Agent')
            elif row == '1':  w_var_type_desc.append('Broker')
            elif row == '2':  w_var_type_desc.append('Banca Assurance')
            elif row == '3':  w_var_type_desc.append('Direct-Internet')
            elif row == '4':  w_var_type_desc.append('Direct-Mail')
            elif row == '5':  w_var_type_desc.append('Direct-Corporate Client')   
            elif row == '6':  w_var_type_desc.append('Direct-Walk In')               
            elif row == '7':  w_var_type_desc.append('Direct-Phone')
            elif row == '9':  w_var_type_desc.append('Others')    
            elif row == '-1':  w_var_type_desc.append('Error') 
    
    
    selection['w_var_type_desc']=w_var_type_desc
    selection['w_var_type_desc'] = pd.DataFrame(w_var_type_desc, index=selection.index)
    selection.reset_index()     

    if w_var_type=='LOB': name='Line of Business'
    elif w_var_type=='RISK': name='Risk Code'
    elif w_var_type=='BASE RATE': name='Base Rate'
    elif w_var_type=='CONSTN': name='Construction'
    elif w_var_type=='PRODUCT': name='Fire Product'
    elif w_var_type=='DCHNL': name='Distribution Channel'   
    
    if w_data_type=='PAIDLS': w_data_type_desc='Total Claims Paid'      
    if w_data_type=='BALOS': w_data_type_desc='Total Claims Outstanding'      
    if w_data_type=='INCTOT': w_data_type_desc='Total Claims Incurred'      
    if w_data_type=='INCCNT': w_data_type_desc='Total Claims Count'    
    
    return{
        'data':[go.Treemap(
            labels=selection['w_var_type_desc'].tolist(),
            values=selection[w_data_type].tolist(),
            parents=[""]*len(selection['w_var_type_desc']),
            # root_color='#1f2c56',
            marker_colorscale = 'peach',
            textinfo = 'label+value+percent entry'
            )],
        'layout':go.Layout(height=650,
            plot_bgcolor='#1f2c56',
            paper_bgcolor='#1f2c56',
            hovermode='closest',
            autosize=True,
            margin = dict(t=80, l=1, r=1, b=1),
            title={
                'text':'{} by '.format(w_data_type_desc) + str(name) +' (' + str(radio_items) + ')',
                'y':0.99,
                'x':0.5,
                'xanchor':'center',
                'yanchor':'top'},
            titlefont={
                'color':'white',
                'size':25},
            font=dict(
                # family='sans-serif',
                size=20,
                color='white'),
            hoverlabel=dict(font_size=20),
            ),
        }      


@app.callback(Output('var_quarterly_chart','figure'),
              [Input('radio_items','value')],
              [Input('w_breakdown','value')],                              
              [Input('w_var_type','value')],                              
              [Input('w_state','value')],
              [Input('w_data_type','value')])

def updated_graph(radio_items,w_breakdown,w_var_type,w_state,w_data_type):
    radio_items=int(radio_items)
    x=latest_year-5
    x1=x+1  
    
    if w_data_type=='PAIDLS': w_data_type_desc='Total Claims Paid'      
    if w_data_type=='BALOS': w_data_type_desc='Total Claims Outstanding'      
    if w_data_type=='INCTOT': w_data_type_desc='Total Claims Incurred'      
    if w_data_type=='INCCNT': w_data_type_desc='Total Claims Count'    
    
    if w_state=='Malaysia':
        df_bys=df.groupby(['LOSSYEAR','LOSSQUARTER',w_var_type])[['PAIDLS','BALOS','INCTOT','INCCNT']].sum().reset_index()
        df_bys=df_bys[(df_bys['LOSSYEAR']>x)&(df_bys[w_var_type]==w_breakdown)]
        
        fig = go.Figure()
        fig.update_layout(height=500,
                          barmode='stack',    
                          paper_bgcolor='#1f2c56',
                          font_color="white",
                          margin = dict(t=80, l=1, r=1, b=145),
                          title={
                              'text':'{} by Quarter: {} ('.format(w_data_type_desc,w_state) + str(x1) + ' - '+ str(latest_year) + ')',
                              'y':0.99,
                              'x':0.5,
                              'xanchor':'center',
                              'yanchor':'top'},
                          titlefont={
                              'color':'white',
                              'size':25},
                          xaxis_title="Quarter",
                          hoverlabel=dict(font_size=20),
                          font=dict(size=18,color='white'))
        fig.update_yaxes(ticksuffix = "  ")
        fig.update_xaxes(ticksuffix = "  ")
                          
        # for r in ( df_bys['STATES'].unique()):
        #     plot_df = df_bys[df_bys['STATES'] == r]
        fig.add_trace(
            go.Bar(x=[df_bys['LOSSQUARTER'],df_bys['LOSSYEAR']], y=df_bys[w_data_type], marker_color='cornflowerblue',
                   hovertemplate = '%{y:,.0f}<extra></extra>'),
            )
        return fig
    
    else:
        df_bys=df.groupby(['LOSSYEAR','LOSSQUARTER','STATES',w_var_type])[['PAIDLS','BALOS','INCTOT','INCCNT']].sum().reset_index()
        df_bys=df_bys[(df_bys['LOSSYEAR']>x)&(df_bys['STATES']==w_state)&(df_bys[w_var_type]==w_breakdown)]
        
        fig = go.Figure()
        fig.update_layout(height=500,
                          barmode='stack',    
                          paper_bgcolor='#1f2c56',
                          font_color="white",
                          margin = dict(t=80, l=1, r=1, b=145),
                          title={
                              'text':'{} by Quarter: {} ('.format(w_data_type_desc,w_state) + str(x1) + ' - '+ str(latest_year) + ')',
                              'y':0.99,
                              'x':0.5,
                              'xanchor':'center',
                              'yanchor':'top'},
                          titlefont={
                              'color':'white',
                              'size':25},
                          xaxis_title="Quarter",
                          hoverlabel=dict(font_size=20),
                          font=dict(size=18,color='white'))
        fig.update_yaxes(ticksuffix = "  ")
        fig.update_xaxes(ticksuffix = "  ")  
        
        for r in ( df_bys['STATES'].unique()):
            plot_df = df_bys[df_bys['STATES'] == r]
            fig.add_trace(
                go.Bar(x=[plot_df['LOSSQUARTER'],plot_df['LOSSYEAR']], y=plot_df[w_data_type], name=r,marker_color='cornflowerblue',
                       hovertemplate = '%{y:,.0f}<extra></extra>'),
            )
        return fig     
    
    

@app.callback(Output('var_monthly_chart','figure'),
              [Input('radio_items','value')],
              [Input('w_breakdown','value')],                              
              [Input('w_var_type','value')],   
              [Input('w_state','value')],                            
              [Input('w_data_type','value')])

def updated_graph(radio_items,w_breakdown,w_var_type,w_state,w_data_type):

    radio_items=int(radio_items)
    if w_data_type=='PAIDLS': w_data_type_desc='Total Claims Paid'      
    if w_data_type=='BALOS': w_data_type_desc='Total Claims Outstanding'      
    if w_data_type=='INCTOT': w_data_type_desc='Total Claims Incurred'      
    if w_data_type=='INCCNT': w_data_type_desc='Total Claims Count'    
    
    df_bys=df.groupby(['LOSSYEAR','LOSSMONTH',w_var_type])[['PAIDLS','BALOS','INCTOT','INCCNT']].sum().reset_index()  
        
    if w_state=='Malaysia':
        df_bys=df.groupby(['LOSSYEAR','LOSSMONTH',w_var_type])[w_data_type].sum().reset_index() 
        selection=df_bys[(df_bys['LOSSYEAR']==radio_items)&(df_bys[w_var_type]==w_breakdown)]
        # df_bys[w_data_type] = df_bys[w_data_type].apply(lambda x : "{:,.0f}".format(x))    
        
    else:
        df_bys=df.groupby(['LOSSYEAR','LOSSMONTH','STATES',w_var_type])[w_data_type].sum().reset_index() 
        selection=df_bys[(df_bys['LOSSYEAR']==radio_items)&(df_bys['STATES']==w_state)&(df_bys[w_var_type]==w_breakdown)]            
    
    
    fig = go.Figure(data=[
        go.Bar(x=selection['LOSSMONTH'], y=selection[w_data_type],marker_color='cornflowerblue',
               hovertemplate = '%{y:,.0f}<extra></extra>'),
    ])    
        
    fig.update_layout(height=500,
                      barmode='stack',  
                      hovermode='closest',
                      paper_bgcolor='#1f2c56',
                      margin = dict(t=80, l=1, r=1, b=1),
                      title={
                          'text':'{} by Month: {} ('.format(w_data_type_desc,w_state) + str(radio_items) + ')',
                          'y':0.99,
                          'x':0.5,
                          'xanchor':'center',
                          'yanchor':'top'},
                      titlefont={
                          'color':'white',
                          'size':25},
                      hoverlabel=dict(font_size=20),
                      font=dict(size=18,color='white'),
                       xaxis=dict(title='Month',tickvals=['1','2','3','4','5','6','7','8','9','10','11','12']))
    fig.update_yaxes(ticksuffix = "  ")
    fig.update_xaxes(ticksuffix = "  ")  
    
    return fig


@app.callback(Output('var_RC_pie_chart','figure'),
              [Input('radio_items','value')],
              [Input('w_data_type','value')],
              [Input('w_var_type','value')],
              [Input('w_breakdown','value')])

def updated_graph(radio_items,w_data_type,w_var_type,w_breakdown):
    radio_items=int(radio_items)
    if w_data_type=='PAIDLS': w_data_type_desc='Total Claims Paid'      
    if w_data_type=='BALOS': w_data_type_desc='Total Claims Outstanding'      
    if w_data_type=='INCTOT': w_data_type_desc='Total Claims Incurred'      
    if w_data_type=='INCCNT': w_data_type_desc='Total Claims Count'    
    
    df_bys=df.groupby(['LOSSYEAR','BUILDING_TYPE',w_var_type])[['PAIDLS','BALOS','INCTOT','INCCNT','BUILDING_TYPE_CNT']].sum().reset_index()
    selection=df_bys[(df_bys['LOSSYEAR']==radio_items)&(df_bys[w_var_type]==w_breakdown)][[w_data_type,'BUILDING_TYPE','BUILDING_TYPE_CNT']].reset_index()      
    
    conditions=[selection['BUILDING_TYPE']=='Residential',
                selection['BUILDING_TYPE']=='Commercial',
                selection['BUILDING_TYPE']=='Error']
    values=['lightgreen','limegreen','grey']
    
    selection['colors'] = np.select(conditions,values)

    fig=go.Figure()
    fig=go.Figure(data=[go.Pie(labels=selection['BUILDING_TYPE'],
               values=selection[w_data_type],
               marker_colors= selection['colors'],
               hoverinfo='label+value+percent',
               textinfo='value+percent',
               textfont=dict(size=18),
               hole=0,    
               )])
    
    fig.update_layout(height=550,
                      showlegend=True,
                      plot_bgcolor='#1f2c56',
                      paper_bgcolor='#1f2c56',
                      hovermode='closest',
                      autosize=True,
                      margin = dict(t=100, l=0, r=0, b=20),
                      title={
                          'text':'{} by Property Type ('.format(w_data_type_desc) + str(radio_items) + ')',
                          'y':0.99,
                          'x':0.5,
                          'xanchor':'center',
                          'yanchor':'top'},
                      titlefont={
                          'color':'white',
                          'size':25},
                      font=dict(
                          # family='sans-serif',
                          size=18,
                          color='white'),
                      legend={
                          'y':0.5,
                          'x':0.8,
                          'font':dict(size = 20, color = "white")
                          },
                      hoverlabel=dict(
                          font_size=20)
                      )
    fig.update_yaxes(ticksuffix = "  ")
    fig.update_xaxes(ticksuffix = "  ")       
        
    return fig



@app.callback(Output('var_RC_bar_chart','figure'),
              [Input('w_breakdown','value')],                              
              [Input('w_var_type','value')],                                            
              [Input('radio_items','value')],
              [Input('w_data_type','value')])

def updated_graph(w_breakdown,w_var_type,radio_items,w_data_type):
    radio_items=int(radio_items)
    if w_data_type=='PAIDLS': w_data_type_desc='Total Claims Paid'      
    if w_data_type=='BALOS': w_data_type_desc='Total Claims Outstanding'      
    if w_data_type=='INCTOT': w_data_type_desc='Total Claims Incurred'      
    if w_data_type=='INCCNT': w_data_type_desc='Total Claims Count'    
    
    df_bys=df.groupby(['LOSSYEAR','STATES','BUILDING_TYPE',w_var_type])[['PAIDLS','BALOS','INCTOT','INCCNT','BUILDING_TYPE_CNT']].sum().reset_index()
    selection=df_bys[(df_bys['LOSSYEAR']==radio_items)&(df_bys[w_var_type]==w_breakdown)][['STATES','LOSSYEAR',w_data_type,'BUILDING_TYPE','BUILDING_TYPE_CNT']]      


    fig = go.Figure()  
    fig = go.Figure(data=[
        go.Bar(name='Commercial', x=selection[(selection['BUILDING_TYPE']=='Commercial')]['STATES'], y=selection[(selection['BUILDING_TYPE']=='Commercial')][w_data_type],marker_color='limegreen',
               hovertemplate = 'Commercial <br>%{x} <br>%{y:,.0f}<extra></extra>'),        
        go.Bar(name='Residential', x=selection[(selection['BUILDING_TYPE']=='Residential')]['STATES'], y=selection[(selection['BUILDING_TYPE']=='Residential')][w_data_type],marker_color='lightgreen',
               hovertemplate = 'Residential <br>%{x} <br>%{y:,.0f}<extra></extra>'),
        go.Bar(name='Error', x=selection[(selection['BUILDING_TYPE']=='Error')]['STATES'], y=selection[(selection['BUILDING_TYPE']=='Error')][w_data_type],marker_color='grey',
               hovertemplate = 'Error <br>%{x} <br>%{y:,.0f}<extra></extra>'),
        ])            
        
    fig.update_layout(height=550,
                      barmode='stack',
                      paper_bgcolor='#1f2c56',
                      margin = dict(t=80, l=1, r=1, b=1),
                      showlegend=False,
                      title={
                          'text':'{} by Property Type & State ('.format(w_data_type_desc) + str(radio_items) + ')',
                          'y':0.99,
                          'x':0.5,
                          'xanchor':'center',
                          'yanchor':'top'},
                      titlefont={
                          'color':'white',
                          'size':25},
                      hoverlabel=dict(
                          font_size=20),
                     font=dict(size=18,color='white'),
                     )
    fig.update_yaxes(ticksuffix = "  ")
    fig.update_xaxes(ticksuffix = "  ")  
    
    return fig



@app.callback(Output('var_report_claims_area_chart','figure'),
              [Input('radio_items','value')],
              [Input('w_breakdown','value')],                              
              [Input('w_var_type','value')],               
              [Input('w_data_type','value')])

def updated_graph(radio_items,w_breakdown,w_var_type,w_data_type):
    radio_items=int(radio_items)
    df_bys=df.groupby(['LOSSYEAR','LOSSMONTH',w_var_type,'CLAIMS_FILING_GROUP'])[['PAIDLS','BALOS','INCTOT','INCCNT']].sum().reset_index()
    selection=df_bys[(df_bys['LOSSYEAR']==radio_items)&(df_bys[w_var_type]==w_breakdown)][['LOSSMONTH',w_data_type,'CLAIMS_FILING_GROUP']]      

    fig = go.Figure()  
    
    fig.add_trace(go.Scatter(name='0-7 days', x=selection[(selection['CLAIMS_FILING_GROUP']=='0-7 days')]['LOSSMONTH'], y=selection[(selection['CLAIMS_FILING_GROUP']=='0-7 days')][w_data_type],fillcolor='rebeccapurple',line=dict(color='rebeccapurple'),stackgroup='one',
                             hovertemplate = '0-7 days: %{y:,.0f}<extra></extra>'))
    fig.add_trace(go.Scatter(name='8-30 days', x=selection[(selection['CLAIMS_FILING_GROUP']=='8-30 days')]['LOSSMONTH'], y=selection[(selection['CLAIMS_FILING_GROUP']=='8-30 days')][w_data_type],fillcolor='darkviolet',line=dict(color='darkviolet'),stackgroup='one',
                             hovertemplate = '8-30 days: %{y:,.0f}<extra></extra>'))              
    fig.add_trace(go.Scatter(name='1-2 months', x=selection[(selection['CLAIMS_FILING_GROUP']=='1-2 months')]['LOSSMONTH'], y=selection[(selection['CLAIMS_FILING_GROUP']=='1-2 months')][w_data_type],fillcolor='mediumorchid',line=dict(color='mediumorchid'),stackgroup='one',
                             hovertemplate = '1-2 months: %{y:,.0f}<extra></extra>'))           
    fig.add_trace(go.Scatter(name='2-3 months', x=selection[(selection['CLAIMS_FILING_GROUP']=='2-3 months')]['LOSSMONTH'], y=selection[(selection['CLAIMS_FILING_GROUP']=='2-3 months')][w_data_type],fillcolor='orchid',line=dict(color='orchid'),stackgroup='one',
                             hovertemplate = '2-3 months: %{y:,.0f}<extra></extra>'))
    fig.add_trace(go.Scatter(name='3-6 months', x=selection[(selection['CLAIMS_FILING_GROUP']=='3-6 months')]['LOSSMONTH'], y=selection[(selection['CLAIMS_FILING_GROUP']=='3-6 months')][w_data_type],fillcolor='plum',line=dict(color='plum'),stackgroup='one',
                             hovertemplate = '3-6 months: %{y:,.0f}<extra></extra>'))
    fig.add_trace(go.Scatter(name='6-12 months', x=selection[(selection['CLAIMS_FILING_GROUP']=='6-12 months')]['LOSSMONTH'], y=selection[(selection['CLAIMS_FILING_GROUP']=='6-12 months')][w_data_type],fillcolor='lavender',line=dict(color='lavender'),stackgroup='one',
                             hovertemplate = '6-12 months: %{y:,.0f}<extra></extra>'))
    # fig.add_trace(go.Scatter(name='1-2 years', x=selection[(selection['CLAIMS_FILING_GROUP']=='1-2 years')]['LOSSMONTH'], y=selection[(selection['CLAIMS_FILING_GROUP']=='1-2 years')][w_data_type],fillcolor='lightsteelblue',line=dict(color='lightsteelblue'),stackgroup='one',
    #                          hovertemplate = '1-2 years: %{y:,.0f}<extra></extra>'))
    # fig.add_trace(go.Scatter(name='>2 years', x=selection[(selection['CLAIMS_FILING_GROUP']=='>2 years')]['LOSSMONTH'], y=selection[(selection['CLAIMS_FILING_GROUP']=='>2 years')][w_data_type],fillcolor='steelblue',line=dict(color='steelblue'),stackgroup='one',
    #                          hovertemplate = '>2 years: %{y:,.0f}<extra></extra>'))
    fig.add_trace(go.Scatter(name='Error', x=selection[(selection['CLAIMS_FILING_GROUP']=='Error')]['LOSSMONTH'], y=selection[(selection['CLAIMS_FILING_GROUP']=='Error')][w_data_type],fillcolor='grey',line=dict(color='grey'),stackgroup='one',
                             hovertemplate = 'Error: %{y:,.0f}<extra></extra>'))
           
    fig.update_layout(height=550,
                      showlegend=True,
                      xaxis_type='category',
                      paper_bgcolor='#1f2c56',
                      font_color="white",
                      margin = dict(t=80, l=1, r=1, b=1),
                      font=dict(size=18,
                                color='white'),                      
                      title={
                          'text':'Gap between Loss Date and Reported Date by Month (' + str(radio_items) + ')',
                          'y':0.99,
                          'x':0.5,
                          'xanchor':'center',
                          'yanchor':'top'},
                      titlefont={
                          'color':'white',
                          'size':25},
                      legend_y=0.5,
                      hoverlabel=dict(
                              font_size=20),
                      xaxis_title="Month",
                      )
    fig.update_yaxes(ticksuffix = "  ")
    fig.update_xaxes(ticksuffix = "  ")
    
    return fig



@app.callback(Output('var_report_claims_bar_chart','figure'),
              [Input('radio_items','value')],
              [Input('w_breakdown','value')],                              
              [Input('w_var_type','value')],                              
              [Input('w_data_type','value')])

def updated_graph(radio_items,w_breakdown,w_var_type,w_data_type):
    radio_items=int(radio_items)
    df_bys=df.groupby(['LOSSYEAR','STATES',w_var_type,'CLAIMS_FILING_GROUP'])[['PAIDLS','BALOS','INCTOT','INCCNT']].sum().reset_index()
    selection=df_bys[(df_bys['LOSSYEAR']==radio_items)&(df_bys[w_var_type]==w_breakdown)][['STATES',w_data_type,'CLAIMS_FILING_GROUP']]      

    fig = go.Figure(data=[
        go.Bar(name='0-7 days', x=selection[(selection['CLAIMS_FILING_GROUP']=='0-7 days')]['STATES'], y=selection[(selection['CLAIMS_FILING_GROUP']=='0-7 days')][w_data_type],marker_color='rebeccapurple',
               hovertemplate = '0-7 days <br>%{x} <br>%{y:,.0f}<extra></extra>'),        
        go.Bar(name='8-30 days', x=selection[(selection['CLAIMS_FILING_GROUP']=='8-30 days')]['STATES'], y=selection[(selection['CLAIMS_FILING_GROUP']=='8-30 days')][w_data_type],marker_color='darkviolet',
               hovertemplate = '8-30 days <br>%{x} <br>%{y:,.0f}<extra></extra>'),
        go.Bar(name='1-2 months', x=selection[(selection['CLAIMS_FILING_GROUP']=='1-2 months')]['STATES'], y=selection[(selection['CLAIMS_FILING_GROUP']=='1-2 months')][w_data_type],marker_color='mediumorchid',
               hovertemplate = '1-2 months <br>%{x} <br>%{y:,.0f}<extra></extra>'),
        go.Bar(name='2-3 months', x=selection[(selection['CLAIMS_FILING_GROUP']=='2-3 months')]['STATES'], y=selection[(selection['CLAIMS_FILING_GROUP']=='2-3 months')][w_data_type],marker_color='orchid',
               hovertemplate = '2-3 months <br>%{x} <br>%{y:,.0f}<extra></extra>'),
        go.Bar(name='3-6 months', x=selection[(selection['CLAIMS_FILING_GROUP']=='3-6 months')]['STATES'], y=selection[(selection['CLAIMS_FILING_GROUP']=='3-6 months')][w_data_type],marker_color='plum',
               hovertemplate = '3-6 months <br>%{x} <br>%{y:,.0f}<extra></extra>'),
        go.Bar(name='6-12 months', x=selection[(selection['CLAIMS_FILING_GROUP']=='6-12 months')]['STATES'], y=selection[(selection['CLAIMS_FILING_GROUP']=='6-12 months')][w_data_type],marker_color='lavender',
               hovertemplate = '6-12 months <br>%{x} <br>%{y:,.0f}<extra></extra>'),
        go.Bar(name='1-2 years', x=selection[(selection['CLAIMS_FILING_GROUP']=='1-2 years')]['STATES'], y=selection[(selection['CLAIMS_FILING_GROUP']=='1-2 years')][w_data_type],marker_color='lightsteelblue',
               hovertemplate = '1-2 years <br>%{x} <br>%{y:,.0f}<extra></extra>'),
        go.Bar(name='>2 years', x=selection[(selection['CLAIMS_FILING_GROUP']=='>2 years')]['STATES'], y=selection[(selection['CLAIMS_FILING_GROUP']=='>2 years')][w_data_type],marker_color='steelblue',
               hovertemplate = '>2 years <br>%{x} <br>%{y:,.0f}<extra></extra>'),
        go.Bar(name='Error', x=selection[(selection['CLAIMS_FILING_GROUP']=='Error')]['STATES'], y=selection[(selection['CLAIMS_FILING_GROUP']=='Error')][w_data_type],marker_color='grey',
               hovertemplate = 'Error <br>%{x} <br>%{y:,.0f}<extra></extra>'),        
        ])  

    fig.update_layout(height=550,
                      barmode='stack',
                      paper_bgcolor='#1f2c56',
                      font_color="white",
                      margin = dict(t=80, l=1, r=1, b=1),
                      showlegend=False,
                      font=dict(size=18,
                                color='white'),                      
                      title={
                          'text':'Gap between Loss Date and Reported Date by States (' + str(radio_items) + ')',
                          'y':0.99,
                          'x':0.5,
                          'xanchor':'center',
                          'yanchor':'top'},
                      titlefont={
                          'color':'white',
                          'size':25},
                      hoverlabel=dict(
                              font_size=20),
                      )
    fig.update_yaxes(ticksuffix = "  ")
    fig.update_xaxes(ticksuffix = "  ")
     
    return fig



@app.callback(Output('var_accident_happen_area_chart','figure'),
              [Input('radio_items','value')],
              [Input('w_breakdown','value')],                              
              [Input('w_var_type','value')],             
              [Input('w_data_type','value')])

def updated_graph(radio_items,w_breakdown,w_var_type,w_data_type):
    radio_items=int(radio_items)
    df_bys=df.groupby(['LOSSYEAR',w_var_type,'ACCIDENT_OCCUR_GROUP'])[['PAIDLS','BALOS','INCTOT','INCCNT']].sum().reset_index()
    selection=df_bys[(df_bys['LOSSYEAR']==radio_items)&(df_bys[w_var_type]==w_breakdown)][[w_data_type,'ACCIDENT_OCCUR_GROUP']]      

    # fig = go.Figure()  
    # fig.add_trace(go.Scatter(name='1-3 months', x=selection[(selection['ACCIDENT_OCCUR_GROUP']=='1-3 months')]['LOSSMONTH'], y=selection[(selection['ACCIDENT_OCCUR_GROUP']=='1-3 months')][w_data_type],fillcolor='mediumvioletred',line=dict(color='mediumvioletred'),stackgroup='one',
    #                          hovertemplate = '1-3 months: %{y:,.0f}<extra></extra>'))
    # fig.add_trace(go.Scatter(name='4-6 months', x=selection[(selection['ACCIDENT_OCCUR_GROUP']=='4-6 months')]['LOSSMONTH'], y=selection[(selection['ACCIDENT_OCCUR_GROUP']=='4-6 months')][w_data_type],fillcolor='palevioletred',line=dict(color='palevioletred'),stackgroup='one',
    #                          hovertemplate = '4-6 months: %{y:,.0f}<extra></extra>'))
    # fig.add_trace(go.Scatter(name='7-9 months', x=selection[(selection['ACCIDENT_OCCUR_GROUP']=='7-9 months')]['LOSSMONTH'], y=selection[(selection['ACCIDENT_OCCUR_GROUP']=='7-9 months')][w_data_type],fillcolor='lightpink',line=dict(color='lightpink'),stackgroup='one',
    #                          hovertemplate = '7-9 months: %{y:,.0f}<extra></extra>'))
    # fig.add_trace(go.Scatter(name='10-12 months', x=selection[(selection['ACCIDENT_OCCUR_GROUP']=='10-12 months')]['LOSSMONTH'], y=selection[(selection['ACCIDENT_OCCUR_GROUP']=='10-12 months')][w_data_type],fillcolor='mistyrose',line=dict(color='mistyrose'),stackgroup='one',
    #                          hovertemplate = '10-12 months: %{y:,.0f}<extra></extra>'))
    # fig.add_trace(go.Scatter(name='>12 months', x=selection[(selection['ACCIDENT_OCCUR_GROUP']=='>12 months')]['LOSSMONTH'], y=selection[(selection['ACCIDENT_OCCUR_GROUP']=='>12 months')][w_data_type],fillcolor='grey',line=dict(color='grey'),stackgroup='one',
    #                          hovertemplate = '>12 months: %{y:,.0f}<extra></extra>'))
    # fig.add_trace(go.Scatter(name='Error', x=selection[(selection['ACCIDENT_OCCUR_GROUP']=='Error')]['LOSSMONTH'], y=selection[(selection['ACCIDENT_OCCUR_GROUP']=='Error')][w_data_type],fillcolor='grey',line=dict(color='grey'),stackgroup='one',
    #                          hovertemplate = 'Error: %{y:,.0f}<extra></extra>'))
    
    selection['ACCIDENT_OCCUR_GROUP'] = pd.Categorical(selection['ACCIDENT_OCCUR_GROUP'], 
                                    ['<1 month','1-3 months',
                                      '3-6 months','6-9 months','9-12 months','>12 months',
                                    ],ordered=True)
    selection.sort_values('ACCIDENT_OCCUR_GROUP')
    selection=selection.sort_values(by=['ACCIDENT_OCCUR_GROUP'])
    
    conditions=[selection['ACCIDENT_OCCUR_GROUP']=='<1 month',
                selection['ACCIDENT_OCCUR_GROUP']=='1-3 months',
                selection['ACCIDENT_OCCUR_GROUP']=='3-6 months',
                selection['ACCIDENT_OCCUR_GROUP']=='6-9 months',
                selection['ACCIDENT_OCCUR_GROUP']=='9-12 months',
                selection['ACCIDENT_OCCUR_GROUP']=='>12 months',
                ]
    values=['mediumvioletred',
            'palevioletred',
            'lightpink',
            'mistyrose',
            'peachpuff',          
            'darksalmon',         
        ]
    selection['colors']=np.select(conditions,values)    
    
    fig=go.Figure()
    fig=go.Figure(data=[go.Pie(labels=selection['ACCIDENT_OCCUR_GROUP'],
               values=selection[w_data_type],
               hoverinfo='label+value+percent',
               # textinfo='value+percent',
               textfont=dict(size=18),
               hole=0.3,
               sort=False,
               marker_colors=selection['colors']
               # marker=dict(colors=colors),
               )])    
    
    
    fig.update_layout(height=550,
                      showlegend=True,
                      # xaxis_type='category',
                      paper_bgcolor='#1f2c56',
                      font_color="white",
                      margin = dict(t=80, l=1, r=1, b=20),
                      font=dict(size=18,
                                color='white'),                      
                      title={
                          'text':'Gap between Policy Inception Date and Loss Date (' + str(radio_items) + ')',
                          'y':0.99,
                          'x':0.5,
                          'xanchor':'center',
                          'yanchor':'top'},
                      titlefont={
                          'color':'white',
                           'size':25},
                      # legend_y=0.5,
                      legend={'y':0.5,
                              'x':0.8,
                              'font':dict(size=20,color='white')
                          },
                      hoverlabel=dict(
                              font_size=20),
                      # xaxis_title="Month",
                      )
    fig.update_yaxes(ticksuffix = "  ")
    fig.update_xaxes(ticksuffix = "  ")    
    
    return fig



@app.callback(Output('var_accident_happen_bar_chart','figure'),
              [Input('radio_items','value')],
              [Input('w_breakdown','value')],                              
              [Input('w_var_type','value')],             
              [Input('w_data_type','value')])

def updated_graph(radio_items,w_breakdown,w_var_type,w_data_type):
    radio_items=int(radio_items)
    df_bys=df.groupby(['LOSSYEAR','STATES',w_var_type,'ACCIDENT_OCCUR_GROUP'])[['PAIDLS','BALOS','INCTOT','INCCNT']].sum().reset_index()
    selection=df_bys[(df_bys['LOSSYEAR']==radio_items)&(df_bys[w_var_type]==w_breakdown)][['STATES',w_data_type,'ACCIDENT_OCCUR_GROUP']]      

    fig = go.Figure(data=[
        go.Bar(name='<1 month', x=selection[(selection['ACCIDENT_OCCUR_GROUP']=='<1 month')]['STATES'], y=selection[(selection['ACCIDENT_OCCUR_GROUP']=='<1 month')][w_data_type],marker_color='mediumvioletred',
               hovertemplate = '<1 month <br>%{x} <br>%{y:,.0f}<extra></extra>'),           
        go.Bar(name='1-3 months', x=selection[(selection['ACCIDENT_OCCUR_GROUP']=='1-3 months')]['STATES'], y=selection[(selection['ACCIDENT_OCCUR_GROUP']=='1-3 months')][w_data_type],marker_color='palevioletred',
               hovertemplate = '1-3 months <br>%{x} <br>%{y:,.0f}<extra></extra>'),        
        go.Bar(name='3-6 months', x=selection[(selection['ACCIDENT_OCCUR_GROUP']=='3-6 months')]['STATES'], y=selection[(selection['ACCIDENT_OCCUR_GROUP']=='3-6 months')][w_data_type],marker_color='lightpink',
               hovertemplate = '3-6 months <br>%{x} <br>%{y:,.0f}<extra></extra>'),        
        go.Bar(name='6-9 months', x=selection[(selection['ACCIDENT_OCCUR_GROUP']=='6-9 months')]['STATES'], y=selection[(selection['ACCIDENT_OCCUR_GROUP']=='6-9 months')][w_data_type],marker_color='mistyrose',
               hovertemplate = '6-9 months <br>%{x} <br>%{y:,.0f}<extra></extra>'),        
        go.Bar(name='9-12 months', x=selection[(selection['ACCIDENT_OCCUR_GROUP']=='9-12 months')]['STATES'], y=selection[(selection['ACCIDENT_OCCUR_GROUP']=='9-12 months')][w_data_type],marker_color='peachpuff',
               hovertemplate = '9-12 months <br>%{x} <br>%{y:,.0f}<extra></extra>'),        
        go.Bar(name='>12 months', x=selection[(selection['ACCIDENT_OCCUR_GROUP']=='>12 months')]['STATES'], y=selection[(selection['ACCIDENT_OCCUR_GROUP']=='>12 months')][w_data_type],marker_color='darksalmon',
               hovertemplate = '>12 months <br>%{x} <br>%{y:,.0f}<extra></extra>'),          
        ])            
        
    fig.update_layout(height=550,
                      barmode='stack',
                      paper_bgcolor='#1f2c56',
                      font_color="white",
                      margin = dict(t=80, l=1, r=1, b=1),
                      showlegend=False,
                      font=dict(size=18,
                                color='white'),                      
                      title={
                          'text':'Gap Between Policy Inception Date and Loss Date by States (' + str(radio_items) + ')',
                          'y':0.99,
                          'x':0.5,
                          'xanchor':'center',
                          'yanchor':'top'},
                      titlefont={
                          'color':'white',
                          'size':25},
                      hoverlabel=dict(
                              font_size=20),
                      )
    fig.update_yaxes(ticksuffix = "  ")
    fig.update_xaxes(ticksuffix = "  ")
        
    return fig



@app.callback(Output('var_CY_pie_chart','figure'),
              [Input('radio_items','value')],
              [Input('w_breakdown','value')],                              
              [Input('w_var_type','value')],                
              [Input('w_data_type','value')])

def updated_graph(radio_items,w_breakdown,w_var_type,w_data_type):
    radio_items=int(radio_items)
    if w_data_type=='PAIDLS': w_data_type_desc='Total Claims Paid'      
    if w_data_type=='BALOS': w_data_type_desc='Total Claims Outstanding'      
    if w_data_type=='INCTOT': w_data_type_desc='Total Claims Incurred'      
    if w_data_type=='INCCNT': w_data_type_desc='Total Claims Count'    
    
    df_bys=df.groupby(['LOSSYEAR',w_var_type,'CONSTNYR_GROUP'])[w_data_type].sum().reset_index()
    selection=df_bys[(df_bys['LOSSYEAR']==radio_items)&(df_bys[w_var_type]==w_breakdown)] 
    selection['CONSTNYR_GROUP'] = pd.Categorical(selection['CONSTNYR_GROUP'], 
                                    ['Before 1990','1990-1999',
                                     '2000-2004','2005-2009','2010-2014','2015-2019',
                                     '2020','Error'
                                    ],ordered=True)
    selection.sort_values('CONSTNYR_GROUP')
    selection=selection.sort_values(by=['CONSTNYR_GROUP'])

    # selection['colors'] = np.where(selection['CONSTNYR_GROUP']!= 'Residential', 'limegreen', 'palegreen')
      
    fig=go.Figure()
    fig=go.Figure(data=[go.Pie(labels=selection['CONSTNYR_GROUP'],
               values=selection[w_data_type],
               hoverinfo='label+value+percent',
               # textinfo='value+percent',
               textfont=dict(size=18),
               hole=0.3,
               sort=False,
               marker=dict(colors=px.colors.sequential.Tealgrn_r)
               # marker=dict(colors=colors),
               )])
    
    fig.update_layout(height=550,
                      showlegend=True,
                      plot_bgcolor='#1f2c56',
                      paper_bgcolor='#1f2c56',
                      hovermode='closest',
                      autosize=True,
                      margin = dict(t=100, l=0, r=0, b=20),
                      title={
                          'text':'{} by Construction Year ('.format(w_data_type_desc) + str(radio_items) + ')',
                          'y':0.99,
                          'x':0.5,
                          'xanchor':'center',
                          'yanchor':'top'},
                      titlefont={
                          'color':'white',
                          'size':25},
                      font=dict(
                          # family='sans-serif',
                          size=18,
                          color='white'),
                      legend={
                          'y':0.5,
                          'x':0.8,
                          'font':dict(size = 20, color = "white")
                          },
                      hoverlabel=dict(
                          font_size=20)
                      )
    fig.update_yaxes(ticksuffix = "  ")
    fig.update_xaxes(ticksuffix = "  ")       
        
    return fig

                         

@app.callback(Output('var_CY_bar_chart','figure'),
              [Input('radio_items','value')],
              [Input('w_breakdown','value')],                              
              [Input('w_var_type','value')],               
              [Input('w_data_type','value')])

def updated_graph(radio_items,w_breakdown,w_var_type,w_data_type):
    radio_items=int(radio_items)
    if w_data_type=='PAIDLS': w_data_type_desc='Total Claims Paid'      
    if w_data_type=='BALOS': w_data_type_desc='Total Claims Outstanding'      
    if w_data_type=='INCTOT': w_data_type_desc='Total Claims Incurred'      
    if w_data_type=='INCCNT': w_data_type_desc='Total Claims Count'    
    
    df_bys=df.groupby(['LOSSYEAR','STATES',w_var_type,'CONSTNYR_GROUP'])[w_data_type].sum().reset_index()
    selection=df_bys[(df_bys['LOSSYEAR']==radio_items)&(df_bys[w_var_type]==w_breakdown)]   
        
    fig = go.Figure()  
    fig = go.Figure(data=[
        go.Bar(name='Before 1990', x=selection[(selection['CONSTNYR_GROUP']=='Before 1990')]['STATES'], y=selection[(selection['CONSTNYR_GROUP']=='Before 1990')][w_data_type],marker_color=px.colors.sequential.Tealgrn[6],
               hovertemplate = 'Before 1990 <br>%{x} <br>%{y:,.0f}<extra></extra>'),        
        # go.Bar(name='1980-1989', x=selection[(selection['CONSTNYR_GROUP']=='1980-1989')]['STATES'], y=selection[(selection['CONSTNYR_GROUP']=='1980-1989')][w_data_type],marker_color=px.colors.sequential.haline[1],
        #        hovertemplate = '1980-1989 <br>%{x} <br>%{y:,.0f}<extra></extra>'),
        go.Bar(name='1990-1999', x=selection[(selection['CONSTNYR_GROUP']=='1990-1999')]['STATES'], y=selection[(selection['CONSTNYR_GROUP']=='1990-1999')][w_data_type],marker_color=px.colors.sequential.Tealgrn[5],
               hovertemplate = '1990-1999 <br>%{x} <br>%{y:,.0f}<extra></extra>'),
        # go.Bar(name='1995-1999', x=selection[(selection['CONSTNYR_GROUP']=='1995-1999')]['STATES'], y=selection[(selection['CONSTNYR_GROUP']=='1995-1999')][w_data_type],marker_color=px.colors.sequential.haline[3],
        #        hovertemplate = '1995-1999 <br>%{x} <br>%{y:,.0f}<extra></extra>'),
        go.Bar(name='2000-2004', x=selection[(selection['CONSTNYR_GROUP']=='2000-2004')]['STATES'], y=selection[(selection['CONSTNYR_GROUP']=='2000-2004')][w_data_type],marker_color=px.colors.sequential.Tealgrn[4],
               hovertemplate = '2000-2004 <br>%{x} <br>%{y:,.0f}<extra></extra>'),
        go.Bar(name='2005-2009', x=selection[(selection['CONSTNYR_GROUP']=='2005-2009')]['STATES'], y=selection[(selection['CONSTNYR_GROUP']=='2005-2009')][w_data_type],marker_color=px.colors.sequential.Tealgrn[3],
               hovertemplate = '2005-2009 <br>%{x} <br>%{y:,.0f}<extra></extra>'),
        go.Bar(name='2010-2014', x=selection[(selection['CONSTNYR_GROUP']=='2010-2014')]['STATES'], y=selection[(selection['CONSTNYR_GROUP']=='2010-2014')][w_data_type],marker_color=px.colors.sequential.Tealgrn[2],
               hovertemplate = '2010-2014 <br>%{x} <br>%{y:,.0f}<extra></extra>'),
        go.Bar(name='2015-2019', x=selection[(selection['CONSTNYR_GROUP']=='2015-2019')]['STATES'], y=selection[(selection['CONSTNYR_GROUP']=='2015-2019')][w_data_type],marker_color=px.colors.sequential.Tealgrn[1],
               hovertemplate = '2015-2019 <br>%{x} <br>%{y:,.0f}<extra></extra>'),
        go.Bar(name='2020-2024', x=selection[(selection['CONSTNYR_GROUP']=='2020')]['STATES'], y=selection[(selection['CONSTNYR_GROUP']=='2020')][w_data_type],marker_color=px.colors.sequential.Tealgrn[0],
               hovertemplate = '2020 <br>%{x} <br>%{y:,.0f}<extra></extra>'),
        go.Bar(name='Error', x=selection[(selection['CONSTNYR_GROUP']=='Error')]['STATES'], y=selection[(selection['CONSTNYR_GROUP']=='Error')][w_data_type],marker_color='blue',
               hovertemplate = 'Error <br>%{x} <br>%{y:,.0f}<extra></extra>'),
        ])            
        
    fig.update_layout(height=550,
                      barmode='stack',
                      paper_bgcolor='#1f2c56',
                      font_color="white",
                      margin = dict(t=80, l=1, r=1, b=1),
                      showlegend=False,
                      font=dict(size=18,
                                color='white'),                      
                      title={
                          'text':'{} by Construction Year & State ('.format(w_data_type_desc) + str(radio_items) + ')',
                          'y':0.99,
                          'x':0.5,
                          'xanchor':'center',
                          'yanchor':'top'},
                      titlefont={
                          'color':'white',
                          'size':25},
                      hoverlabel=dict(
                              font_size=20),
                      )
    fig.update_yaxes(ticksuffix = "  ")
    fig.update_xaxes(ticksuffix = "  ")
        
    return fig



@app.callback(Output('var_BH_pie_chart','figure'),
              [Input('radio_items','value')],
              [Input('w_breakdown','value')],                              
              [Input('w_var_type','value')],               
              [Input('w_data_type','value')])

def updated_graph(radio_items,w_breakdown,w_var_type,w_data_type):
    radio_items=int(radio_items)
    if w_data_type=='PAIDLS': w_data_type_desc='Total Claims Paid'      
    if w_data_type=='BALOS': w_data_type_desc='Total Claims Outstanding'      
    if w_data_type=='INCTOT': w_data_type_desc='Total Claims Incurred'      
    if w_data_type=='INCCNT': w_data_type_desc='Total Claims Count'    
    
    df_bys=df.groupby(['LOSSYEAR',w_var_type,'BHEIGHT_GROUP'])[w_data_type].sum().reset_index()
    selection=df_bys[(df_bys['LOSSYEAR']==radio_items)&(df_bys[w_var_type]==w_breakdown)] 
    selection['BHEIGHT_GROUP'] = pd.Categorical(selection['BHEIGHT_GROUP'], 
                                    ['One Storey Building','Two Storey Building','Three Storey Building','Three and Above','Error'
                                    ],ordered=True)
    # selection.sort_values('BHEIGHT_GROUP')
    selection=selection.sort_values(by=['BHEIGHT_GROUP'])

    # selection['colors'] = np.where(selection['BHEIGHT_GROUP']!= 'Residential', 'limegreen', 'palegreen')
      
    fig=go.Figure()
    fig=go.Figure(data=[go.Pie(labels=selection['BHEIGHT_GROUP'],
               values=selection[w_data_type],
               hoverinfo='label+value+percent',
               # textinfo='value+percent',
               textfont=dict(size=18),
               hole=0.3,
               sort=False,
               marker=dict(colors=px.colors.sequential.Oryel)
               # marker=dict(colors=colors),
               )])
    
    fig.update_layout(height=550,
                      showlegend=True,
                      plot_bgcolor='#1f2c56',
                      paper_bgcolor='#1f2c56',
                      hovermode='closest',
                      autosize=True,
                      margin = dict(t=100, l=0, r=0, b=20),
                      title={
                          'text':' {} by Building Height ('.format(w_data_type_desc) + str(radio_items) + ')',
                          'y':0.99,
                          'x':0.5,
                          'xanchor':'center',
                          'yanchor':'top'},
                      titlefont={
                          'color':'white',
                          'size':25},
                      font=dict(
                          # family='sans-serif',
                          size=18,
                          color='white'),
                      legend={
                          'y':0.5,
                          'x':0.8,
                          'font':dict(size = 20, color = "white")
                          },
                      hoverlabel=dict(
                          font_size=20)
                      )
    fig.update_yaxes(ticksuffix = "  ")
    fig.update_xaxes(ticksuffix = "  ")       
        
    return fig



@app.callback(Output('var_BH_bar_chart','figure'),
              [Input('radio_items','value')],
              [Input('w_breakdown','value')],                              
              [Input('w_var_type','value')],              
              [Input('w_data_type','value')])

def updated_graph(radio_items,w_breakdown,w_var_type,w_data_type):
    radio_items=int(radio_items)
    if w_data_type=='PAIDLS': w_data_type_desc='Total Claims Paid'      
    if w_data_type=='BALOS': w_data_type_desc='Total Claims Outstanding'      
    if w_data_type=='INCTOT': w_data_type_desc='Total Claims Incurred'      
    if w_data_type=='INCCNT': w_data_type_desc='Total Claims Count'    
    
    df_bys=df.groupby(['LOSSYEAR','STATES',w_var_type,'BHEIGHT_GROUP'])[w_data_type].sum().reset_index()
    selection=df_bys[(df_bys['LOSSYEAR']==radio_items)&(df_bys[w_var_type]==w_breakdown)]   
        
    fig = go.Figure()  
    fig = go.Figure(data=[
        go.Bar(name='One Storey Building', x=selection[(selection['BHEIGHT_GROUP']=='One Storey Building')]['STATES'], y=selection[(selection['BHEIGHT_GROUP']=='One Storey Building')][w_data_type],marker_color=px.colors.sequential.Oryel[4],
               hovertemplate = 'One Storey Building <br>%{x} <br>%{y:,.0f}<extra></extra>'),        
        go.Bar(name='Two Storey Building', x=selection[(selection['BHEIGHT_GROUP']=='Two Storey Building')]['STATES'], y=selection[(selection['BHEIGHT_GROUP']=='Two Storey Building')][w_data_type],marker_color=px.colors.sequential.Oryel[3],
               hovertemplate = 'Two Storey Building <br>%{x} <br>%{y:,.0f}<extra></extra>'),
        go.Bar(name='Three Storey Building', x=selection[(selection['BHEIGHT_GROUP']=='Three Storey Building')]['STATES'], y=selection[(selection['BHEIGHT_GROUP']=='Three Storey Building')][w_data_type],marker_color=px.colors.sequential.Oryel[2],
               hovertemplate = 'Three Storey Building <br>%{x} <br>%{y:,.0f}<extra></extra>'),
        go.Bar(name='Three and Above', x=selection[(selection['BHEIGHT_GROUP']=='Three and Above')]['STATES'], y=selection[(selection['BHEIGHT_GROUP']=='Three and Above')][w_data_type],marker_color=px.colors.sequential.Oryel[1],
               hovertemplate = 'Three and Above <br>%{x} <br>%{y:,.0f}<extra></extra>'),
        go.Bar(name='Error', x=selection[(selection['BHEIGHT_GROUP']=='Error')]['STATES'], y=selection[(selection['BHEIGHT_GROUP']=='Error')][w_data_type],marker_color=px.colors.sequential.Oryel[0],
               hovertemplate = 'Error <br>%{x} <br>%{y:,.0f}<extra></extra>'),
        ])            
        
    fig.update_layout(height=550,
                      barmode='stack',
                      paper_bgcolor='#1f2c56',
                      font_color="white",
                      margin = dict(t=80, l=1, r=1, b=1),
                      showlegend=False,
                      font=dict(size=18,
                                color='white'),                      
                      title={
                          'text':'{} by Construction Year & State ('.format(w_data_type_desc) + str(radio_items) + ')',
                          'y':0.99,
                          'x':0.5,
                          'xanchor':'center',
                          'yanchor':'top'},
                      titlefont={
                          'color':'white',
                          'size':25},
                      hoverlabel=dict(
                              font_size=20),
                      )
    fig.update_yaxes(ticksuffix = "  ")
    fig.update_xaxes(ticksuffix = "  ")
        
    return fig



#########################################################################################################
   

@app.callback(Output('map','figure'),
              [Input('map_type','value')],
              # [Input('radio_items','value')],
              [Input('w_data_type','value')])
    
def display_choropleth(map_type,w_data_type):
    # radio_items=int(radio_items)     
    w_data_type=str(w_data_type)
    x=latest_year-5
    df_bys=df_map.groupby(['LOSSYEAR','STATES'])[w_data_type].sum().reset_index()  
    selection=df_bys[df_bys['LOSSYEAR']>x] 
    selection=selection.sort_values(by=['LOSSYEAR'])    
    selection= selection.reset_index(drop=True)
    selection['VALUE']=selection[w_data_type].map('{:,.0f}'.format)

    if map_type == 'choropleth':
        # selection2=df_map.groupby(['LOSSYEAR','LAT','LOT','DISTRICT'])[w_data_type].sum().reset_index()     
        # # selection2=selection2[selection2['LOSSYEAR']==radio_items][[w_data_type,'LAT','LOT','DISTRICT']]
        # selection2['VALUE']=selection2[w_data_type].map('{:,.0f}'.format)
        
        
        fig = px.choropleth_mapbox(selection, 
                            geojson=geojson, 
                            locations=selection['STATES'], 
                            featureidkey='properties.state',
                            color=w_data_type,
                            color_continuous_scale="YlOrRd",
                            range_color=(min(selection[w_data_type]), max(selection[w_data_type])),
                            animation_frame=selection['LOSSYEAR'],
                            opacity=0.5,
                            )
    
        
        fig.update_layout(mapbox_style="open-street-map", 
                          mapbox_zoom=5.8, mapbox_center = {"lat": 4.5693754, "lon": 109.3})
        fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0},
                          paper_bgcolor='#1f2c56',
                          title='STATE',
                          font_color="white",
                          font_size=18,
                          hoverlabel=dict(font_size=20),
                          )
        
        # fig.add_trace(px.scatter_mapbox(selection2,
        #     lat = selection2['LAT'],
        #     lon = selection2['LOT'],
        #     color=selection2['DISTRICT'],
        #     # mode = 'markers',
        #     # text = selection2[['DISTRICT','VALUE']],
        #     # below='',  
        #     # hoverinfo='text',       
        #     # marker=go.scattermapbox.Marker(symbol ='circle', size=8, color='black'),
        #     animation_frame=selection2['LOSSYEAR'],
        #     # hoverlabel=dict(font=dict(family='sans-serif', size=18))        
        #     ))
        
        fig.show()
        return fig
            

    elif map_type == 'bubble':
        def longitude(selection):
            if selection['STATES']== 'Johor':
                return 103.7414
            elif selection['STATES'] == 'Kedah':
                return 100.3685
            elif selection['STATES'] == 'Kelantan':
                return 102.2381
            elif selection['STATES'] == 'Melaka':
                return 102.2501    
            elif selection['STATES'] == 'Negeri Sembilan':
                return 101.9424    
            elif selection['STATES'] == 'Pahang':
                return 103.3256     
            elif selection['STATES'] == 'Perak':
                return 101.0901    
            elif selection['STATES'] == 'Perlis':
                return 100.2048    
            elif selection['STATES'] == 'Pulau Pinang':
                return 100.3327    
            elif selection['STATES'] == 'Sabah':
                return 116.0753    
            elif selection['STATES'] == 'Sarawak':
                return 110.3592    
            elif selection['STATES'] == 'Selangor':
                return 101.5183    
            elif selection['STATES'] == 'Terengganu':
                return 103.1324    
            elif selection['STATES'] == 'WP Kuala Lumpur':
                return 101.6869    
            elif selection['STATES'] == 'WP Labuan':
                return 115.2308    
            elif selection['STATES'] == 'WP Putrajaya':
                return 101.6964    
          
            
        def latitude(selection):
            if selection['STATES']== 'Johor':
                return 1.4927
            elif selection['STATES'] == 'Kedah':
                return 6.1184
            elif selection['STATES'] == 'Kelantan':
                return 6.1254
            elif selection['STATES'] == 'Melaka':
                return 2.1896    
            elif selection['STATES'] == 'Negeri Sembilan':
                return 2.7258    
            elif selection['STATES'] == 'Pahang':
                return 3.8126    
            elif selection['STATES'] == 'Perak':
                return 4.5921    
            elif selection['STATES'] == 'Perlis':
                return 6.4449    
            elif selection['STATES'] == 'Pulau Pinang':
                return 5.4164    
            elif selection['STATES'] == 'Sabah':
                return 5.9788    
            elif selection['STATES'] == 'Sarawak':
                return 1.5533    
            elif selection['STATES'] == 'Selangor':
                return 3.0738    
            elif selection['STATES'] == 'Terengganu':
                return 5.3117    
            elif selection['STATES'] == 'WP Kuala Lumpur':
                return 3.1390    
            elif selection['STATES'] == 'WP Labuan':
                return 5.2831    
            elif selection['STATES'] == 'WP Putrajaya':
                return 2.9264      
        
        selection['LONGITUDE']=selection.apply(longitude, axis=1)
        selection['LATITUDE']=selection.apply(latitude, axis=1)

        fig=go.Figure()
        fig = px.scatter_mapbox(
            selection, 
            lat=selection['LATITUDE'], 
            lon=selection['LONGITUDE'],     
            color=selection['STATES'], 
            size=selection[w_data_type],
            color_discrete_sequence=px.colors.cyclical.Phase,
            size_max=60,
            hover_name=selection['STATES'],
            hover_data={'STATES':False,
                        'LATITUDE':False, 
                        'LONGITUDE':False,                         
                         w_data_type:':,.0f'},
            opacity =0.8,
            animation_frame=selection['LOSSYEAR'],
            )
        
        fig.update_layout(
            hoverlabel=dict(
                font_size=18,
                )
            )        
        
        fig.update_layout(mapbox_style="open-street-map", 
                          mapbox_zoom=5.8, mapbox_center = {"lat": 4.5693754, "lon": 109.3})
        fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0},
                          paper_bgcolor='#1f2c56',
                          title='STATE',
                          font_color="white",
                          font_size=18,
                          hoverlabel=dict(font_size=20),
                          legend_y=0.5
                          )        
        fig.show()
        return fig

       
#########################################################################################################
  
@app.callback(Output('line_chart', 'figure'),
              [Input('w_data_type','value')],
              [Input('w_state','value')]
              )

def update_graph(w_data_type,w_state):
    
    if w_data_type=='PAIDLS': w_data_type_desc='Total Claims Paid'      
    if w_data_type=='BALOS': w_data_type_desc='Total Claims Outstanding'      
    if w_data_type=='INCTOT': w_data_type_desc='Total Claims Incurred'      
    if w_data_type=='INCCNT': w_data_type_desc='Total Claims Count'
    
    if w_state=='Malaysia':
        df_bys=df.groupby(['LOSSDATE'])[w_data_type].sum().reset_index()
        selection=df_bys.sort_values(by=['LOSSDATE'])
        # selection.set_index('LOSSDATE',inplace=True)
        selection['LOSSDATE'] = selection['LOSSDATE'].apply(lambda x: str(x))
        
    else:
        df_bys=df.groupby(['LOSSDATE','STATES'])[w_data_type].sum().reset_index()
        selection=df_bys[(df_bys['STATES']==w_state)]   
        selection=selection.sort_values(by=['LOSSDATE'])
        # selection.set_index('LOSSDATE',inplace=True)
        selection['LOSSDATE'] = selection['LOSSDATE'].apply(lambda x: str(x))

    fig=go.Figure()
    fig.add_trace(go.Scatter(x=selection['LOSSDATE'], y=selection[w_data_type]))
    
    minimum=min(selection[w_data_type])
    maximum=max(selection[w_data_type])
    
    fig.update_layout(
                      paper_bgcolor='#1f2c56',
                      font_color="white",
                      # margin = dict(t=80, l=1, r=1, b=1),
                      font=dict(size=18,
                                color='white'),                      
                      title={
                           # 'text':'{}: {}'.format(w_data_type_desc,w_state),
                          'y':0.99,
                          'x':0.5,
                          'xanchor':'center',
                          'yanchor':'top'},
                      titlefont={
                          'color':'white',
                          'size':25},
                      hoverlabel=dict(
                              font_size=20),
                      xaxis_title=None,
                      yaxis_title=None,
                      yaxis = dict(range = [minimum,maximum+((maximum-minimum)/5)]),
                      
                       xaxis=dict(                           
                             rangeselector=dict(
                                 buttons=list([
                                     dict(count=1,
                                          label="  1m  ",
                                          step="month",
                                          stepmode="backward"),
                                     dict(count=6,
                                          label="  6m  ",
                                          step="month",
                                          stepmode="backward"),
                                     dict(count=1,
                                          label="  YTD  ",
                                          step="year",
                                          stepmode="todate"),
                                     dict(count=1,
                                          label="  1y  ",
                                          step="year",
                                          stepmode="backward"),
                                     dict(label="  all  ",
                                          step="all")
                                     ]),
                                 ),
                             rangeslider=dict(visible=True),
                             rangeselector_font=dict(color='black')
                             )                               
                       )
                      
    fig.update_yaxes(ticksuffix = "  ")
    fig.update_xaxes(ticksuffix = "  ")    
    fig.update_xaxes(rangeslider_thickness = 0.1)

    fig.update_traces(
        hovertemplate='%{x}<br>%{y:,.0f}<extra></extra>',
        # line_color='#1f2c56'
        )    
    
    return fig

            
if __name__ == '__main__' :
    app.run_server(debug=True,use_reloader=False)
                                
        
