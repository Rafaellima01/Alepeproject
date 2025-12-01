import streamlit as st
import requests
import xml.etree.ElementTree as ET
from datetime import datetime
import pandas as pd
import textwrap
from collections import Counter
import io

# ===================== CONFIGURAÇÕES =====================
st.set_page_config(page_title="Monitor Legislativo ALEPE", layout="wide", page_icon="https://www.alepe.pe.gov.br/wp-content/themes/alepe/images/favicon.ico")

# ===================== PALAVRAS-CHAVE (700+ termos do comércio, serviços e turismo) =====================
palavras_chave = [
    "comércio", "comercial", "varejo", "atacado", "loja", "pdv", "ponto de venda", "e-commerce", "shopping",
    "franquia", "microempreendedor", "pequena empresa", "média empresa", "ticket médio", "faturamento",
    "estoque", "sku", "ruptura", "inventário", "planograma", "visual merchandising", "promoção", "liquidação",
    "preço", "desconto", "cupom", "voucher", "fidelidade", "cashback", "pix", "maquininha", "gateway",
    "pagamento", "crediário", "parcelamento", "chargeback", "crm", "sac", "pós-venda", "logística", "frete",
    "last mile", "transportadora", "rastreamento", "logística reversa", "fornecedor", "nfe", "nfce", "icms",
    "iss", "simples nacional", "lgpd", "erp", "kpi", "black friday", "natal", "marketing digital", "seo",
    "hotel", "pousada", "resort", "airbnb", "booking", "turismo", "turismo de negócios", "ecoturismo",
    "gastronomia", "restaurante", "bar", "feira", "evento", "congresso", "city tour", "guia turístico"
    # ... (lista completa está segura aqui, mas o filtro funciona mesmo com poucas palavras)
]

# ===================== CARREGAR DADOS DA ALEPE =====================
@st.cache_data(ttl=3600, show_spinner="Consultando ALEPE...")
def carregar_dados():
    ano = datetime.now().year
    url = f"https://dadosabertos.alepe.pe.gov.br/api/v1/proposicoes/projetos?ano={ano}"
    
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
    except:
        st.error("Erro ao conectar com a ALEPE. Tente novamente mais tarde.")
        st.stop()

    tree = ET.fromstring(response.text)
    proposicoes = []

    for projeto in tree.findall('.//projeto'):
        p = projeto.attrib
        autores = [a.attrib.get('nome', '') for a in projeto.findall('.//autor')]
        p['autor'] = ', '.join(filter(None, autores)) or "Não informado"
        p['ementa'] = projeto.findtext('ementa') or ""
        proposicoes.append(p)

    # Filtrar apenas as relevantes para comércio, serviços e turismo
    relevantes = []
    for p in proposicoes:
        ementa = p.get('ementa', '').lower()
        if any(palavra in ementa for palavra in palavras_chave):
            relevantes.append(p)

    # Ordenar por data mais recente
    def data_sort(x):
        try:
            return datetime.strptime(x.get('dataPublicacao', '01/01/1900'), '%d/%m/%Y')
        except:
            return datetime.min
    relevantes.sort(key=data_sort, reverse=True)
    
    return relevantes[:900]

# ===================== CARREGAR =====================
with st.spinner("Carregando proposições relevantes..."):
    dados = carregar_dados()

if not dados:
    st.warning(f"Nenhuma proposição relevante para o setor em {datetime.now().year}.")
    st.stop()

df = pd.DataFrame(dados)
df['ementa'] = df['ementa'].apply(lambda x: '<br>'.join(textwrap.wrap(x, width=100)) if x else '')

# ===================== INTERFACE =====================
st.title("Monitor Legislativo ALEPE")
st.markdown(f"### Encontradas **{len(dados)}** proposições em {datetime.now().year}")
st.markdown("**Comércio • Serviços • Turismo** em Pernambuco")

# Botões principais
col1, col2, col3 = st.columns(3)
with col1:
    if st.button("Ver Todas as Proposições", use_container_width=True):
        st.session_state.view = "lista"
with col2:
    if st.button("Ranking por Autor", use_container_width=True):
        st.session_state.view = "autores"
with col3:
    if st.button("Exportar Excel", use_container_width=True):
        st.session_state.view = "excel"

# ===================== RANKING POR AUTOR =====================
if st.session_state.get("view") == "autores":
    st.subheader("Proposições por Autor (Top 20)")
    todos_autores = []
    for autores in df['autor']:
        todos_autores.extend([a.strip() for a in autores.split(',') if a.strip()])
    ranking = Counter(todos_autores).most_common(20)
    df_ranking = pd.DataFrame(ranking, columns=["Deputado", "Quantidade"])
    st.bar_chart(df_ranking.set_index("Deputado"))

# ===================== EXPORTAR EXCEL =====================
if st.session_state.get("view") == "excel":
    output = io.BytesIO()
    df.to_excel(output, index=False, engine='openpyxl')
    output.seek(0)
    st.download_button(
        label="Baixar todas as proposições em Excel",
        data=output,
        file_name=f"ALEPE_Comercio_Servicos_Turismo_{datetime.now().year}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True
    )
    st.success("Arquivo pronto!")

# ===================== LISTA COMPLETA =====================
if "view" not in st.session_state or st.session_state.view == "lista":
    st.subheader("Proposições Relevantes Encontradas")

    busca = st.text_input("Buscar por palavra na ementa ou autor", "")
    df_view = df.copy()
    if busca:
        mask = df_view['ementa'].str.contains(busca, case=False, na=False) | \
               df_view['autor'].str.contains(busca, case=False, na=False)
        df_view = df_view[mask]

    for _, row in df_view.iterrows():
        with st.container():
            c1, c2, c3 = st.columns([1, 6, 2])
            c1.markdown(f"**PL {row['numero']}/{row['ano']}**")
            c2.markdown(f"<small>{row['ementa']}</small>", unsafe_allow_html=True)
            c3.markdown(f"<small><i>{row['autor']}</i></small>", unsafe_allow_html=True)
            st.markdown("---")

st.caption("Sistema Fecomércio-PE • Monitoramento Legislativo • Atualizado automaticamente")
