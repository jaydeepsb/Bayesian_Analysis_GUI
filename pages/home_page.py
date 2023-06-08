#=== to kill previously running ports
# to list: sudo lsof -iTCP:8050 -sTCP:LISTEN
# to kill: kill -9 $(lsof -t -i:"8050")
#==================== for training_insights ===============
import os
import sys
from scripts.utils import *
#==================== for dashboard ===============

import time
import numpy as np
from datetime import datetime, date
import pandas as pd
from copy import deepcopy
from collections import Counter

import plotly.express as px
import plotly.graph_objs as go
import seaborn as sns

import dash
from dash import Dash, dcc, html, Input, Output, ctx, State
from dash import dash_table as dt
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate

import logging

dash.register_page(__name__, path='/', name='Home', title='Home')
#dash.register_page(__name__, path='/', name='Home', title='Home')

#=================================================
btn_ex = dbc.Button(children=["Button 1"], color="info", className="me-1", style={"width":"100%", 'margin':'20px'})
#dbc.Button("row 1 col 1",style={"width":"100%"})
fig_ex = dcc.Graph(figure={}, style={"width":"100%"})

#=================================================
#====================================================================
#-------------------  LAYOUT ----------------------------------------
#====================================================================

title = dbc.Container([ html.H1("Welcome to Stats-Lab",  style={'text-align':'center'}) ])
logo_img_box = dbc.Container([ html.Img(src='assets/icon.png', style={'height':'400px'}),
                               ], style={'text-align':'center', 'margin':'20px'} )

shape_search_btn = dbc.Button(children=[  html.H3("Protein Shape Search",  style={'text-align':'center'}) ],
                            href="/shape_search",
                            color="info", className="me-1",
                            style={"width":"100%", 'margin-top':'20px'})

bayes_calc_btn = dbc.Button(children=[  html.H3("Bayesian Calculator",  style={'text-align':'center'}) ],
                            href="/bayes",
                            color="info", className="me-1",
                            style={"width":"100%", 'margin-top':'20px'})

# Main content from pages
layout = dbc.Container([
        html.Div(
            className="row",
            #style={'margin': '10px'},
            children=[  dbc.Row([title]),
                        dbc.Row([logo_img_box]),
                        dbc.Col([dbc.Row([dbc.Col([shape_search_btn], width=6),
                                          dbc.Col([bayes_calc_btn], width=6)],
                                          )],
                                width=12, ),
                # html.Br(),
                # html.Hr(),
            ]
        )
    ])
