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
    "comércio", "comercial", "varejo", "atacado", "distribuição", "loja", "pdv", "ponto de venda", "e-commerce",
    "loja virtual", "marketplace", "omnichannel", "multicanal", "placa física", "shopping", "centro comercial",
    "outlet", "varejo especializado", "varejo de conveniência", "loja de bairro", "franquia", "franchising",
    "franqueado", "franqueador", "microempreendedor", "pequena empresa", "média empresa", "grande varejista",
    "comércio eletrônico", "catálogo online", "site institucional", "checkout", "carrinho de compras",
    "abandono de carrinho", "conversão de vendas", "ticket médio", "faturamento", "receita", "margem bruta", "markup",
    "lucro operacional", "fluxo de caixa", "capital de giro", "estoque", "gestão de estoque", "sku", "sku por loja",
    "rotatividade de estoque", "ruptura de estoque", "inventário", "planograma", "visual merchandising", "vitrine",
    "merchandising", "promoção", "campanha sazonal", "liquidação", "preço", "precificação", "preço dinâmico",
    "desconto", "cupom", "voucher", "programa de fidelidade", "cartão fidelidade", "cashback", "promoção cross sell",
    "upsell", "trade marketing", "comunicação de ponto de venda", "display", "material de PDV", "POS (point of sale)",
    "maquininha", "gateway de pagamento", "adquirente", "pagamentos", "pix", "cartão de crédito", "cartão de débito",
    "boleto bancário", "financiamento ao consumidor", "crediário", "parcelamento", "antifraude", "chargeback",
    "concorrência", "benchmarking", "inteligência comercial", "pesquisa de mercado", "segmentação de mercado",
    "perfil do consumidor", "comportamento do consumidor", "loyalty", "crm", "gestão de relacionamento", "sac",
    "atendimento ao cliente", "central de relacionamento", "pós-venda", "garantia", "assistência técnica", "reclamação",
    "reembolso", "troca", "retorno de mercadoria", "logística", "logística de distribuição", "centro de distribuição",
    "armazém", "almoxarifado", "cross-docking", "last mile", "coleta", "entrega", "frete", "frete grátis",
    "contrato de transporte", "transportadora", "frota", "rastreamento", "tracking", "logística reversa", "armazenagem",
    "packing", "embalagem", "cadeia de suprimentos", "supply chain", "fornecedor", "sourcing", "compras", "procurement",
    "contrato de fornecimento", "controle de qualidade", "certificação de produto", "inspeção", "compliance",
    "compliance fiscal", "nota fiscal eletrônica", "nfe", "nfce", "sped", "obrigação acessória", "tributação", "icms",
    "iss", "ipi", "simples nacional", "regime tributário", "planejamento tributário", "auditoria", "contabilidade",
    "escrituração", "balanço", "demonstração do resultado", "contas a pagar", "contas a receber",
    "conciliação bancária", "pagamentos eletrônicos", "conciliador", "gateway", "fintech", "acquirer",
    "meios de pagamento", "segurança da informação", "certificado digital", "lgpd", "proteção de dados", "privacidade",
    "autenticação", "tokenização", "criptografia", "site responsivo", "mobile first", "app", "aplicativo",
    "integração omnicanais", "api", "erp", "sistema de gestão", "bi", "business intelligence", "power bi",
    "relatórios gerenciais", "dashboards", "kpi", "indicadores de performance", "relação estoque/vendas",
    "giro de estoque", "taxa de ocupação (hospedagem)", "adr (average daily rate)", "revpar", "taxa de conversão",
    "custo de aquisição de cliente (cac)", "lifetime value (ltv)", "retorno sobre investimento (roi)",
    "análise de coorte", "segmento", "nichos de mercado", "previsão de demanda", "forecast", "sazonalidade",
    "calendário promocional", "campanhas de datas comemorativas", "black friday", "natal", "dia das mães",
    "dia dos pais", "liquidações de temporada", "assessoria de imprensa", "relações públicas",
    "comunicação institucional", "branding", "posicionamento de marca", "identidade visual", "design de marca",
    "slogan", "logomarca", "trade dress", "marketing", "marketing digital", "marketing de conteúdo", "conteúdo",
    "inbound marketing", "outbound marketing", "seo", "sem", "google ads", "facebook ads", "instagram ads",
    "social media", "gestão de redes sociais", "influenciadores", "publicidade", "assessoria de imprensa", "release",
    "e-mail marketing", "crm marketing", "sms marketing", "push notification", "remarketing", "programa de afiliados",
    "analytics", "google analytics", "conversão", "experimentação a/b", "pesquisa de satisfação", "nps",
    "pesquisa net promoter score", "mystery shopping", "capacitação", "treinamento", "formação profissional",
    "qualificação de mão de obra", "recursos humanos", "rh", "recrutamento", "seleção", "folha de pagamento",
    "benefícios", "jornada de trabalho", "escala", "turnover", "clt", "pj", "autônomo", "terceirização", "terceirizado",
    "assédio", "segurança do trabalho", "normas regulamentadoras", "saúde ocupacional", "seguro", "seguro empresarial",
    "seguro de responsabilidade civil", "prevenção de perdas", "controle de perdas", "monitoramento por câmeras",
    "cftv", "alarmes", "portaria", "vigília", "controle de acesso", "sistemas de vigilância", "sustentabilidade",
    "responsabilidade social", "economia circular", "gestão de resíduos", "eficiência energética", "crédito verde",
    "certificação ambiental", "responsabilidade ambiental", "compras públicas", "licitação",
    "contratos administrativos", "alvará", "licença sanitária", "vigilância sanitária", "inspeção sanitária",
    "corpo de bombeiros", "licenciamento", "zoneamento urbano", "alvará de funcionamento",
    "registro de estabelecimento", "cnaes", "cnae", "cnae principal", "regime de tributação",
    "registro na junta comercial", "contrato social", "estatuto", "constituição de empresa", "constituição de filial",
    "matriz", "filial", "cnpj", "cnpj completo", "certidão negativa", "certidões fiscais", "certificado digital",
    "documentação empresarial", "integração bancária", "conta PJ", "maquininha de cartão", "split de pagamento",
    "contabilidade gerencial", "governança corporativa", "comitê de riscos", "governo corporativo",
    "governo do comércio", "associações comerciais", "sindicatos", "federação", "câmaras setoriais",
    "associação de hotéis", "convention bureau", "embratur", "secretaria de turismo", "política pública de turismo",
    "incentivos fiscais", "programas de fomento", "microcrédito", "linhas de crédito", "banco de fomento",
    "banco de desenvolvimento", "microfinanças", "investimento privado", "private equity", "venture capital",
    "incubadora", "aceleradora", "hub de inovação", "transformação digital", "automação comercial", "self checkout",
    "quiosque de atendimento", "balcão eletrônico", "beacon", "iot", "internet das coisas", "rfid", "nfc", "qr code",
    "pagamento por aproximação", "contactless", "rastreamento de clientes", "heatmap de loja",
    "contagem de fluxo de clientes", "ppl (people counting)", "geolocalização", "geofencing", "analytics geoespacial",
    "consultoria empresarial", "assessoria econômica", "estudo de mercado", "diagnóstico setorial",
    "benchmark setorial", "plano de negócios", "modelagem financeira", "business plan", "due diligence",
    "relatório gerencial", "indicadores setoriais", "índices de confiança", "índice de vendas", "índice de consumo",
    "peic (pesquisa de endividamento e inadimplência do consumidor)", "icv", "pmc (pesquisa mensal do comércio)",
    "pms (pesquisa mensal de serviços)", "estatística setorial", "censo econômico", "pesquisa amostral",
    "painel de empresas", "dados administrativos", "open data", "bases públicas", "ibge", "ipea", "bndes", "serasa",
    "sistema de informações", "integração de bases", "etl", "pipeline de dados", "qualidade de dados",
    "governança de dados", "privacidade de dados", "visualização de dados", "mapa de calor", "tabela dinâmica",
    "relatório executivo", "nota técnica", "release para imprensa", "assessoria de imprensa",
    "comunicado institucional", "nota à presidência", "press kit", "media kit", "treinamento de porta-voz",
    "entrevista coletiva", "coletiva de imprensa", "relacionamento com a imprensa", "eventos comerciais", "feiras",
    "exposições", "rodadas de negócios", "congressos", "workshops", "palestras", "seminários",
    "captação de expositores", "sponsorship", "patrocínio", "patrocinador",
    "mice (meetings, incentives, conferences, exhibitions)", "turismo de eventos", "turismo de negócios",
    "turismo corporativo", "hospedagem", "hotel", "hotelaria", "pousada", "resort", "flat", "apart-hotel", "hostel",
    "camping", "alojamento local", "airbnb", "aluguel por temporada", "check-in", "check-out", "reserva", "booking",
    "ota (online travel agency)", "agência de viagem", "operador turístico", "operadora receptiva", "pacote turístico",
    "roteiro", "roteiro temático", "roteiro cultural", "roteiro gastronômico", "roteiro histórico",
    "roteiro de aventura", "guia turístico", "guia credenciado", "licença de guia", "transfer", "traslado",
    "serviço de transfer", "transporte turístico", "locadora de veículos", "aluguel de carro", "aluguel de van",
    "ônibus turístico", "city tour", "passeio", "excursão", "bate-volta", "tour privado", "tour guiado", "ingresso",
    "bilheteria", "reserva de atrações", "atrativos turísticos", "ponto turístico", "ponto de interesse",
    "patrimônio cultural", "patrimônio histórico", "museu", "monumento", "centro histórico", "trilha",
    "parque nacional", "unidade de conservação", "parque estadual", "parque municipal", "ecoturismo", "turismo rural",
    "agroturismo", "aventura", "turismo náutico", "turismo de pesca", "mergulho", "praia", "praia turística", "golfe",
    "esporte náutico", "bem-estar", "spa", "termal", "saúde e bem-estar", "turismo de saúde", "turismo médico",
    "estética", "tratamento de saúde", "certificado de qualidade", "selo de turismo", "certificação hoteleira",
    "qualidade de serviço", "sustentabilidade turística", "turismo responsável", "impacto socioambiental",
    "comunidade local", "benefício local", "cadeia de valor local", "artesanato", "produtos locais",
    "gastronomia local", "restaurante", "bar", "cafeteria", "bistrô", "cozinha regional", "cooking class", "degustação",
    "rota gastronômica", "mercado municipal", "feira livre", "comércio ambulante", "feirinha", "economia criativa",
    "economia de experiência", "experiência turística", "experiência imersiva", "memorabilidade",
    "serviço personalizado", "concierge", "receptivo", "central de reservas", "sistema de reservas",
    "motor de reservas", "api de reservas", "pagamento antecipado", "política de cancelamento", "seguro viagem",
    "assistência em viagem", "visto", "imigração", "alfândega", "controle aduaneiro", "bagagem", "bagagem extraviada",
    "bagagem perdida", "companhia aérea", "voo", "rota aérea", "aeroporto", "terminal rodoviário", "rodoviária",
    "porto", "porto turístico", "marina", "operador portuário", "infraestrutura turística", "sinalização turística",
    "centro de informações turísticas", "centro de visitantes", "mapa turístico", "app de roteiro",
    "plataforma de roteiros", "capacitação profissional", "formação de guias", "curso de hospitalidade",
    "curso de gastronomia", "curso técnico", "certificação profissional", "selos de qualidade",
    "indicadores de desempenho", "monitoramento de demanda", "relatório de ocupação", "relatório de receita",
    "análise de demanda", "estudo de viabilidade", "regulação do setor", "normas técnicas", "normas de segurança",
    "normas sanitárias", "fiscalização", "inspeção", "licenciamento ambiental", "zoneamento", "plano diretor",
    "política urbana", "conexão entre turismo e comércio", "economia local", "renda turística",
    "multiplicador econômico", "efeito multiplicador", "receita tributária", "arrecadação de icms",
    "arrecadação municipal", "simples nacional optantes", "micro e pequenas empresas (mpe)", "apoio institucional",
    "programas de incentivo", "linhas de crédito dedicadas", "programas de capacitação", "parcerias público-privadas",
    "ppp", "governo municipal", "governo estadual", "secretaria de desenvolvimento econômico",
    "secretaria de turismo estadual", "planos estratégicos setoriais", "mapa de investimentos", "china inbound",
    "mercado emissor", "perfil do turista emissor", "turista nacional", "turista internacional", "fluxo turístico",
    "temporalidade da demanda", "pico turístico", "baixa temporada", "alto fluxo", "sazonalidade climática",
    "clima e turismo", "resiliência do setor", "gestão de crise", "planos de contingência", "segurança pública",
    "saúde pública", "protocolos sanitários", "higienização", "distanciamento", "protocolos de atendimento",
    "qualidade percebida", "satisfação do cliente", "reputação", "avaliações online", "reviews", "tripadvisor",
    "google maps reviews", "comentários", "resposta a avaliações", "gestão de reputação", "gestão de crises",
    "relacionamento com stakeholders", "parcerias estratégicas", "rede de parceiros", "integração intermunicipal",
    "rota regional", "rota interestadual", "rota internacional", "conveniência", "comércio local",
    "sistema de pagamentos locais", "moeda local", "câmbio", "cambistas", "tour operador internacional",
    "embalagem turística", "itinerário", "serviços complementares", "estacionamento", "acessibilidade",
    "turismo acessível", "infraestrutura para pessoas com mobilidade reduzida", "sinalização inclusiva",
    "capacitação em acessibilidade", "indicadores sociais", "inclusão", "emprego formal no turismo", "emprejo informal",
    "renda do trabalhador", "salário médio do setor", "qualificação profissional", "carreira hoteleira",
    "gestão hoteleira", "governo corporativo no turismo", "plano de investimento", "inovação",
    "transformação digital no turismo", "productização de serviços", "servitização", "experiência do cliente",
    "customer experience", "customer journey", "mapa de jornada do cliente", "touchpoints", "momento da verdade",
    "lealdade do cliente", "retorno do cliente", "recompra", "rede de franquias", "expansão de rede",
    "licenciamento de marca", "royalties", "contrato de franquia", "modelo de negócios", "modelo de receita",
    "assinatura", "assinatura mensal", "assinatura anual", "economia de escala", "economia local", "clúster setorial",
    "arranjo produtivo local", "aglomeração industrial", "articulação institucional",
    "parcerias entre universidade e setor", "pesquisa aplicada", "inovação aberta", "propriedade intelectual",
    "marcas registradas", "patentes", "design industrial", "projetos de turismo cultural", "circuitos turísticos",
    "planos de capacitação municipal", "observatório do turismo", "mapa de risco", "indicadores de turismo municipal",
    "base de dados turística", "sistema de informações turísticas"
]

# ===================== CARREGAR DADOS DA ALEPE =====================
@st.cache_data(ttl=3600, show_spinner="Consultando ALEPE...")
def carregar_dados():
    ano = datetime.now().year
    url = f"https://dadosabertos.alepe.pe.gov.br/api/v1/proposicoes/projetos?ano={ano}"
    
    try:
        response = requests.get(url, timeout=50)
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
