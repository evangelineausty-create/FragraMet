import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


# ==========================================
# MICROBIAL GROWTH SIMULATION
# ==========================================

def simulate_growth(
    initial_biomass,
    initial_substrate,
    initial_precursor,
    mu_max,
    ks,
    yield_xs,
    alpha,
    beta,
    ic50,
    hill,
    duration,
    inhibition=True
):

    dt = 0.05

    steps = int(duration / dt) + 1

    time = np.linspace(0, duration, steps)

    biomass = np.zeros(steps)
    substrate = np.zeros(steps)
    precursor = np.zeros(steps)
    product = np.zeros(steps)
    growth_rate = np.zeros(steps)

    biomass[0] = initial_biomass
    substrate[0] = initial_substrate
    precursor[0] = initial_precursor

    # Maximum theoretical mass conversion:
    # Ferulic acid to vanillin

    yield_ps = 152.15 / 194.18

    for i in range(steps - 1):

        x = biomass[i]
        s = substrate[i]
        f = precursor[i]
        p = product[i]

        # MONOD KINETICS

        mu = mu_max * s / (ks + s)

        # PRODUCT INHIBITION

        if inhibition:

            inhibition_factor = (
                1 / (1 + (p / ic50) ** hill)
            )

        else:

            inhibition_factor = 1.0

        mu_effective = mu * inhibition_factor

        growth_rate[i] = mu_effective

        # BIOMASS FORMATION

        dx = mu_effective * x * dt

        # LIMIT GROWTH BY AVAILABLE NUTRIENT

        dx = min(dx, s * yield_xs)

        ds = dx / yield_xs

        # LUEDEKING-PIRET PRODUCT FORMATION

        dp = (
            alpha * dx
            + beta * x * dt * inhibition_factor
        )

        # LIMIT PRODUCT BY FERULIC ACID

        dp = min(dp, f * yield_ps)

        df = dp / yield_ps

        biomass[i + 1] = x + dx

        substrate[i + 1] = max(0, s - ds)

        precursor[i + 1] = max(0, f - df)

        product[i + 1] = p + dp

    final_factor = (

        1 / (1 + (product[-1] / ic50) ** hill)

        if inhibition else 1.0
    )

    growth_rate[-1] = (

        mu_max
        * substrate[-1]
        / (ks + substrate[-1])
        * final_factor
    )

    return pd.DataFrame({

        "Time (h)": time,

        "Biomass (g/L)": biomass,

        "Growth Substrate (g/L)": substrate,

        "Ferulic Acid (g/L)": precursor,

        "Vanillin (g/L)": product,

        "Specific Growth Rate (1/h)": growth_rate
    })


# ==========================================
# STREAMLIT INTERFACE
# ==========================================

def show_microbial_growth():

    st.title("🦠 Microbial Growth Analysis")

    st.markdown(
        "Simulate microbial biomass formation, "
        "nutrient consumption and vanillin production "
        "during fermentation."
    )

    st.warning(
        "Exploratory kinetic simulation using assumed "
        "parameters. Results are not experimentally "
        "validated or strain-specific predictions."
    )

    # ======================================
    # FERMENTATION PARAMETERS
    # ======================================

    st.subheader("⚙️ Fermentation Parameters")

    col1, col2 = st.columns(2)

    with col1:

        initial_biomass = st.slider(
            "Initial Biomass (g/L)",
            0.1, 5.0, 0.5, 0.1
        )

        initial_substrate = st.slider(
            "Initial Growth Substrate (g/L)",
            1.0, 100.0, 20.0, 1.0
        )

    with col2:

        initial_precursor = st.slider(
            "Initial Ferulic Acid (g/L)",
            0.5, 20.0, 5.0, 0.5
        )

        duration = st.slider(
            "Fermentation Time (hours)",
            1, 96, 48
        )

    # ======================================
    # KINETIC PARAMETERS
    # ======================================

    st.subheader("🔬 Microbial Kinetic Parameters")

    with st.expander(
        "Configure Growth and Production Parameters",
        expanded=True
    ):

        k1, k2 = st.columns(2)

        with k1:

            mu_max = st.slider(
                "Maximum Specific Growth Rate (1/h)",
                0.05, 1.0, 0.30, 0.05
            )

            ks = st.slider(
                "Monod Saturation Constant (g/L)",
                0.1, 10.0, 1.0, 0.1
            )

            yield_xs = st.slider(
                "Biomass Yield (g biomass/g substrate)",
                0.1, 0.8, 0.5, 0.05
            )

        with k2:

            alpha = st.slider(
                "Growth-Associated Production Coefficient",
                0.0, 1.0, 0.1, 0.05
            )

            beta = st.slider(
                "Non-Growth-Associated Production Coefficient",
                0.0, 0.2, 0.02, 0.01
            )

            ic50 = st.slider(
                "Assumed Product Inhibition IC50 (g/L)",
                0.1, 20.0, 2.0, 0.1
            )

            hill = st.slider(
                "Inhibition Curve Steepness",
                1.0, 4.0, 2.0, 0.1
            )

    # ======================================
    # MODEL EQUATIONS
    # ======================================

    with st.expander("📘 Mathematical Model"):

        st.markdown("### Monod Growth Kinetics")

        st.latex(
            r"\mu = \mu_{max}\frac{S}{K_s+S}"
        )

        st.markdown("### Product Inhibition")

        st.latex(
            r"\mu_{eff}=\frac{\mu}{1+(P/IC_{50})^n}"
        )

        st.markdown("### Biomass Formation")

        st.latex(
            r"\frac{dX}{dt}=\mu_{eff}X"
        )

        st.markdown("### Substrate Consumption")

        st.latex(
            r"\frac{dS}{dt}=-\frac{1}{Y_{X/S}}\frac{dX}{dt}"
        )

        st.markdown(
            "### Modified Luedeking-Piret Model"
        )

        st.latex(
            r"\frac{dP}{dt}=\alpha\frac{dX}{dt}"
            r"+\frac{\beta X}{1+(P/IC_{50})^n}"
        )

        st.write(
            "Product formation is additionally limited "
            "by available ferulic acid using the "
            "theoretical 1:1 molar conversion."
        )

        st.caption(
            "Alpha: g product/g biomass. "
            "Beta: g product/g biomass/hour. "
            "The numerical simulation uses a "
            "fixed-step Euler method."
        )

    # ======================================
    # RUN SIMULATIONS
    # ======================================

    inhibited = simulate_growth(
        initial_biomass,
        initial_substrate,
        initial_precursor,
        mu_max,
        ks,
        yield_xs,
        alpha,
        beta,
        ic50,
        hill,
        duration,
        inhibition=True
    )

    uninhibited = simulate_growth(
        initial_biomass,
        initial_substrate,
        initial_precursor,
        mu_max,
        ks,
        yield_xs,
        alpha,
        beta,
        ic50,
        hill,
        duration,
        inhibition=False
    )

    final = inhibited.iloc[-1]

    final_biomass = final["Biomass (g/L)"]

    final_product = final["Vanillin (g/L)"]

    final_substrate = final["Growth Substrate (g/L)"]

    final_precursor = final["Ferulic Acid (g/L)"]

    productivity = final_product / duration

    precursor_consumed = (
        initial_precursor - final_precursor
    )

    conversion = (
        precursor_consumed / initial_precursor * 100
    )

    # ======================================
    # SIMULATION RESULTS
    # ======================================

    st.divider()

    st.subheader("📊 Fermentation Simulation Results")

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Simulated Final Biomass",
        f"{final_biomass:.3f} g/L"
    )

    c2.metric(
        "Simulated Vanillin",
        f"{final_product:.3f} g/L"
    )

    c3.metric(
        "Average Productivity",
        f"{productivity:.4f} g/L/h"
    )

    c4, c5, c6 = st.columns(3)

    c4.metric(
        "Remaining Growth Substrate",
        f"{final_substrate:.3f} g/L"
    )

    c5.metric(
        "Remaining Ferulic Acid",
        f"{final_precursor:.3f} g/L"
    )

    c6.metric(
        "Simulated Precursor Conversion",
        f"{conversion:.2f}%"
    )

    # ======================================
    # MICROBIAL GROWTH CURVE
    # ======================================

    st.subheader("📈 Microbial Growth Profile")

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=inhibited["Time (h)"],
            y=inhibited["Biomass (g/L)"],
            mode="lines",
            name="With Product Inhibition",
            line=dict(
                color="#A78BFA",
                width=4
            )
        )
    )

    fig.add_trace(
        go.Scatter(
            x=uninhibited["Time (h)"],
            y=uninhibited["Biomass (g/L)"],
            mode="lines",
            name="Without Product Inhibition",
            line=dict(
                color="#38BDF8",
                width=3,
                dash="dash"
            )
        )
    )

    fig.update_layout(
        template="plotly_dark",
        title="Microbial Biomass Over Time",
        xaxis_title="Fermentation Time (h)",
        yaxis_title="Biomass (g/L)"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    # ======================================
    # SUBSTRATE UTILIZATION
    # ======================================

    st.subheader("🌱 Substrate Utilization")

    fig2 = go.Figure()

    fig2.add_trace(
        go.Scatter(
            x=inhibited["Time (h)"],
            y=inhibited["Growth Substrate (g/L)"],
            mode="lines",
            name="Growth Substrate",
            line=dict(
                color="#34D399",
                width=4
            )
        )
    )

    fig2.add_trace(
        go.Scatter(
            x=inhibited["Time (h)"],
            y=inhibited["Ferulic Acid (g/L)"],
            mode="lines",
            name="Ferulic Acid",
            line=dict(
                color="#38BDF8",
                width=4
            )
        )
    )

    fig2.update_layout(
        template="plotly_dark",
        title="Substrate and Precursor Consumption",
        xaxis_title="Fermentation Time (h)",
        yaxis_title="Concentration (g/L)"
    )

    st.plotly_chart(
        fig2,
        use_container_width=True
    )

    # ======================================
    # VANILLIN PRODUCTION
    # ======================================

    st.subheader("🧪 Vanillin Production Profile")

    fig3 = go.Figure()

    fig3.add_trace(
        go.Scatter(
            x=inhibited["Time (h)"],
            y=inhibited["Vanillin (g/L)"],
            mode="lines",
            name="With Product Inhibition",
            line=dict(
                color="#A78BFA",
                width=4
            )
        )
    )

    fig3.add_trace(
        go.Scatter(
            x=uninhibited["Time (h)"],
            y=uninhibited["Vanillin (g/L)"],
            mode="lines",
            name="Without Product Inhibition",
            line=dict(
                color="#38BDF8",
                width=3,
                dash="dash"
            )
        )
    )

    fig3.update_layout(
        template="plotly_dark",
        title="Simulated Vanillin Production",
        xaxis_title="Fermentation Time (h)",
        yaxis_title="Vanillin Concentration (g/L)"
    )

    st.plotly_chart(
        fig3,
        use_container_width=True
    )

    # ======================================
    # SPECIFIC GROWTH RATE
    # ======================================

    st.subheader("⚡ Specific Growth Rate")

    fig4 = px.line(
        inhibited,
        x="Time (h)",
        y="Specific Growth Rate (1/h)",
        title="Specific Growth Rate During Fermentation",
        template="plotly_dark"
    )

    fig4.update_traces(
        line=dict(
            color="#34D399",
            width=4
        )
    )

    st.plotly_chart(
        fig4,
        use_container_width=True
    )

    # ======================================
    # COMPARATIVE ANALYSIS
    # ======================================

    st.divider()

    st.subheader("🔍 Product Inhibition Comparison")

    comparison = pd.DataFrame({

        "Scenario": [
            "With Product Inhibition",
            "Without Product Inhibition"
        ],

        "Final Biomass (g/L)": [

            inhibited["Biomass (g/L)"].iloc[-1],

            uninhibited["Biomass (g/L)"].iloc[-1]
        ],

        "Final Vanillin (g/L)": [

            inhibited["Vanillin (g/L)"].iloc[-1],

            uninhibited["Vanillin (g/L)"].iloc[-1]
        ]
    })

    fig5 = px.bar(
        comparison,
        x="Scenario",
        y="Final Vanillin (g/L)",
        color="Scenario",
        text_auto=".3f",
        title="Effect of Product Inhibition",
        template="plotly_dark",
        color_discrete_sequence=[
            "#A78BFA",
            "#38BDF8"
        ]
    )

    fig5.update_layout(showlegend=False)

    st.plotly_chart(
        fig5,
        use_container_width=True
    )

    st.dataframe(
        comparison,
        use_container_width=True
    )

    # ======================================
    # THEORETICAL YIELD
    # ======================================

    st.subheader("🎯 Theoretical Conversion Limit")

    theoretical_max = (
        initial_precursor * 152.15 / 194.18
    )

    theoretical_percentage = (
        final_product / theoretical_max * 100
    )

    y1, y2 = st.columns(2)

    y1.metric(
        "Stoichiometric Vanillin Limit",
        f"{theoretical_max:.3f} g/L"
    )

    y2.metric(
        "Percentage of Theoretical Limit",
        f"{theoretical_percentage:.2f}%"
    )

    st.caption(
        "Calculated using a 1:1 molar conversion "
        "of ferulic acid to vanillin. This is a "
        "stoichiometric upper bound, not an "
        "experimentally achievable yield."
    )

    # ======================================
    # RECOMMENDATIONS
    # ======================================

    st.divider()

    st.subheader("💡 Model-Based Recommendations")

    if final_substrate < 0.1:

        st.info(
            "Growth substrate is nearly depleted. "
            "Investigate nutrient feeding strategies."
        )

    if final_precursor < 0.1:

        st.info(
            "Ferulic acid is nearly depleted. "
            "Investigate controlled precursor feeding."
        )

    if final_product >= ic50:

        st.warning(
            "Vanillin has reached the assumed "
            "50% inhibition concentration. "
            "Investigate tolerance engineering "
            "or product removal."
        )

    if final_product < theoretical_max * 0.5:

        st.write(
            "The simulated production remains below "
            "50% of the theoretical conversion limit. "
            "Investigate kinetic parameters and "
            "fermentation duration."
        )

    # ======================================
    # EXPORT RESULTS
    # ======================================

    st.divider()

    st.subheader("📥 Export Simulation Results")

    st.dataframe(
        inhibited,
        use_container_width=True
    )

    export_data = inhibited.copy()

    export_data["Initial Biomass"] = initial_biomass

    export_data["Initial Growth Substrate"] = (
        initial_substrate
    )

    export_data["Initial Ferulic Acid"] = (
        initial_precursor
    )

    export_data["Mu Max"] = mu_max

    export_data["Ks"] = ks

    export_data["Biomass Yield"] = yield_xs

    export_data["Alpha"] = alpha

    export_data["Beta"] = beta

    export_data["IC50"] = ic50

    export_data["Hill Coefficient"] = hill

    st.download_button(
        "Download Growth Simulation Results",
        export_data.to_csv(index=False),
        "microbial_growth_results.csv",
        "text/csv"
    )

    st.download_button(
        "Download Inhibition Comparison",
        comparison.to_csv(index=False),
        "growth_inhibition_comparison.csv",
        "text/csv"
    )

    st.caption(
        "This exploratory model combines Monod "
        "kinetics, Hill-type product inhibition "
        "and modified Luedeking-Piret kinetics. "
        "It assumes idealized batch fermentation, "
        "constant volume and no cell death. "
        "Maintenance energy, oxygen limitation, "
        "lag phase, substrate inhibition and "
        "vanillin degradation are not explicitly "
        "modeled. Experimental calibration is "
        "required. This module is not yet coupled "
        "to the COBRApy flux model."
    )
