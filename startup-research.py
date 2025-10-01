
import os
import pandas as pd
from crewai import Agent, Task, Crew, Process, LLM
from crewai_tools import ScrapeWebsiteTool

# --- 1. Configuração Inicial --- #

# Carrega a chave da API do ambiente
PERPLEXITY_API_KEY = os.environ.get("PERPLEXITY_API_KEY")

if not PERPLEXITY_API_KEY:
    raise ValueError("A variável de ambiente PERPLEXITY_API_KEY não está definida.")

# Instancia o LLM para todos os agentes
perplexity_llm = LLM(
    model="sonar",
    base_url="https://api.perplexity.ai/",
    api_key=PERPLEXITY_API_KEY
)

# Instancia a ferramenta de scraping
scrape_tool = ScrapeWebsiteTool()

# --- 2. Definição de Agentes --- #

vc_research_agent = Agent(
    role="Especialista em Venture Capital e Inteligência de Mercado",
    goal="Coletar e organizar informações detalhadas sobre startups de tecnologia na América Latina que receberam investimentos de firmas específicas de Venture Capital",
    backstory=(
        """Você é um analista sênior de venture capital com amplo conhecimento
        do ecossistema de startups latino-americanas e experiência em monitorar
        portfólios de fundos de investimento. Você tem conhecimento atualizado sobre
        o mercado de VC na região e pode identificar startups relevantes investidas
        por essas firmas baseado em seu conhecimento e pesquisa online.
        
        IMPORTANTE: Sua meta é identificar NO MÍNIMO 25 startups únicas para garantir
        que o pipeline final tenha pelo menos 50 startups após o enriquecimento.
        
        Sua missão é identificar startups de tecnologia investidas por VCs listadas,
        trazendo dados confiáveis, claros e estruturados em formato CSV.
        Você nunca inventa informações: apenas utiliza dados concretos que conhece
        ou pode verificar. Suas análises são objetivas e segue estritamente o output esperado."""
    ),
    llm=perplexity_llm,
    verbose=True
)

portfolio_analyser_agent = Agent(
    role="Especialista em Análise de Portfólio e Riqueza de Dados",
    goal="Completar as informações coletadas pelo primeiro agente usando scraping, buscando o máximo de startups possível",
    backstory=("""
        Você é um analista de dados especializado em venture capital e startups.
        Seu foco é examinar cuidadosamente os portfólios oficiais das firmas de VC
        usando ferramentas de web scraping para identificar startups investidas,
        detalhes de rodadas, setores e datas relevantes. 
        
        META CRÍTICA: Você deve garantir que o resultado final tenha PELO MENOS 50 startups únicas.
        Se após o scraping inicial não atingir essa meta, você deve:
        1. Expandir a pesquisa para mais VCs da lista
        2. Incluir startups de diferentes estágios (pre-seed, seed, growth)
        
        Sua missão é complementar e validar as informações coletadas pelo primeiro agente, 
        garantindo precisão, consistência e clareza através de scraping real das páginas web.
        
        INSTRUÇÕES ESPECÍFICAS PARA USO DE FERRAMENTAS:
        1. Use ScrapeWebsiteTool para acessar cada URL de portfólio fornecida
        2. Extraia informações reais das páginas web dos portfólios
        3. Procure por seções como "Portfolio", "Companies", "Investments", "Our Companies"
        4. Para cada startup encontrada, colete:
           - Nome da empresa
           - País Sede
           - Site oficial (quando disponível)
           - Setor/área de atuação
           - Detalhes do investimento (quando disponível)
           - Informações dos fundadores
        5. Se não atingir 50 startups, expanda para incluir:
           - Diferentes estágios de investimento
           - Mais VCs da lista fornecida
        6. Se não encontrar informações específicas, indique como "N/A" ou deixe em branco
        
        Você nunca inventa informações: apenas utiliza dados concretos extraídos das páginas.
        """),
    llm=perplexity_llm,
    tools=[scrape_tool],
    verbose=True
)

startup_analyser_agent = Agent(
    role="Especialista em Análise de Startups e Riqueza de Dados",
    goal="Enriquecer as informações das startups com dados detalhados de mercado, financeiros e operacionais",
    backstory=("""
        Você é um especialista rigoroso em validação de dados. Sua função é verificar se o dataset final contém startups únicas e válidas, 
        removendo duplicatas e entradas inválidas.
        
        METODOLOGIA (6 ETAPAS):
        1. Validação inicial dados básicos
        2. Scraping inteligente site oficial  
        3. Pesquisa complementar LinkedIn/Crunchbase/Github
        4. Cross-validation entre fontes
        5. Enrichment com contexto de mercado
        6. Quality check consistência/completude
        
        FONTES PRIORITÁRIAS: Website oficial, LinkedIn fundadores, Crunchbase/AngelList/Github,
        press releases, relatórios setoriais, plataformas review
        
        DADOS SEMPRE ENRIQUECIDOS: github, TAM/SAM, tech stack, tamanho equipe.
        
        PRINCÍPIO FUNDAMENTAL: NUNCA inventa informações. Dados não encontrados = "N/A".
        Trabalha sistematicamente, documenta fontes, mantém alto padrão qualidade.
        Objetivo: transformar lista básica em database acionável para decisões investimento."""
    ),
    llm=perplexity_llm,
    verbose=True,
    max_iter=3,
    memory=True 
)

revisor_agent = Agent(
    role="Validador de Qualidade de Dados",
    goal="Garantir que o resultado final contenha startups únicas e válidas",
    backstory=("""
        Você é um especialista rigoroso em validação de dados e controle de qualidade.
        Sua única função é verificar se o dataset final está adequado.
        
        REGRAS OBRIGATÓRIAS:
        1. Contar o número total de startups no dataset
        2. Verificar e remover duplicatas (mesmo nome de startup)
        3. Remover entradas inválidas ou vazias
        
        Você é inflexível quanto ao output e não aceita NADA que não seja um CSV puro com as startups.
        """
    ),
    llm=perplexity_llm,
    verbose=True
)

format_guardian_agent = Agent(
    role="Especialista em Padronização de Saída",
    goal="Garantir que as respostas estejam estritamente no formato CSV solicitado",
    backstory=("""
        Você é um especialista em validação de dados e padronização de saídas.
        Seu foco é revisar, ajustar e garantir que qualquer resultado gerado esteja
        exatamente no formato solicitado: uma tabela CSV PURA, sem comentários extras,
        sem blocos markdown e apenas com as colunas exigidas.
        
        Você combina dados de múltiplas fontes, elimina duplicatas, padroniza formatos
        e garante consistência em todas as informações.
        """),
    llm=perplexity_llm,
    verbose=True
)

# --- 3. Definição de Tarefas --- #

vc_research_task = Task(
    description=("""
        Pesquise startups latinas (menos do Brasil) de tecnologia que receberam investimentos em 2023-2025
        pelas seguintes firmas de Venture Capital: {vc_list}.
        
        Para cada VC listada, identifique PELO MENOS 1-2 startups que receberam
        investimentos nesse período. Use seu conhecimento do ecossistema de startups
        latino-americano para identificar:
        
        - Startups de fintech, e-commerce, healthtech, edtech, proptech, logistics
        - Rodadas de investimento Pre-seed, Seed, Series A, Series B, Growth
        - Informações públicas sobre os investimentos
        
        Priorize startups inovadoras em tecnologia e forneça informações detalhadas
        quando disponíveis. Se não tiver informação específica sobre um campo,
        indique como "N/A"."""
    ),
    expected_output="""
    Forneça em formato CSV APENAS a tabela, SEM conclusões, introduções ou texto extra.
    NÃO INVENTE exemplos fictícios - use apenas informações que você conhece.
    As colunas DEVEM SER exatamente as seguintes (nessa ordem):
    - Nome da Startup
    - País Sede
    - Site
    - Setor
    - Ano de Fundação
    - Valor do Investimento
    - Rodada (Seed, Series A, B, etc.)
    - Data do Investimento
    - Venture Capital Investidor
    - LinkedIn do Fundador""",
    agent=vc_research_agent,
    output_file="startups_pesquisa_inicial.csv"
)

portfolio_analyser_task = Task(
    description=("""
        Faça scraping dos portfólios oficiais das firmas de Venture Capital: {portfolio_list}
        
        INSTRUÇÕES OBRIGATÓRIAS:
        1. Para CADA URL fornecida, use ScrapeWebsiteTool(website_url="URL_AQUI") para extrair o conteúdo
        2. Analise o HTML/conteúdo extraído procurando por:
           - Listas de empresas investidas
           - Seções de portfólio
           - Informações de startups de tecnologia
           - Detalhes de investimentos quando disponíveis
        3. Para cada startup encontrada, tente extrair:
           - Nome da empresa
           - Site/URL oficial
           - Setor de atuação
           - Ano de fundação (se disponível)
           - Detalhes do investimento (valor, rodada, data)
           - Informações dos fundadores
        4. Combine com os dados do primeiro agente, mas priorize informações extraídas via scraping
        5. Elimine duplicatas e padronize informações
        
        IMPORTANTE: 
        - Use a ferramenta de scraping para cada URL individual
        - Não invente informações - apenas use dados extraídos
        """),
    expected_output="Formato CSV com as mesmas colunas da tarefa anterior, complementado com os dados do scraping.",
    agent=portfolio_analyser_agent,
    context=[vc_research_task],
    output_file="startups_enriquecidos_portfolio.csv"
)

startup_analysis_task = Task(
    description="Enriqueça os dados de cada startup com informações detalhadas sobre produto, tecnologias, equipe, etc.",
    expected_output="CSV enriquecido com colunas adicionais: Link do Github, Tecnologias Utilizadas, Tamanho da Equipe, Tamanho do Mercado.",
    agent=startup_analyser_agent,
    context=[portfolio_analyser_task], 
    output_file="startups_enriquecidos_startup.csv"
)

review_task = Task(
    description="Valide o dataset coletado, garantindo que todas as startups sejam únicas e válidas, removendo duplicatas e entradas inválidas e garantindo que todas as colunas estejam com valores coerentes.",
    expected_output="Um arquivo CSV contendo todas as startups validadas, sem duplicatas e sem entradas inválidas.",
    agent=revisor_agent,
    context=[startup_analysis_task],
    output_file="startups_revisado.csv"
)

final_csv_task = Task(
    description="Formate a saída final em um único arquivo CSV, garantindo que todos os dados estejam consistentes e bem estruturados.",
    expected_output="Um único arquivo CSV chamado 'startups_final.csv' contendo todas as startups validadas e formatadas.",
    agent=format_guardian_agent,
    context=[review_task],
    output_file="startups_final.csv"
)

# --- 4. Funções de Execução e Mesclagem --- #

def load_and_merge_data(new_data_path, final_data_path):
    """
    Carrega dados existentes, mescla com novos dados e remove duplicatas.
    """
    if not os.path.exists(new_data_path):
        print(f"Aviso: O arquivo {new_data_path} não foi encontrado. Nenhuma nova startup para mesclar.")
        return

    new_df = pd.read_csv(new_data_path)
    
    if os.path.exists(final_data_path):
        existing_df = pd.read_csv(final_data_path)
        combined_df = pd.concat([existing_df, new_df], ignore_index=True)
        combined_df.drop_duplicates(subset=['Nome da Startup', 'Site'], keep='first', inplace=True)
        combined_df.to_csv(final_data_path, index=False)
        print(f"Dados mesclados e deduplicados em {final_data_path}. Total de startups: {len(combined_df)}")
    else:
        new_df.to_csv(final_data_path, index=False)
        print(f"Novo arquivo {final_data_path} criado. Total de startups: {len(new_df)}")

def run_crew_challenge(vc_list, portfolio_list):
    """
    Executa o desafio NVIDIA usando CrewAI para pesquisar e enriquecer dados de startups.
    """
    crew = Crew(
        agents=[
            vc_research_agent,
            portfolio_analyser_agent,
            startup_analyser_agent,
            revisor_agent,
            format_guardian_agent
        ],
        tasks=[
            vc_research_task,
            portfolio_analyser_task,
            startup_analysis_task,
            review_task,
            final_csv_task
        ],
        process=Process.sequential,
        verbose=True
    )

    result = crew.kickoff(inputs={'vc_list': vc_list, 'portfolio_list': portfolio_list})
    
    load_and_merge_data("startups_final.csv", "startups_consolidado.csv")
    
    return result

# --- 5. Listas de VCs e Portfólios --- #

vc_list = [
    "Kaszek Ventures", "Monashees", "Valor Capital Group", "NXTP Ventures", "Canary", "Astella Investimentos", "Ignia Partners",
    "Dalus Capital", "Maya Capital", "Mouro Capital", "Redwood Ventures", "Endeavor Catalyst",
    "Variv Capital", "Seaya Ventures", "Genesis Ventures", "Cometa VC", "Magma Partners"
]

portfolio_list = [
    "https://kaszek.com/companies/",
    "https://www.monashees.com/portfolio",
    "https://www.valorcapitalgroup.com/companies",
    "https://www.nxtp.vc/portfolio",
    "https://canary.com.br/portfolio/",
    "https://www.astella.com.br/pt/portfolio",
    "https://www.ignia.vc/portfolio",
    "https://daluscapital.com/portfolio",
    "https://mayacapital.com/portfolio/",
    "https://www.mourocapital.com/our-portfolio/",
    "https://redwood.ventures/portfolio",
    "https://www.mapeos.endeavor.org.ar/",
    "https://variv.com/",
    "https://seaya.vc/portfolio/",
    "https://genesisventures.vc/genesis-ventures-i/",
    "https://www.cometa.vc/portfolio",
    "https://magmapartners.com/companies"
]

# --- 6. Execução Principal --- #

if __name__ == "__main__":
    print("🎯 NVIDIA Challenge - Pipeline de Coleta e Enriquecimento de Startups")
    print(f"📊 VCs a pesquisar: {len(vc_list)}")
    print(f"🔗 Portfólios para scraping: {len(portfolio_list)}")
    print("-" * 60)
    
    try:
        resultado_final = run_crew_challenge(vc_list, portfolio_list)
        
        print("\n" + "=" * 60)
        print("🎉 EXECUÇÃO CONCLUÍDA COM SUCESSO!")
        print("=" * 60)
        print(f"📄 Resultado final do Crew: {resultado_final}")
        print("\n📁 Arquivos gerados:")
        print("   - startups_final.csv (startups coletadas nesta execução)")
        print("   - startups_consolidado.csv (base de dados acumulada e deduplicada)")
        
    except Exception as e:
        print(f"\n❌ ERRO durante a execução: {e}")
        print("🔧 Verifique se todas as dependências estão instaladas e as chaves de API são válidas.")
