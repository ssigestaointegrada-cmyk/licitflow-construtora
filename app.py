import streamlit as st
import pandas as pd
from groq import Groq
import io, os, re
from docx import Document
import PyPDF2
import plotly.express as px # Adicionado para garantir os gráficos

# --- CONFIGURAÇÃO ---
# No Streamlit Cloud, adicione a chave em Settings -> Secrets
GROQ_API_KEY = st.secrets.get("GROQ_API_KEY") or os.getenv("GROQ_API_KEY")
client = Groq(api_key=GROQ_API_KEY)

# --- DIRETÓRIOS BASE (Caminhos Relativos para Nuvem) ---
RAIZ_DOCS = "documentos_licitacao"
if not os.path.exists(RAIZ_DOCS):
    os.makedirs(RAIZ_DOCS)

# --- FUNÇÕES TÉCNICAS ---
def extrair_texto_pdf(arquivo):
    if arquivo is None: return ""
    try:
        pdf_reader = PyPDF2.PdfReader(arquivo)
        texto = "".join([p.extract_text() for p in pdf_reader.pages[:40] if p.extract_text()])
        return texto
    except: return "Erro na leitura."

def aplicar_cabecalho_ssi():
    col_logo, col_texto = st.columns([1, 4])
    with col_logo:
        # Recomendo subir a imagem logo_ssi.png para a raiz do seu GitHub
        if os.path.exists("logo_ssi.png"):
            st.image("logo_ssi.png", width=120)
        else:
            st.title("🏗️")
    with col_texto:
        st.subheader("SSI ENGENHARIA & CONSULTORIA")
        obra_nome = st.session_state.get('nome_obra_input', 'Gestão de Obras e Licitações')
        st.caption(f"LicitFlow CE | Unidade: {obra_nome}")
    st.divider()

# --- INTERFACE ---
st.set_page_config(page_title="SSI LicitFlow v30.0", layout="wide")

if 'memoria' not in st.session_state:
    st.session_state.memoria = {k: "" for k in ["Edital", "TR", "Planilha", "Parecer", "Plano", "Memorial", "Proposta", "Checklist_Auto"]}

with st.sidebar:
    if os.path.exists("logo_ssi.png"):
        st.image("logo_ssi.png", width=150)
    menu = st.radio("Módulos:", ["1. Fase Preparatória", "2. Fase Comercial", "3. Gestão Administrativa", "4. Inteligência de Preços", "5. Execução/Medição", "6. Diario de Obra"])
    if st.button("🗑️ Limpar Tudo"):
        st.session_state.memoria = {k: "" for k in st.session_state.memoria}
        if 'df_crono' in st.session_state: del st.session_state.df_crono
        st.rerun()

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
