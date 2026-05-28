import streamlit as st


def apply_base_theme() -> None:
    """Apply a consistent app-wide visual theme."""
    st.markdown(
        """
<style>
    .stApp {
        background: linear-gradient(135deg, #0f0f1a 0%, #1a1a2e 50%, #16213e 100%);
    }
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%);
        border-right: 1px solid #2d2d4e;
    }
    [data-testid="metric-container"] {
        background: linear-gradient(135deg, #1e1e3a, #2d2d4e);
        border: 1px solid #3d3d6e;
        border-radius: 12px;
        padding: 16px;
    }
    .stButton > button {
        border-radius: 12px !important;
        font-weight: 600 !important;
        transition: all 0.2s !important;
    }
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 24px rgba(108, 99, 255, 0.35) !important;
    }
    footer {
        visibility: hidden;
    }
    @media (max-width: 768px) {
        .block-container {
            padding-top: 1rem;
            padding-left: 1rem;
            padding-right: 1rem;
            max-width: 100% !important;
        }
        [data-testid="stSidebar"] {
            border-right: none;
            border-bottom: 1px solid #2d2d4e;
        }
        h1 {
            font-size: 1.8rem !important;
        }
        h2 {
            font-size: 1.4rem !important;
        }
    }
</style>
        """,
        unsafe_allow_html=True,
    )
