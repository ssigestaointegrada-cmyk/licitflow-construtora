import streamlit as st
import pandas as pd
from groq import Groq
import io, os, re
from docx import Document
import PyPDF2
import plotly.express as px

# --- CONFIGURAÇÃO DE ACESSO E RAIZ ---
RAIZ_GERAL = "Gestao_Construtoras"
if not os.path.exists(RAIZ_GERAL):
    os.makedirs(RAIZ_GERAL)

# --- INICIALIZAÇÃO DA SESSÃO ---
if 'autenticado_biz' not in st.session_state:
    st.session_state['autenticado_biz'] = False
if 'memoria' not in st.session_state:
    st.session_state.memoria = {k: "" for k in ["Edital", "TR", "Planilha", "Parecer", "Plano", "Memorial", "Proposta", "Checklist_Auto"]}

# --- CONFIGURAÇÃO IA ---
GROQ_API_KEY = st.secrets.get("GROQ_API_KEY") or os.getenv("GROQ_API_KEY")
client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

# --- FUNÇÕES TÉCNICAS (AJUSTADAS) ---
def extrair_texto_pdf(arquivo):
    if arquivo is None: return ""
    try:
        pdf_reader = PyPDF2.PdfReader(arquivo)
        return "".join([p.extract_text() for p in pdf_reader.pages[:40] if p.extract_text()])
    except: return "Erro na leitura."

def main():
    st.set_page_config(page_title="SSI LicitFlow v30.0", layout="wide")

    # 1. TELA DE LOGIN (CHAVE DE ACESSO)
    if not st.session_state['autenticado_biz']:
        st.header("🏗️ SSI LicitFlow - Acesso Restrito")
        chave = st.text_input("Digite sua Chave de Construtora:", type="password")
        if st.button("Acessar Painel"):
            if chave.strip():
                st.session_state['id_empresa'] = chave.upper().strip()
                st.session_state['autenticado_biz'] = True
                st.rerun()
        return

    # 2. DEFINIÇÃO DE CAMINHOS ISOLADOS
    ID_EMP = st.session_state['id_empresa']
    PATH_EMPRESA = os.path.join(RAIZ_GERAL, ID_EMP)
    os.makedirs(PATH_EMPRESA, exist_ok=True)

    # 3. SIDEBAR E PERSONALIZAÇÃO
    with st.sidebar:
        st.header("🎨 Identidade")
        nome_empresa = st.text_input("Razão Social:", value=f"CONSTRUTORA {ID_EMP}")
        logo_upload = st.file_uploader("Trocar Logo (PNG/JPG):", type=["png", "jpg"])
        
        st.divider()
        if logo_upload: st.image(logo_upload, width=150)
        else: st.title("🏗️")
        
        st.subheader(nome_empresa)
        menu = st.radio("Módulos:", ["1. Fase Preparatória", "2. Fase Comercial", "3. Gestão Administrativa", "4. Inteligência de Preços", "5. Execução/Medição", "6. Diario de Obra"])
        
        if st.button("🚪 Sair"):
            st.session_state['autenticado_biz'] = False
            st.rerun()

    def aplicar_cabecalho():
        c1, c2 = st.columns([1, 4])
        with c1:
            if logo_upload: st.image(logo_upload, width=100)
            else: st.title("🏗️")
        with c2:
            st.subheader(nome_empresa)
            st.caption(f"LicitFlow CE | {st.session_state.get('nome_obra_input', 'Nova Obra')}")
        st.divider()

    # --- MÓDULO 1: FASE PREPARATÓRIA ---
    if menu == "1. Fase Preparatória":
        aplicar_cabecalho()
        st.title("🔍 Auditoria e Repositório")
        
        col1, col2 = st.columns(2)
        nome_obra = col1.text_input("Nome da Obra", key="nome_obra_input")
        num_lic = col2.text_input("Nº da Licitação", key="num_lic_input")

        if nome_obra and num_lic:
            slug = f"{nome_obra.replace(' ', '_')}_{num_lic.replace('/', '-')}"
            pasta_obra = os.path.join(PATH_EMPRESA, slug)
            os.makedirs(pasta_obra, exist_ok=True)
            st.session_state['pasta_ativa'] = pasta_obra
        
        st.subheader("📤 Arquivamento de Documentos")
        ups = st.file_uploader("Arraste Editais, TRs e Planilhas (PDF/Excel)", accept_multiple_files=True)
        
        if st.button("💾 Salvar na Nuvem") and 'pasta_ativa' in st.session_state:
            for arq in ups:
                with open(os.path.join(st.session_state['pasta_ativa'], arq.name), "wb") as f:
                    f.write(arq.getbuffer())
            st.success("Documentos protegidos com sucesso!")

    # --- MÓDULO 5: EXECUÇÃO/MEDIÇÃO (AJUSTADO PARA SALVAR NA PASTA CERTA) ---
    elif menu == "5. Execução/Medição":
        aplicar_cabecalho()
        st.title("🏗️ Medição de Obra")
        
        if 'pasta_ativa' not in st.session_state:
            st.warning("⚠️ Selecione uma obra no Módulo 1 primeiro.")
        else:
            p_obra = st.session_state['pasta_ativa']
            p_med = os.path.join(p_obra, "Medicoes")
            os.makedirs(p_med, exist_ok=True)

            # Exemplo simplificado de tabela de medição
            df_med = st.data_editor(pd.DataFrame({'Item': ['Serviço A'], 'Total (R$)': [1000.0], 'Exec (%)': [0.0]}))
            
            if st.button("💾 Finalizar Medição"):
                data_str = pd.Timestamp.now().strftime("%Y-%m-%d_%H-%M")
                nome_arq = f"Medicao_{data_str}.xlsx"
                caminho_final = os.path.join(p_med, nome_arq)
                
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    df_med.to_excel(writer, index=False)
                
                with open(caminho_final, "wb") as f:
                    f.write(output.getvalue())
                
                st.success(f"Medição arquivada em: {caminho_final}")
                st.download_button("📥 Baixar Agora", output.getvalue(), nome_arq)

    # --- (Outros módulos seguem a mesma lógica de usar st.session_state['pasta_ativa']) ---

if __name__ == "__main__":
    main()
