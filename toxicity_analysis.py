import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def show_toxicity_analysis():

    st.title("🛡️ Vanillin Toxicity Analysis")

    st.markdown(
        "Explore product inhibition, microbial tolerance "
        "and product removal strategies."
    )

    st.warning(
        "Exploratory mathematical simulation using "
        "user-defined assumptions. Not a validated "
        "strain-specific toxicity prediction."
    )

    st.subheader("⚙️ Simulation Parameters")

    col1, col2 = st.columns(2)

    with col1:

        concentration = st.slider(
            "Vanillin Concentration (g/L)",
            0.0, 20.0, 5.0, 0.1
        )

        ic50 = st.slider(
            "Assumed 50% Activity Inhibition (g/L)",
            0.1, 20.0, 5.0, 0.1
        )

    with col2:

        tolerance_multiplier = st.slider(
            "Engineered Strain Tolerance Multiplier",
            1.0, 5.0, 2.0, 0.1
        )

        removal = st.slider(
            "Product Removal Efficiency (%)",
            0, 95, 50
        )

    hill = st.slider(
        "Inhibition Curve Steepness",
        1.0, 4.0, 2.0, 0.1
    )

    def relative_activity(product, tolerance):

        return 100 / (
            1 + (product / tolerance) ** hill
        )

    engineered_ic50 = (
        ic50 * tolerance_multiplier
    )

    remaining_product = (
        concentration * (1 - removal / 100)
    )

    normal_activity = relative_activity(
        concentration,
        ic50
    )

    engineered_activity = relative_activity(
        concentration,
        engineered_ic50
    )

    removal_activity = relative_activity(
        remaining_product,
        ic50
    )

    combined_activity = relative_activity(
        remaining_product,
        engineered_ic50
    )

    inhibition = 100 - normal_activity

    st.divider()

    st.subheader("📊 Toxicity Simulation Results")

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Baseline Relative Activity",
        f"{normal_activity:.2f}%"
    )

    c2.metric(
        "Product Inhibition",
        f"{inhibition:.2f}%"
    )

    c3.metric(
        "Engineered Relative Activity",
        f"{engineered_activity:.2f}%"
    )

    st.subheader(
        "📈 Vanillin Concentration vs Microbial Activity"
    )

    concentrations = np.linspace(
        0, max(20, engineered_ic50 * 1.5), 200
    )

    normal_curve = relative_activity(
        concentrations,
        ic50
    )

    engineered_curve = relative_activity(
        concentrations,
        engineered_ic50
    )

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=concentrations,
            y=normal_curve,
            mode="lines",
            name="Baseline Strain",
            line=dict(
                color="#F87171",
                width=4
            )
        )
    )

    fig.add_trace(
        go.Scatter(
            x=concentrations,
            y=engineered_curve,
            mode="lines",
            name="Hypothetical Tolerant Strain",
            line=dict(
                color="#A78BFA",
                width=4
            )
        )
    )

    fig.add_vline(
        x=concentration,
        line_dash="dash",
        line_color="#38BDF8",
        annotation_text="Selected Concentration"
    )

    fig.update_layout(
        template="plotly_dark",
        xaxis_title="Vanillin Concentration (g/L)",
        yaxis_title="Relative Microbial Activity (%)",
        yaxis_range=[0, 105],
        title="Product Inhibition Response"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    st.divider()

    st.subheader(
        "🧬 Product Inhibition Mitigation Strategies"
    )

    comparison = pd.DataFrame({

        "Strategy": [
            "Baseline Strain",
            "Increased Tolerance",
            "Product Removal",
            "Combined Strategy"
        ],

        "Relative Activity (%)": [
            normal_activity,
            engineered_activity,
            removal_activity,
            combined_activity
        ],

        "Remaining Vanillin (g/L)": [
            concentration,
            concentration,
            remaining_product,
            remaining_product
        ],

        "Assumed IC50 (g/L)": [
            ic50,
            engineered_ic50,
            ic50,
            engineered_ic50
        ]
    })

    fig2 = px.bar(
        comparison,
        x="Strategy",
        y="Relative Activity (%)",
        color="Strategy",
        text_auto=".2f",
        template="plotly_dark",
        title="Comparison of Toxicity Mitigation Strategies",
        color_discrete_sequence=[
            "#F87171",
            "#A78BFA",
            "#38BDF8",
            "#34D399"
        ]
    )

    fig2.update_layout(
        showlegend=False,
        yaxis_range=[0, 110]
    )

    st.plotly_chart(
        fig2,
        use_container_width=True
    )

    st.dataframe(
        comparison,
        use_container_width=True
    )

    st.subheader("🧪 Product Removal Simulation")

    r1, r2, r3 = st.columns(3)

    r1.metric(
        "Initial Vanillin",
        f"{concentration:.2f} g/L"
    )

    r2.metric(
        "Remaining Vanillin",
        f"{remaining_product:.2f} g/L"
    )

    r3.metric(
        "Removed Vanillin",
        f"{concentration - remaining_product:.2f} g/L"
    )

    st.caption(
        "Product removal assumes constant broth volume "
        "and does not model recovery losses or "
        "extraction efficiency beyond the selected fraction."
    )

    st.divider()

    st.subheader("💡 Model-Based Recommendations")

    if normal_activity < 50:

        st.warning(
            "The selected concentration causes "
            "more than 50% inhibition under "
            "the assumed model."
        )

        st.write(
            "Investigate product removal, "
            "tolerance engineering or controlled "
            "substrate feeding."
        )

    elif normal_activity < 80:

        st.info(
            "Moderate inhibition is indicated "
            "under the selected assumptions."
        )

        st.write(
            "Investigate improved microbial tolerance "
            "and product concentration control."
        )

    else:

        st.success(
            "Relatively low inhibition is indicated "
            "under the selected assumptions."
        )

    best = comparison.loc[
        comparison["Relative Activity (%)"].idxmax()
    ]

    st.metric(
        "Highest Simulated Relative Activity",
        f"{best['Relative Activity (%)']:.2f}%"
    )

    st.write(
        f"Best simulated strategy: "
        f"**{best['Strategy']}**"
    )

    st.subheader("📥 Export Simulation Results")

    comparison["Initial Vanillin (g/L)"] = concentration

    comparison["Inhibition Curve Steepness"] = hill

    comparison["Tolerance Multiplier"] = [
        1.0,
        tolerance_multiplier,
        1.0,
        tolerance_multiplier
    ]

    comparison["Product Removal (%)"] = [
        0,
        0,
        removal,
        removal
    ]

    st.download_button(
        "Download Toxicity Analysis Results",
        comparison.to_csv(index=False),
        "vanillin_toxicity_analysis.csv",
        "text/csv"
    )

    st.caption(
        "This module uses a hypothetical Hill-type "
        "product inhibition equation. Relative activity "
        "is a dimensionless model output, not measured "
        "cell viability, growth rate or vanillin yield. "
        "Tolerance parameters require experimental "
        "calibration. The module is not yet coupled "
        "to the metabolic flux model."
    )
