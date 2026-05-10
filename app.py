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
        "TITULO",
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


def tela_catalogo():
    st.title("🎬 Catálogo TMDB")  # nova função inserida em 10/05/2026

    nome = st.text_input("Digite o nome do filme/série:")

    if st.button("🔎 Buscar catálogo"):

        if nome.strip() == "":
            st.warning("Digite um nome para pesquisar.")
            return

        conn = conectar()

        query = """
        SELECT 
            "NOME_NACIONAL",
            "NOME_INTERNACIONAL",
            "TIPO_VIDEO",
            "ANO_CADASTRO",
            "SINOPSE",
            "DIRETOR",
            "ELENCO",
            "AUDIO_ORIGINAL",
            "IMAGEM_URL"
        FROM captura_web.tb_catalogo_tmdb
        WHERE "NOME_NACIONAL" ILIKE %s
        ORDER BY "ANO_CADASTRO", "NOME_NACIONAL"
        """

        df = pd.read_sql(
            query,
            conn,
            params=[f"%{nome}%"]
        )

        conn.close()

        st.success(f"{len(df)} registros encontrados")

        # =============================
        # EXIBIR RESULTADOS
        # =============================
        for _, row in df.iterrows():

            with st.container(border=True):

                col1, col2 = st.columns([1, 3])

                # =============================
                # IMAGEM
                # =============================
                with col1:

                    if row["IMAGEM_URL"]:
                        try:
                            st.image(
                                row["IMAGEM_URL"],
                                use_container_width=True
                            )
                        except:
                            st.warning("Imagem não disponível")

                # =============================
                # DADOS
                # =============================
                with col2:

                    st.subheader(row["NOME_NACIONAL"])

                    if row["NOME_INTERNACIONAL"]:
                        st.caption(row["NOME_INTERNACIONAL"])

                    st.write(f"🎞️ Tipo: {row['TIPO_VIDEO']}")
                    st.write(f"📅 Ano: {row['ANO_CADASTRO']}")
                    st.write(f"🎤 Áudio Original: {row['AUDIO_ORIGINAL']}")

                    st.write(f"🎬 Diretor: {row['DIRETOR']}")

                    st.markdown("### 👥 Elenco")
                    st.write(row["ELENCO"])

                    st.markdown("### 📖 Sinopse")
                    st.write(row["SINOPSE"])




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
    pagina = st.sidebar.radio("Menu", ["Discos", "Busca", "Catálogo Interno"])

    if pagina == "Discos":
        tela_discos()

    elif pagina == "Busca":
        tela_busca()

    elif pagina == "Catálogo Interno":
        tela_catalogo()

# =============================
# MAIN
# =============================
if not st.session_state.logado:
    tela_login()
else:
    sistema()