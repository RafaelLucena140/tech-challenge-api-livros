API de Consulta de Livros - Tech Challenge

Este projeto implementa um pipeline de dados completo, desde a extração de dados de livros (via web scraping) até a disponibilização desses dados através de uma API RESTful pública.

Arquitetura

O projeto é dividido em dois componentes principais:

Scraper (scripts/book_scraper.py): Um script Python que navega pelo site books.toscrape.com, extrai os detalhes de todos os livros e os salva em um arquivo CSV local (data/books_scrape_data.csv).

API (api/main.py): Uma API RESTful construída com FastAPI que carrega os dados do CSV para a memória e os expõe através de endpoints JSON.

O fluxo de dados é:
Scraper → data/books_scrape_data.csv → API → Cliente (Usuário)

1. Instruções de Instalação e Configuração

Siga os passos abaixo para configurar o ambiente e instalar as dependências.

Pré-requisitos:

Python 3.8+

pip (gerenciador de pacotes)

Passos:

Clone este repositório:

git clone [https://github.com/SEU-USUARIO/SEU-REPOSITORIO.git](https://github.com/SEU-USUARIO/SEU-REPOSITORIO.git)
cd SEU-REPOSITORIO


(Recomendado) Crie e ative um ambiente virtual:

# Windows
python -m venv .venv
.\.venv\Scripts\activate

# macOS / Linux
python3 -m venv .venv
source .venv/bin/activate


Instale as bibliotecas necessárias:

pip install -r requirements.txt


2. Instruções para Execução

A execução é feita em duas etapas:

Etapa 1: Executar o Scraper

Primeiro, você deve executar o scraper para coletar os dados e criar o arquivo books_scrape_data.csv.

python scripts/book_scraper.py


Você verá o progresso no terminal. Ao final, o arquivo será salvo em data/books_scrape_data.csv.

Etapa 2: Iniciar a API

Com os dados prontos, inicie o servidor da API:

uvicorn api.main:app --reload


api.main refere-se ao arquivo main.py dentro da pasta api.

app é o nome da instância FastAPI dentro do arquivo.

--reload reinicia o servidor automaticamente quando você faz alterações no código.

O servidor estará rodando em http://127.0.0.1:8000.

3. Documentação das Rotas da API

A documentação completa e interativa da API (Swagger UI) é gerada automaticamente pelo FastAPI e está disponível em:

http://127.0.0.1:8000/docs

Endpoints Obrigatórios

GET /api/v1/health

Descrição: Verifica o status da API e a conectividade com os dados.

GET /api/v1/categories

Descrição: Lista todas as categorias de livros únicas.

GET /api/v1/books

Descrição: Lista todos os livros disponíveis na base de dados.

GET /api/v1/books/search

Descrição: Busca livros por título (parcial) e/ou categoria (exata).

Query Params: title (opcional), category (opcional).

GET /api/v1/books/{id}

Descrição: Retorna os detalhes de um livro específico pelo seu id.

4. Exemplos de Chamadas (Requests/Responses)

Você pode usar curl (ou qualquer cliente de API) para testar os endpoints.

Exemplo 1: GET /api/v1/health

curl -X 'GET' '[http://127.0.0.1:8000/api/v1/health](http://127.0.0.1:8000/api/v1/health)'


Resposta:

{
  "status": "ok",
  "database_size": 1000,
  "categories_found": 50
}


Exemplo 2: GET /api/v1/books/search?category=Crime

curl -X 'GET' '[http://127.0.0.1:8000/api/v1/books/search?category=Crime](http://127.0.0.1:8000/api/v1/books/search?category=Crime)'


Resposta (amostra):

[
  {
    "id": 87,
    "Titulo": "The Black Maria",
    "Preco": "£52.15",
    "Rating": 1,
    "Disponibilidade": "In stock (19 available)",
    "Categoria": "Crime",
    "URL_Imagem": "[https://books.toscrape.com/media/cache/58/94/58944114d5f3563a6f1118f09b5c312b.jpg](https://books.toscrape.com/media/cache/58/94/58944114d5f3563a6f1118f09b5c312b.jpg)",
    "URL_Livro": "[https://books.toscrape.com/catalogue/the-black-maria_913/index.html](https://books.toscrape.com/catalogue/the-black-maria_913/index.html)"
  }
  // ... (outros livros da categoria Crime)
]


Exemplo 3: GET /api/v1/books/1

curl -X 'GET' '[http://127.0.0.1:8000/api/v1/books/1](http://127.0.0.1:8000/api/v1/books/1)'


Resposta:

{
  "id": 1,
  "Titulo": "A Light in the Attic",
  "Preco": "£51.77",
  "Rating": 3,
  "Disponibilidade": "In stock (22 available)",
  "Categoria": "Poetry",
  "URL_Imagem": "[https://books.toscrape.com/media/cache/2c/da/2cda635a8cd296b30b5b271dff7e034b.jpg](https://books.toscrape.com/media/cache/2c/da/2cda635a8cd296b30b5b271dff7e034b.jpg)",
  "URL_Livro": "[https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html](https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html)"
}
