
import streamlit as st
import pandas as pd

GENES = [
    ["fcs", "Feruloyl-CoA synthetase",
     "Ferulic acid activation", "Production"],
    ["ech", "Enoyl-CoA hydratase/aldolase",
     "Vanillin formation", "Production"],
    ["vdh", "Vanillin dehydrogenase",
     "Vanillin to vanillic acid", "Degradation"],
    ["vanA", "Vanillate O-demethylase component",
     "Vanillate degradation", "Degradation"],
    ["vanB", "Vanillate O-demethylase component",
     "Electron transfer for demethylation", "Degradation"],
    ["aroZ", "3-Dehydroshikimate dehydratase",
     "Protocatechuate formation", "Alternative pathway"],
    ["comt", "O-Methyltransferase",
     "Methylation of aromatic precursors", "Alternative pathway"],
    ["car", "Carboxylic acid reductase",
     "Aromatic aldehyde formation", "Alternative pathway"]
]

def show_gene_database():

    st.title("🧬 Vanillin Gene Database")

    st.markdown(
        "Explore potential gene targets associated "
        "with microbial vanillin production and degradation."
    )

    df = pd.DataFrame(
        GENES,
        columns=["Gene", "Enzyme", "Function", "Category"]
    )

    c1, c2, c3 = st.columns(3)

    c1.metric("Gene Targets", len(df))
    c2.metric("Core Production Genes", 2)
    c3.metric("Functional Categories", 3)

    st.subheader("🔍 Search Gene Targets")

    search = st.text_input(
        "Search by gene, enzyme or function"
    )

    category = st.selectbox(
        "Select functional category",
        ["All", "Production", "Degradation",
         "Alternative pathway"]
    )

    filtered = df.copy()

    if category != "All":
        filtered = filtered[
            filtered["Category"] == category
        ]

    if search:
        filtered = filtered[
            filtered.astype(str).apply(
                lambda row: row.str.contains(
                    search, case=False, regex=False
                ).any(), axis=1
            )
        ]

    st.dataframe(
        filtered,
        use_container_width=True,
        hide_index=True
    )

    st.subheader("🎯 Potential Engineering Strategies")

    gene = st.selectbox(
        "Select a gene target", df["Gene"]
    )

    selected = df[df["Gene"] == gene].iloc[0]

    st.write("**Enzyme:**", selected["Enzyme"])
    st.write("**Function:**", selected["Function"])

    if selected["Category"] == "Production":
        st.success(
            "Potential strategy: Gene overexpression "
            "to increase pathway capacity."
        )

    elif selected["Category"] == "Degradation":
        st.warning(
            "Potential strategy: Investigate gene "
            "knockout or downregulation."
        )

    else:
        st.info(
            "Potential strategy: Explore alternative "
            "vanillin biosynthesis pathways."
        )

    st.download_button(
        "Download Gene Database",
        df.to_csv(index=False),
        "vanillin_gene_database.csv",
        "text/csv"
    )

    st.caption(
        "Preliminary candidate gene catalogue. "
        "Genes are from different biological pathways "
        "and may not coexist in one organism. "
        "Organism-specific identities, accession IDs "
        "and engineering effects require verification."
    )
