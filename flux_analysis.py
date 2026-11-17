
import streamlit as st
import pandas as pd

from fba_model import run_fba


def show_flux_analysis():

    st.title("📊 Metabolic Flux Analysis")

    st.write(
        "Explore metabolic flux distributions "
        "using constraint-based Flux Balance Analysis (FBA)."
    )

    # =====================================
    # INTRODUCTION
    # =====================================

    st.subheader("Introduction to FBA")

    st.info(
        "Flux Balance Analysis uses a stoichiometric "
        "metabolic network, mass-balance constraints, "
        "and linear optimization to calculate "
        "feasible reaction fluxes."
    )

    # =====================================
    # METABOLIC PATHWAY
    # =====================================

    st.subheader("Simplified Metabolic Network")

    st.graphviz_chart("""
    digraph {
        rankdir=LR;
        bgcolor="transparent";

        node [
            shape=box,
            style="rounded,filled",
            fillcolor="#28204F",
            fontcolor="white",
            color="#A78BFA",
            fontsize=14,
            margin=0.25
        ];

        edge [
            color="#A78BFA",
            fontcolor="#E2E8F0",
            fontsize=12
        ];

        A [label="Ferulic Acid"];
        B [label="Feruloyl-CoA"];
        C [label="Vanillin"];

        A -> B [label="FCS (v1)"];
        B -> C [label="ECH (v2)"];
    }
    """)

    # =====================================
    # FBA INPUT
    # =====================================

    st.divider()

    st.subheader("⚙️ FBA Simulation Parameters")

    st.write(
        "Adjust the maximum ferulic acid supply "
        "and calculate the corresponding "
        "vanillin production flux."
    )

    substrate_uptake = st.slider(
        "Maximum Ferulic Acid Supply (model flux units)",
        min_value=1.0,
        max_value=30.0,
        value=10.0,
        step=1.0
    )

    # =====================================
    # RUN FBA
    # =====================================

    if st.button(
        "▶ Run Flux Balance Analysis",
        use_container_width=True
    ):

        with st.spinner("Optimizing metabolic fluxes..."):

            result = run_fba(
                substrate_uptake=substrate_uptake
            )

        if result["status"] == "optimal":

            st.success(
                "FBA Optimization Completed Successfully!"
            )

            # =================================
            # RESULTS
            # =================================

            st.subheader("FBA Results")

            col1, col2 = st.columns(2)

            with col1:
                st.metric(
                    "Ferulic Acid Supply Limit",
                    f"{substrate_uptake:.2f}"
                )

            with col2:
                st.metric(
                    "Maximum Vanillin Export Flux",
                    f"{result['vanillin_flux']:.2f}"
                )

            # =================================
            # FLUX TABLE
            # =================================

            st.subheader("Reaction Flux Distribution")

            flux_data = pd.DataFrame(
                [
                    {
                        "Reaction": reaction,
                        "Flux (model units)": flux
                    }
                    for reaction, flux
                    in result["reaction_fluxes"].items()
                ]
            )

            st.dataframe(
                flux_data,
                use_container_width=True,
                hide_index=True
            )

            # =================================
            # FLUX GRAPH
            # =================================

            st.subheader("Metabolic Flux Visualization")

            st.bar_chart(
                flux_data.set_index("Reaction")
                ["Flux (model units)"]
            )

            # =================================
            # INTERPRETATION
            # =================================

            st.subheader("Interpretation")

            st.write(
                "In this simplified model, the "
                "maximum vanillin export flux is "
                "determined by the available "
                "ferulic acid supply."
            )

            st.write(
                "Because all pathway reactions "
                "use simplified 1:1 stoichiometry, "
                "the optimized reaction fluxes "
                "are equal."
            )

        else:

            st.error(
                "FBA optimization did not produce "
                "an optimal solution."
            )

    # =====================================
    # SCIENTIFIC LIMITATIONS
    # =====================================

    st.divider()

    st.caption(
        "Research note: This is a simplified "
        "demonstration FBA model implemented "
        "using COBRApy. It does not include "
        "biomass formation, cofactors, "
        "competing reactions, or experimentally "
        "validated kinetic constraints. "
        "The results are illustrative model "
        "fluxes, not measured vanillin yields "
        "or validated E. coli production predictions."
    )
