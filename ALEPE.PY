import requests
import xml.etree.ElementTree as ET
from datetime import datetime
import pandas as pd
import customtkinter as ctk
from tkinter import ttk, messagebox, scrolledtext
import threading
from tkinter import filedialog
import textwrap
from collections import Counter
import os
import tkinter as tk
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold

GEMINI_API_KEY = "a chave"

genai.configure(api_key=GEMINI_API_KEY)

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


class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Consulta de Proposições ALEPE")
        self.root.geometry("800x600")

        self.model = genai.GenerativeModel('gemini-2.5-pro')
        self.show_loading_screen()
        threading.Thread(target=self.fetch_data, daemon=True).start()

    def show_loading_screen(self):
        self.loading_label = ctk.CTkLabel(self.root, text="Carregando dados da ALEPE...", font=("Arial", 20, "bold"))
        self.loading_label.pack(expand=True, pady=100)

    def hide_loading_screen(self):
        self.loading_label.destroy()

    def fetch_data(self):
        ano = datetime.now().year
        url = f"https://dadosabertos.alepe.pe.gov.br/api/v1/proposicoes/projetos?ano={ano}"
        try:
            response = requests.get(url, timeout=15)
            response.raise_for_status()
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Erro", f"Não foi possível conectar à ALEPE:\n{e}"))
            self.root.after(0, self.hide_loading_screen)
            return

        try:
            tree = ET.fromstring(response.text)
        except ET.ParseError as e:
            self.root.after(0, lambda: messagebox.showerror("Erro", f"XML inválido:\n{e}"))
            return

        proposicoes = []
        for elem in tree.findall('projeto'):
            prop = elem.attrib
            autores = [autor.attrib.get('nome', '') for autor in elem.findall('./autores/autor')]
            prop['autor'] = ', '.join(autores) if autores else ''
            proposicoes.append(prop)

        def parse_date(date_str):
            try:
                return datetime.strptime(date_str, '%d/%m/%Y')
            except:
                return datetime.min

        filtradas = [
            prop for prop in proposicoes
            if any(palavra.lower() in prop.get('ementa', '').lower() for palavra in palavras_chave)
        ]

        filtradas.sort(key=lambda x: parse_date(x.get('dataPublicacao', '')), reverse=True)
        self.recentes_900 = filtradas[:900]

        for prop in self.recentes_900:
            if 'ementa' in prop:
                prop['ementa'] = '\n'.join(textwrap.wrap(prop['ementa'], width=80))

        self.df = pd.DataFrame(self.recentes_900) if self.recentes_900 else None
        self.root.after(0, self.show_main_screen)

    def show_main_screen(self):
        self.hide_loading_screen()

        if not self.recentes_900:
            ctk.CTkLabel(self.root, text=f"Nenhuma proposição encontrada em {datetime.now().year}", font=("Arial", 16)).pack(pady=50)
            return

        header_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        header_frame.pack(pady=20)

        ctk.CTkLabel(header_frame, text="Encontradas", font=("Poppins", 38)).pack(side="left")
        ctk.CTkLabel(header_frame, text=str(len(self.recentes_900)), text_color="#296FB5", font=("Poppins", 42, "bold")).pack(side="left", padx=10)

        ctk.CTkLabel(self.root, text="Proposições filtradas", font=("Poppins", 38)).pack(pady=5)
        ctk.CTkLabel(self.root, text=f"em {datetime.now().year}", font=("Poppins", 38)).pack(pady=5)
        ctk.CTkLabel(self.root, text="Escolha a opção", font=("Arial", 38, "bold")).pack(pady=30)

        btn_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        btn_frame.pack(pady=10)

        ctk.CTkButton(btn_frame, text="Visualizar na tela", command=self.view_on_screen, corner_radius=20, width=200).pack(side="left", padx=15)
        ctk.CTkButton(btn_frame, text="Proposições por Autor", command=self.show_author_counts, corner_radius=20, width=200).pack(side="left", padx=15)
        ctk.CTkButton(btn_frame, text="Exportar para XLSX", command=self.export_to_excel, corner_radius=20, width=200).pack(side="left", padx=15)

        ctk.CTkLabel(self.root, text="Clique e veja as proposições que influenciam", font=("Arial", 14)).pack(pady=5)
        ctk.CTkLabel(self.root, text="o ambiente de negócios do Comércio, Serviços e Turismo.", font=("Arial", 14)).pack()

    def get_author_counts(self):
        author_list = []
        for authors in self.df['autor']:
            author_list.extend([a.strip() for a in authors.split(',') if a.strip()])
        return Counter(author_list)

    def show_author_counts(self):
        counts = self.get_author_counts()
        if not counts:
            messagebox.showinfo("Info", "Nenhum autor encontrado.")
            return

        win = ctk.CTkToplevel(self.root)
        win.title("Proposições por Autor")
        win.geometry("600x800")

        tree = ttk.Treeview(win, columns=['Autor', 'Qtd'], show='headings')
        tree.heading('Autor', text='Autor')
        tree.heading('Qtd', text='Quantidade')
        tree.column('Autor', width=400)
        tree.column('Qtd', width=120, anchor='center')

        for autor, qtd in counts.most_common():
            tree.insert('', 'end', values=(autor, qtd))

        tree.pack(fill="both", expand=True, padx=10, pady=10)
        scrollbar = ttk.Scrollbar(win, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

    def view_on_screen(self):
        win = ctk.CTkToplevel(self.root)
        win.title("Proposições Encontradas")
        win.geometry("1400x900")

        filter_frame = ctk.CTkFrame(win)
        filter_frame.pack(fill="x", pady=5)

        self.filter_entries = {}
        excluded = ['ano', 'legislatura', 'subtipo']
        for col in self.df.columns:
            if col not in excluded:
                ctk.CTkLabel(filter_frame, text=col, width=12).pack(side="left", padx=2)
                entry = ctk.CTkEntry(filter_frame, width=140)
                entry.pack(side="left", padx=2)
                entry.bind('<KeyRelease>', self.filter_tree)
                self.filter_entries[col] = entry

        ctk.CTkLabel(filter_frame, text="Análise", width=30).pack(side="left", padx=20)

        style = ttk.Style()
        style.configure("Treeview", rowheight=70)

        columns = [c for c in self.df.columns if c not in excluded] + ['analise']
        self.tree = ttk.Treeview(win, columns=columns, show='headings')

        for col in columns:
            self.tree.heading(col, text=col, command=lambda c=col: self.treeview_sort_column(c, False) if c != 'analise' else None)
            self.tree.column(col, width=150, anchor='w')
        self.tree.column('ementa', width=550)
        self.tree.column('analise', width=120, anchor='center')

        for idx, (_, row) in enumerate(self.df.iterrows()):
            values = [row[col] for col in columns[:-1]] + ['Analisar']
            self.tree.insert('', 'end', iid=str(idx), values=values)

        self.tree.bind('<Button-1>', self.on_tree_click)

        scroll_y = ttk.Scrollbar(win, orient="vertical", command=self.tree.yview)
        scroll_x = ttk.Scrollbar(win, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)

        self.tree.pack(fill="both", expand=True, padx=10, pady=5)
        scroll_y.pack(side="right", fill="y")
        scroll_x.pack(side="bottom", fill="x")

    def on_tree_click(self, event):
        col = self.tree.identify_column(event.x)
        if col != f'#{len(self.tree["columns"])}':  # última coluna = analise
            return

        row_id = self.tree.identify_row(event.y)
        if not row_id:
            return

        index = int(row_id)
        row = self.df.iloc[index]
        numero = row['numero']
        ano = row['ano']
        tipo = 'projetos'

        # Busca texto completo
        url = f"https://dadosabertos.alepe.pe.gov.br/api/v1/proposicoes/{tipo}/?numero={numero}&ano={ano}"
        try:
            resp = requests.get(url, timeout=10)
            resp.raise_for_status()
            full_tree = ET.fromstring(resp.text)
        except Exception as e:
            messagebox.showerror("Erro", f"Não foi possível carregar o texto completo:\n{e}")
            return

        # Extração limpa do conteúdo
        details = {child.tag: (child.text.strip() if child.text else "") for child in full_tree}
        details_upper = {k.upper(): v for k, v in details.items()}

        chaves_essenciais = ['MATERIA']
        partes_para_analise = []
        partes_para_visualizacao = []

        for key in details_upper:
            conteudo = details_upper[key]
            if not conteudo:
                continue
            if key in chaves_essenciais and 'HTML' not in key:
                partes_para_analise.append(f"{key}:\n{conteudo}")
            if 'HTML' not in key:
                partes_para_visualizacao.append(f"{key}: {conteudo}")

        texto_limpo_para_analise = "\n\n---\n\n".join(partes_para_analise)
        full_text = "\n\n".join(partes_para_visualizacao)

        if not texto_limpo_para_analise:
            messagebox.showerror("Erro", "Não foi possível extrair MATERIA para análise.")
            return

        # Janela 1 - Texto completo
        details_win = ctk.CTkToplevel(self.root)
        details_win.title(f"PL {numero}/{ano} - Texto Completo")
        details_win.geometry("1000x750")
        txt = scrolledtext.ScrolledText(details_win, wrap=tk.WORD, font=("Segoe UI", 11))
        txt.pack(fill="both", expand=True, padx=10, pady=10)
        txt.insert(tk.END, full_text)
        txt.config(state=tk.DISABLED)

        # Janela 2 - Análise Gemini
        ai_win = ctk.CTkToplevel(self.root)
        ai_win.title(f"Análise Gemini - PL {numero}/{ano}")
        ai_win.geometry("1000x750")

        ai_text = scrolledtext.ScrolledText(ai_win, wrap=tk.WORD, font=("Segoe UI", 11))
        ai_text.pack(fill="both", expand=True, padx=10, pady=10)

        loading = ctk.CTkLabel(ai_win, text="Gemini está analisando o projeto de lei...", font=("Arial", 28, "bold"),
                               text_color="#00AAFF")
        loading.place(relx=0.5, rely=0.5, anchor="center")

        def analisar_com_gemini():
            try:
                prompt = f"""
                Você é um analista legislativo especializado no setor de Comércio, Serviços e Turismo de Pernambuco, atuando em nome do Sistema Fecomércio-PE / Sesc / Senac.
                Analise o seguinte projeto de lei e responda APENAS em português, de forma clara, objetiva e profissional.
                Texto do projeto:
                {texto_limpo_para_analise}
                REGRAS OBRIGATÓRIAS DE FORMATAÇÃO:
                - Use texto 100% limpo e plano
                - NÃO use Markdown de forma alguma (nada de **negrito**, *itálico*, # títulos, - listas com traço, 1. listas numeradas com ponto, --- separadores, ___ ou qualquer outro símbolo de formatação)
                - Use apenas parágrafos normais e quebras de linha simples
                - se precisar enumerar, use apenas números ou letras seguidos de parêntese: 1) 2) ou a) b)
                - se precisar destacar algo muito importante, escreva em CAIXA ALTA (ex: OPOR-SE)
                - se precisar separar seções grandes, deixe apenas duas linhas em branco entre elas

                Estrutura obrigatória da resposta:
                Impacto esperado no setor de Comércio, Serviços e Turismo
                Pontos de positivos e pontos de riscos identificados  
                Recomendação final: [APOIAR / MONITORAR / OPOR-SE]

                Justifique cada item de forma clara e direta.
                """

                # MODELOS VÁLIDOS EM NOVEMBRO 2025:
                response = self.model.generate_content(
                    prompt,
                    generation_config=genai.types.GenerationConfig(
                        temperature=0.3,
                        max_output_tokens=3300,
                        stop_sequences=['O comando tá assim', 'Gostaria de uma análise'] # Opcional: para parar após a análise principal.

                    # O prompt do usuário viria a seguir, contendo o texto_limpo_para_analise.
                    ),
                    safety_settings={
                        HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                        HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                        HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
                        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
                    }
                )

                # Tratamento de bloqueio por segurança
                if hasattr(response, 'candidates') and response.candidates:
                    candidate = response.candidates[0]
                    if candidate.finish_reason.name != 'STOP':
                        if candidate.finish_reason.name == 'SAFETY':
                            erros = "\n".join([f"- {r.category.name}: {r.probability.name}"
                                               for r in candidate.safety_ratings if
                                               r.probability.name in ('MEDIUM', 'HIGH')])
                            analise = f"Conteúdo bloqueado pelos filtros de segurança do Gemini.\nMotivos:\n{erros}"
                        else:
                            analise = f"Geração interrompida. Motivo: {candidate.finish_reason.name}"
                    else:
                        analise = candidate.content.parts[0].text
                else:
                    analise = response.text if hasattr(response, 'text') else "Resposta vazia ou bloqueada."

            except Exception as e:
                analise = f"Erro ao chamar a API do Gemini:\n{str(e)}\n\nVerifique se a chave está válida e se há créditos na conta."

            # Atualiza a interface na thread principal
            def atualizar():
                loading.destroy()
                ai_text.insert(tk.END, analise)
                ai_text.config(state=tk.DISABLED)

            self.root.after(0, atualizar)

        threading.Thread(target=analisar_com_gemini, daemon=True).start()

    def treeview_sort_column(self, col, reverse):
        data = [(self.tree.set(k, col), k) for k in self.tree.get_children('')]
        if col == 'dataPublicacao':
            data.sort(key=lambda t: datetime.strptime(t[0], '%d/%m/%Y') if t[0] != '' else datetime.min, reverse=reverse)
        else:
            data.sort(reverse=reverse)

        for idx, (val, k) in enumerate(data):
            self.tree.move(k, '', idx)

        self.tree.heading(col, command=lambda: self.treeview_sort_column(col, not reverse))

    def filter_tree(self, event=None):
        filters = {col: entry.get().lower() for col, entry in self.filter_entries.items() if entry.get()}
        for iid in self.tree.get_children():
            self.tree.detach(iid)

        for iid in map(str, range(len(self.df))):
            row = self.df.iloc[int(iid)]
            if all(filt in str(row[col]).lower() for col, filt in filters.items()):
                self.tree.move(iid, '', 'end')

    def export_to_excel(self):
        path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel", "*.xlsx")])
        if path:
            try:
                self.df.to_excel(path, index=False, engine='openpyxl')
                messagebox.showinfo("Sucesso", f"Exportado com sucesso!\n{path}")
            except Exception as e:
                messagebox.showerror("Erro", f"Não foi possível exportar:\n{e}")


if __name__ == "__main__":
    ctk.set_appearance_mode("Dark")
    ctk.set_default_color_theme("dark-blue")
    root = ctk.CTk()
    app = App(root)
    root.mainloop()
