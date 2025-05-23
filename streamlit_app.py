import streamlit as st
import numpy as np
import plotly.figure_factory as ff
import BC_Methods
import random

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
        x.append(BC_Methods.BusinessCase(*dot_variables).total_savings)

    # Add to session state
    st.session_state.results.append(x)
    st.session_state.names.append(run_name)
    st.session_state.colors.append(color_palette[(len(st.session_state.results)-1) % len(color_palette)])

# If there are any results, show the chart
if st.session_state.results:
    fig = make_figure(st.session_state.results, st.session_state.names, st.session_state.colors)
    chart_placeholder.plotly_chart(fig, use_container_width=True)
