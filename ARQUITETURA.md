Plano Arquitetural - Tech Challenge API de Livros

Este documento descreve a arquitetura do pipeline de dados e da API pública desenvolvida para o Tech Challenge, com foco na ingestão, processamento, disponibilização e consumo futuro por cientistas de dados e modelos de Machine Learning.

1. Visão Geral da Arquitetura

O projeto é composto por dois componentes principais: um Pipeline de Ingestão de Dados (Scraper) e uma API de Consulta (Serviço RESTful).

O pipeline é responsável por extrair os dados brutos do site "Books to Scrape" e estruturá-los. A API é responsável por carregar esses dados e servi-los de forma eficiente para o público.

Diagrama do Pipeline

[Site: books.toscrape.com]
         |
         |  1. Extração (Scraping)
         v
[Pipeline Python (scripts/book_scraper.py)]
         |
         |  2. Transformação (Pandas)
         v
[Arquivo de Dados (data/books_scrape_data.csv)]
         |
         |  3. Carregamento (Startup Event)
         v
[API RESTful (api/main.py - FastAPI)]
         |
         |  4. Disponibilização (Deploy)
         v
[Plataforma de Deploy (Render)]
         |
         +------------------+
         |                  |
         v                  v
[Cientista de Dados]   [Modelos de ML]
(Consumindo a API)     (Consumindo a API)


2. Detalhamento do Pipeline

2.1. Ingestão e Processamento (Scraping)

Ferramentas: requests (para requisições HTTP) e BeautifulSoup4 (para parsing do HTML).

Processo: O script scripts/book_scraper.py automatiza a extração.

Paginação: O script inicia na primeira página e navega por todas as páginas seguintes (2, 3, ... 50) localizando o botão "next".

Coleta de Links: Em cada página de listagem, ele coleta as URLs individuais de cada livro.

Extração Detalhada: Para cada livro, o script visita sua página de detalhes para extrair os dados completos (Título, Preço, Rating, Disponibilidade, Categoria, URL da Imagem, etc.).

Armazenamento: Os dados são coletados em uma lista, transformados em um DataFrame do Pandas e, ao final, salvos localmente no arquivo data/books_scrape_data.csv.

2.2. Disponibilização via API

Ferramentas: FastAPI (pelo seu alto desempenho e documentação automática Swagger) e Uvicorn (como servidor ASGI).

Carregamento de Dados: Para máxima performance, a API não lê o arquivo .csv a cada requisição. Em vez disso, ela usa o evento @app.on_event("startup") do FastAPI para carregar todo o CSV para a memória (em uma variável DB) uma única vez, quando o servidor é iniciado.

Banco de Dados em Memória: Os dados (1000 livros) são pequenos o suficiente para residirem na memória RAM do servidor, permitindo que os endpoints de consulta (filtros, buscas, estatísticas) sejam respondidos em milissegundos, sem latência de I/O de disco ou banco de dados.

2.3. Deploy

Plataforma: A API foi deployada na Render (plataforma PaaS).

Gatilho: O Render está conectado ao repositório GitHub. Qualquer git push na branch main dispara um novo build e deploy automaticamente.

Processo de Build: O Render executa pip install -r requirements.txt para instalar as dependências.

Comando de Início: O serviço é iniciado com uvicorn api.main:app --host 0.0.0.0 --port 10000, expondo a API para a internet pública.

3. Cenário de Uso (Cientistas de Dados / ML)

Um cientista de dados ou engenheiro de ML pode usar esta API como a fonte de dados primária para um Sistema de Recomendação de Livros.

3.1. Análise Exploratória de Dados (EDA)

Um Cientista de Dados pode consumir os novos endpoints de estatísticas para uma análise exploratória rápida sem precisar baixar os dados:

Entender o Mercado: Chamar GET /api/v1/stats/overview para ver o preço médio geral e a distribuição de ratings.

Analisar Nichos: Chamar GET /api/v1/stats/categories para identificar quais categorias têm mais livros, quais são as mais caras (maior preco_max) ou as mais baratas (menor preco_min).

Identificar Oportunidades: Chamar GET /api/v1/books/top-rated?min_rating=5 para ver todos os livros 5 estrelas e analisar o que eles têm em comum (categoria, faixa de preço).

3.2. Engenharia de Features e Treinamento

Um Engenheiro de ML pode criar um script que consome a API para gerar um dataset de treinamento:

Buscar Dados Brutos: Chamar GET /api/v1/books para obter todos os 1000 livros.

Engenharia de Features:

Feature Numérica (Preço): Converter Preco (ex: "£51.77") para float (51.77).

Feature Numérica (Rating): Usar Rating (ex: 3) diretamente.

Feature Categórica (Categoria): Usar Categoria (ex: "Mystery") para aplicar One-Hot Encoding.

Feature Textual (Título): Usar Titulo para aplicar TF-IDF ou Word Embeddings.

Feature Numérica (Disponibilidade): Converter Disponibilidade (ex: "In stock (19 available)") para um int (19).

Treinamento: Com essas features, o modelo (ex: Regressão Linear, Random Forest) pode ser treinado para prever o Rating de um livro com base em seu Preco, Categoria e Disponibilidade.

4. Plano de Escalabilidade Futura

A arquitetura atual (CSV + API em memória) é perfeita para 1000 livros, mas não escalaria para milhões.

Plano de Evolução:

Fase 2 (Banco de Dados Gerenciado): Substituir o data/books_scrape_data.csv por um banco de dados NoSQL (como MongoDB Atlas) ou Relacional (como PostgreSQL no Render).

Mudança no Scraper: O book_scraper.py passaria a escrever os dados diretamente no banco de dados, em vez de um CSV.

Mudança na API: A API deixaria de carregar dados no startup. Os endpoints fariam consultas diretas ao banco (ex: db.books.find(...)), tornando a API stateless e permitindo o escalonamento horizontal (múltiplas instâncias da API).

Fase 3 (Pipeline de Dados Assíncrono): Para milhões de livros, o scraping demoraria horas.

O book_scraper.py seria refatorado para rodar como um job agendado (ex: um "Cron Job" no Render) que roda diariamente.

Ele usaria uma fila de tarefas (como Celery com Redis) para processar os livros em paralelo, aumentando drasticamente a velocidade de ingestão.

Fase 4 (Integração de Modelos ML):

Criar um endpoint POST /api/v1/ml/recommend que recebe um user_id e retorna recomendações.

Este endpoint consultaria um modelo de ML (treinado e deployado separadamente, talvez no Vertex AI ou Sagemaker) que foi alimentado pelos dados do banco.