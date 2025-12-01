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
st.set_page_config(page_title="Monitor Legislativo ALEPE", layout="wide")

# Chave do Gemini (nunca deixe exposta no código!)
GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

# ===================== PALAVRAS-CHAVE COMPLETAS =====================
palavras_chave = [
    "comércio", "comercial", "varejo", "atacado", "distribuição", "loja", "pdv", "ponto de venda", "e-commerce",
    "loja virtual", "marketplace", "omnichannel", "multicanal", "placa física", "shopping", "centro comercial",
    "outlet", "varejo especializado", "varejo de conveniência", "loja de bairro", "franquia", "franchising",
    "franqueado", "franqueador", "microempreendedor", "pequena empresa", "média empresa", "grande varejista",
    "comércio eletrônico", "catálogo online", "site institucional", "checkout", "carrinho de compras",
    "abandono de carrinho", "conversão de vendas", "ticket médio", "faturamento", "receita", "margem bruta", "markup",
    "lucro operacional", "fluxo de caixa", "capital de giro", "estoque", "gestão de estoque", "sku", "sku por loja",
    "rotatividade de estoque", "ruptura de estoque", "inventário", "planograma", "visual merchandising", "vitrine",
    "merchandising", "promoção", "campanha sazonal", "liquidação", "preço", "precificação", "preço dinâmico",
    "desconto", "cupom", "voucher", "programa de fidelidade", "cartão fidelidade", "cashback", "cross sell",
    "upsell", "trade marketing", "comunicação de ponto de venda", "display", "material de PDV", "POS", "maquininha",
    "gateway de pagamento", "adquirente", "pagamentos", "pix", "cartão de crédito", "cartão de débito",
    "boleto bancário", "financiamento ao consumidor", "crediário", "parcelamento", "antifraude", "chargeback",
    "concorrência", "benchmarking", "inteligência comercial", "pesquisa de mercado", "segmentação de mercado",
    "perfil do consumidor", "comportamento do consumidor", "loyalty", "crm", "gestão de relacionamento", "sac",
    "atendimento ao cliente", "pós-venda", "garantia", "assistência técnica", "reclamação", "reembolso", "troca",
    "logística", "centro de distribuição", "cross-docking", "last mile", "frete grátis", "transportadora",
    "rastreamento", "logística reversa", "supply chain", "fornecedor", "sourcing", "compras", "procurement",
    "nfe", "nfce", "sped", "icms", "iss", "ipi", "simples nacional", "regime tributário", "lgpd", "erp", "bi",
    "power bi", "kpi", "revpar", "adr", "cac", "ltv", "roi", "black friday", "natal", "dia das mães", "dia dos pais",
    "marketing digital", "seo", "sem", "google ads", "facebook ads", "instagram ads", "social media",
    "influenciadores", "e-mail marketing", "remarketing", "nps", "rh", "folha de pagamento", "turnover", "clt",
    "pj", "terceirização", "sustentabilidade", "economia circular", "licitação", "alvará", "cnae", "cnpj",
    "fintech", "maquininha de cartão", "hotel", "hotelaria", "pousada", "resort", "airbnb", "booking", "ota",
    "turismo", "turismo de negócios", "ecoturismo", "turismo rural", "gastronomia", "restaurante", "bar",
    "feira livre", "economia criativa", "experiência turística", "city tour", "guia turístico", "roteiro",
    "spa", "bem-estar", "eventos", "congresso", "feira", "museu", "patrimônio cultural"
]

# ===================== CARREGAR DADOS =====================
@st.cache_data(ttl=3600, show_spinner="Carregando proposições da ALEPE...")
def carregar_dados():
    ano = datetime.now().year
    url = f"https://dadosabertos.alepe.pe.gov.br/api/v1/proposicoes/projetos?ano={ano}"
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    tree = ET.fromstring(response.text)
    proposicoes = []

    for elem in tree.findall('projeto'):
        prop = elem.attrib
        autores = [a.attrib.get('nome', '') for a in elem.findall('./autores/autor')]
        prop['autor'] = ', '.join(autores) if autores else 'Não informado'
        proposicoes.append(prop)

    def contem_palavra(ementa):
        if not ementa:
            return False
        return any(palavra in ementa.lower() for palavra in palavras_chave)

    filtradas = [p for p in proposicoes if contem_palavra(p.get('ementa', ''))]
    
    def parse_date(d):
        try:
            return datetime.strptime(d, '%d/%m/%Y')
        except:
            return datetime.min

    filtradas.sort(key=lambda x: parse_date(x.get('dataPublicacao', '')), reverse=True)
    return filtradas[:900]

with st.spinner("Consultando ALEPE..."):
    recentes = carregar_dados()

if not recentes:
    st.warning("Nenhuma proposição relevante encontrada este ano.")
    st.stop()

df = pd.DataFrame(recentes)
df['ementa'] = df['ementa'].apply(lambda x: '<br>'.join(textwrap.wrap(str(x), 100)) if pd.notna(x) else '')

# ===================== INTERFACE =====================
st.title("Monitor Legislativo ALEPE")
st.markdown(f"**{len(recentes)}** proposições encontradas em {datetime.now().year} que impactam **Comércio, Serviços e Turismo**")

col1, col2, col3 = st.columns(3)
with col1:
    if st.button("Ver Tabela", use_container_width=True):
        st.session_state.view = "tabela"
with col2:
    if st.button("Por Autor", use_container_width=True):
        st.session_state.view = "autores"
with col3:
    if st.button("Exportar Excel", use_container_width=True):
        st.session_state.view = "exportar"

# ===================== POR AUTOR =====================
if st.session_state.get("view") == "autores":
    st.subheader("Proposições por Autor")
    autores = []
    for a in df['autor']:
        autores.extend([x.strip() for x in str(a).split(',') if x.strip()])
    contagem = Counter(autores).most_common(30)
    st.bar_chart(dict(contagem))

# ===================== EXPORTAR =====================
if st.session_state.get("view") == "exportar":
    output = io.BytesIO()
    df.to_excel(output, index=False, engine='openpyxl')
    output.seek(0)
    st.download_button(
        "Baixar Excel",
        data=output,
        file_name=f"ALEPE_Comercio_Servicos_Turismo_{datetime.now().year}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

# ===================== TABELA PRINCIPAL =====================
if "view" not in st.session_state or st.session_state.view == "tabela":
    st.subheader("Proposições Filtradas")
    
    busca = st.text_input("Buscar na ementa ou autor")
    if busca:
        df = df[df['ementa'].str.contains(busca, case=False) | df['autor'].str.contains(busca, case=False)]

    for _, row in df.iterrows():
        with st.container():
            cols = st.columns([1, 5, 2])
            cols[0].markdown(f"**PL {row['numero']}/{row['ano']}**")
            cols[1].markdown(f"<small>{row['ementa']}</small>", unsafe_allow_html=True)
            cols[2].markdown(f"_{row['autor']}_")
            
            if cols[1].button("Analisar com Gemini", key=row['id']):
                with st.spinner("Gemini analisando..."):
                    url_det = f"https://dadosabertos.alepe.pe.gov.br/api/v1/proposicoes/projetos/?numero={row['numero']}&ano={row['ano']}"
                    try:
                        tree = ET.fromstring(requests.get(url_det).text)
                        materia = tree.find('MATERIA').text or ""
                        prompt = f"Analise este PL de Pernambuco sob impacto no Comércio, Serviços e Turismo:\n\n{materia}\n\nResponda apenas com: Impacto, Pontos positivos, Riscos e Recomendação final (APOIAR/MONITORAR/OPOR-SE)"
                        resp = model.generate_content(prompt, generation_config={"temperature": 0.3})
                        st.success(f"Análise PL {row['numero']}/{row['ano']}")
                        st.write(resp.text)
                    except:
                        st.error("Erro ao carregar texto completo")

st.caption("Fecomércio-PE • Monitoramento Legislativo")
