import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px


def show_fermentation_optimization():

    st.title("🧪 Fermentation Optimization")

    st.markdown(
        "Explore the influence of fermentation "
        "conditions on microbial vanillin production."
    )

    st.warning(
        "Exploratory simulation using assumed parameters. "
        "Not an experimentally validated prediction."
    )

    st.subheader("⚙️ Fermentation Conditions")

    col1, col2 = st.columns(2)

    with col1:

        temperature = st.slider(
            "Temperature (°C)", 20, 50, 30
        )

        ph = st.slider(
            "pH", 4.0, 9.0, 7.0, 0.1
        )

    with col2:

        duration = st.slider(
            "Incubation Time (hours)", 1, 96, 24
        )

        substrate = st.slider(
            "Ferulic Acid (g/L)",
            0.5, 20.0, 5.0, 0.5
        )

    st.subheader("🔬 Assumed Model Parameters")

    with st.expander("Configure model assumptions"):

        optimal_temp = st.number_input(
            "Assumed optimal temperature (°C)",
            20.0, 50.0, 30.0
        )

        optimal_ph = st.number_input(
            "Assumed optimal pH",
            4.0, 9.0, 7.0
        )

        temp_width = st.number_input(
            "Temperature response width",
            1.0, 20.0, 8.0
        )

        ph_width = st.number_input(
            "pH response width",
            0.1, 5.0, 1.5
        )

        time_constant = st.number_input(
            "Time constant (hours)",
            1.0, 96.0, 24.0
        )

        half_saturation = st.number_input(
            "Substrate half-saturation (g/L)",
            0.1, 20.0, 2.0
        )

    temp_factor = np.exp(
        -((temperature - optimal_temp)
          / temp_width) ** 2
    )

    ph_factor = np.exp(
        -((ph - optimal_ph)
          / ph_width) ** 2
    )

    time_factor = 1 - np.exp(
        -duration / time_constant
    )

    substrate_factor = substrate / (
        substrate + half_saturation
    )

    score = (
        temp_factor
        * ph_factor
        * time_factor
        * substrate_factor
        * 100
    )

    st.divider()

    st.subheader("📊 Simulation Results")

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Relative Production Score",
        f"{score:.2f}/100"
    )

    c2.metric(
        "Temperature Suitability",
        f"{temp_factor * 100:.1f}%"
    )

    c3.metric(
        "pH Suitability",
        f"{ph_factor * 100:.1f}%"
    )

    factors = pd.DataFrame({
        "Parameter": [
            "Temperature",
            "pH",
            "Incubation Time",
            "Substrate"
        ],
        "Relative Factor (%)": [
            temp_factor * 100,
            ph_factor * 100,
            time_factor * 100,
            substrate_factor * 100
        ]
    })

    fig = px.bar(
        factors,
        x="Parameter",
        y="Relative Factor (%)",
        color="Parameter",
        title="Fermentation Factor Analysis",
        template="plotly_dark"
    )

    fig.update_layout(
        showlegend=False,
        yaxis_range=[0, 100]
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    st.subheader("📈 Production Time Profile")

    hours = np.arange(0, 97)

    profile = (
        temp_factor
        * ph_factor
        * (1 - np.exp(-hours / time_constant))
        * substrate_factor
        * 100
    )

    time_data = pd.DataFrame({
        "Time (hours)": hours,
        "Relative Production Score": profile
    })

    fig2 = px.line(
        time_data,
        x="Time (hours)",
        y="Relative Production Score",
        title="Simulated Fermentation Time Profile",
        template="plotly_dark"
    )

    fig2.update_traces(
        line=dict(color="#A78BFA", width=4)
    )

    st.plotly_chart(
        fig2,
        use_container_width=True
    )

    st.subheader("💡 Model-Based Recommendations")

    limiting_factor = factors.loc[
        factors["Relative Factor (%)"].idxmin(),
        "Parameter"
    ]

    st.info(
        f"Lowest relative factor: {limiting_factor}"
    )

    if limiting_factor == "Temperature":
        st.write(
            "Investigate temperatures closer "
            "to the assumed optimum."
        )

    elif limiting_factor == "pH":
        st.write(
            "Investigate pH conditions closer "
            "to the assumed optimum."
        )

    elif limiting_factor == "Incubation Time":
        st.write(
            "Investigate longer fermentation periods."
        )

    else:
        st.write(
            "Investigate substrate availability "
            "and possible inhibition effects."
        )

    st.subheader("📥 Export Simulation Results")

    results = pd.DataFrame({
        "Temperature (C)": [temperature],
        "pH": [ph],
        "Incubation Time (h)": [duration],
        "Ferulic Acid (g/L)": [substrate],
        "Relative Production Score": [score],
        "Assumed Optimal Temperature": [optimal_temp],
        "Assumed Optimal pH": [optimal_ph],
        "Temperature Response Width": [temp_width],
        "pH Response Width": [ph_width],
        "Time Constant": [time_constant],
        "Half Saturation": [half_saturation],
        "Lowest Relative Factor": [limiting_factor]
    })

    st.dataframe(
        results,
        use_container_width=True
    )

    st.download_button(
        "Download Fermentation Results",
        results.to_csv(index=False),
        "fermentation_results.csv",
        "text/csv"
    )

    st.caption(
        "This module uses hypothetical Gaussian "
        "response functions and saturation equations. "
        "Scores are dimensionless and do not represent "
        "actual vanillin yield or concentration. "
        "Experimental calibration is required."
    )
