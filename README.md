Tech Challenge: API Pública de Livros

Este repositório contém o projeto final do Tech Challenge, focado na criação de um pipeline de dados completo, desde a extração (web scraping) até a disponibilização via uma API RESTful pública.

Link da API em Produção (Render):
https://tech-challenge-api-livros.onrender.com

Documentação Swagger (Swagger UI):
https://tech-challenge-api-livros.onrender.com/docs

1. Descrição do Projeto e Arquitetura

O objetivo deste projeto foi construir uma infraestrutura de dados para um futuro sistema de recomendação de livros. O pipeline extrai dados do site books.toscrape.com, os processa e os disponibiliza através de uma API RESTful de alta performance.

A arquitetura é composta por dois módulos principais:

Scraper (scripts/book_scraper.py): Um script Python que usa requests e BeautifulSoup para navegar por todas as 50 páginas do site, visitar a página de detalhes de cada um dos 1000 livros e extrair seus dados (título, preço, rating, categoria, etc.). Os dados são salvos em data/books_scrape_data.csv.

API (api/main.py): Uma API RESTful construída com FastAPI que, ao ser iniciada, carrega o arquivo .csv para a memória. Isso garante que todas as consultas (buscas, filtros, estatísticas) sejam respondidas em milissegundos, sem latência de disco.

Deploy (Render): A API está hospedada na plataforma Render, conectada diretamente a este repositório. Qualquer push na branch main aciona um novo deploy automaticamente.

Para um detalhamento completo, consulte o Plano Arquitetural (ARQUITETURA.md).

2. Instruções de Execução (Local)

Siga estes passos para executar o projeto em sua máquina local.

2.1. Pré-requisitos

Python 3.10+

Git (para clonar o repositório)

2.2. Instalação e Configuração

Clone o repositório:

git clone [https://github.com/RafaelLucena140/tech-challenge-api-livros.git](https://github.com/RafaelLucena140/tech-challenge-api-livros.git)
cd tech-challenge-api-livros


Crie e ative um ambiente virtual:

# Windows
python -m venv .venv
.\.venv\Scripts\activate

# macOS / Linux
python3 -m venv .venv
source .venv/bin/activate


Instale as dependências:

pip install -r requirements.txt


2.3. Execução

Execute o Scraper (Obrigatório, 1ª vez):
Este comando irá criar o arquivo data/books_scrape_data.csv.

python scripts/book_scraper.py


Inicie a API localmente:

uvicorn api.main:app --reload


A API estará disponível em http://127.0.0.1:8000.

3. Documentação das Rotas da API

Abaixo estão os endpoints disponíveis, com exemplos de chamadas usando a URL de produção.

Endpoints de Status

GET /api/v1/health

Verifica o status da API e a conectividade com os dados.

Exemplo de Chamada (Browser):
https://tech-challenge-api-livros.onrender.com/api/v1/health

Resposta (200 OK):

{
  "status": "ok",
  "database_size": 1000,
  "categories_found": 50
}


Endpoints Obrigatórios (Core)

GET /api/v1/categories

Lista todas as categorias de livros disponíveis, em ordem alfabética.

Exemplo de Chamada:
https://tech-challenge-api-livros.onrender.com/api/v1/categories

Resposta (200 OK):

[
  "Add a comment",
  "Art",
  "Business",
  "Childrens",
  "Christian",
  ...
]


GET /api/v1/books

Lista todos os 1000 livros da base de dados.

Exemplo de Chamada:
https://tech-challenge-api-livros.onrender.com/api/v1/books

Resposta (200 OK):

[
  {
    "id": 1,
    "Titulo": "A Light in the Attic",
    "Preco": "£51.77",
    "Rating": 3,
    "Disponibilidade": "In stock (22 available)",
    "Categoria": "Poetry",
    "URL_Imagem": "[https://books.toscrape.com/media/cache/2c/da/2cdad67c44b002e7ead0cc35693c0e8b.jpg](https://books.toscrape.com/media/cache/2c/da/2cdad67c44b002e7ead0cc35693c0e8b.jpg)",
    "URL_Livro": "[https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html](https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html)"
  },
  ...
]


GET /api/v1/books/{id}

Retorna detalhes completos de um livro específico pelo ID (1 a 1000).

Exemplo de Chamada (Livro ID 5):
https://tech-challenge-api-livros.onrender.com/api/v1/books/5

Resposta (200 OK):

{
  "id": 5,
  "Titulo": "The Black Maria",
  "Preco": "£52.15",
  "Rating": 1,
  "Disponibilidade": "In stock (19 available)",
  "Categoria": "Poetry",
  ...
}


GET /api/v1/books/search

Busca livros por título (parcial) e/ou categoria (exata). Ambas as buscas são case-insensitive.

Exemplo de Chamada (Busca por título "world"):
https://tech-challenge-api-livros.onrender.com/api/v1/books/search?title=world

Exemplo de Chamada (Busca por categoria "History"):
https://tech-challenge-api-livros.onrender.com/api/v1/books/search?category=History

Exemplo de Chamada (Busca combinada):
https://tech-challenge-api-livros.onrender.com/api/v1/books/search?title=the&category=Mystery

Endpoints Opcionais (Insights & Estatísticas)

GET /api/v1/books/top-rated

Lista os livros com melhor avaliação (Padrão: 5 estrelas).

Exemplo de Chamada (Rating 5):
https://tech-challenge-api-livros.onrender.com/api/v1/books/top-rated

Exemplo de Chamada (Rating 4 ou mais):
https://tech-challenge-api-livros.onrender.com/api/v1/books/top-rated?min_rating=4

GET /api/v1/books/price-range

Filtra livros dentro de uma faixa de preço específica (em £).

Exemplo de Chamada (Livros entre £10 e £15):
https://tech-challenge-api-livros.onrender.com/api/v1/books/price-range?min_price=10&max_price=15

GET /api/v1/stats/overview

Retorna estatísticas gerais da coleção (total de livros, preço médio, distribuição de ratings).

Exemplo de Chamada:
https://tech-challenge-api-livros.onrender.com/api/v1/stats/overview

Resposta (200 OK):

{
  "total_livros": 1000,
  "preco_medio_geral": 35.07,
  "distribuicao_ratings": {
    "rating_1": 226,
    "rating_2": 196,
    "rating_3": 203,
    "rating_4": 179,
    "rating_5": 196
  }
}


GET /api/v1/stats/categories

Retorna estatísticas detalhadas por categoria (quantidade de livros, preços médios, min e max).

Exemplo de Chamada:
https://tech-challenge-api-livros.onrender.com/api/v1/stats/categories

Resposta (200 OK):

[
  {
    "categoria": "Add a comment",
    "total_livros": 67,
    "preco_medio": 35.53,
    "preco_min": 10.02,
    "preco_max": 59.98
  },
  {
    "categoria": "Art",
    "total_livros": 8,
    "preco_medio": 43.1,
    "preco_min": 25.04,
    "preco_max": 58.61
  },
  ...
]
