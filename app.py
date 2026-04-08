import streamlit as st
import pandas as pd
from db import conectar
from auth import validar_login
from datetime import datetime, timedelta

st.set_page_config(page_title="Sistema de Busca de Arquivos", layout="wide")

# =============================
# SESSION
# =============================
if "logado" not in st.session_state:
    st.session_state.logado = False

if "usuario" not in st.session_state:
    st.session_state.usuario = None

if "login_time" not in st.session_state:
    st.session_state.login_time = None

# =============================
# TIMEOUT DE SESSÃO
# =============================
def verificar_timeout():
    if st.session_state.login_time:
        tempo_max = st.secrets["security"]["session_timeout_minutes"]
        limite = st.session_state.login_time + timedelta(minutes=tempo_max)

        if datetime.now() > limite:
            st.session_state.logado = False
            st.warning("Sessão expirada. Faça login novamente.")
            st.rerun()

# =============================
# LOGIN
# =============================
def tela_login():
    st.title("🔐 Login")

    usuario = st.text_input("Usuário")
    senha = st.text_input("Senha", type="password")

    if st.button("Entrar"):
        if validar_login(usuario, senha):
            st.session_state.logado = True
            st.session_state.usuario = usuario
            st.session_state.login_time = datetime.now()
            st.success("Login realizado!")
            st.rerun()
        else:
            st.error("Usuário ou senha inválidos")

# =============================
# DISCOS
# =============================
def tela_discos():
    st.title("📀 Consulta de Discos")

    if st.button("Carregar dados"):
        conn = conectar()
        df = pd.read_sql("SELECT * FROM captura_web.tb_disco;", conn)
        conn.close()

        st.dataframe(df, use_container_width=True)

# =============================
# BUSCA
# =============================
# def tela_busca():
#     st.title("🔍 Busca de Arquivos")
#
#     termo = st.text_input("Buscar por nome de arquivo:")
#
#     if st.button("Buscar"):
#         if termo.strip() == "":
#             st.warning("Digite algo.")
#             return
#
#         conn = conectar()
#
#         query = """
#         SELECT
#         "ID_CARGA_CAPTURA",
#         "NOME_DISCO",
#         "NOME_PASTA",
#         "NOME_ARQUIVO",
#         "DATA_GRAVACAO",
#         "TITULO",
#         "TAMANHO_ARQUIVO",
#         "DATA_ARQUIVO",
#         "TIPO_ARQUIVO"
#         FROM captura_web.tb_carga_captura
#         WHERE "CAMINHO_COMPLETO" ILIKE %s
#         ORDER BY "NOME_DISCO", "NOME_PASTA", "NOME_ARQUIVO";
#         """
#
#         df = pd.read_sql(query, conn, params=[f"%{termo}%"])
#         conn.close()
#
#         st.write(f"{len(df)} registros encontrados")
#         st.dataframe(df, use_container_width=True)

def tela_busca():
    st.title("🔍 Busca de Arquivos")

    termo = st.text_input("Buscar no caminho completo:")

    tipo = st.radio(
        "Tipo de arquivo:",
        ["Todos", "Vídeo", "Áudio"]
    )

    if st.button("Buscar"):
        if termo.strip() == "":
            st.warning("Digite algo.")
            return

        conn = conectar()

        # =============================
        # LISTAS DE TIPOS
        # =============================
        tipos_video = [
            'MP4','MKV','AVI','WMV','MOV','FLV','WEBM','MPG','MPEG','RMVB',
            'DIVX','XVID','TS','M2TS','ASF','3GP','3G2','F4V','RM','MXF',
            'AVCHD','MTS','OGM','NUT','AMV','SWF'
        ]

        tipos_audio = [
            'MP3','WAV','FLAC','AAC','M4A','OGG','WMA','ALAC','APE','AIFF',
            'AIF','DSD','DSF','DFF','MID','MIDI','RA','OPUS','AMR','3GA',
            'AC3','DTS','EAC3'
        ]

        # =============================
        # QUERY BASE
        # =============================
        query = """
        SELECT 
        "ID_CARGA_CAPTURA", 
        "NOME_DISCO", 
        "NOME_ARQUIVO",
        "TIPO_ARQUIVO",
        "TAMANHO_ARQUIVO",
        "DATA_ARQUIVO"
        FROM captura_web.tb_carga_captura
        WHERE "CAMINHO_COMPLETO" ILIKE %s
        """

        params = [f"%{termo}%"]

        # =============================
        # FILTRO POR TIPO
        # =============================
        if tipo == "Vídeo":
            query += ' AND "TIPO_ARQUIVO" = ANY(%s)'
            params.append(tipos_video)

        elif tipo == "Áudio":
            query += ' AND "TIPO_ARQUIVO" = ANY(%s)'
            params.append(tipos_audio)

        # =============================
        # ORDER BY
        # =============================
        query += """
        ORDER BY "NOME_DISCO", "NOME_PASTA", "NOME_ARQUIVO"
        """

        df = pd.read_sql(query, conn, params=params)
        conn.close()

        st.success(f"{len(df)} registros encontrados")
        st.dataframe(df, use_container_width=True)

# =============================
# SISTEMA
# =============================
def sistema():
    verificar_timeout()

    st.sidebar.title(f"👤 {st.session_state.usuario}")

    if st.sidebar.button("Logout"):
        st.session_state.logado = False
        st.rerun()

    # pagina = st.sidebar.radio("Menu", ["Discos", "Busca"])
    pagina = st.sidebar.radio("Menu", ["Busca", "Discos"])

    if pagina == "Discos":
        tela_discos()
    else:
        tela_busca()

# =============================
# MAIN
# =============================
if not st.session_state.logado:
    tela_login()
else:
    sistema()