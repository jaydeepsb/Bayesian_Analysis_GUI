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

dash.register_page(__name__, path='/bayes',  name='Bayes', title='Bayes')

#=================================================
btn_ex = dbc.Button(children=["Button 1"], color="primary", className="mb-3")
#dbc.Button("row 1 col 1",style={"width":"100%"})
fig_ex = dcc.Graph(figure={}, style={"width":"100%"})

#=================================================
#====================================================================
#-------------------  LAYOUT ----------------------------------------
#====================================================================

v1 = np.random.randint(90,110,30)
v2 = np.random.randint(100,120,30)

#====================================================================


# mean1_slider, std1_slider, length_n1
mean1_slider = dcc.Slider(0, 100, 1, id="mean1_slider", value=40, marks=None, tooltip={"placement": "bottom", "always_visible": True})
std1_slider = dcc.Slider(0, 30, 1, id="std1_slider", value=15, marks=None, tooltip={"placement": "bottom", "always_visible": True})
length_n1 = dcc.Slider(3, 10000, 1, id="length_n1", value=30, marks=None, tooltip={"placement": "bottom", "always_visible": True})
    #dbc.Input(id="length_n1", value=30, type="number", min=3, max=10000, step=1, style={'width':'20%'})

mean2_slider = dcc.Slider(0, 100, 1, id="mean2_slider", value=60, marks=None, tooltip={"placement": "bottom", "always_visible": True})
std2_slider = dcc.Slider(1, 30, 1, id="std2_slider", value=15, marks=None, tooltip={"placement": "bottom", "always_visible": True})
length_n2 = dcc.Slider(3, 10000, 1, id="length_n2", value=30, marks=None, tooltip={"placement": "bottom", "always_visible": True})
    #dbc.Input(id="length_n2", value=30, type="number", min=3, max=10000, step=1, style={'width':'20%'})
n1_same_as_n2_check_box = dcc.Checklist(id="set_n1_eq_n2_check", options=[{'label': ' Same lengths', 'value': True}], value=[True], inline=True)

hist_fig_input_data = dbc.Container([dcc.Graph(id="hist_fig_input_data", figure=get_random_fig(), style={"height": 380, "width": 460})])

#random_n_input = dbc.Input(id="random_n_input", value=30, type="number", min=3, max=10000, step=1, style={'width':'20%'})

input_data_1 = dbc.Container(
    [dbc.Label(html.H5("Group 1 data:")),
        dbc.Textarea(id="input_data_1",
                value=v1,
                className="mb-3",
                style = {
                        "width": "100%",
                        "height": "100px",
                        "lineHeight": "22px",
                        "borderWidth": "2px",
                        "borderStyle": "dashed",
                        "borderRadius": "5px",
                        #"textAlign": "left",
                        #"margin": "10px",
                        "overflow": "scroll",
                },
    ),
])

input_data_2 = dbc.Container(
    [dbc.Label(html.H5("Group 2 data:")),
        dbc.Textarea(id="input_data_2",
                value=v2,
                className="mb-3",
                style = {
                        "width": "100%",
                        "height": "100px",
                        "lineHeight": "22px",
                        "borderWidth": "2px",
                        "borderStyle": "dashed",
                        "borderRadius": "5px",
                        #"textAlign": "left",
                        #"margin": "10px",
                        "overflow": "scroll",
                },
    ),
])

calculate_btn = dbc.Spinner(dbc.Button(id="calculate_btn", children="Calculate", color="info", className="me-1", style={'width':'100%'}),
                            color='info',)
progress_bar = dbc.Progress(id="progress_bar", value=0, label="0 %" , style={'margin':'10px'})
interval_block = dcc.Interval(id="interval_block", n_intervals=0, interval=10000, disabled=False, max_intervals=-1)

output_msg = dbc.Container(
    [dbc.Textarea(id="output_msg",
                value="No running process.",
                className="mb-3",
                style = {
                        "width": "100%",
                        "height": "200px",
                        "lineHeight": "22px",
                        "borderWidth": "2px",
                        "borderStyle": "solid",
                        "borderRadius": "5px",
                        #"textAlign": "left",
                        #"margin": "10px",
                        "overflow": "scroll",
                },
    ),
])

process_info_btn = dbc.Button(
            "Process info",
            id="collapse_button",
            #className="mb-3",
            color="primary",
            n_clicks=0, style={'margin-top':'5px'}
        )
#n1_same_as_n2_check_box
p_value = calc_p_value(v1, v2)
p_val_msg = html.Span("T-test p-value = "+str(p_value), style={"color": "gray"})
p_value_box = dbc.Spinner([html.Div(id="p_value_box", children=[p_val_msg],) ], color='info')


group_1 = dbc.Card([dbc.CardBody([
    dbc.Col([
        dbc.Row([
            # dbc.Col([dbc.Row([dbc.Label("Mean 1:"), mean1_slider, dbc.Label("Std 1:"), std1_slider, dbc.Label("Samples (n):"), ]), input_data_1], width=6),
            # dbc.Col([dbc.Row([dbc.Label("Mean 2:"), mean1_slider, dbc.Label("Std 2:"), std1_slider, dbc.Label("Samples (n):"), ]), input_data_2], width=6),
            dbc.Row([dbc.Label("Generate random data", style={"textAlign": "left", 'color':'indigo', 'font-size': '24px'})]),
            dbc.Row([dbc.Col([dbc.Label("Mean:")], width=2), dbc.Col([mean1_slider], width=5), dbc.Col([mean2_slider], width=5)]),
            dbc.Row([dbc.Col([dbc.Label("Std:")], width=2), dbc.Col([std1_slider], width=5), dbc.Col([std2_slider], width=5)]),
            dbc.Row([dbc.Col([dbc.Label("samples (n):"), n1_same_as_n2_check_box], width=2), dbc.Col([length_n1], width=5), dbc.Col([length_n2], width=5)]),
            html.Hr(),
            dbc.Row([dbc.Label("Or provide input data", style={"textAlign": "left", 'color':'indigo', 'font-size': '24px'})]),
            dbc.Row([dbc.Col([dbc.Label("Input Data:")], width=2), dbc.Col([input_data_1], width=5), dbc.Col([input_data_2], width=5)]),
            dbc.Row([dbc.Col([p_value_box], width=2)]),
        ]),
    ], width=12)
])])

input_data_df = get_tabled_df()

input_data_table = dbc.Container(id="input_data_table", children=[input_data_df], style={"maxHeight": "400px", "overflow": "scroll"})

input_data_fig_container = dbc.Container([
    dbc.Col([
                dbc.Row([
                    dbc.Col([input_data_table], width=4),
                    dbc.Col([hist_fig_input_data], width=8),
                ])
], width={'size':8, 'offset':2})
], style={'margin':'10px'})

process_block_box = html.Div(
    [dbc.Container([
        dbc.Col([calculate_btn], width=12),
        dbc.Col([
            dbc.Row([
                        dbc.Col([process_info_btn], width=3),
                        dbc.Col([progress_bar, interval_block], width=9),
                    ]),
                ], width=12),
        ], style={'margin':'10px'}),
        dbc.Collapse(
            dbc.Card(dbc.CardBody([output_msg])),
            id="collapse_msg_box",
            is_open=False,
        ),
    ]
)

# main_content = dbc.Col([
#                     dbc.Container([
#                         calculate_btn,
#                         collapse_box,
#                     ])
# ], width=12)

fig_ex = dbc.Spinner(dcc.Graph(figure=get_random_fig(), style={"width":"100%"}))

figure_panel = dbc.Col([
                        #dcc.Graph(id="fig1", figure=get_random_fig(), style={"width":"100%"})
                        dbc.Row([
                            dbc.Col([dcc.Graph(id="fig1", figure=get_random_fig(), style={"width":"100%"})], width=4),
                            dbc.Col([dcc.Graph(id="fig2", figure=get_random_fig(), style={"width":"100%"})], width=4),
                            dbc.Col([dcc.Graph(id="fig3", figure=get_random_fig(), style={"width":"100%"})], width=4),
                        ]),
                        # dbc.Row([
                        #     dbc.Col([dcc.Graph(figure=get_random_fig(), style={"width":"100%"})], width=4),
                        #     dbc.Col([dcc.Graph(figure=get_random_fig(), style={"width":"100%"})], width=4),
                        #     dbc.Col([dcc.Graph(figure=get_random_fig(), style={"width":"100%"})], width=4),
                        # ]),
], width=12)

output_table = get_random_df(n=0)
bayes_results_table = dbc.Col([
                dbc.Container(id="bayes_results_table", children=[output_table], style={"maxHeight": "400px", "overflow": "scroll"})
], width=12, align='center')


# Main content from pages
layout = dbc.Container([
        html.Div(
            className="row",
            #style={'margin': '10px'},
            children=[ dbc.Row([html.H4("Bayesian Parameter Estimation", style={"textAlign": "center", 'color':'indigo'})]),
                group_1,
                input_data_fig_container,
                process_block_box,
                figure_panel,
                bayes_results_table
                # html.Br(),
                # html.Hr(),
            ]
        )
    ])

