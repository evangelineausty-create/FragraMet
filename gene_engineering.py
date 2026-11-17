
import streamlit as st


def show_gene_engineering():
    st.title("🔬 Gene Engineering Explorer")

    st.write(
        "Explore genes associated with microbial "
        "vanillin biosynthesis and their potential "
        "roles in metabolic engineering."
    )

    st.subheader("Gene Selection")

    gene = st.selectbox(
        "Select a gene to investigate:",
        ["fcs", "ech"]
    )

    if gene == "fcs":
        st.success("Selected Gene: fcs")

        st.write(
            "**Enzyme:** Feruloyl-CoA synthetase"
        )

        st.write(
            "**Function:** Activates ferulic acid "
            "by forming feruloyl-CoA."
        )

        st.write(
            "**Pathway role:** First step in the "
            "ferulic acid-to-vanillin pathway."
        )

        st.info(
            "Potential engineering strategy: "
            "Investigate whether increased fcs "
            "expression improves substrate conversion."
        )

    elif gene == "ech":
        st.success("Selected Gene: ech")

        st.write(
            "**Enzyme:** Enoyl-CoA hydratase/aldolase"
        )

        st.write(
            "**Function:** Catalyzes conversion of "
            "feruloyl-CoA toward vanillin."
        )

        st.write(
            "**Pathway role:** Vanillin formation."
        )

        st.info(
            "Potential engineering strategy: "
            "Investigate whether increased ech "
            "expression improves vanillin formation."
        )

    st.caption(
        "Educational, literature-informed gene "
        "exploration. These strategies are hypotheses, "
        "not experimentally verified improvements."
    )
