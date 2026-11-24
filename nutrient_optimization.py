import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px


def show_nutrient_optimization():

    st.title("🌱 Nutrient Optimization")

    st.markdown(
        "Compare carbon and nitrogen sources "
        "for microbial vanillin production."
    )

    st.info(
        "Nutrient comparison and experimental "
        "data analysis for fermentation planning."
    )

    st.subheader("⚙️ Nutrient Selection")

    carbon_sources = {
        "Glucose": 0.4000,
        "Glycerol": 0.3913,
        "Sucrose": 0.4211,
        "Fructose": 0.4000
    }

    nitrogen_sources = {
        "Ammonium sulphate": 0.2120,
        "Ammonium chloride": 0.2619,
        "Yeast extract": None,
        "Peptone": None
    }

    col1, col2 = st.columns(2)

    with col1:

        carbon = st.selectbox(
            "Carbon Source",
            list(carbon_sources.keys())
        )

        carbon_conc = st.slider(
            "Carbon Source Concentration (g/L)",
            1.0, 100.0, 20.0
        )

        carbon_cost = st.number_input(
            "Carbon Source Cost (INR/kg)",
            min_value=0.0,
            value=0.0
        )

    with col2:

        nitrogen = st.selectbox(
            "Nitrogen Source",
            list(nitrogen_sources.keys())
        )

        nitrogen_conc = st.slider(
            "Nitrogen Source Concentration (g/L)",
            0.1, 30.0, 5.0
        )

        nitrogen_cost = st.number_input(
            "Nitrogen Source Cost (INR/kg)",
            min_value=0.0,
            value=0.0
        )

    carbon_fraction = carbon_sources[carbon]
    nitrogen_fraction = nitrogen_sources[nitrogen]

    nitrogen_carbon_fraction = 0.0

    if nitrogen_fraction is None:

        st.warning(
            "Complex nutrients have variable "
            "elemental compositions. Enter values "
            "from the supplier specification."
        )

        nitrogen_fraction = st.number_input(
            "Nitrogen mass fraction (0 to 1)",
            min_value=0.001,
            max_value=1.0,
            value=0.10,
            format="%.3f"
        )

        nitrogen_carbon_fraction = st.number_input(
            "Carbon mass fraction of nitrogen source",
            min_value=0.0,
            max_value=1.0 - nitrogen_fraction,
            value=min(0.40, 1.0 - nitrogen_fraction),
            format="%.3f"
        )

    carbon_mass = (
        carbon_conc * carbon_fraction
        + nitrogen_conc * nitrogen_carbon_fraction
    )

    nitrogen_mass = nitrogen_conc * nitrogen_fraction

    cn_ratio = carbon_mass / nitrogen_mass

    total_cost = (
        carbon_conc * carbon_cost / 1000
        + nitrogen_conc * nitrogen_cost / 1000
    )

    st.divider()

    st.subheader("📊 Nutrient Composition Analysis")

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Elemental Carbon",
        f"{carbon_mass:.2f} g/L"
    )

    c2.metric(
        "Elemental Nitrogen",
        f"{nitrogen_mass:.2f} g/L"
    )

    c3.metric(
        "C:N Mass Ratio",
        f"{cn_ratio:.2f}:1"
    )

    st.metric(
        "Selected Nutrient Cost per Litre",
        f"INR {total_cost:.2f}"
    )

    composition = pd.DataFrame({
        "Element": ["Carbon", "Nitrogen"],
        "Concentration (g/L)": [
            carbon_mass,
            nitrogen_mass
        ]
    })

    fig = px.bar(
        composition,
        x="Element",
        y="Concentration (g/L)",
        color="Element",
        title="Elemental Nutrient Composition",
        template="plotly_dark",
        color_discrete_sequence=[
            "#A78BFA",
            "#38BDF8"
        ]
    )

    fig.update_layout(showlegend=False)

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    st.caption(
        "The C:N ratio includes only the selected "
        "nutrient sources. Ferulic acid and other "
        "medium components are excluded."
    )

    st.divider()

    st.subheader("🔬 Experimental Nutrient Comparison")

    st.write(
        "Enter measured vanillin production data "
        "to compare different nutrient combinations."
    )

    experimental_data = pd.DataFrame({
        "Carbon Source": [
            "Glucose",
            "Glycerol",
            "Sucrose",
            "Fructose"
        ],
        "Nitrogen Source": [
            "Yeast extract",
            "Peptone",
            "Ammonium sulphate",
            "Ammonium chloride"
        ],
        "Carbon Source (g/L)": [
            20.0, 20.0, 20.0, 20.0
        ],
        "Nitrogen Source (g/L)": [
            5.0, 5.0, 5.0, 5.0
        ],
        "Ferulic Acid (g/L)": [
            5.0, 5.0, 5.0, 5.0
        ],
        "Time (h)": [
            24.0, 24.0, 24.0, 24.0
        ],
        "Vanillin (g/L)": [
            np.nan, np.nan, np.nan, np.nan
        ]
    })

    edited_data = st.data_editor(
        experimental_data,
        num_rows="dynamic",
        use_container_width=True,
        key="nutrient_experimental_data"
    )

    valid_data = edited_data.dropna(
        subset=[
            "Vanillin (g/L)",
            "Ferulic Acid (g/L)",
            "Time (h)"
        ]
    ).copy()

    valid_data = valid_data[
        (valid_data["Vanillin (g/L)"] >= 0)
        & (valid_data["Ferulic Acid (g/L)"] > 0)
        & (valid_data["Time (h)"] > 0)
    ]

    if not valid_data.empty:

        valid_data["Nutrient Combination"] = (
            valid_data["Carbon Source"]
            + " + "
            + valid_data["Nitrogen Source"]
        )

        valid_data["Productivity (g/L/h)"] = (
            valid_data["Vanillin (g/L)"]
            / valid_data["Time (h)"]
        )

        valid_data["Product per Initial Substrate (g/g)"] = (
            valid_data["Vanillin (g/L)"]
            / valid_data["Ferulic Acid (g/L)"]
        )

        valid_data["Trial"] = [
            f"Trial {i + 1}"
            for i in range(len(valid_data))
        ]

        st.subheader("📈 Comparative Results")

        fig2 = px.bar(
            valid_data,
            x="Trial",
            y="Vanillin (g/L)",
            color="Nutrient Combination",
            title="Vanillin Production Comparison",
            template="plotly_dark"
        )

        st.plotly_chart(
            fig2,
            use_container_width=True
        )

        fig3 = px.bar(
            valid_data,
            x="Trial",
            y="Productivity (g/L/h)",
            color="Nutrient Combination",
            title="Volumetric Productivity Comparison",
            template="plotly_dark"
        )

        st.plotly_chart(
            fig3,
            use_container_width=True
        )

        best = valid_data.loc[
            valid_data["Vanillin (g/L)"].idxmax()
        ]

        st.subheader("💡 Best Observed Condition")

        st.success(
            f"Highest entered vanillin concentration: "
            f"{best['Nutrient Combination']}"
        )

        st.metric(
            "Highest Observed Vanillin Concentration",
            f"{best['Vanillin (g/L)']:.3f} g/L"
        )

        st.dataframe(
            valid_data,
            use_container_width=True
        )

        st.download_button(
            "Download Experimental Comparison",
            valid_data.to_csv(index=False),
            "nutrient_comparison.csv",
            "text/csv"
        )

    else:

        st.info(
            "Enter experimental vanillin concentrations "
            "in the table to generate comparative results."
        )

    st.divider()

    st.subheader("📥 Export Nutrient Formulation")

    formulation = pd.DataFrame({
        "Carbon Source": [carbon],
        "Nitrogen Source": [nitrogen],
        "Carbon Source (g/L)": [carbon_conc],
        "Nitrogen Source (g/L)": [nitrogen_conc],
        "Elemental Carbon (g/L)": [carbon_mass],
        "Elemental Nitrogen (g/L)": [nitrogen_mass],
        "C:N Mass Ratio": [cn_ratio],
        "Selected Nutrient Cost (INR/L)": [
            total_cost
        ]
    })

    st.dataframe(
        formulation,
        use_container_width=True
    )

    st.download_button(
        "Download Nutrient Formulation",
        formulation.to_csv(index=False),
        "nutrient_formulation.csv",
        "text/csv"
    )

    st.caption(
        "This module calculates nutrient composition "
        "and compares user-entered experimental data. "
        "It does not predict biological production "
        "from nutrient composition alone. "
        "Controlled experiments and replicates "
        "are required to establish optimal conditions."
    )
