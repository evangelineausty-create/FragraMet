
import streamlit as st

from production_optimization import show_production_optimization
from pathway import show_pathway
from gene_engineering import show_gene_engineering
from flux_analysis import show_flux_analysis
from bottleneck_analysis import show_bottleneck_analysis


# ==========================================
# PAGE SETTINGS
# ==========================================

st.set_page_config(
    page_title="AUSFEL BioSystems | FragraMet",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# ==========================================
# WEBSITE STYLING
# ==========================================

st.markdown("""
<style>

/* ==========================================
   ORIGINAL FRAGRAMET THEME
   ========================================== */

.stApp {
    background: linear-gradient(
        135deg,
        #0B1020,
        #151C38,
        #10172D
    );
    color: #F4F5FF;
}

.block-container {
    max-width: 1150px;
    padding-top: 2rem;
}

.brand {
    font-size: 26px;
    font-weight: 800;
    color: #C4B5FD;
    letter-spacing: 1px;
    margin-bottom: 30px;
}

.hero {
    background: linear-gradient(
        120deg,
        #28204F,
        #12324B
    );
    padding: 65px 30px;
    border-radius: 25px;
    text-align: center;
    border: 1px solid #6554A0;
    margin-bottom: 35px;
}

.hero h1 {
    color: #FFFFFF !important;
    font-size: 65px;
    font-weight: 800;
    margin: 15px 0;
}

.hero h3 {
    color: #C4B5FD !important;
    font-size: 25px;
}

.hero p {
    color: #E2E8F0;
    font-size: 18px;
}

.section-title {
    color: #FFFFFF;
    font-size: 30px;
    font-weight: 700;
    margin-bottom: 20px;
}

.feature {
    background: #1C2540;
    padding: 28px;
    border-radius: 18px;
    border: 1px solid #384568;
    min-height: 165px;
    color: #E2E8F0;
}

.feature h3 {
    color: #B8A5FF;
    font-size: 22px;
    margin-top: 0;
}

.feature p {
    color: #E2E8F0;
    font-size: 16px;
}

.footer {
    text-align: center;
    color: #B9C5DD;
    padding: 35px 0;
    font-size: 16px;
}

.footer b {
    color: #C4B5FD;
}

.footer-symbol {
    font-size: 16px;
    margin-top: 10px;
    opacity: 0.85;
}

/* ==========================================
   BUTTON STYLING
   ========================================== */

div.stButton > button {
    background: linear-gradient(
        90deg,
        #6750A4,
        #4338CA
    );
    color: #FFFFFF !important;
    border: 1px solid #A78BFA;
    border-radius: 12px;
    padding: 12px 24px;
    font-weight: 600;
}

div.stButton > button:hover {
    background: #7C3AED;
    color: #FFFFFF !important;
    border-color: #C4B5FD;
}

/* ==========================================
   METRIC VISIBILITY
   ========================================== */

div[data-testid="stMetric"] {
    background: #1C2540;
    border: 1px solid #384568;
    border-radius: 14px;
    padding: 16px;
}

div[data-testid="stMetricValue"],
div[data-testid="stMetricValue"] * {
    color: #D8C5FF !important;
    opacity: 1 !important;
}

div[data-testid="stMetricLabel"],
div[data-testid="stMetricLabel"] * {
    color: #E8E4FF !important;
    opacity: 1 !important;
}

/* ==========================================
   SLIDER VISIBILITY
   ========================================== */

div[data-testid="stSlider"] label,
div[data-testid="stSlider"] label *,
div[data-testid="stSlider"] p {
    color: #F4F0FF !important;
}

div[data-testid="stSlider"] {
    color: #E8E4FF !important;
}

/* ==========================================
   GENERAL TEXT AND TABLES
   ========================================== */

div[data-testid="stMarkdownContainer"] h1,
div[data-testid="stMarkdownContainer"] h2,
div[data-testid="stMarkdownContainer"] h3 {
    color: #F4F0FF;
}

div[data-testid="stMarkdownContainer"] p {
    color: #E2E8F0;
}

div[data-testid="stDataFrame"] {
    border: 1px solid #384568;
    border-radius: 12px;
    overflow: hidden;
}

hr {
    border-color: #384568 !important;
}

div[data-testid="stCaptionContainer"],
div[data-testid="stCaptionContainer"] * {
    color: #B9C5DD !important;
}

/* ==========================================
   FIX: ALL STREAMLIT NOTIFICATION BOXES
   ========================================== */

/* Outer alert container */

div[data-testid="stAlert"] {
    background: #252044 !important;
    border: 1px solid #8B5CF6 !important;
    border-radius: 12px !important;
    color: #F5F0FF !important;
}

/* Inner BaseWeb notification */

div[data-testid="stAlert"]
[data-baseweb="notification"] {
    background: #252044 !important;
    border-radius: 12px !important;
    color: #F5F0FF !important;
}

/* Notification content */

div[data-testid="stAlert"]
[data-testid="stMarkdownContainer"],
div[data-testid="stAlert"] p,
div[data-testid="stAlert"] span,
div[data-testid="stAlert"] div,
div[data-testid="stAlert"] svg {
    color: #F5F0FF !important;
    fill: currentColor;
}

/* Streamlit version compatibility */

[data-baseweb="notification"] {
    background-color: #252044 !important;
    color: #F5F0FF !important;
    border-radius: 12px !important;
}

[data-baseweb="notification"] p,
[data-baseweb="notification"] span {
    color: #F5F0FF !important;
}

/* ==========================================
   END OF STYLING
   ========================================== */

</style>
""", unsafe_allow_html=True)


# ==========================================
# NAVIGATION STATE
# ==========================================

if "page" not in st.session_state:
    st.session_state.page = "home"


# ==========================================
# HOMEPAGE
# ==========================================

if st.session_state.page == "home":

    st.markdown("""
<div class="brand">AUSFEL BioSystems</div>
""", unsafe_allow_html=True)

    st.markdown("""
<div class="hero">
<h1>FragraMet</h1>
<h3>In-Silico Metabolic Pathway Engineering</h3>
<p>
Engineering Microbial Pathways for
Sustainable Vanillin Production
</p>
</div>
""", unsafe_allow_html=True)

    st.markdown("""
<div class="section-title">
Explore Our Research Platform
</div>
""", unsafe_allow_html=True)

    # ======================================
    # FEATURE CARDS
    # ======================================

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
<div class="feature">
<h3>🧬 Pathway Explorer</h3>
<p>
Visualize microbial vanillin
biosynthesis pathways.
</p>
</div>
""", unsafe_allow_html=True)

    with col2:
        st.markdown("""
<div class="feature">
<h3>🔬 Gene Engineering</h3>
<p>
Investigate potential genetic
engineering strategies.
</p>
</div>
""", unsafe_allow_html=True)

    st.write("")

    col3, col4 = st.columns(2)

    with col3:
        st.markdown("""
<div class="feature">
<h3>📊 Metabolic Flux Analysis</h3>
<p>
Explore computational metabolic
flux simulations.
</p>
</div>
""", unsafe_allow_html=True)

    with col4:
        st.markdown("""
<div class="feature">
<h3>⚡ Production Optimization</h3>
<p>
Compare strategies for microbial
vanillin production.
</p>
</div>
""", unsafe_allow_html=True)

    st.write("")

    # ======================================
    # NAVIGATION BUTTONS
    # ======================================

    st.subheader("Research Modules")

    button_col1, button_col2 = st.columns(2)

    with button_col1:
        if st.button(
            "🧬 Open Pathway Explorer",
            use_container_width=True
        ):
            st.session_state.page = "pathway"
            st.rerun()

    with button_col2:
        if st.button(
            "🔬 Open Gene Engineering",
            use_container_width=True
        ):
            st.session_state.page = "gene"
            st.rerun()

    if st.button(
        "📊 Open Metabolic Flux Analysis",
        use_container_width=True
    ):
        st.session_state.page = "flux"
        st.rerun()

    if st.button(
        "⚡ Open Production Optimization",
        use_container_width=True
    ):
        st.session_state.page = "optimization"
        st.rerun()

    # ======================================
    # FOOTER
    # ======================================

    st.markdown("""
<div class="footer">
Developed by <b>Austy & Felicia</b><br>
AUSFEL BioSystems | FragraMet Research Platform
<div class="footer-symbol">🌻💛</div>
</div>
""", unsafe_allow_html=True)


# ==========================================
# PATHWAY EXPLORER
# ==========================================

elif st.session_state.page == "pathway":

    if st.button(
        "← Back to Homepage",
        key="pathway_back"
    ):
        st.session_state.page = "home"
        st.rerun()

    st.divider()
    show_pathway()


# ==========================================
# GENE ENGINEERING
# ==========================================

elif st.session_state.page == "gene":

    if st.button(
        "← Back to Homepage",
        key="gene_back"
    ):
        st.session_state.page = "home"
        st.rerun()

    st.divider()
    show_gene_engineering()


# ==========================================
# METABOLIC FLUX ANALYSIS
# ==========================================

elif st.session_state.page == "flux":

    if st.button(
        "← Back to Homepage",
        key="flux_back"
    ):
        st.session_state.page = "home"
        st.rerun()

    st.divider()
    show_flux_analysis()


# ==========================================
# PRODUCTION OPTIMIZATION
# ==========================================

elif st.session_state.page == "optimization":

    if st.button(
        "← Back to Homepage",
        key="optimization_back"
    ):
        st.session_state.page = "home"
        st.rerun()

    st.divider()
    show_production_optimization()

    st.divider()

    if st.button(
        "📈 Open Comparative Bottleneck Analysis",
        use_container_width=True
    ):
        st.session_state.page = "bottleneck"
        st.rerun()


# ==========================================
# COMPARATIVE BOTTLENECK ANALYSIS
# ==========================================

elif st.session_state.page == "bottleneck":

    back_col1, back_col2 = st.columns(2)

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
