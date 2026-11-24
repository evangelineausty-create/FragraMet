import streamlit as st

from production_optimization import show_production_optimization
from pathway import show_pathway
from gene_engineering import show_gene_engineering
from flux_analysis import show_flux_analysis
from bottleneck_analysis import show_bottleneck_analysis
from gene_database import show_gene_database
from virtual_engineering import show_virtual_engineering
from fermentation_optimization import show_fermentation_optimization
from nutrient_optimization import show_nutrient_optimization
from toxicity_analysis import show_toxicity_analysis
from cofactor_analysis import show_cofactor_analysis
from microbial_growth import show_microbial_growth


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


/* BUTTON STYLING */

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


/* METRIC VISIBILITY */

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


/* SLIDER VISIBILITY */

div[data-testid="stSlider"] label,
div[data-testid="stSlider"] label *,
div[data-testid="stSlider"] p {
    color: #F4F0FF !important;
}

div[data-testid="stSlider"] {
    color: #E8E4FF !important;
}


/* GENERAL TEXT AND TABLES */

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


/* NOTIFICATION BOXES */

div[data-testid="stAlert"] {
    background: #252044 !important;
    border: 1px solid #8B5CF6 !important;
    border-radius: 12px !important;
    color: #F5F0FF !important;
}

div[data-testid="stAlert"]
[data-baseweb="notification"] {
    background: #252044 !important;
    border-radius: 12px !important;
    color: #F5F0FF !important;
}

div[data-testid="stAlert"]
[data-testid="stMarkdownContainer"],
div[data-testid="stAlert"] p,
div[data-testid="stAlert"] span,
div[data-testid="stAlert"] div,
div[data-testid="stAlert"] svg {
    color: #F5F0FF !important;
    fill: currentColor;
}

[data-baseweb="notification"] {
    background-color: #252044 !important;
    color: #F5F0FF !important;
    border-radius: 12px !important;
}

[data-baseweb="notification"] p,
[data-baseweb="notification"] span {
    color: #F5F0FF !important;
}

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


    # ORIGINAL FEATURE CARDS

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


    # GENE DATABASE BUTTON

    if st.button(
        "🧬 Open Vanillin Gene Database",
        use_container_width=True
    ):
        st.session_state.page = "gene_database"
        st.rerun()


    # VIRTUAL GENE ENGINEERING BUTTON

    if st.button(
        "🧪 Open Virtual Gene Engineering",
        use_container_width=True
    ):
        st.session_state.page = "virtual_engineering"
        st.rerun()


    # FERMENTATION OPTIMIZATION BUTTON

    if st.button(
        "🧪 Open Fermentation Optimization",
        use_container_width=True
    ):
        st.session_state.page = "fermentation"
        st.rerun()


    # NUTRIENT OPTIMIZATION BUTTON

    if st.button(
        "🌱 Open Nutrient Optimization",
        use_container_width=True
    ):
        st.session_state.page = "nutrient"
        st.rerun()


    # TOXICITY ANALYSIS BUTTON

    if st.button(
        "🛡️ Open Vanillin Toxicity Analysis",
        use_container_width=True
    ):
        st.session_state.page = "toxicity"
        st.rerun()


    # ATP AND COFACTOR ANALYSIS BUTTON

    if st.button(
        "⚡ Open ATP and Cofactor Analysis",
        use_container_width=True
    ):
        st.session_state.page = "cofactor"
        st.rerun()


    # MICROBIAL GROWTH ANALYSIS BUTTON

    if st.button(
        "🦠 Open Microbial Growth Analysis",
        use_container_width=True
    ):
        st.session_state.page = "microbial_growth"
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


# ==========================================
# VANILLIN GENE DATABASE
# ==========================================

elif st.session_state.page == "gene_database":

    if st.button(
        "← Back to Homepage",
        key="database_back"
    ):
        st.session_state.page = "home"
        st.rerun()

    st.divider()
    show_gene_database()


# ==========================================
# VIRTUAL GENE ENGINEERING
# ==========================================

elif st.session_state.page == "virtual_engineering":

    if st.button(
        "← Back to Homepage",
        key="virtual_engineering_back"
    ):
        st.session_state.page = "home"
        st.rerun()

    st.divider()
    show_virtual_engineering()


# ==========================================
# FERMENTATION OPTIMIZATION
# ==========================================

elif st.session_state.page == "fermentation":

    if st.button(
        "← Back to Homepage",
        key="fermentation_back"
    ):
        st.session_state.page = "home"
        st.rerun()

    st.divider()
    show_fermentation_optimization()


# ==========================================
# NUTRIENT OPTIMIZATION
# ==========================================

elif st.session_state.page == "nutrient":

    if st.button(
        "← Back to Homepage",
        key="nutrient_back"
    ):
        st.session_state.page = "home"
        st.rerun()

    st.divider()
    show_nutrient_optimization()


# ==========================================
# VANILLIN TOXICITY ANALYSIS
# ==========================================

elif st.session_state.page == "toxicity":

    if st.button(
        "← Back to Homepage",
        key="toxicity_back"
    ):
        st.session_state.page = "home"
        st.rerun()

    st.divider()
    show_toxicity_analysis()


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


# ==========================================
# MICROBIAL GROWTH ANALYSIS
# ==========================================

elif st.session_state.page == "microbial_growth":

    if st.button(
        "← Back to Homepage",
        key="microbial_growth_back"
    ):
        st.session_state.page = "home"
        st.rerun()

    st.divider()
    show_microbial_growth()
