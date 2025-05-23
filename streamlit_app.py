import streamlit as st
import numpy as np
import plotly.figure_factory as ff
import random

class BusinessCase:
    total_baseline = 130000000
    def __init__(self, retain_payroll_pct, stop_r, less_r, lower_r, stop_o, less_o, lower_o,
                            pmo, load, sol_con, fin_eng, cola_fx, margin, np_pr_ratio, retain_nonpayroll_pct, save_r, save_o):
        self.payroll_baseline = 100000000
        self.retain_payroll_pct = retain_payroll_pct
        self.stop_r = stop_r
        self.less_r = less_r
        self.lower_r = lower_r
        self.stop_o = stop_o
        self.less_o = less_o
        self.lower_o = lower_o
        self.pmo = pmo
        self.load = load
        self.sol_con = sol_con
        self.fin_eng = fin_eng
        self.cola_fx = cola_fx
        self.margin = margin
        self.np_pr_ratio = np_pr_ratio
        self.retain_nonpayroll_pct = retain_nonpayroll_pct
        self.save_r = save_r
        self.save_o = save_o

        self.nonpayroll_baseline = np_pr_ratio * self.payroll_baseline

        self.payroll = calculate_payroll(self)
        self.nonpayroll = calculate_nonpayroll(self)

        self.total_new_cost = self.payroll + self.nonpayroll
        self.total_savings = (self.total_baseline - self.total_new_cost)/ self.total_baseline

def calculate_payroll(bc):
    # Payroll
    retain_payroll = bc.payroll_baseline * bc.retain_payroll_pct
    net_retain = retain_payroll * (1-bc.stop_r)
    net_retain = net_retain * (1-bc.less_r)
    net_retain = net_retain * (1-bc.lower_r)
    retain_saving_pct = (retain_payroll- net_retain)/retain_payroll

    outsource_payroll = bc.payroll_baseline * (1-bc.retain_payroll_pct)
    gross_outsource_unloaded_cost = outsource_payroll * (1-bc.stop_o)
    gross_outsource_unloaded_cost = gross_outsource_unloaded_cost * (1-bc.less_o)
    gross_outsource_unloaded_cost = gross_outsource_unloaded_cost * (1-bc.lower_o)
    gross_outsource_saving_pct = (outsource_payroll - gross_outsource_unloaded_cost)/outsource_payroll

    add_pmo = gross_outsource_unloaded_cost * bc.pmo
    add_load =  (gross_outsource_unloaded_cost + add_pmo) * bc.load
    add_sol_con = (gross_outsource_unloaded_cost + add_pmo + add_load) * bc.sol_con
    add_cola = (gross_outsource_unloaded_cost + add_pmo + add_load + add_sol_con) * bc.cola_fx
    add_fin_eng = (outsource_payroll* bc.fin_eng * 1.25) / 5
    gross_outsource_loaded_cost = gross_outsource_unloaded_cost + add_cola + add_load + add_sol_con + add_fin_eng

    net_outsource = gross_outsource_loaded_cost + (gross_outsource_loaded_cost / (1-bc.margin))-gross_outsource_loaded_cost
    outsource_saving_pc = (outsource_payroll - net_outsource)/outsource_payroll

    total_payroll_savings = bc.payroll_baseline - net_outsource - net_retain
    total_payroll_savings_pct = total_payroll_savings/bc.payroll_baseline

    total_p = bc.payroll_baseline - total_payroll_savings

    return total_p

def calculate_nonpayroll(bc):
    # Non-payroll
    retain_np = bc.retain_nonpayroll_pct * bc.nonpayroll_baseline
    net_retained_np = retain_np * (1-bc.save_r)

    outsource_non_payroll = (1-bc.retain_nonpayroll_pct) * bc.nonpayroll_baseline
    gross_outsource_non_payroll = outsource_non_payroll * (1-bc.save_o)
    add_np_cont = gross_outsource_non_payroll * bc.sol_con
    add_np_load = (gross_outsource_non_payroll + add_np_cont) * bc.load
    add_np_cola = (gross_outsource_non_payroll + add_np_cont + add_np_load) * bc.cola_fx
    new_np_cost = gross_outsource_non_payroll + add_np_cola + add_np_load + add_np_cont
    net_np_outsource_cost = (new_np_cost/(1-bc.margin))

    total_np = net_retained_np + net_np_outsource_cost
    total_savings_np = (bc.nonpayroll_baseline-total_np)
    total_savings_np_pct = total_savings_np/bc.nonpayroll_baseline

    return total_np

# Function to build the plot
def make_figure(data, names, colors):
    means = [np.mean(x) for x in data]
    fig = ff.create_distplot(data, group_labels=names, show_curve=True, show_hist=False, show_rug=False,
                             colors=colors, histnorm="percent")

    for index in range(len(means)):
        fig.add_shape(
            type="line", x0=means[index], x1=means[index], y0=0, y1=1,
            yref="paper", line=dict(color=colors[index], width=2, dash="dash")
        )
        fig.add_annotation(
            x=means[index], y=1.1, yref="paper",
            text=f"{names[index]} Mean: {means[index]:.0%}", showarrow=False,
            font=dict(color=colors[index], size=13)
        )

    fig.update_layout(
        showlegend=False,
        xaxis=dict(title="Net Savings", tickformat=".0%"),
        yaxis=dict(title="Probability"),
        margin=dict(t=40, l=40, r=40, b=40)
    )
    return fig

# --------------------------
# Streamlit App Starts Here
# --------------------------
st.set_page_config(layout="wide", page_title="Business Case Calculator")
st.markdown("""
    <style>
    .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
    }
    .stSlider {
        margin-bottom: -20px;
    }
    [data-testid="stSliderTickBarMin"], [data-testid="stSliderTickBarMax"] {
            font-size: 0px;
    }
    [data-testid="stForm"] {
        padding-bottom: 2rem;
    }
    
    .stSlider > div {
        padding: 0px !important;
    }
    </style>
""", unsafe_allow_html=True)
st.title("Business Case Calculator")
chart_placeholder = st.empty()

# Initialize session state storage for previous submissions
if 'results' not in st.session_state:
    st.session_state.results = []
    st.session_state.names = []
    st.session_state.colors = []

# Unique color palette
color_palette = [
    "#A100FF", "#FF5C00", "#009EFF", "#00C49A", "#FFC107", "#FF0080", "#8BC34A", "#FF4444"
]

# Form
if st.button("Reset Simulations"):
    st.session_state.results = []
    st.session_state.names = []
    st.session_state.colors = []
with st.form("slider_form"):

    # Inject custom CSS with st.markdown()

    submit = st.form_submit_button("Run Simulation")
    run_name = st.text_input(label="run_name")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Payroll Outsourced")
        stop_outsourced_payroll = st.slider("STOP_", 0.0, 1.0, [0.03, 0.07], 0.01)
        less_outsourced_payroll = st.slider("LESS_", 0.0, 1.0, [0.38, 0.42], 0.01)
        lower_outsourced_payroll = st.slider("LOWER_", 0.0, 1.0, [0.68, 0.72], 0.01)
        pmo_outsourced_payroll = st.slider("PMO/QA/TOOLS/OTHER", 0.0, 1.0, [0.01, 0.05], 0.01)
        load_outsourced_payroll = st.slider("LOAD", 0.0, 1.0, [0.28, 0.32], 0.01)
        sol_con_outsourced_payroll = st.slider("SOL_CON", 0.0, 1.0, [0.03, 0.07], 0.01)
        fin_eng_outsourced_payroll = st.slider("FIN_ENG", 0.0, 1.0, [0.08, 0.12], 0.01)
        cola_fx_outsourced_payroll = st.slider("COLA/FX", 0.0, 1.0, [0.13, 0.17], 0.01)
        margin_outsourced_payroll = st.slider("MARGIN", 0.0, 1.0, [0.28, 0.32], 0.01)

    with col2:
        st.subheader("Payroll Retained")
        retained_payroll_percent = st.slider("Retained Payroll Percent", 0.0, 1.0, [0.28, 0.32], 0.01)
        stop_retained_payroll = st.slider("STOP", 0.0, 1.0, [0.01, 0.05], 0.01)
        less_retained_payroll = st.slider("LESS", 0.0, 1.0, [0.08, 0.12], 0.01)
        lower_retained_payroll = st.slider("LOWER", 0.0, 1.0, [0.01, 0.05], 0.01)

        st.subheader("Non Payroll")
        nonpayroll_payroll_ratio = st.slider("Nonpayroll to Payroll Ratio", 0.0, 1.0, [0.28, 0.32], 0.01)
        retained_nonpayroll_percent = st.slider("Retained Nonpayroll %", 0.0, 1.0, [0.33, 0.37], 0.01)
        save_retained_nonpayroll = st.slider("Retained Nonpayroll Savings", 0.0, 1.0, [0.08, 0.12], 0.01)
        save_other_nonpayroll = st.slider("Outsourced Nonpayroll Savings", 0.0, 1.0, [0.68, 0.72], 0.01)

# If submitted, run a new simulation and store the results
if submit:
    variables = [
        retained_payroll_percent, stop_retained_payroll, less_retained_payroll, lower_retained_payroll,
        stop_outsourced_payroll, less_outsourced_payroll, lower_outsourced_payroll,
        pmo_outsourced_payroll, load_outsourced_payroll, sol_con_outsourced_payroll,
        fin_eng_outsourced_payroll, cola_fx_outsourced_payroll, margin_outsourced_payroll,
        nonpayroll_payroll_ratio, retained_nonpayroll_percent,
        save_retained_nonpayroll, save_other_nonpayroll
    ]

    x = []
    # Run 1000 business cases, with variables ranging within the values
    for i in range (1, 15000):
        dot_variables = [random.uniform(low, high) for (low, high) in variables]
        x.append(BusinessCase(*dot_variables).total_savings)

    # Add to session state
    st.session_state.results.append(x)
    st.session_state.names.append(run_name)
    st.session_state.colors.append(color_palette[(len(st.session_state.results)-1) % len(color_palette)])

# If there are any results, show the chart
if st.session_state.results:
    fig = make_figure(st.session_state.results, st.session_state.names, st.session_state.colors)
    chart_placeholder.plotly_chart(fig, use_container_width=True)
