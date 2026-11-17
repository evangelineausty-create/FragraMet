
import streamlit as st
import pandas as pd
from cobra import Model, Reaction, Metabolite


def run_optimization(substrate_supply, fcs_capacity, ech_capacity):
    # Simplified pathway model
    model = Model("FragraMet_Optimization")

    ferulic = Metabolite("ferulic_c")
    feruloyl_coa = Metabolite("feruloyl_coa_c")
    vanillin = Metabolite("vanillin_c")

    supply = Reaction("FERULIC_SUPPLY")
    supply.lower_bound = 0
    supply.upper_bound = substrate_supply
    supply.add_metabolites({ferulic: 1})

    fcs = Reaction("FCS")
    fcs.lower_bound = 0
    fcs.upper_bound = fcs_capacity
    fcs.add_metabolites({
        ferulic: -1,
        feruloyl_coa: 1
    })

    ech = Reaction("ECH")
    ech.lower_bound = 0
    ech.upper_bound = ech_capacity
    ech.add_metabolites({
        feruloyl_coa: -1,
        vanillin: 1
    })

    export = Reaction("VANILLIN_EXPORT")
    export.lower_bound = 0
    export.upper_bound = 1000
    export.add_metabolites({vanillin: -1})

    model.add_reactions([supply, fcs, ech, export])
    model.objective = export

    solution = model.optimize()

    return solution


def show_production_optimization():
    st.title("Production Optimization")
    st.write(
        "Explore how substrate availability and enzyme "
        "reaction capacities influence predicted vanillin flux."
    )

    st.info(
        "This is a simplified constraint-based demonstration. "
        "Enzyme capacities are model flux limits, not measured "
        "enzyme activities or gene-expression levels."
    )

    st.subheader("Optimization Parameters")

    substrate = st.slider(
        "Ferulic Acid Supply",
        min_value=1,
        max_value=30,
        value=10
    )

    fcs_capacity = st.slider(
        "FCS Reaction Capacity",
        min_value=1,
        max_value=30,
        value=10
    )

    ech_capacity = st.slider(
        "ECH Reaction Capacity",
        min_value=1,
        max_value=30,
        value=10
    )

    if st.button("Run Production Optimization"):
        solution = run_optimization(
            substrate,
            fcs_capacity,
            ech_capacity
        )

        if solution.status == "optimal":
            st.success("Optimization completed successfully!")

            st.metric(
                "Maximum Predicted Vanillin Flux",
                f"{solution.objective_value:.2f}"
            )

            flux_table = pd.DataFrame({
                "Reaction": solution.fluxes.index,
                "Flux": solution.fluxes.values
            })

            st.subheader("Optimized Reaction Fluxes")
            st.dataframe(
                flux_table,
                hide_index=True,
                use_container_width=True
            )

            st.bar_chart(
                flux_table.set_index("Reaction")["Flux"]
            )

            limiting_value = min(
                substrate,
                fcs_capacity,
                ech_capacity
            )

            bottlenecks = [
                name
                for name, value in [
                    ("Ferulic Acid Supply", substrate),
                    ("FCS", fcs_capacity),
                    ("ECH", ech_capacity)
                ]
                if value == limiting_value
            ]

            st.subheader("Bottleneck Analysis")
            st.write(
                "Limiting constraint(s): "
                + ", ".join(bottlenecks)
            )

            st.caption(
                "These results describe a toy 1:1 pathway model. "
                "They are not experimentally validated production "
                "yields or predictions for a complete E. coli strain."
            )
        else:
            st.error(
                "Optimization could not find an optimal solution."
            )
