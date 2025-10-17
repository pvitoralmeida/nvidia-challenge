# 🧠 Sistema Multiagentes para Identificação de Startups na América Latina

## 📘 Visão Geral

Este projeto, desenvolvido para o **Inteli Academy Challenge** em parceria com a **NVIDIA**, é um sistema multiagente (MAS) que automatiza a identificação e qualificação de startups latino-americanas com potencial para integrar o programa **NVIDIA Inception**.

A solução enfrenta a dificuldade de encontrar startups promissoras em um ecossistema com informações descentralizadas, utilizando uma abordagem baseada em agentes de IA para pesquisar, analisar e organizar os dados de forma autônoma.

## ⚙️ Tecnologias Utilizadas

* **Linguagem:** Python
* **Orquestração Multiagente:** [CrewAI](https://github.com/joaomdmoura/crewAI)
* **LLM:** Perplexity

## 💡 Como Funciona

### Estratégia de Busca

A metodologia consiste em pesquisar startups que receberam investimentos recentes de **Venture Capitals (VCs)** renomadas na região (como **Kaszek**, **Monashees** e **Canary**). O rigoroso processo de seleção dessas VCs serve como um filtro inicial de qualidade, garantindo que as startups identificadas já possuam um alto potencial validado pelo mercado.

### Arquitetura do Sistema

O sistema utiliza cinco agentes especializados que colaboram para executar o fluxo de trabalho:

| **Agente** | **Função** |
| ------------------------------- | -------------------------------------------------------------------------- |
| 🕵️‍♂️ **Pesquisador** | Encontra startups com base em uma lista pré-definida de VCs.               |
| 📂 **Analisador de Portfólio** | Extrai e enriquece dados a partir das páginas de portfólio das VCs.        |
| 🧩 **Analisador de Startup** | Coleta informações detalhadas sobre cada startup identificada.             |
| ✅ **Revisores (2 no total)** | Validam a coerência dos dados e formatam o resultado final em um arquivo `.csv`. |

### Etapas do Processo

1.  **Buscar por VCs**: Inicia a pesquisa a partir da lista de VCs.
2.  **Analisar Portfólio**: Coleta dados das startups listadas nos portfólios.
3.  **Buscar por Startups**: Aprofunda a pesquisa sobre cada startup encontrada.
4.  **Revisão de Dados**: Valida a consistência das informações.
5.  **Revisão de Formato**: Exporta os dados consolidados para um arquivo `.csv`.

## 📊 Dados Coletados

O output do sistema é um arquivo `.csv` com os seguintes campos para cada startup:

* Nome da Startup
* Data do Investimento
* Venture Capital Investidora
* País Sede
* Site e LinkedIn do Fundador
* Setor de Atuação e Ano de Fundação
* Tecnologias Utilizadas
* Valor e Rodada do Investimento
* Tamanho da Equipe e do Mercado
* Link do GitHub (se disponível)

## 📈 Resultados

Em testes iniciais (3 execuções), o sistema identificou **107 startups** em países como **México, Argentina, Peru, Chile e Colômbia**, principalmente nos setores de **Fintech, Healthtech e Proptech**.

## 🚀 Como Executar

1.  **Clone o repositório:**
    ```
    git clone [https://github.com/](https://github.com/)<usuario>/<repositorio>.git
    cd <repositorio>
    ```
2.  **Instale as dependências:**

3.  **Execute o script principal:**
    ```
    python main.py
    ```

Os resultados serão salvos no diretório `outputs/`.

## 🧾 Estrutura do Repositório
```
.
├── outputs/             # Arquivos CSV gerados pelos agentes  
├── main.py              # Script principal que executa o sistema de agentes
└── README.md            # Este arquivo  
```
---

## 🔍 Pontos de Melhoria

* **Modelos Especializados:** Utilizar LLMs diferentes e mais adequados para cada agente.
* **Visualização de Dados:** Criar um dashboard interativo para explorar os resultados.
* **Sistema de Classificação:** Implementar um ranqueamento automático para priorizar as startups mais promissoras.
