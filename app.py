

# ==========================================
# ATP AND COFACTOR ANALYSIS
# ==========================================

elif st.session_state.page == "cofactor":

    if st.button(
        "← Back to Homepage",
        key="cofactor_back"
    ):
        st.session_state.page = "home"
        st.rerun()

    st.divider()
    show_cofactor_analysis()
