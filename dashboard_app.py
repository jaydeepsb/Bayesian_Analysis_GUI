#=== to kill previously running ports
# to list: sudo lsof -iTCP:8050 -sTCP:LISTEN
# to kill: kill -9 $(lsof -t -i:"8050")
#==================== for training_insights ===============
import os
import base64
from urllib.parse import quote as urlquote
import contextlib
import sys, io
from scripts.utils import *
from scripts.bayes_calc import *
from scripts.bayes_two_samples import *
#==================== for dashboard ===============

import time
import numpy as np
from datetime import datetime, date
import pandas as pd
from copy import deepcopy
from collections import Counter

import subprocess
import threading

import plotly.express as px
import plotly.graph_objs as go
from plotly.subplots import make_subplots
import seaborn as sns

import dash
from dash import Dash, dcc, html, Input, Output, ctx, State
from dash import dash_table as dt
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate

import logging
#=================================================
app = dash.Dash(__name__, use_pages=True, external_stylesheets=[dbc.themes.SPACELAB, dbc.icons.BOOTSTRAP, "my_theme.css"]) #PULSE, SPACELAB
app.title = 'SillyBayes'
app._favicon = ('icon.png')
UPLOAD_DIRECTORY = "uploads/"

if not os.path.exists(UPLOAD_DIRECTORY):
    os.makedirs(UPLOAD_DIRECTORY)

#app = dash.Dash(external_stylesheets=[dbc.themes.LUX])
#app = dash.Dash(__name__)

#app.layout = html.Div([])
my_text_color_vio = 'blueviolet'

btn_ex = dbc.Button(children=["Button 1"], color="primary", className="mb-3")
#dbc.Button("row 1 col 1",style={"width":"100%"})
fig_ex = dcc.Graph(figure={}, style={"width":"100%"})

#=================================================
#====================================================================
#-------------------  LAYOUT ----------------------------------------
#====================================================================

# Menu Bar
menu_bar = dbc.Navbar([dbc.Container([
                    dbc.NavbarBrand("Stats-Lab", href=dash.page_registry['pages.home_page']['path']),
                    dbc.Nav(id="nav_bar",
                        children=[
                            #dbc.NavItem(dbc.NavLink("Shape Search", href=dash.page_registry['pages.Shape_search']['path'])),
                            dbc.NavItem(dbc.NavLink("Bayesian Estimation", href=dash.page_registry['pages.Bayes']['path'])),
                            dbc.NavItem(dbc.NavLink("About", href=dash.page_registry['pages.about']['path'])),
                        ],
                        className='navbar-nav',
                        navbar=True,
                        pills=True
                        ),
                    ]),
                ],
                color="dark",
                dark=True,
                style={'margin': '10px'},
    )


# Layout
app.layout = html.Div([
    menu_bar,
    dash.page_container,
    html.Div(id='output')
])

def save_file(name, content):
    """Decode and store a file uploaded with Plotly Dash."""
    content_type, content_string = content.split(',')
    data = content_string.encode("utf8")#.split(b";base64,") [0]
    with open(os.path.join(UPLOAD_DIRECTORY, name), "wb") as fp:
        fp.write(base64.decodebytes(data))

def uploaded_files():
    """List the files in the upload directory."""
    files = []
    for filename in os.listdir(UPLOAD_DIRECTORY):
        path = os.path.join(UPLOAD_DIRECTORY, filename)
        if os.path.isfile(path):
            files.append(filename)
    return files

# @app.callback([
#     Output("shapes_results_table", "children"),
#     Output("fig_3D_block", "children")],
#     [Input("search_btn", "n_clicks"),
#      Input("delete_all", "n_clicks")],
#     [State("upload_data", "filename"),
#      State("upload_data", "contents"),
#      State("emd_id_input", "value"),
#      State("select_database", "value")],
# suppress_callback_exceptions=True,
# prevent_initial_call=True
#               )
# def upload_or_delete(search_clicks, del_clicks, uploaded_filename, uploaded_file_content, emd_id, db_types):
#     return_table = dash.no_update
#     return_fig = dash.no_update
#     if (ctx.triggered_id == 'delete_all'):
#         return_table = get_random_shape_search_df(n=0)
#         return_fig = None
#     if (ctx.triggered_id == 'search_btn'):
#         if (uploaded_filename is not None) and (uploaded_file_content is not None):
#             return_table = [get_random_shape_search_df(n=10)]
#             fig = get_random_3D_fig()
#             return_fig = dcc.Graph(figure=fig, style={"width": "100%"})
#         elif (emd_id is not None) and (len(db_types) > 0):
#             return_table = [get_random_shape_search_df(n=10)]
#             fig = get_random_3D_fig()
#             return_fig = dcc.Graph(figure=fig, style={"width":"100%"})
#         time.sleep(3)
#     return return_table, return_fig

# @app.callback(
#     Output("drag_n_drop_msg", "children"),
#      [Input("upload_data", "filename"),
#      Input("upload_data", "contents"),
#      Input("delete_all", "n_clicks"),],
# suppress_callback_exceptions=True,
# prevent_initial_call=True
# )
# def upload_box_msg(uploaded_filename, uploaded_file_content, del_clicks):
#     """Save uploaded files."""
#     default_msg = html.Span(" (Drag and drop or click to upload a new file.)", style={"color": "gray"})
#     if ctx.triggered_id == 'delete_all':
#         filelist = [f for f in os.listdir(UPLOAD_DIRECTORY)]
#         n=len(filelist)
#         if n>0:
#             for f in filelist:
#                 os.remove(os.path.join(UPLOAD_DIRECTORY, f))
#             msg1 = html.Span("Deleted!", style={"color": "red"})
#             return_msg = html.Div([msg1, html.Br(),  default_msg])
#         else:
#             msg1 = html.Span("No files to delete!", style={"color": "red"})
#             return_msg = html.Div([msg1, html.Br(),  default_msg])
#         return return_msg
#     if (uploaded_filename is not None) and (uploaded_file_content is not None):
#         save_file(uploaded_filename, uploaded_file_content)
#         msg1 = html.Span(uploaded_filename, style={"color": "green"})
#         return_msg = html.Div([msg1, html.Br(),  default_msg])
#         return return_msg
#     else:
#         return dash.no_update

@app.callback(
    Output("collapse_msg_box", "is_open"),
    [Input("collapse_button", "n_clicks")],
    [State("collapse_msg_box", "is_open")],
)
def toggle_collapse(n_clicks, is_open):
    if n_clicks:
        return not is_open
    return is_open

@app.callback(
    [Output("fig1", "figure"),
     Output("fig2", "figure"),
     Output("fig3", "figure"),
     Output("bayes_results_table", "children")],
    [Input("calculate_btn", "n_clicks"),
    Input("interval_block", "n_intervals")],
    [State("input_data_1", "value"),
    State("input_data_2", "value")],
prevent_initial_call=True
)
def write_stdout_to_file(n_clicks, n_intervals, data1, data2):
    hdi=0.95
    command = 'python scripts/bayes_two_samples.py'
    if ctx.triggered_id == 'calculate_btn':
        time.sleep(5)
        fname = 'bayes_output/stdout.txt'
        with open(fname, 'w') as output_file:
            with contextlib.redirect_stdout(output_file):
                sys.stdout.flush()
                #add_one_to_number(t=0.1)
                #trace_json, df_summary = get_bayes_param_estimation(data1, data2, hdi=hdi, plotit=False, savefig=False)
                #====
                base_dir = "bayes_output/"
                trace_file = os.path.join(base_dir, "trace.json")
                with open(trace_file) as json_file:
                    trace_json = json.load(json_file)
                #====
                fname = os.path.join(base_dir, "summary_df.csv")
                df = pd.read_csv(fname, index_col=0)
                df.index.name = 'Params'
                df.reset_index(drop=False, inplace=True)
                print(df)
                #df.columns[0] = 'Param'
                output_table = dbc.Table.from_dataframe(df, striped=True, bordered=True, hover=True, id="bayes_results_table",
                                                        color="light",
                                                        style={'width': '100%', 'textAlign': 'center'})
                print("Process complete")
                sys.stdout.flush()
                figs = []
                colors = ['indianred', 'darkkhaki', 'blueviolet']
                for i,param in enumerate(["difference of means", "difference of stds", "effect size"]):
                    figs.append(get_figure_of(trace_json, param=param, color=colors[i], hdi=hdi))
                return figs[0], figs[1], figs[2], output_table
    else:
        return dash.no_update, dash.no_update, dash.no_update, dash.no_update

@app.callback(
    Output("output_msg", "value"),
     Input("interval_block", "n_intervals"),
)
def capture_stdout(n_intervals):
    if n_intervals:
        fname = 'bayes_output/stdout.txt'
        with open(fname, 'r') as f:
            output_msges = f.read()
            return output_msges


# # Define a callback function that updates slider2 based on slider1
@app.callback(Output('length_n2', 'value'),
              [Input('set_n1_eq_n2_check', 'value'),
              Input('length_n1', 'value')])
def set_n1_eq_n2(n1n2_bool, value_n1):
    if n1n2_bool:
        return value_n1
    else:
        return dash.no_update


#mean1_slider, std1_slider, length_n1
@app.callback(
    [Output("input_data_table", "children"),
    Output("hist_fig_input_data", "figure"),
     Output("p_value_box", "children")],
    [Input("input_data_1", "value"),
    Input("input_data_2", "value")],
)
def update_input_table(data1, data2):
    data_dict = {"Group 1": data1, "Group 2": data2}
    # to fill Nan values, incase of uneven lengths of data1, data2
    df = pd.DataFrame(dict([ (k,pd.Series(v)) for k,v in data_dict.items() ]))
    input_data_df = get_tabled_df(df)
    #print(input_data_df)
    #==========
    if (len(data1)>=3) & (len(data2)>=3):
        p_value = calc_p_value(data1, data2)
        p_val_msg = html.Span("T-test p-value = "+str(p_value), style={"color": "gray"})
    else:
        print("hi")
        p_val_msg = None
    #======= figure =============
    v = np.concatenate((data1, data2), axis=None)
    bin_size = (np.max(v) - np.min(v)) / 71.
    fig = ff.create_distplot([data1, data2], group_labels=['Group 1', 'Group 2'], show_rug=False, curve_type='kde',
                             bin_size=bin_size)
    fig.update_layout(legend=dict(
        yanchor="top",
        y=0.99,
        xanchor="left",
        x=0.01
    ), margin=dict(l=10, r=10, t=15, b=15), )
    return input_data_df, fig, p_val_msg

@app.callback(
    [Output("input_data_1", "value"),
     Output("input_data_2", "value"),],
     [Input("mean1_slider", "value"),
      Input("std1_slider", "value"),
      Input("length_n1", "value"),
      Input("mean2_slider", "value"),
      Input("std2_slider", "value"),
      Input("length_n2", "value"),
      ]
)
def generate_random_data(m1, s1, n1, m2, s2, n2):
    v1 = np.random.normal(m1, s1, n1)
    v2 = np.random.normal(m2, s2, n2)
    v1, v2 = np.round(v1,0), np.round(v2,0)
    v = np.concatenate((v1, v2), axis=None)
    #df = pd.DataFrame({'Group 1': v1, 'Group 2': v2})
    # bin_size = (np.max(v) - np.min(v))/71.
    # fig = ff.create_distplot([v1,v2], group_labels=['Group 1', 'Group 2'], show_rug=False, curve_type='kde', bin_size=bin_size)
    # fig.update_layout(legend=dict(
    #     yanchor="top",
    #     y=0.99,
    #     xanchor="left",
    #     x=0.01
    # ), margin=dict(l=10, r=10, t=15, b=15),)
    return v1, v2

if __name__ == "__main__":
    #141.48.22.21
    #app.run_server(debug=False, port=8050, host='0.0.0.0')
    app.run_server(debug=True, port=8050, host='127.0.0.1')