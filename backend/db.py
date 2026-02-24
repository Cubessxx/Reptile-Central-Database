import streamlit as st
from sqlalchemy import create_engine


@st.cache_resource
def get_engine():
    mysql = st.secrets["mysql"]
    return create_engine(
        "mysql+pymysql://"
        f"{mysql['user']}:{mysql['password']}"
        f"@{mysql['host']}:{mysql.get('port', 3306)}"
        f"/{mysql['database']}"
    )
