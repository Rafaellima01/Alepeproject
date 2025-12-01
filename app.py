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
palavras_chave = ["comércio", "comercial", "varejo", "atacado", "distribuição", "loja", "pdv", "ponto de venda", "e-commerce",
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
    "base de dados turística", "sistema de informações turísticas"]
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
