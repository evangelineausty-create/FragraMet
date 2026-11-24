import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from itertools import product
from cofactor_analysis import run_cofactor_model


# ==========================================
# MOLECULAR WEIGHTS
# ==========================================

MW_FERULIC = 194.18
MW_VANILLIN = 152.15


# ==========================================
# INTEGRATED FERMENTATION MODEL
# ==========================================

def simulate_integrated(
    duration,
    temperature,
    ph,
    initial_biomass,
    growth_substrate,
    ferulic_acid,
    pathway_flux,
    degradation,
    tolerance,
    mu_max,
    ks,
    biomass_yield,
    ic50,
    optimal_temp,
    optimal_ph,
    temp_width,
    ph_width,
    flux_conversion
):

    dt = 0.25

    steps = int(np.ceil(duration / dt))

    time = np.linspace(0, duration, steps + 1)

    dt = duration / steps

    biomass = np.zeros(steps + 1)

    substrate = np.zeros(steps + 1)

    precursor = np.zeros(steps + 1)

    vanillin = np.zeros(steps + 1)

    degraded_product = np.zeros(steps + 1)

    biomass[0] = initial_biomass

    substrate[0] = growth_substrate

    precursor[0] = ferulic_acid

    # TEMPERATURE RESPONSE

    temp_factor = np.exp(
        -((temperature - optimal_temp)
          / temp_width) ** 2
    )

    # pH RESPONSE

    ph_factor = np.exp(
        -((ph - optimal_ph)
          / ph_width) ** 2
    )

    environmental_factor = (
        temp_factor * ph_factor
    )

    effective_ic50 = ic50 * tolerance

    # THEORETICAL MASS CONVERSION

    theoretical_yield = (
        MW_VANILLIN / MW_FERULIC
    )

    # CONVERT THEORETICAL FBA FLUX
    # TO ASSUMED SPECIFIC PRODUCTION RATE

    specific_production_rate = (
        pathway_flux
        * flux_conversion
        * MW_VANILLIN
        / 1000
    )

    # TIME-DEPENDENT SIMULATION

    for i in range(steps):

        x = biomass[i]

        s = substrate[i]

        f = precursor[i]

        p = vanillin[i]

        # PRODUCT INHIBITION

        inhibition_factor = (
            1 / (1 + (p / effective_ic50) ** 2)
        )

        # MONOD GROWTH KINETICS

        nutrient_factor = s / (ks + s)

        mu = (
            mu_max
            * nutrient_factor
            * environmental_factor
            * inhibition_factor
        )

        # BIOMASS FORMATION

        dx = mu * x * dt

        dx = min(
            dx,
            s * biomass_yield
        )

        ds = dx / biomass_yield

        # VANILLIN PRODUCTION

        gross_product = (
            specific_production_rate
            * x
            * environmental_factor
            * inhibition_factor
            * nutrient_factor
            * dt
        )

        # LIMIT PRODUCTION BY PRECURSOR

        gross_product = min(
            gross_product,
            f * theoretical_yield
        )

        precursor_consumed = (
            gross_product / theoretical_yield
        )

        # COMPETING DEGRADATION PATHWAY

        lost_product = (
            gross_product * degradation
        )

        net_product = (
            gross_product - lost_product
        )

        # UPDATE FERMENTATION STATE

        biomass[i + 1] = x + dx

        substrate[i + 1] = max(
            0,
            s - ds
        )

        precursor[i + 1] = max(
            0,
            f - precursor_consumed
        )

        vanillin[i + 1] = (
            p + net_product
        )

        degraded_product[i + 1] = (
            degraded_product[i]
            + lost_product
        )

    return pd.DataFrame({

        "Time (h)": time,

        "Biomass (g/L)": biomass,

        "Growth Substrate (g/L)": substrate,

        "Ferulic Acid (g/L)": precursor,

        "Vanillin (g/L)": vanillin,

        "Vanillin-equivalent Loss (g/L)":
            degraded_product
    })


# ==========================================
# ENGINEERING SCENARIO EVALUATION
# ==========================================

def evaluate_scenario(
    scenario,
    parameters,
    flux_cache
):

    fcs_capacity = (
        parameters["fcs"]
        * scenario["FCS Multiplier"]
    )

    ech_capacity = (
        parameters["ech"]
        * scenario["ECH Multiplier"]
    )

    atp_supply = (
        parameters["atp"]
        * scenario["ATP Multiplier"]
    )

    coa_supply = (
        parameters["coa"]
        * scenario["CoA Multiplier"]
    )

    degradation = (
        0.0
        if scenario["VDH Knockout"]
        else parameters["degradation"]
    )

    flux_key = (
        parameters["substrate_supply"],
        fcs_capacity,
        ech_capacity,
        atp_supply,
        coa_supply
    )

    # REUSE IDENTICAL FBA SOLUTIONS

    if flux_key not in flux_cache:

        flux_cache[flux_key] = run_cofactor_model(
            parameters["substrate_supply"],
            fcs_capacity,
            ech_capacity,
            atp_supply,
            coa_supply
        )

    flux_result = flux_cache[flux_key]

    if flux_result is None:

        return None, None

    pathway_flux = flux_result["Vanillin Flux"]

    simulation = simulate_integrated(

        duration=scenario["Duration"],

        temperature=scenario["Temperature"],

        ph=scenario["pH"],

        initial_biomass=parameters["biomass"],

        growth_substrate=scenario["Growth Substrate"],

        ferulic_acid=parameters["ferulic_acid"],

        pathway_flux=pathway_flux,

        degradation=degradation,

        tolerance=scenario["Tolerance Multiplier"],

        mu_max=parameters["mu_max"],

        ks=parameters["ks"],

        biomass_yield=parameters["biomass_yield"],

        ic50=parameters["ic50"],

        optimal_temp=parameters["optimal_temp"],

        optimal_ph=parameters["optimal_ph"],

        temp_width=parameters["temp_width"],

        ph_width=parameters["ph_width"],

        flux_conversion=parameters["flux_conversion"]
    )

    final = simulation.iloc[-1]

    final_product = final["Vanillin (g/L)"]

    theoretical_max = (
        parameters["ferulic_acid"]
        * MW_VANILLIN
        / MW_FERULIC
    )

    productivity = (
        final_product / scenario["Duration"]
    )

    yield_percentage = (
        final_product / theoretical_max * 100
    )

    constraints = {

        "Ferulic Acid Supply":
            parameters["substrate_supply"],

        "FCS": fcs_capacity,

        "ECH": ech_capacity,

        "ATP": atp_supply,

        "CoA": coa_supply
    }

    minimum = min(constraints.values())

    bottleneck = ", ".join([

        name

        for name, value in constraints.items()

        if np.isclose(value, minimum)
    ])

    result = scenario.copy()

    result.update({

        "Pathway Flux": pathway_flux,

        "Final Biomass (g/L)":
            final["Biomass (g/L)"],

        "Vanillin (g/L)": final_product,

        "Productivity (g/L/h)": productivity,

        "Theoretical Yield (%)":
            yield_percentage,

        "Remaining Ferulic Acid (g/L)":
            final["Ferulic Acid (g/L)"],

        "Vanillin-equivalent Loss (g/L)":
            final["Vanillin-equivalent Loss (g/L)"],

        "Metabolic Bottleneck": bottleneck
    })

    return result, simulation


# ==========================================
# STREAMLIT INTERFACE
# ==========================================

def show_integrated_optimization():

    st.title("🚀 Integrated Metabolic Engineering")

    st.markdown(
        "An integrated computational framework "
        "for screening microbial vanillin "
        "production strategies."
    )

    st.warning(
        "Research decision-support prototype. "
        "Model parameters, engineering multipliers "
        "and flux-to-rate conversion are assumed. "
        "Results are simulated, not experimentally "
        "validated production predictions."
    )

    # ======================================
    # WORKFLOW
    # ======================================

    st.subheader("🧬 Integrated Research Workflow")

    st.graphviz_chart("""
    digraph {

        rankdir=TB;

        node [
            shape=box,
            style="rounded,filled",
            fillcolor="#312E81",
            color="#A78BFA",
            fontcolor="white"
        ];

        edge [
            color="#A78BFA"
        ];

        G [label="Gene Engineering"];

        E [label="ATP and Cofactor Constraints"];

        F [label="COBRApy Flux Optimization"];

        C [label="Fermentation Conditions"];

        N [label="Nutrient Availability"];

        T [label="Vanillin Toxicity"];

        K [label="Microbial Growth Model"];

        P [label="Vanillin Production Simulation"];

        S [label="Automated Scenario Screening"];

        R [label="Ranked Engineering Strategies",
           fillcolor="#0F766E"];

        G -> F;

        E -> F;

        F -> P;

        C -> K;

        N -> K;

        T -> K;

        K -> P;

        P -> S;

        S -> R;
    }
    """)

    # ======================================
    # BASELINE PARAMETERS
    # ======================================

    st.divider()

    st.subheader("⚙️ Baseline Metabolic Parameters")

    col1, col2 = st.columns(2)

    with col1:

        substrate_supply = st.slider(
            "Ferulic Acid Supply Capacity",
            1.0, 50.0, 20.0
        )

        fcs = st.slider(
            "Baseline FCS Capacity",
            1.0, 30.0, 5.0
        )

        ech = st.slider(
            "Baseline ECH Capacity",
            1.0, 30.0, 15.0
        )

        degradation = st.slider(
            "Assumed VDH-Associated Product Loss (%)",
            0, 90, 20
        ) / 100

    with col2:

        atp = st.slider(
            "Baseline ATP Supply",
            1.0, 50.0, 5.0
        )

        coa = st.slider(
            "Baseline CoA Supply",
            1.0, 50.0, 15.0
        )

        biomass = st.slider(
            "Initial Biomass (g/L)",
            0.1, 5.0, 0.5, 0.1
        )

        ferulic_acid = st.slider(
            "Initial Ferulic Acid (g/L)",
            0.5, 20.0, 5.0, 0.5
        )

    st.caption(
        "FBA supply capacities are theoretical "
        "flux units. Ferulic acid concentration "
        "is a separate batch fermentation input."
    )

    # ======================================
    # BASELINE FERMENTATION
    # ======================================

    st.subheader("🧪 Baseline Fermentation Conditions")

    c1, c2 = st.columns(2)

    with c1:

        temperature = st.slider(
            "Baseline Temperature (°C)",
            20, 45, 30
        )

        ph = st.slider(
            "Baseline pH",
            4.0, 9.0, 7.0, 0.1
        )

    with c2:

        duration = st.slider(
            "Baseline Duration (h)",
            12, 96, 24, 12
        )

        growth_substrate = st.slider(
            "Baseline Growth Substrate (g/L)",
            5.0, 60.0, 20.0, 5.0
        )

    # ======================================
    # MODEL ASSUMPTIONS
    # ======================================

    with st.expander(
        "🔬 Configure Mathematical Model Assumptions"
    ):

        a1, a2 = st.columns(2)

        with a1:

            mu_max = st.number_input(
                "Maximum Growth Rate (1/h)",
                min_value=0.01,
                max_value=2.0,
                value=0.30
            )

            ks = st.number_input(
                "Monod Constant (g/L)",
                min_value=0.1,
                max_value=20.0,
                value=1.0
            )

            biomass_yield = st.number_input(
                "Biomass Yield (g/g)",
                min_value=0.1,
                max_value=1.0,
                value=0.5
            )

            ic50 = st.number_input(
                "Assumed Vanillin IC50 (g/L)",
                min_value=0.1,
                max_value=20.0,
                value=2.0
            )

        with a2:

            optimal_temp = st.number_input(
                "Assumed Optimal Temperature (°C)",
                min_value=20.0,
                max_value=45.0,
                value=30.0
            )

            optimal_ph = st.number_input(
                "Assumed Optimal pH",
                min_value=4.0,
                max_value=9.0,
                value=7.0
            )

            temp_width = st.number_input(
                "Temperature Response Width",
                min_value=1.0,
                max_value=20.0,
                value=8.0
            )

            ph_width = st.number_input(
                "pH Response Width",
                min_value=0.1,
                max_value=5.0,
                value=1.5
            )

        flux_conversion = st.number_input(
            "Assumed Flux-to-Rate Conversion Factor",
            min_value=0.001,
            max_value=1.0,
            value=0.01,
            step=0.001,
            format="%.3f"
        )

        st.caption(
            "Conversion factor units: mmol vanillin "
            "per g biomass per hour per model flux unit. "
            "This factor links theoretical FBA flux "
            "to an assumed specific production rate. "
            "It requires experimental calibration."
        )

    parameters = {

        "substrate_supply": substrate_supply,

        "fcs": fcs,

        "ech": ech,

        "atp": atp,

        "coa": coa,

        "degradation": degradation,

        "biomass": biomass,

        "ferulic_acid": ferulic_acid,

        "mu_max": mu_max,

        "ks": ks,

        "biomass_yield": biomass_yield,

        "ic50": ic50,

        "optimal_temp": optimal_temp,

        "optimal_ph": optimal_ph,

        "temp_width": temp_width,

        "ph_width": ph_width,

        "flux_conversion": flux_conversion
    }

    # ======================================
    # AUTOMATED SCREENING SETTINGS
    # ======================================

    st.divider()

    st.subheader("🔍 Automated Strategy Screening")

    st.write(
        "Select engineering interventions and "
        "fermentation conditions to evaluate."
    )

    s1, s2 = st.columns(2)

    with s1:

        fcs_options = st.multiselect(
            "FCS Capacity Multipliers",
            [1.0, 2.0, 3.0],
            default=[1.0, 2.0]
        )

        ech_options = st.multiselect(
            "ECH Capacity Multipliers",
            [1.0, 2.0, 3.0],
            default=[1.0, 2.0]
        )

        atp_options = st.multiselect(
            "ATP Supply Multipliers",
            [1.0, 2.0, 3.0],
            default=[1.0, 2.0]
        )

        coa_options = st.multiselect(
            "CoA Supply Multipliers",
            [1.0, 2.0, 3.0],
            default=[1.0, 2.0]
        )

        vdh_options = st.multiselect(
            "VDH Engineering",
            ["Unmodified", "Knockout"],
            default=["Unmodified", "Knockout"]
        )

    with s2:

        tolerance_options = st.multiselect(
            "Vanillin Tolerance Multipliers",
            [1.0, 2.0, 3.0],
            default=[1.0, 2.0]
        )

        temperature_options = st.multiselect(
            "Temperature Conditions (°C)",
            [25, 30, 35, 40],
            default=[30]
        )

        ph_options = st.multiselect(
            "pH Conditions",
            [5.0, 6.0, 7.0, 8.0],
            default=[7.0]
        )

        duration_options = st.multiselect(
            "Fermentation Duration (h)",
            [12, 24, 48, 72, 96],
            default=[24, 48]
        )

        nutrient_options = st.multiselect(
            "Growth Substrate (g/L)",
            [10.0, 20.0, 30.0, 40.0],
            default=[20.0]
        )

    objective = st.selectbox(
        "Optimization Objective",
        [
            "Maximum Vanillin Concentration",
            "Maximum Volumetric Productivity",
            "Maximum Theoretical Yield Percentage"
        ]
    )

    objective_map = {

        "Maximum Vanillin Concentration":
            "Vanillin (g/L)",

        "Maximum Volumetric Productivity":
            "Productivity (g/L/h)",

        "Maximum Theoretical Yield Percentage":
            "Theoretical Yield (%)"
    }

    objective_column = objective_map[objective]

    option_lists = [

        fcs_options,

        ech_options,

        atp_options,

        coa_options,

        vdh_options,

        tolerance_options,

        temperature_options,

        ph_options,

        duration_options,

        nutrient_options
    ]

    scenario_count = int(
        np.prod([len(x) for x in option_lists])
    )

    st.metric(
        "Candidate Engineering Scenarios",
        scenario_count
    )

    st.caption(
        "The optimizer uses exhaustive grid search "
        "over the selected combinations. "
        "The maximum permitted search size is "
        "5,000 scenarios."
    )

    # ======================================
    # RUN OPTIMIZATION
    # ======================================

    if not st.button(
        "🚀 Run Integrated Optimization",
        use_container_width=True,
        type="primary"
    ):

        st.info(
            "Configure the parameters and click "
            "Run Integrated Optimization."
        )

        return

    if scenario_count == 0:

        st.error(
            "Select at least one option "
            "in every screening category."
        )

        return

    if scenario_count > 5000:

        st.error(
            "Too many combinations. Reduce the "
            "selected options to 5,000 or fewer."
        )

        return

    flux_cache = {}

    # ======================================
    # BASELINE SIMULATION
    # ======================================

    baseline = {

        "FCS Multiplier": 1.0,

        "ECH Multiplier": 1.0,

        "ATP Multiplier": 1.0,

        "CoA Multiplier": 1.0,

        "VDH Knockout": False,

        "Tolerance Multiplier": 1.0,

        "Temperature": temperature,

        "pH": ph,

        "Duration": duration,

        "Growth Substrate": growth_substrate
    }

    baseline_result, baseline_curve = (
        evaluate_scenario(
            baseline,
            parameters,
            flux_cache
        )
    )

    if baseline_result is None:

        st.error("Baseline FBA optimization failed.")

        return

    # ======================================
    # GRID SEARCH
    # ======================================

    results = []

    progress = st.progress(0)

    status = st.empty()

    with st.spinner(
        "Evaluating engineering scenarios..."
    ):

        for i, values in enumerate(
            product(*option_lists)
        ):

            scenario = {

                "FCS Multiplier": values[0],

                "ECH Multiplier": values[1],

                "ATP Multiplier": values[2],

                "CoA Multiplier": values[3],

                "VDH Knockout":
                    values[4] == "Knockout",

                "Tolerance Multiplier": values[5],

                "Temperature": values[6],

                "pH": values[7],

                "Duration": values[8],

                "Growth Substrate": values[9]
            }

            result, _ = evaluate_scenario(

                scenario,

                parameters,

                flux_cache
            )

            if result is not None:

                result["Scenario"] = i + 1

                results.append(result)

            if i % 10 == 0 or i == scenario_count - 1:

                progress.progress(
                    (i + 1) / scenario_count
                )

                status.text(
                    f"Evaluated {i + 1} "
                    f"of {scenario_count} scenarios"
                )

    if not results:

        st.error("No successful simulations.")

        return

    results_df = pd.DataFrame(results)

    results_df = results_df.sort_values(

        by=[
            objective_column,
            "Productivity (g/L/h)"
        ],

        ascending=False

    ).reset_index(drop=True)

    results_df.insert(
        0,
        "Rank",
        np.arange(1, len(results_df) + 1)
    )

    best = results_df.iloc[0]

    st.success(
        f"Screening completed: "
        f"{len(results_df)} successful scenarios."
    )

    # ======================================
    # OPTIMIZATION RESULTS
    # ======================================

    st.divider()

    st.subheader("🏆 Integrated Optimization Results")

    baseline_product = (
        baseline_result["Vanillin (g/L)"]
    )

    best_product = best["Vanillin (g/L)"]

    improvement = (

        (best_product - baseline_product)

        / baseline_product * 100

        if baseline_product > 0

        else None
    )

    m1, m2, m3 = st.columns(3)

    m1.metric(
        "Baseline Vanillin",
        f"{baseline_product:.3f} g/L"
    )

    m2.metric(
        "Best Scenario Vanillin",
        f"{best_product:.3f} g/L"
    )

    m3.metric(
        "Concentration Change",
        f"{improvement:.2f}%"
        if improvement is not None
        else "Undefined"
    )

    m4, m5, m6 = st.columns(3)

    m4.metric(
        "Best Scenario Productivity",
        f"{best['Productivity (g/L/h)']:.4f}"
        " g/L/h"
    )

    m5.metric(
        "Theoretical Yield Percentage",
        f"{best['Theoretical Yield (%)']:.2f}%"
    )

    m6.metric(
        "Successful Scenarios",
        len(results_df)
    )

    st.caption(
        f"Ranking objective: {objective}. "
        "The highest-ranked scenario is the best "
        "among the tested combinations, not "
        "necessarily a global biological optimum."
    )

    # ======================================
    # BASELINE VS BEST SCENARIO
    # ======================================

    st.subheader("📊 Baseline vs Best Scenario")

    comparison = pd.DataFrame({

        "Scenario": [

            "Baseline",

            "Best Screened Scenario"
        ],

        "Vanillin (g/L)": [

            baseline_product,

            best_product
        ],

        "Productivity (g/L/h)": [

            baseline_result["Productivity (g/L/h)"],

            best["Productivity (g/L/h)"]
        ],

        "Final Biomass (g/L)": [

            baseline_result["Final Biomass (g/L)"],

            best["Final Biomass (g/L)"]
        ]
    })

    fig = px.bar(

        comparison,

        x="Scenario",

        y="Vanillin (g/L)",

        color="Scenario",

        text_auto=".3f",

        title="Vanillin Concentration Comparison",

        template="plotly_dark",

        color_discrete_sequence=[
            "#38BDF8",
            "#A78BFA"
        ]
    )

    fig.update_layout(showlegend=False)

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    st.dataframe(
        comparison,
        use_container_width=True
    )

    # ======================================
    # BEST ENGINEERING STRATEGY
    # ======================================

    st.subheader("🧬 Best Screened Engineering Strategy")

    strategy = pd.DataFrame({

        "Parameter": [

            "FCS Capacity Multiplier",

            "ECH Capacity Multiplier",

            "ATP Supply Multiplier",

            "CoA Supply Multiplier",

            "VDH Engineering",

            "Vanillin Tolerance Multiplier",

            "Temperature",

            "pH",

            "Fermentation Duration",

            "Growth Substrate",

            "Remaining Metabolic Bottleneck"
        ],

        "Selected Condition": [

            f"{best['FCS Multiplier']:.1f}x",

            f"{best['ECH Multiplier']:.1f}x",

            f"{best['ATP Multiplier']:.1f}x",

            f"{best['CoA Multiplier']:.1f}x",

            "Knockout"
            if best["VDH Knockout"]
            else "Unmodified",

            f"{best['Tolerance Multiplier']:.1f}x",

            f"{best['Temperature']} °C",

            str(best["pH"]),

            f"{best['Duration']} h",

            f"{best['Growth Substrate']} g/L",

            best["Metabolic Bottleneck"]
        ]
    })

    st.dataframe(
        strategy,
        use_container_width=True,
        hide_index=True
    )

    # ======================================
    # BEST SCENARIO TIME PROFILE
    # ======================================

    best_scenario = {

        key: best[key]

        for key in baseline.keys()
    }

    _, best_curve = evaluate_scenario(

        best_scenario,

        parameters,

        flux_cache
    )

    st.subheader("📈 Integrated Production Profile")

    fig2 = go.Figure()

    fig2.add_trace(

        go.Scatter(

            x=baseline_curve["Time (h)"],

            y=baseline_curve["Vanillin (g/L)"],

            name="Baseline",

            mode="lines",

            line=dict(
                color="#38BDF8",
                width=3,
                dash="dash"
            )
        )
    )

    fig2.add_trace(

        go.Scatter(

            x=best_curve["Time (h)"],

            y=best_curve["Vanillin (g/L)"],

            name="Best Screened Scenario",

            mode="lines",

            line=dict(
                color="#A78BFA",
                width=4
            )
        )
    )

    fig2.update_layout(

        template="plotly_dark",

        title="Simulated Vanillin Production Over Time",

        xaxis_title="Fermentation Time (h)",

        yaxis_title="Vanillin Concentration (g/L)"
    )

    st.plotly_chart(
        fig2,
        use_container_width=True
    )

    # ======================================
    # BIOMASS COMPARISON
    # ======================================

    st.subheader("🦠 Microbial Growth Comparison")

    fig3 = go.Figure()

    fig3.add_trace(

        go.Scatter(

            x=baseline_curve["Time (h)"],

            y=baseline_curve["Biomass (g/L)"],

            name="Baseline Biomass",

            mode="lines",

            line=dict(
                color="#38BDF8",
                width=3,
                dash="dash"
            )
        )
    )

    fig3.add_trace(

        go.Scatter(

            x=best_curve["Time (h)"],

            y=best_curve["Biomass (g/L)"],

            name="Best Scenario Biomass",

            mode="lines",

            line=dict(
                color="#34D399",
                width=4
            )
        )
    )

    fig3.update_layout(

        template="plotly_dark",

        title="Simulated Microbial Growth",

        xaxis_title="Fermentation Time (h)",

        yaxis_title="Biomass (g/L)"
    )

    st.plotly_chart(
        fig3,
        use_container_width=True
    )

    # ======================================
    # TOP 10 SCENARIOS
    # ======================================

    st.divider()

    st.subheader("🏅 Top 10 Engineering Scenarios")

    top10 = results_df.head(10).copy()

    top10["Scenario Label"] = (

        "Rank "

        + top10["Rank"].astype(str)
    )

    fig4 = px.bar(

        top10,

        x="Scenario Label",

        y=objective_column,

        color=objective_column,

        title="Top 10 Ranked Scenarios",

        template="plotly_dark",

        color_continuous_scale="Purples"
    )

    st.plotly_chart(
        fig4,
        use_container_width=True
    )

    st.dataframe(
        top10.drop(columns=["Scenario Label"]),
        use_container_width=True
    )

    # ======================================
    # FACTOR INFLUENCE ANALYSIS
    # ======================================

    st.divider()

    st.subheader("🔬 Screening Factor Influence")

    factors = [

        "FCS Multiplier",

        "ECH Multiplier",

        "ATP Multiplier",

        "CoA Multiplier",

        "VDH Knockout",

        "Tolerance Multiplier",

        "Temperature",

        "pH",

        "Duration",

        "Growth Substrate"
    ]

    sensitivity = []

    for factor in factors:

        if results_df[factor].nunique() > 1:

            means = results_df.groupby(
                factor
            )[objective_column].mean()

            influence = (
                means.max() - means.min()
            )

            sensitivity.append({

                "Parameter": factor,

                "Mean Response Range": influence
            })

    if sensitivity:

        sensitivity_df = pd.DataFrame(
            sensitivity
        ).sort_values(

            "Mean Response Range",

            ascending=False
        )

        fig5 = px.bar(

            sensitivity_df,

            x="Mean Response Range",

            y="Parameter",

            orientation="h",

            color="Mean Response Range",

            title="Screened Factor Influence",

            template="plotly_dark",

            color_continuous_scale="Purples"
        )

        fig5.update_layout(
            yaxis=dict(autorange="reversed")
        )

        st.plotly_chart(
            fig5,
            use_container_width=True
        )

        strongest_factor = (
            sensitivity_df.iloc[0]["Parameter"]
        )

        st.info(

            f"Largest average response difference "
            f"within the screened ranges: "
            f"{strongest_factor}"
        )

        st.caption(
            "Influence is estimated from differences "
            "in mean simulated outcomes across "
            "tested factor levels. This is a "
            "descriptive screening measure, not "
            "causal importance or formal global "
            "sensitivity analysis."
        )

    else:

        sensitivity_df = pd.DataFrame()

        st.info(
            "Select multiple levels for at least "
            "one factor to compare its influence."
        )

    # ======================================
    # RESEARCH RECOMMENDATIONS
    # ======================================

    st.divider()

    st.subheader("💡 Proposed Research Strategies")

    if best["FCS Multiplier"] > 1:

        st.write(
            "• Investigate increased FCS expression "
            "or catalytic capacity."
        )

    if best["ECH Multiplier"] > 1:

        st.write(
            "• Investigate increased ECH expression "
            "or catalytic capacity."
        )

    if best["VDH Knockout"]:

        st.write(
            "• Investigate VDH downregulation "
            "or knockout to reduce product loss."
        )

    if best["ATP Multiplier"] > 1:

        st.write(
            "• Investigate cellular energy supply "
            "and ATP regeneration."
        )

    if best["CoA Multiplier"] > 1:

        st.write(
            "• Investigate CoA availability "
            "and recycling pathways."
        )

    if best["Tolerance Multiplier"] > 1:

        st.write(
            "• Investigate microbial tolerance "
            "to vanillin accumulation."
        )

    st.write(

        f"• Evaluate the selected fermentation "
        f"conditions: {best['Temperature']} °C, "
        f"pH {best['pH']}, "
        f"{best['Duration']} hours."
    )

    st.write(

        f"• Investigate the remaining modeled "
        f"bottleneck: "
        f"{best['Metabolic Bottleneck']}."
    )

    st.warning(
        "These recommendations are generated "
        "from simulated scenario rankings. "
        "Gene modifications and fermentation "
        "conditions require strain-specific "
        "experimental validation."
    )

    # ======================================
    # COMPLETE RESULTS AND EXPORT
    # ======================================

    st.divider()

    st.subheader("📥 Research Results and Export")

    st.dataframe(
        results_df,
        use_container_width=True
    )

    # INCLUDE ASSUMPTIONS IN EXPORTED RESULTS

    export_results = results_df.copy()

    for key, value in parameters.items():

        export_results[
            f"Model Parameter: {key}"
        ] = value

    export_results["Ranking Objective"] = objective

    st.download_button(

        "Download All Ranked Scenarios",

        export_results.to_csv(index=False),

        "fragramet_integrated_results.csv",

        "text/csv"
    )

    st.download_button(

        "Download Best Engineering Strategy",

        strategy.to_csv(index=False),

        "fragramet_best_strategy.csv",

        "text/csv"
    )

    st.download_button(

        "Download Best Production Profile",

        best_curve.to_csv(index=False),

        "fragramet_production_profile.csv",

        "text/csv"
    )

    st.download_button(

        "Download Baseline Production Profile",

        baseline_curve.to_csv(index=False),

        "fragramet_baseline_profile.csv",

        "text/csv"
    )

    if not sensitivity_df.empty:

        st.download_button(

            "Download Factor Influence Analysis",

            sensitivity_df.to_csv(index=False),

            "fragramet_factor_influence.csv",

            "text/csv"
        )

    # ======================================
    # SCIENTIFIC LIMITATIONS
    # ======================================

    with st.expander(
        "📘 Scientific Methodology and Limitations"
    ):

        st.markdown(
            """
            ### Computational Methods

            - Constraint-based flux balance analysis
            - Linear programming using COBRApy
            - Monod microbial growth kinetics
            - Gaussian environmental response functions
            - Hill-type product inhibition
            - Time-dependent numerical simulation
            - Exhaustive grid-search optimization
            - Descriptive factor influence analysis

            ### Model Limitations

            - The metabolic network is pathway-based,
              not genome-scale.
            - Gene expression changes are represented
              by assumed reaction capacity multipliers.
            - VDH knockout is represented by eliminating
              an assumed product loss fraction.
            - ATP and CoA supply constraints do not
              represent measured intracellular pools.
            - The flux-to-production-rate conversion
              factor requires experimental calibration.
            - Temperature and pH responses use
              assumed optimum values.
            - The nutrient model represents a generic
              growth substrate, not detailed medium
              composition or nitrogen metabolism.
            - Oxygen transfer, maintenance energy,
              cell death and detailed cofactor recycling
              are not explicitly represented.
            - The integrated kinetic model is a
              simplified coupling framework rather
              than a complete dynamic FBA model.
            - Results are intended for hypothesis
              generation and experimental planning.
            """
        )

    st.caption(
        "AUSFEL BioSystems | FragraMet "
        "Integrated Research Platform"
    )
