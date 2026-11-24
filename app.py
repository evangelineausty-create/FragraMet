t.columns(2)

    with back_col1:
        if st.button(
            "← Back to Production Optimization",
            key="bottleneck_back_optimization",
            use_container_width=True
        ):
            st.session_state.page = "optimization"
            st.rerun()

    with back_col2:
        if st.button(
            "⌂ Back to Homepage",
            key="bottleneck_back_home",
            use_container_width=True
        ):
            st.session_state.page = "home"
            st.rerun()

    st.divider()
    show_bottleneck_analysis()

elif st.session_state.page == "gene_database":
    if st.button("← Back to Homepage", key="gene_database_back"):
        st.session_state.page = "home"
        st.rerun()
    st.divider()
    show_gene_database()
