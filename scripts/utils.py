#!/usr/bin/env python

# import json
# import yaml
# import datetime, isodate, calendar
# from datetime import timedelta
# from dateutil.relativedelta import relativedelta

import os
import sys
import numpy as np
import pandas as pd
import dash_bootstrap_components as dbc
from scipy.stats import ttest_ind

import plotly.express as px
import plotly.graph_objs as go
import seaborn as sns

#============================================
scripts_path = os.path.dirname(__file__)
dir_scripts = os.path.abspath(os.path.join(scripts_path, '..'))
dir_app_root = os.path.abspath(os.path.join(dir_scripts, ".."))
assets_path = os.path.abspath(os.path.join(dir_app_root,"assets"))
dir_uploads_path = os.path.abspath(os.path.join(dir_app_root,"uploads"))

if scripts_path not in sys.path:
    sys.path.append(scripts_path)

def get_random_df(n=5):
    if n>0:
        x = np.random.randint(1000,10000,n)
        y = np.random.randint(1000,10000,n)
    else:
        x = []
        y = []
    df = pd.DataFrame(
        {
            "x": x,
            "y": y,
        }
    )
    output_table = get_tabled_df(df)
    return output_table

def get_random_shape_search_df(n=5):
    # search result table
    base_string = "https://www.ebi.ac.uk/emdb/EMD-"
    #==================
    if n>0:
        id_list = np.random.randint(1000,10000,n)
        links_list = [base_string+str(v) for v in id_list]
        ranks = np.arange(1,n+1)
        scores = sorted([ str(v) for v in np.round(np.random.uniform(0,1,n), 2)], reverse=True)
    else:
        id_list = []
        links_list = []
        ranks = []
        scores = []
    #================
    df = pd.DataFrame(
        {
            "ID": id_list,
            "Rank": ranks,
            "Score": scores,
            "Links": links_list,
        }
    )
    output_table = get_tabled_df(df)
    return output_table

def get_tabled_df(df=None):
    if df is None:
        df = pd.DataFrame({"x":[], "y": []})#get_random_df(n=5)
    output_table = dbc.Table.from_dataframe(df, striped=True, bordered=True, hover=True, responsive=True,
                                            id="results_table",
                                            color="light",
                                            style={'width': '100%', 'textAlign': 'center'})
    return output_table

def get_random_fig():
    df = pd.DataFrame({"x": np.random.normal(loc=50, scale=15, size=1000)})
    fig = px.histogram(df, x="x", color_discrete_sequence=['darkblue'], opacity=0.8,)
    fig.update_layout(legend=dict(
        yanchor="top",
        y=1.01,
        xanchor="left",
        x=0.01),
        margin=dict(l=10, r=10, t=15, b=15),
    )
    return fig

def get_random_3D_fig():
    X, Y, Z = np.mgrid[-8:8:40j, -8:8:40j, -8:8:40j]
    values = np.sin(X * Y * Z) / (X * Y * Z)

    fig = go.Figure(data=go.Volume(
        x=X.flatten(),
        y=Y.flatten(),
        z=Z.flatten(),
        value=values.flatten(),
        isomin=0.1,
        isomax=0.8,
        opacity=0.1,  # needs to be small to see through all surfaces
        surface_count=17,  # needs to be a large number for good volume rendering
    ))
    fig.update_layout(margin=dict(l=10, r=10, t=15, b=15) )
    return fig

def calc_p_value(a,b):
    s, p = ttest_ind(a, b)
    return np.round(p,4)

def str2bool(v):
    return v.lower() in ("yes", "true", "t", "1")



# def load_config(filename):
#     """Load configuration from a yaml file"""
#     with open(filename) as f:
#         return yaml.full_load(f)
#
#
# def save_config(config, filename):
#     """Save configuration to a yaml file"""
#     with open(filename, "w+") as f:
#         yaml.safe_dump(config, f, default_flow_style=False)
#
#
# def pretty_print_json(data):
#     print(json.dumps(data, indent=4, sort_keys=True))
#
# def get_default_start_date():
#     today = datetime.datetime.today().date()
#     first_day_of_month = datetime.datetime.today().replace(day=1).date()
#     first_day_of_last_month = today - relativedelta(months=1)
#     if today == first_day_of_month:
#         return first_day_of_last_month.strftime('%Y-%m-%d')
#     else:
#         return first_day_of_month.strftime('%Y-%m-%d')
#
# def get_default_end_date():
#     today = datetime.datetime.today().date()
#     first_day_of_month = datetime.datetime.today().replace(day=1).date()
#     endmonth = calendar.monthrange(today.year, today.month)
#     last_day_of_month = datetime.datetime(today.year, today.month, endmonth[1])
#     return last_day_of_month.strftime('%Y-%m-%d')
#
# def get_default_current_calendar_month_range():
#     first_day_of_month = datetime.datetime.today().replace(day=1).date().strftime('%Y-%m-%d')
#     last_day_of_month = get_default_end_date()
#     return first_day_of_month, last_day_of_month
#
# def trailing_1_week_range():
#     today = datetime.datetime.today().date()
#     same_day_last_week = today - relativedelta(days=7)
#     return same_day_last_week, today
#
# def trailing_1_month_range():
#     today = datetime.datetime.today().date()
#     same_day_last_month = today - relativedelta(months=1)
#     return same_day_last_month, today
#
# def trailing_3_months_range():
#     today = datetime.datetime.today().date()
#     same_day_last_3_month = today - relativedelta(months=3)
#     return same_day_last_3_month, today
#
# def trailing_1_year_range():
#     today = datetime.datetime.today().date()
#     same_day_last_year = today - relativedelta(months=12)
#     return same_day_last_year, today