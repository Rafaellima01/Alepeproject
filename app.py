import streamlit as st
import requests
import xml.etree.ElementTree as ET
from datetime import datetime
import pandas as pd
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
import textwrap
from collections import Counter
import io
# ===================== CONFIGURAÇÕES =====================
st.set_page_config(page_title="Consulta Proposições ALEPE", layout="wide")
# Sua chave da API do Gemini
GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY", "SUA_CHAVE_AQUI") # Recomendado usar st.secrets
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash') # ou 'gemini-1.5-pro'
# Lista gigante de palavras-chave (mesma do original)
palavras_chave = [...] # ← Cole aqui TODAS as palavras do seu código original (vou deixar abreviada por espaço)
# ===================== CACHE DOS DADOS =====================
@st.cache_data(ttl=3600, show_spinner="Carregando proposições da ALEPE...")
def carregar_dados():
    ano = datetime.now().year
    url = f"https://dadosabertos.alepe.pe.gov.br/api/v1/proposicoes/projetos?ano={ano}"
    response = requests.get(url, timeout=20)
    response.raise_for_status()
    tree = ET.fromstring(response.text)
    proposicoes = []
    for elem in tree.findall('projeto'):
        prop = elem.attrib
        autores = [a.attrib.get('nome', '') for a in elem.findall('./autores/autor')]
        prop['autor'] = ', '.join(autores) if autores else ''
        proposicoes.append(prop)
    # Filtrar por palavras-chave
    def contem_palavra(ementa):
        if not ementa:
            return False
        ementa_lower = ementa.lower()
        return any(palavra.lower() in ementa_lower for palavra in palavras_chave)
    filtradas = [p for p in proposicoes if contem_palavra(p.get('ementa', ''))]
   
    # Ordenar por data mais recente
    def parse_date(d):
        try:
            return datetime.strptime(d, '%d/%m/%Y')
        except:
            return datetime.min
    filtradas.sort(key=lambda x: parse_date(x.get('dataPublicacao', '')), reverse=True)
    return filtradas[:900]
# ===================== CARREGAR DADOS =====================
with st.spinner("Carregando proposições da ALEPE..."):
    try:
        recentes_900 = carregar_dados()
    except Exception as e:
        st.error(f"Erro ao carregar dados da ALEPE: {e}")
        st.stop()
if not recentes_900:
    st.warning(f"Nenhuma proposição relevante encontrada em {datetime.now().year}")
    st.stop()
df = pd.DataFrame(recentes_900)
# Formatando ementa para melhor leitura
df['ementa'] = df['ementa'].apply(lambda x: '\n'.join(textwrap.wrap(str(x), width=100)) if pd.notna(x) else '')
# ===================== INTERFACE =====================
st.title("Proposições ALEPE")
st.markdown(f"### Encontradas **{len(recentes_900)}** proposições relevantes em {datetime.now().year}")
st.markdown("#### Que impactam o **Comércio, Serviços e Turismo** em Pernambuco")
col1, col2, col3 = st.columns(3)
with col1:
    if st.button("Visualizar Tabela Completa", use_container_width=True):
        st.session_state.view = "tabela"
with col2:
    if st.button("Proposições por Autor", use_container_width=True):
        st.session_state.view = "autores"
with col3:
    if st.button("Exportar para Excel", use_container_width=True):
        st.session_state.view = "exportar"
# ===================== VISÃO POR AUTORES =====================
if st.session_state.get("view") == "autores":
    st.subheader("Proposições por Autor")
    autores_lista = []
    for autores in df['autor']:
        autores_lista.extend([a.strip() for a in str(autores).split(',') if a.strip()])
   
    contagem = Counter(autores_lista)
    df_autores = pd.DataFrame(contagem.most_common(), columns=["Autor", "Quantidade"])
    st.dataframe(df_autores, use_container_width=True, hide_index=True)
# ===================== EXPORTAR EXCEL =====================
if st.session_state.get("view") == "exportar":
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Proposições')
    output.seek(0)
   
    st.download_button(
        label="Baixar Excel com todas as proposições",
        data=output,
        file_name=f"proposicoes_comercio_servicos_turismo_{datetime.now().year}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    st.success("Arquivo pronto para download!")
# ===================== TABELA PRINCIPAL =====================
if st.session_state.get("view") == "tabela" or "view" not in st.session_state:
    st.subheader("Tabela de Proposições")
    # Filtros
    with st.expander("Filtros avançados", expanded=False):
        cols = st.columns(4)
        filtro_numero = cols[0].text_input("Número")
        filtro_autor = cols[1].text_input("Autor")
        filtro_ementa = cols[2].text_input("Palavra na ementa")
        filtro_tipo = cols[3].selectbox("Tipo", options=["Todos"] + sorted(df['tipo'].unique()))
    df_display = df.copy()
    if filtro_numero:
        df_display = df_display[df_display['numero'].astype(str).str.contains(filtro_numero, case=False)]
    if filtro_autor:
        df_display = df_display[df_display['autor'].str.contains(filtro_autor, case=False, na=False)]
    if filtro_ementa:
        df_display = df_display[df_display['ementa'].str.contains(filtro_ementa, case=False, na=False)]
    if filtro_tipo != "Todos":
        df_display = df_display[df_display['tipo'] == filtro_tipo]
    # Mostrar tabela com botão de análise
    for idx, row in df_display.iterrows():
        with st.container():
            col_a, col_b, col_c = st.columns([1, 6, 2])
            col_a.write(f"**{row['numero']}/{row['ano']}**")
            col_b.write(f"**{row['ementa'][:200]}...**")
            col_c.write(f"*{row['autor']}*")
            if st.button(f"Analisar com Gemini", key=f"btn_{idx}"):
                with st.spinner("Gemini está analisando o projeto..."):
                    # Buscar texto completo
                    url_detail = f"https://dadosabertos.alepe.pe.gov.br/api/v1/proposicoes/projetos/?numero={row['numero']}&ano={row['ano']}"
                    try:
                        resp = requests.get(url_detail, timeout=15).text
                        tree = ET.fromstring(resp)
                        detalhes = {child.tag: (child.text or "").strip() for child in tree}
                        materia = detalhes.get('MATERIA', 'Não encontrada')
                        texto_completo = "\n\n".join([f"{k}: {v}" for k, v in detalhes.items() if v])
                        prompt = f"""
                        Você é analista legislativo do Sistema Fecomércio-PE.
                        Analise este projeto de lei de Pernambuco sob a ótica do Comércio, Serviços e Turismo.
                        Texto do projeto:
                        {materia}
                        Responda em português, de forma objetiva e profissional, com a seguinte estrutura:
                        Impacto esperado no setor de Comércio, Serviços e Turismo
                        Pontos positivos identificados
                        Pontos de risco identificados
                        Recomendação final: [APOIAR / MONITORAR / OPOR-SE]
                        Justifique cada item.
                        """
                        response = model.generate_content(
                            prompt,
                            generation_config=genai.types.GenerationConfig(
                                temperature=0.4,
                                max_output_tokens=3000
                            ),
                            safety_settings={cat: HarmBlockThreshold.BLOCK_NONE for cat in HarmCategory}
                        )
                        analise = response.text
                        st.success(f"**Análise PL {row['numero']}/{row['ano']}**")
                        st.markdown(analise)
                        with st.expander("Ver texto completo do projeto"):
                            st.text(texto_completo)
                    except Exception as e:
                        st.error(f"Erro ao analisar: {e}")
    st.caption("Sistema Fecomércio-PE / Sesc / Senac – Monitoramento Legislativo")
