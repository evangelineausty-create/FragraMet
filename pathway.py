
import streamlit as st

def show_pathway():
    st.title("🧬 Vanillin Pathway Explorer")

    st.write(
        "Explore the proposed microbial conversion "
        "of ferulic acid into vanillin."
    )

    st.subheader("Interactive Metabolic Pathway")

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
            fontsize=15,
            margin=0.25
        ];

        edge [
            color="#A78BFA",
            fontcolor="#E2E8F0",
            fontsize=11
        ];

        A [label="Ferulic Acid"];
        B [label="Feruloyl-CoA"];
        C [label="Vanillin"];

        A -> B [label="Feruloyl-CoA Synthetase"];
        B -> C [label="Enoyl-CoA Hydratase/Aldolase"];
    }
    """)

    st.subheader("Pathway Information")

    st.write("**Microorganism:** Engineered E. coli")
    st.write("**Starting substrate:** Ferulic acid")
    st.write("**Target product:** Vanillin")

    st.caption(
        "Simplified literature-based pathway representation. "
        "This is not a validated FragraMet simulation."
    )

    st.divider()
    st.subheader("🔬 Enzyme Information Explorer")

    enzyme = st.selectbox(
        "Select an enzyme to explore:",
        [
            "Feruloyl-CoA Synthetase",
            "Enoyl-CoA Hydratase/Aldolase"
        ]
    )

    if enzyme == "Feruloyl-CoA Synthetase":
        st.write("**Function:** Activates ferulic acid by attaching Coenzyme A.")
        st.write("**Reaction:** Ferulic Acid → Feruloyl-CoA")
        st.write("**Associated gene:** fcs")

    elif enzyme == "Enoyl-CoA Hydratase/Aldolase":
        st.write("**Function:** Converts feruloyl-CoA into vanillin through hydration and cleavage.")
        st.write("**Reaction:** Feruloyl-CoA → Vanillin")
        st.write("**Associated gene:** ech")

    st.caption(
        "Gene associations are examples from reported microbial "
        "ferulic acid conversion pathways; they are not verified "
        "for a specific engineered E. coli strain."
    )
    st.caption(
        "Simplified literature-based pathway representation. "
        "This is not a validated FragraMet simulation."
    )


    