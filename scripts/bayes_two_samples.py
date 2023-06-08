import arviz as az
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pymc3 as pm
import os
import sys
import time
import argparse

import json
import plotly.express as px
import plotly.figure_factory as ff
import plotly.graph_objs as go
import seaborn as sns


scripts_path = os.path.dirname(__file__)
base_dir = os.path.abspath(os.path.join(scripts_path, '..', 'bayes_output'))

#print(f"Running on PyMC3 v{pm.__version__}")

az.style.use("arviz-darkgrid")
rng = np.random.default_rng(seed=42)

group1_data = (101,100,102,104,102,97,105,105,98,101,100,123,105,103,100,95,102,106,
        109,102,82,102,100,102,102,101,102,102,103,103,97,97,103,101,97,104,
        96,103,124,101,101,100,101,101,104,100,101)
group2_data = (99,101,100,101,102,100,97,101,104,101,102,102,100,105,88,101,100,
           104,100,100,100,101,102,103,97,101,101,100,101,99,101,100,100,
           101,100,99,101,100,102,99,100,99)
# fmt: on

def add_one_to_number(t=0.1):
    print('hi')
    n=1
    while n < 100:
        n+=1
        print(n)
        sys.stdout.flush()  # flush output buffer to ensure it is written to the file immediately
        time.sleep(t)

def get_bayes_param_estimation(y1, y2, hdi=0.95, plotit=False, savefig=True):
    if y1 == 'None':
        y1 = group1_data
    else:
        y1 = np.array(y1)
    if y2 == 'None':
        y2 = group2_data
    else:
        y2 = np.array(y2)
    y = pd.DataFrame(
        dict(value=np.r_[y1, y2], group=np.r_[["group1"] * len(y1), ["group2"] * len(y2)])
    )
    μ_m = y.value.mean()
    μ_s = y.value.std() * 2

    with pm.Model() as model:
        group1_mean = pm.Normal("group1_mean", mu=μ_m, sigma=μ_s)
        group2_mean = pm.Normal("group2_mean", mu=μ_m, sigma=μ_s)

    σ_low = 1
    σ_high = 10

    with model:
        group1_std = pm.Uniform("group1_std", lower=σ_low, upper=σ_high)
        group2_std = pm.Uniform("group2_std", lower=σ_low, upper=σ_high)

    with model:
        ν = pm.Exponential("ν_minus_one", 1 / 29.0) + 1

    with model:
        λ1 = group1_std ** -2
        λ2 = group2_std ** -2

        group1 = pm.StudentT("group1", nu=ν, mu=group1_mean, lam=λ1, observed=y1)
        group2 = pm.StudentT("group2", nu=ν, mu=group2_mean, lam=λ2, observed=y2)


    with model:
        diff_of_means = pm.Deterministic("difference of means", group1_mean - group2_mean)
        diff_of_stds = pm.Deterministic("difference of stds", group1_std - group2_std)
        effect_size = pm.Deterministic(
            "effect size", diff_of_means / np.sqrt((group1_std ** 2 + group2_std ** 2) / 2)
        )

    print("sampling....")
    with model:
        trace = pm.sample(2000, return_inferencedata=True)
        print(len(trace))
    # =============
    sys.stdout.flush()  # flush output buffer to ensure it is written to the file immediately
    # ==============
    if plotit:
        az.plot_posterior(
            trace,
            var_names=["difference of means", "difference of stds", "effect size"],
            ref_val=0,
            color="#87ceeb",
        )
        if savefig:
            plt.savefig(os.path.join(base_dir,"test_fig.jpeg"), dpi=450)
    print("#============ Process completed. ===============")
    sys.stdout.flush()
    #az.summary(trace, var_names=["difference of means", "difference of stds", "effect size"])
    #df_summary = az.summary(trace, hdi_prob=hdi, var_names=["difference of means", "difference of stds", "effect size"])#[["mean", "sd", "hdi_5%", "hdi_95%"]]
    df_summary = az.summary(trace, hdi_prob=hdi)
    #print(df_summary)
    trace.to_json(os.path.join(base_dir, "trace.json"))
    df_summary.to_csv(os.path.join(base_dir, "summary_df.csv"))
    return trace, df_summary

def get_figure_of(trace_json, param="effect size", color='indianred', hdi=0.95):
    """
    Options: "difference of means", "difference of stds", "effect size"
    """
    values = sum(trace_json["posterior"][param], [])
    hist_data = [values]
    group_labels = [param.title()] # name of the dataset
    fig1 = ff.create_distplot(hist_data, group_labels, colors=[color], show_rug=False, bin_size=0.05)
    fig2 = ff.create_distplot(hist_data, group_labels, curve_type = 'normal')
    normal_x = fig2.data[1]['x']
    normal_y = fig2.data[1]['y']

    fig1.add_vline(x=np.percentile(values, q=int(100*(1-hdi))), line = dict(color='black',
                                          dash = 'dash',
                                          width = 1))
    fig1.add_vline(x=np.mean(values))

    fig1.add_vline(x=np.percentile(values, q=int(100*hdi)), line = dict(color='black',
                                          dash = 'dash',
                                          width = 1))
    fig1.add_traces(go.Scatter(x=normal_x, y=normal_y, mode = 'lines',
                              line = dict(color='black',
                                          #dash = 'dash'
                                          width = 1),
                              name = 'Normal',
                             ))
    fig1.update_layout(legend=dict(
                                yanchor="top",
                                y=1.01,
                                xanchor="left",
                                x=0.01),
                        margin=dict(l=10, r=10, t=15, b=15),
                        xaxis_title= param.title()
                        )
    return fig1


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--y1', default=group1_data)
    parser.add_argument('--y2', default=group2_data)
    parser.add_argument('--hdi', type=float, default=0.95)
    parser.add_argument('--plotit', type=bool, default=False)
    parser.add_argument('--savefig', type=bool, default=False)
    input_args = parser.parse_args()
    #print(input_args)
    #input_args.y1 = [float(v) for v in input_args.y1.replace('[','').replace(']','').replace(' ','').split(',')]
    #input_args.y2 = [float(v) for v in input_args.y2.replace('[','').replace(']','').replace(' ','').split(',')]
    #print(input_args.y1)
    #============
    #add_one_to_number(t=0.1)
    get_bayes_param_estimation(y1=input_args.y1,
                               y2=input_args.y2,
                               hdi=input_args.hdi,
                               plotit=input_args.plotit,
                               savefig=input_args.savefig)


#====== save or read a trace file ========
#====== save a trace file ========
# trace.to_json(os.path.join(base_dir, "test_trace.json"))
# trace = az.from_json(os.path.join(base_dir, "test_trace.json"))

# df_summary = get_bayes_param_estimation(group1_data, group2_data)
