import psycopg2
import streamlit as st

def conectar():
    return psycopg2.connect(
        host=st.secrets["database"]["host"],
        port=st.secrets["database"]["port"],
        database=st.secrets["database"]["name"],
        user=st.secrets["database"]["user"],
        password=st.secrets["database"]["password"],
        sslmode="require"
    )