
import streamlit as st
import pandas as pd

from production_optimization import run_optimization


# ==========================================
# COMPARATIVE BOTTLENECK ANALYSIS
# ==========================================

def show_bottleneck_analysis():

    st.title("📈 Comparative Bottleneck Analysis")

    st.write(
        "Compare how FCS and ECH reaction capacities "
        "influence the maximum predicted vanillin flux."
    )

    st.info(
        "This simulation uses a simplified "
        "constraint-based metabolic pathway model. "
        "Reaction capacities represent model flux "
        "limits, not measured enzyme activities."
    )

    # ======================================
    # SIMULATION PARAMETERS
    # ======================================

    st.subheader("Simulation Parameters")

    substrate_supply = st.slider(
        "Ferulic Acid Supply",
        min_value=1,
        max_value=30,
        value=20,
        key="comparison_substrate"
    )

    fixed_capacity = st.slider(
        "Fixed Enzyme Capacity",
        min_value=1,
        max_value=30,
        value=15,
        key="comparison_fixed"
    )

    # ======================================
    # RUN COMPARATIVE ANALYSIS
    # ======================================

    if st.button(
        "▶ Run Comparative Analysis",
        use_container_width=True
    ):

        results = []

        with st.spinner(
            "Running FCS and ECH capacity simulations..."
        ):

            for capacity in range(1, 31):

                # Vary FCS; keep ECH fixed
                fcs_solution = run_optimization(
                    substrate_supply,
                    capacity,
                    fixed_capacity
                )

                # Vary ECH; keep FCS fixed
                ech_solution = run_optimization(
                    substrate_supply,
                    fixed_capacity,
                    capacity
                )

                if (
                    fcs_solution.status == "optimal"
                    and ech_solution.status == "optimal"
                ):

                    results.append({
                        "Reaction Capacity": capacity,
                        "FCS Variation": float(
                            fcs_solution.objective_value
                        ),
                        "ECH Variation": float(
                            ech_solution.objective_value
                        )
                    })

        # ======================================
        # DISPLAY RESULTS
        # ======================================

        if results:

            df = pd.DataFrame(results)

            st.success(
                "Comparative analysis completed successfully!"
            )

            # ==================================
            # SUMMARY
            # ==================================

            st.subheader("Simulation Summary")

            col1, col2 = st.columns(2)

            with col1:
                st.metric(
                    "Ferulic Acid Supply",
                    substrate_supply
                )

            with col2:
                st.metric(
                    "Fixed Enzyme Capacity",
                    fixed_capacity
                )

            # ==================================
            # COMPARISON GRAPH
            # ==================================

            st.subheader("Vanillin Flux Comparison")

            st.line_chart(
                df.set_index("Reaction Capacity")[
                    ["FCS Variation", "ECH Variation"]
                ]
            )

            st.caption(
                "The curves may overlap because "
                "FCS and ECH are represented using "
                "identical 1:1 pathway constraints."
            )

            # ==================================
            # RESULTS TABLE
            # ==================================

            st.subheader("Simulation Results")

            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True
            )

            # ==================================
            # BOTTLENECK INTERPRETATION
            # ==================================

            st.subheader("Bottleneck Interpretation")

            maximum_flux = min(
                substrate_supply,
                fixed_capacity
            )

            st.metric(
                "Maximum Flux Under Fixed Constraints",
                f"{maximum_flux:.2f}"
            )

            st.write(
                "When the varied reaction capacity is "
                "below the other pathway constraints, "
                "it limits the maximum vanillin flux."
            )

            st.write(
                "Increasing its capacity improves "
                "the predicted flux until another "
                "constraint becomes limiting."
            )

            st.write(
                "Beyond that point, increasing the "
                "reaction capacity does not further "
                "increase predicted vanillin flux."
            )

            # ==================================
            # SCIENTIFIC LIMITATIONS
            # ==================================

            st.divider()

            st.caption(
                "Research limitation: This is a toy "
                "stoichiometric model implemented using "
                "COBRApy. It does not include competing "
                "pathways, biomass formation, cofactors, "
                "or experimentally validated enzyme "
                "capacities. Results represent theoretical "
                "model fluxes, not measured vanillin yields "
                "or validated E. coli predictions."
            )

        else:

            st.error(
                "No optimal solutions were obtained. "
                "Please check the model constraints."
            )
