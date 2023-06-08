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

dash.register_page(__name__, path='/about', name='about', title='About')

#=================================================
btn_ex = dbc.Button(children=["Button 1"], color="primary", className="mb-3")
#dbc.Button("row 1 col 1",style={"width":"100%"})
fig_ex = dcc.Graph(figure={}, style={"width":"100%"})

#=================================================
#====================================================================
#-------------------  LAYOUT ----------------------------------------
#====================================================================

info_block = html.H3("K-Lab offers different statistical and machine learning tools for biochemistry applications.")
web_page_block = html.Iframe(src="https://blogs.urz.uni-halle.de/kastritislab/about/", height="1000px", width="1200px")

layout = dbc.Container([ info_block, web_page_block ])