from html import escape

import streamlit as st
from sqlalchemy import text

from backend.db import get_engine


RESET_DB_SUCCESS_KEY = "reset_db_success"
RESET_DB_SUCCESS_SEQUENCE_KEY = "reset_db_success_sequence"


def render_center_success_overlay(message: str, sequence: int) -> None:
    """Render a center-screen success popup that fades out after 3 seconds."""
    animation_name = f"resetSuccessFadeOut_{sequence}"
    overlay_class = f"reset-success-overlay-{sequence}"
    st.markdown(
        f"""
<style>
@keyframes {animation_name} {{
    0%, 85% {{
        opacity: 1;
        transform: translate(-50%, -50%) scale(1);
    }}
    100% {{
        opacity: 0;
        transform: translate(-50%, -50%) scale(0.98);
    }}
}}
.{overlay_class} {{
    position: fixed;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    z-index: 99999;
    padding: 0.95rem 1.25rem;
    border-radius: 0.75rem;
    background: #dc2626;
    color: #ffffff;
    font-weight: 600;
    box-shadow: 0 14px 30px rgba(0, 0, 0, 0.28);
    animation: {animation_name} 3s ease-in-out forwards;
    pointer-events: none;
}}
</style>
<div class="{overlay_class}">{escape(message)}</div>
        """,
        unsafe_allow_html=True,
    )


# Calls the sp_reset_database stored procedure, which resets the database to the initial configuration.
def render_reset_button(key: str) -> None:
    engine = get_engine()

    success_payload = st.session_state.pop(RESET_DB_SUCCESS_KEY, None)
    if success_payload:
        if isinstance(success_payload, dict):
            message = str(success_payload.get("message", "Database reset complete."))
            sequence = int(success_payload.get("sequence", 0))
        else:
            message = str(success_payload)
            sequence = 0
        render_center_success_overlay(message, sequence)

    # Hacky fix to make the button red.
    st.sidebar.markdown(
        """
<style>
section[data-testid="stSidebar"] div.stButton > button[kind="primary"] {
    background-color: #dc2626 !important;
    color: #ffffff !important;
    border: 1px solid #b91c1c !important;
}
section[data-testid="stSidebar"] div.stButton > button[kind="primary"]:hover {
    background-color: #b91c1c !important;
    color: #ffffff !important;
    border: 1px solid #991b1b !important;
}
section[data-testid="stSidebar"] div.stButton > button[kind="primary"]:focus {
    box-shadow: 0 0 0 0.2rem rgba(220, 38, 38, 0.35) !important;
}
</style>
        """,
        unsafe_allow_html=True,
    )

    if st.sidebar.button("Reset Database", key=key, type="primary"):
        with engine.begin() as conn:
            conn.execute(text("CALL sp_reset_database();"))
        sequence = int(st.session_state.get(RESET_DB_SUCCESS_SEQUENCE_KEY, 0)) + 1
        st.session_state[RESET_DB_SUCCESS_SEQUENCE_KEY] = sequence
        st.session_state[RESET_DB_SUCCESS_KEY] = {
            "message": "Database reset complete.",
            "sequence": sequence,
        }
        st.rerun()
