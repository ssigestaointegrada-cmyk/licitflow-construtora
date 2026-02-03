import streamlit as st
import pandas as pd
from groq import Groq
import io, os, re
from docx import Document
import PyPDF2
import plotly.express as px

# --- CONFIGURAÇÃO DE ACESSO ---
if 'autenticado_biz' not in st.session_state:
    st.session_state['autenticado_biz'] = False

def main():
    # 1. TELA DE ACESSO (O "LOGIN" POR CONSTRUTORA)
    if not st.session_state['autenticado_biz']:
        st.set_page_config(page_title="Acesso SSI LicitFlow", layout="centered")
        st.header("🏗️ SSI LicitFlow - Portal da Construtora")
        chave = st.text_input("Digite sua Chave de Acesso (CNPJ ou Código):", type="password")
        if st.button("Entrar no Sistema"):
            if chave.strip() != "":
                st.session_state['id_empresa'] = chave.upper().strip()
                st.session_state['autenticado_biz'] = True
                st.rerun()
        return

    # 2. CONFIGURAÇÃO DE PASTA POR EMPRESA
    ID_EMPRESA = st.session_state['id_empresa']
    RAIZ_EMPRESAS = "Gestao_Construtoras"
    PATH_EMPRESA = os.path.join(RAIZ_EMPRESAS, ID_EMPRESA)
    if not os.path.exists(PATH_EMPRESA):
        os.makedirs(PATH_EMPRESA)

    st.set_page_config(page_title=f"SSI LicitFlow - {ID_EMPRESA}", layout="wide")

    # 3. SIDEBAR PERSONALIZÁVEL
    with st.sidebar:
        st.header("🎨 Identidade Visual")
        nome_empresa = st.text_input("Razão Social:", value=f"CONSTRUTORA {ID_EMPRESA}")
        logo_upload = st.file_uploader("Logo da Empresa (PNG/JPG):", type=["png", "jpg"])
        
        st.divider()
        if logo_upload:
            st.image(logo_upload, width=150)
        else:
            # Fallback para o seu logo original se estiver na pasta
            if os.path.exists("logo_ssi.png"):
                st.image("logo_ssi.png", width=150)
            else:
                st.title("🏗️")
        
        st.subheader(nome_empresa)
        st.caption(f"ID de Acesso: {ID_EMPRESA}")
        
        if st.button("🚪 Sair"):
            st.session_state['autenticado_biz'] = False
            st.rerun()
        
        st.divider()
        menu = st.radio("Módulos:", ["1. Fase Preparatória", "2. Fase Comercial", "3. Gestão Administrativa", "4. Inteligência de Preços", "5. Execução/Medição", "6. Diario de Obra"])

    # 4. APLICAR CABEÇALHO DINÂMICO NOS DOCUMENTOS
    def aplicar_cabecalho_dinamico():
        c1, c2 = st.columns([1, 4])
        with c1:
            if logo_upload: st.image(logo_upload, width=100)
            else: st.title("🏗️")
        with c2:
            st.subheader(nome_empresa)
            obra_atual = st.session_state.get('nome_obra_input', 'Nova Obra')
            st.caption(f"Sistema de Apoio a Licitações e Obras | {obra_atual}")
        st.divider()

    # --- AQUI SEGUE O RESTANTE DO SEU CÓDIGO (Fase Preparatória, etc.) ---
    # Substitua as chamadas de aplicar_cabecalho_ssi() por aplicar_cabecalho_dinamico()

# --- CONTEÚDO DOS MÓDULOS ---

if menu == "1. Fase Preparatória":
    aplicar_cabecalho_ssi()
    st.title("🔍 Fase Preparatória: Auditoria e Repositório")
    
    col_id1, col_id2 = st.columns(2)
    with col_id1:
        nome_obra = st.text_input("Nome da Obra / Objeto", value=st.session_state.get('nome_obra_input', ""), key="nome_obra_input")
    with col_id2:
        num_licitacao = st.text_input("Nº da Licitação", value=st.session_state.get('num_lic_input', ""), key="num_lic_input")

    # Definição de Pasta por Obra
    if nome_obra and num_licitacao:
        pasta_slug = f"{nome_obra.replace(' ', '_')}_{num_licitacao.replace('/', '-')}"
        pasta_obra = os.path.join(RAIZ_DOCS, pasta_slug)
        if not os.path.exists(pasta_obra): os.makedirs(pasta_obra)
        st.session_state['pasta_da_obra'] = pasta_obra # Salva para os outros módulos
    else:
        pasta_obra = None

    st.divider()
    
    # Uploads
    st.subheader("📤 Upload de Documentos Obrigatórios")
    u_edital = st.file_uploader("Editais / TRs (PDF)", type="pdf", accept_multiple_files=True)
    if st.button("💾 Arquivar Documentos"):
        if pasta_obra and u_edital:
            for arq in u_edital:
                with open(os.path.join(pasta_obra, arq.name), "wb") as f:
                    f.write(arq.getbuffer())
            st.success(f"Arquivado em {pasta_obra}")

# --- (Aqui você continua com o resto do seu código original) ---
# Apenas certifique-se de que onde houver caminhos de arquivos, use a variável 'pasta_obra'

