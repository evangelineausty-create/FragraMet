import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px

from cobra import Model, Reaction, Metabolite


# ==========================================
# COFACTOR CONSTRAINED FBA MODEL
# ==========================================

def run_cofactor_model(
    substrate,
    fcs_capacity,
    ech_capacity,
    atp_supply,
    coa_supply
):

    model = Model("FragraMet_Cofactor_Model")

    # METABOLITES

    fa = Metabolite("ferulic_acid_c")
    fc = Metabolite("feruloyl_coa_c")
    van = Metabolite("vanillin_c")

    atp = Metabolite("atp_c")
    amp = Metabolite("amp_c")
    ppi = Metabolite("ppi_c")

    coa = Metabolite("coa_c")
    acetyl_coa = Metabolite("acetyl_coa_c")

    water = Metabolite("water_c")


    # SUBSTRATE SUPPLY

    substrate_rxn = Reaction("SUBSTRATE")
    substrate_rxn.bounds = (0, substrate)

    substrate_rxn.add_metabolites({
        fa: 1
    })


    # ATP SUPPLY

    atp_rxn = Reaction("ATP_SUPPLY")
    atp_rxn.bounds = (0, atp_supply)

    atp_rxn.add_metabolites({
        atp: 1
    })


    # COENZYME A SUPPLY

    coa_rxn = Reaction("COA_SUPPLY")
    coa_rxn.bounds = (0, coa_supply)

    coa_rxn.add_metabolites({
        coa: 1
    })


    # WATER SUPPLY

    water_rxn = Reaction("WATER_SUPPLY")
    water_rxn.bounds = (0, 1000)

    water_rxn.add_metabolites({
        water: 1
    })


    # FCS REACTION

    fcs = Reaction("FCS")
    fcs.bounds = (0, fcs_capacity)

    fcs.add_metabolites({
        fa: -1,
        atp: -1,
        coa: -1,
        fc: 1,
        amp: 1,
        ppi: 1
    })

    fcs.gene_reaction_rule = "fcs"


    # ECH REACTION

    ech = Reaction("ECH")
    ech.bounds = (0, ech_capacity)

    ech.add_metabolites({
        fc: -1,
        water: -1,
        van: 1,
        acetyl_coa: 1
    })

    ech.gene_reaction_rule = "ech"


    # VANILLIN EXPORT

    export = Reaction("VANILLIN_EXPORT")
    export.bounds = (0, 1000)

    export.add_metabolites({
        van: -1
    })


    # BYPRODUCT SINKS

    amp_sink = Reaction("AMP_SINK")
    amp_sink.bounds = (0, 1000)

    amp_sink.add_metabolites({
        amp: -1
    })

    ppi_sink = Reaction("PPI_SINK")
    ppi_sink.bounds = (0, 1000)

    ppi_sink.add_metabolites({
        ppi: -1
    })

    acetyl_sink = Reaction("ACETYL_COA_SINK")
    acetyl_sink.bounds = (0, 1000)

    acetyl_sink.add_metabolites({
        acetyl_coa: -1
    })


    # ADD REACTIONS

    model.add_reactions([
        substrate_rxn,
        atp_rxn,
        coa_rxn,
        water_rxn,
        fcs,
        ech,
        export,
        amp_sink,
        ppi_sink,
        acetyl_sink
    ])


    # OBJECTIVE FUNCTION

    model.objective = "VANILLIN_EXPORT"

    solution = model.optimize()

    if solution.status != "optimal":
        return None

    return {
        "Vanillin Flux": float(
            solution.fluxes["VANILLIN_EXPORT"]
        ),

        "ATP Consumption": float(
            solution.fluxes["ATP_SUPPLY"]
        ),

        "CoA Supply Flux": float(
            solution.fluxes["COA_SUPPLY"]
        ),

        "FCS Flux": float(
            solution.fluxes["FCS"]
        ),

        "ECH Flux": float(
            solution.fluxes["ECH"]
        )
    }


# ==========================================
# STREAMLIT INTERFACE
# ==========================================

def show_cofactor_analysis():

    st.title("⚡ ATP and Cofactor Analysis")

    st.markdown(
        "Investigate energy and cofactor constraints "
        "in microbial vanillin biosynthesis."
    )

    st.warning(
        "Simplified pathway-based FBA model. "
        "ATP and CoA supply rates are assumed constraints, "
        "not measured intracellular concentrations."
    )


    # ======================================
    # BIOCHEMICAL PATHWAY
    # ======================================

    st.subheader("🧬 Cofactor-Dependent Pathway")

    st.graphviz_chart("""
    digraph {

        rankdir=TB;

        node [
            shape=box,
            style="rounded,filled",
            color="#A78BFA",
            fillcolor="#312E81",
            fontcolor="white"
        ];

        edge [
            color="#A78BFA",
            fontcolor="#A78BFA"
        ];

        FA [label="Ferulic Acid"];

        FC [label="Feruloyl-CoA"];

        VAN [label="Vanillin"];

        ATP [label="ATP + CoA"];

        AMP [label="AMP + PPi"];

        AC [label="Acetyl-CoA"];

        FA -> FC [label="FCS"];

        ATP -> FC [label="Required"];

        FA -> AMP [style=dashed];

        FC -> VAN [label="ECH"];

        FC -> AC [label="Byproduct"];
    }
    """)

    st.markdown(
        "**FCS:** Ferulic acid + ATP + CoA "
        "→ Feruloyl-CoA + AMP + PPi"
    )

    st.markdown(
        "**ECH:** Feruloyl-CoA + H₂O "
        "→ Vanillin + Acetyl-CoA"
    )


    # ======================================
    # INPUT PARAMETERS
    # ======================================

    st.divider()

    st.subheader("⚙️ Metabolic Constraints")

    col1, col2 = st.columns(2)

    with col1:

        substrate = st.slider(
            "Ferulic Acid Supply",
            0.0, 50.0, 20.0
        )

        fcs_capacity = st.slider(
            "FCS Reaction Capacity",
            0.0, 50.0, 15.0
        )

        ech_capacity = st.slider(
            "ECH Reaction Capacity",
            0.0, 50.0, 15.0
        )

    with col2:

        atp_supply = st.slider(
            "ATP Supply Rate",
            0.0, 50.0, 5.0
        )

        coa_supply = st.slider(
            "Coenzyme A Supply Rate",
            0.0, 50.0, 15.0
        )

    st.caption(
        "All supply rates and reaction capacities "
        "use theoretical model flux units."
    )


    # ======================================
    # FBA SIMULATION
    # ======================================

    result = run_cofactor_model(
        substrate,
        fcs_capacity,
        ech_capacity,
        atp_supply,
        coa_supply
    )

    if result is None:

        st.error("Optimization failed.")
        return


    # ======================================
    # SIMULATION RESULTS
    # ======================================

    st.divider()

    st.subheader("📊 Metabolic Simulation Results")

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Vanillin Flux",
        f"{result['Vanillin Flux']:.2f}"
    )

    c2.metric(
        "ATP Consumption Flux",
        f"{result['ATP Consumption']:.2f}"
    )

    c3.metric(
        "CoA Supply Flux",
        f"{result['CoA Supply Flux']:.2f}"
    )


    # ATP EQUIVALENT DEMAND

    st.metric(
        "ATP Equivalent Demand",
        f"{2 * result['ATP Consumption']:.2f}"
    )

    st.caption(
        "ATP is converted to AMP and PPi during "
        "ferulic acid activation. With PPi hydrolysis, "
        "this corresponds to approximately two "
        "high-energy phosphate bond equivalents."
    )


    # ======================================
    # BOTTLENECK ANALYSIS
    # ======================================

    st.subheader("🔍 Metabolic Bottleneck Identification")

    constraints = {

        "Substrate Supply": substrate,

        "FCS Capacity": fcs_capacity,

        "ECH Capacity": ech_capacity,

        "ATP Supply": atp_supply,

        "CoA Supply": coa_supply
    }

    minimum = min(constraints.values())

    limiting_factors = [

        name

        for name, value in constraints.items()

        if np.isclose(value, minimum)
    ]

    st.info(
        "Limiting constraint(s): "
        + ", ".join(limiting_factors)
    )

    constraint_data = pd.DataFrame({

        "Metabolic Constraint": list(
            constraints.keys()
        ),

        "Available Capacity": list(
            constraints.values()
        )
    })

    fig = px.bar(

        constraint_data,

        x="Metabolic Constraint",

        y="Available Capacity",

        color="Metabolic Constraint",

        title="Metabolic Capacity Comparison",

        template="plotly_dark"
    )

    fig.update_layout(showlegend=False)

    st.plotly_chart(
        fig,
        use_container_width=True
    )


    # ======================================
    # ATP SENSITIVITY ANALYSIS
    # ======================================

    st.divider()

    st.subheader("📈 ATP Supply Sensitivity Analysis")

    atp_values = np.linspace(0, 50, 51)

    flux_values = []

    for value in atp_values:

        simulation = run_cofactor_model(
            substrate,
            fcs_capacity,
            ech_capacity,
            float(value),
            coa_supply
        )

        if simulation is not None:

            flux_values.append(
                simulation["Vanillin Flux"]
            )

        else:

            flux_values.append(np.nan)

    sensitivity_data = pd.DataFrame({

        "ATP Supply Rate": atp_values,

        "Vanillin Flux": flux_values
    })

    fig2 = px.line(

        sensitivity_data,

        x="ATP Supply Rate",

        y="Vanillin Flux",

        title="Influence of ATP Supply on Vanillin Flux",

        template="plotly_dark"
    )

    fig2.update_traces(
        line=dict(
            color="#A78BFA",
            width=4
        )
    )

    st.plotly_chart(
        fig2,
        use_container_width=True
    )


    # ======================================
    # ENERGY ENGINEERING SIMULATION
    # ======================================

    st.divider()

    st.subheader("🧪 Virtual Energy Engineering")

    atp_multiplier = st.slider(
        "ATP Supply Improvement",
        1.0, 5.0, 2.0, 0.1
    )

    coa_multiplier = st.slider(
        "CoA Supply Improvement",
        1.0, 5.0, 1.0, 0.1
    )

    engineered = run_cofactor_model(

        substrate,

        fcs_capacity,

        ech_capacity,

        atp_supply * atp_multiplier,

        coa_supply * coa_multiplier
    )

    if engineered is None:

        st.error("Engineered simulation failed.")
        return

    baseline_flux = result["Vanillin Flux"]

    engineered_flux = engineered["Vanillin Flux"]

    improvement = (

        (engineered_flux - baseline_flux)

        / baseline_flux * 100

        if baseline_flux > 0

        else None
    )

    m1, m2, m3 = st.columns(3)

    m1.metric(
        "Baseline Flux",
        f"{baseline_flux:.2f}"
    )

    m2.metric(
        "Engineered Flux",
        f"{engineered_flux:.2f}"
    )

    m3.metric(
        "Flux Improvement",

        f"{improvement:.2f}%"

        if improvement is not None

        else "Undefined"
    )

    comparison = pd.DataFrame({

        "Scenario": [
            "Baseline",
            "Energy Engineering"
        ],

        "Vanillin Flux": [
            baseline_flux,
            engineered_flux
        ],

        "ATP Supply": [
            atp_supply,
            atp_supply * atp_multiplier
        ],

        "CoA Supply": [
            coa_supply,
            coa_supply * coa_multiplier
        ]
    })

    fig3 = px.bar(

        comparison,

        x="Scenario",

        y="Vanillin Flux",

        color="Scenario",

        text_auto=".2f",

        template="plotly_dark",

        title="Baseline vs Energy Engineering",

        color_discrete_sequence=[
            "#38BDF8",
            "#A78BFA"
        ]
    )

    fig3.update_layout(showlegend=False)

    st.plotly_chart(
        fig3,
        use_container_width=True
    )


    # ======================================
    # RECOMMENDATIONS
    # ======================================

    st.subheader("💡 Model-Based Recommendations")

    if "ATP Supply" in limiting_factors:

        st.write(
            "• Investigate ATP regeneration and "
            "cellular energy metabolism."
        )

    if "CoA Supply" in limiting_factors:

        st.write(
            "• Investigate CoA biosynthesis, "
            "availability and recycling."
        )

    if "FCS Capacity" in limiting_factors:

        st.write(
            "• Investigate FCS reaction capacity "
            "and gene expression."
        )

    if "ECH Capacity" in limiting_factors:

        st.write(
            "• Investigate ECH reaction capacity "
            "and enzyme activity."
        )

    if "Substrate Supply" in limiting_factors:

        st.write(
            "• Investigate substrate availability "
            "and controlled feeding."
        )

    if engineered_flux > baseline_flux:

        st.success(
            "Increasing the assumed energy or "
            "cofactor supply improves vanillin "
            "flux in this model."
        )

    else:

        st.info(
            "Increasing energy supply alone does "
            "not improve flux under these constraints."
        )


    # ======================================
    # EXPORT RESULTS
    # ======================================

    st.divider()

    st.subheader("📥 Export Simulation Results")

    comparison["Substrate Supply"] = substrate

    comparison["FCS Capacity"] = fcs_capacity

    comparison["ECH Capacity"] = ech_capacity

    comparison["ATP Consumption"] = [
        result["ATP Consumption"],
        engineered["ATP Consumption"]
    ]

    comparison["CoA Supply Flux"] = [
        result["CoA Supply Flux"],
        engineered["CoA Supply Flux"]
    ]

    st.dataframe(
        comparison,
        use_container_width=True
    )

    st.download_button(

        "Download Cofactor Analysis",

        comparison.to_csv(index=False),

        "cofactor_analysis.csv",

        "text/csv"
    )

    st.download_button(

        "Download ATP Sensitivity Results",

        sensitivity_data.to_csv(index=False),

        "atp_sensitivity.csv",

        "text/csv"
    )

    st.caption(
        "This simplified FBA model includes ATP "
        "consumption and net CoA supply constraints. "
        "It does not explicitly model ATP regeneration, "
        "CoA recycling, biomass formation, cellular "
        "maintenance or complete charge and proton "
        "balance. Results are theoretical and require "
        "experimental validation."
    )
