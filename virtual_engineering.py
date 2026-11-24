
import streamlit as st
import pandas as pd
from cobra import Model, Reaction, Metabolite


def simulate_engineering(substrate, fcs, ech, degradation):

    model = Model("FragraMet_Extended")

    fa = Metabolite("ferulic_acid_c", compartment="c")
    fc = Metabolite("feruloyl_coa_c", compartment="c")
    van = Metabolite("vanillin_c", compartment="c")
    va = Metabolite("vanillic_acid_c", compartment="c")

    supply = Reaction("SUBSTRATE")
    supply.bounds = (0, substrate)
    supply.add_metabolites({fa: 1})

    r1 = Reaction("FCS")
    r1.bounds = (0, fcs)
    r1.add_metabolites({fa: -1, fc: 1})
    r1.gene_reaction_rule = "fcs"

    r2 = Reaction("ECH")
    r2.bounds = (0, ech)
    r2.add_metabolites({fc: -1, van: 1})
    r2.gene_reaction_rule = "ech"

    r3 = Reaction("VDH")
    r3.bounds = (0, 1000)
    r3.add_metabolites({van: -1, va: 1})
    r3.gene_reaction_rule = "vdh"

    export = Reaction("VANILLIN_EXPORT")
    export.bounds = (0, 1000)
    export.add_metabolites({van: -1})

    waste = Reaction("VANILLIC_ACID_EXPORT")
    waste.bounds = (0, 1000)
    waste.add_metabolites({va: -1})

    model.add_reactions([
        supply, r1, r2, r3, export, waste
    ])

    model.add_cons_vars(
        model.problem.Constraint(
            r3.flux_expression
            - degradation * r2.flux_expression,
            lb=0,
            ub=0,
            name="assumed_degradation_fraction"
        )
    )

    model.objective = export

    solution = model.optimize()

    if solution.status != "optimal":
        return None

    return {
        "production": float(
            solution.fluxes["VANILLIN_EXPORT"]
        ),
        "degradation": float(
            solution.fluxes["VDH"]
        ),
        "fcs": float(solution.fluxes["FCS"]),
        "ech": float(solution.fluxes["ECH"])
    }


def show_virtual_engineering():

    st.title("Virtual Gene Engineering")

    st.markdown(
        "Simulate gene overexpression, knockout "
        "and competing metabolic pathways."
    )

    st.info(
        "This is a simplified constraint-based "
        "metabolic model for exploratory research."
    )

    st.subheader("Extended Metabolic Pathway")

    st.graphviz_chart("""
    digraph {
        rankdir=LR;
        node [shape=box, style="rounded,filled",
              fillcolor="#302653", fontcolor="white"];

        A [label="Ferulic Acid"];
        B [label="Feruloyl-CoA"];
        C [label="Vanillin", fillcolor="#176B50"];
        D [label="Vanillic Acid", fillcolor="#873F4B"];

        A -> B [label="FCS"];
        B -> C [label="ECH"];
        C -> D [label="VDH"];
    }
    """)

    st.subheader("Baseline Metabolic Conditions")

    c1, c2 = st.columns(2)

    with c1:

        substrate = st.slider(
            "Ferulic acid supply",
            1, 50, 20
        )

        fcs = st.slider(
            "Baseline FCS capacity",
            1, 30, 5
        )

    with c2:

        ech = st.slider(
            "Baseline ECH capacity",
            1, 30, 15
        )

        loss = st.slider(
            "Assumed vanillin degradation (%)",
            0, 90, 20
        )

    st.divider()

    st.subheader("Select Gene Modifications")

    fcs_fold = st.slider(
        "fcs overexpression capacity multiplier",
        1.0, 5.0, 2.0, 0.5
    )

    ech_fold = st.slider(
        "ech overexpression capacity multiplier",
        1.0, 5.0, 1.0, 0.5
    )

    knockout = st.checkbox(
        "Simulate vdh knockout"
    )

    baseline = simulate_engineering(
        substrate,
        fcs,
        ech,
        loss / 100
    )

    engineered = simulate_engineering(
        substrate,
        fcs * fcs_fold,
        ech * ech_fold,
        0 if knockout else loss / 100
    )

    if baseline is None or engineered is None:
        st.error("Optimization failed.")
        return

    normal = baseline["production"]
    modified = engineered["production"]

    improvement = (
        (modified - normal) / normal * 100
        if normal > 0 else 0
    )

    st.divider()

    st.subheader("Simulation Results")

    m1, m2, m3 = st.columns(3)

    m1.metric(
        "Baseline Vanillin Flux",
        f"{normal:.2f}"
    )

    m2.metric(
        "Engineered Vanillin Flux",
        f"{modified:.2f}"
    )

    m3.metric(
        "Simulated Improvement",
        f"{improvement:.1f}%"
    )

    comparison = pd.DataFrame({
        "Condition": [
            "Baseline", "Engineered"
        ],
        "Vanillin Production": [
            normal, modified
        ],
        "Vanillin Degradation": [
            baseline["degradation"],
            engineered["degradation"]
        ]
    })

    st.subheader("Production Comparison")

    st.bar_chart(
        comparison.set_index("Condition")
    )

    st.dataframe(
        comparison,
        hide_index=True,
        use_container_width=True
    )

    st.subheader("Smart Engineering Recommendations")

    capacities = {
        "Substrate supply": substrate,
        "FCS": fcs * fcs_fold,
        "ECH": ech * ech_fold
    }

    minimum = min(capacities.values())

    limiting = [
        name for name, value in capacities.items()
        if abs(value - minimum) < 0.000001
    ]

    st.write(
        "**Current limiting constraints:**",
        ", ".join(limiting)
    )

    if "FCS" in limiting:
        st.info(
            "Investigate further fcs overexpression."
        )

    if "ECH" in limiting:
        st.info(
            "Investigate further ech overexpression."
        )

    if "Substrate supply" in limiting:
        st.info(
            "Investigate increased precursor availability."
        )

    if not knockout and loss > 0:
        st.warning(
            "Investigate vdh downregulation or knockout "
            "to reduce assumed vanillin degradation."
        )

    if improvement > 0:
        st.success(
            "The selected engineering strategy "
            "improved simulated vanillin production."
        )

    else:
        st.warning(
            "The selected modifications did not "
            "improve simulated production."
        )

    st.download_button(
        "Download Simulation Results",
        comparison.to_csv(index=False),
        "virtual_engineering_results.csv",
        "text/csv"
    )

    st.caption(
        "All flux values are theoretical model units. "
        "Degradation fractions and capacity multipliers "
        "are user-defined assumptions. The model excludes "
        "biomass, cofactors and enzyme kinetics. "
        "Recommendations are rule-based and require "
        "organism-specific experimental validation."
    )
