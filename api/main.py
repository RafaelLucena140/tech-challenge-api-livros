import pandas as pd
import uvicorn
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional, Dict
import os # Para verificar se o arquivo existe
from collections import Counter, defaultdict
import re

# --- DEFINIR CAMINHO RAIZ ---
# ... (caminho ROOT_DIR como antes)
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# --- Configuração da Aplicação FastAPI ---
app = FastAPI(
    title="API de Livros - Tech Challenge",
    description="Uma API para consultar dados de livros extraídos do 'books.toscrape.com'.",
    version="1.0.0"
)

# --- Variáveis Globais (Nosso "Banco de Dados" em memória) ---
DB: List[dict] = []
CATEGORIES: set = set()

# --- Modelos Pydantic (para validação e Swagger) ---

class Book(BaseModel):
    id: int
    Titulo: str
    Preco: str 
    Rating: int
    Disponibilidade: str
    Categoria: str
    URL_Imagem: str
    URL_Livro: str

# --- INÍCIO DOS NOVOS MODELOS (para Endpoints Opcionais) ---

class RatingDistribution(BaseModel):
    rating_1: int
    rating_2: int
    rating_3: int
    rating_4: int
    rating_5: int

class StatsOverview(BaseModel):
    total_livros: int
    preco_medio_geral: Optional[float]
    distribuicao_ratings: RatingDistribution

class CategoryStats(BaseModel):
    categoria: str
    total_livros: int
    preco_medio: Optional[float]
    preco_min: Optional[float]
    preco_max: Optional[float]

# --- FIM DOS NOVOS MODELOS ---


# --- Funções Helper ---

def parse_price(price_str: str) -> Optional[float]:
    """
    Converte uma string de preço (ex: '£51.77') para um float.
    Retorna None se a conversão falhar.
    """
    try:
        # Remove qualquer caractere que não seja dígito ou ponto
        # (Isso lida com '£' e outros símbolos)
        price_float = float(re.sub(r"[^0-9.]", "", price_str))
        return price_float
    except (ValueError, TypeError):
        return None

# --- Lógica de Carregamento dos Dados ---

@app.on_event("startup")
def load_database():
    """
    Carrega os dados do CSV para a memória ao iniciar a API.
    """
    global DB, CATEGORIES
    
    csv_path = os.path.join(ROOT_DIR, "data", "books_scrape_data.csv")
    
    if not os.path.exists(csv_path):
        print(f"AVISO: Arquivo '{csv_path}' não encontrado.")
        print("Por favor, execute o 'book_scraper.py' primeiro para gerar os dados.")
        return 

    try:
        df = pd.read_csv(csv_path)
        
        # Adiciona um ID simples baseado no índice (começando em 1)
        df.reset_index(inplace=True)
        df['id'] = df.index + 1
        
        DB = df.to_dict('records')
        CATEGORIES = set(df['Categoria'].unique())
        
        print(f"Banco de dados carregado. Total de {len(DB)} livros e {len(CATEGORIES)} categorias.")
        
    except Exception as e:
        print(f"Erro crítico ao carregar o CSV: {e}")

# --- Endpoints Obrigatórios ---

# 1. Health Check
@app.get("/api/v1/health", tags=["Status"])
def get_health():
    """
    Verifica o status da API e a conectividade com os dados.
    """
    if not DB:
        raise HTTPException(status_code=503, detail="Banco de dados não carregado. Execute o scraper.")
    
    return {
        "status": "ok",
        "database_size": len(DB),
        "categories_found": len(CATEGORIES)
    }

# 2. Listar todas as categorias
@app.get("/api/v1/categories", tags=["Livros"], response_model=List[str])
def get_categories():
    """
    Lista todas as categorias de livros disponíveis.
    """
    if not CATEGORIES:
         raise HTTPException(status_code=404, detail="Nenhuma categoria encontrada")
    return sorted(list(CATEGORIES))

# 3. Listar todos os livros
@app.get("/api/v1/books", tags=["Livros"], response_model=List[Book])
def get_books():
    """
    Lista todos os livros disponíveis na base de dados.
    """
    return DB

# 4. Buscar livros
@app.get("/api/v1/books/search", tags=["Livros"], response_model=List[Book])
def search_books(
    title: Optional[str] = None,
    category: Optional[str] = None
):
    """
    Busca livros por título e/ou categoria.
    A busca no título é case-insensitive e parcial.
    A busca na categoria é case-insensitive e exata.
    """
    results = DB
    
    if title:
        results = [book for book in results if title.lower() in book['Titulo'].lower()]
        
    if category:
        results = [book for book in results if category.lower() == book['Categoria'].lower()]
        
    if not results and (title or category):
        raise HTTPException(status_code=404, detail="Nenhum livro encontrado para os critérios de busca")

    return results

# --- INÍCIO DOS ENDPOINTS OPCIONAIS (Livros) ---

@app.get("/api/v1/books/top-rated", tags=["Livros"], response_model=List[Book])
def get_top_rated_books(
    min_rating: int = Query(5, ge=1, le=5)
):
    """
    Lista os livros com a avaliação mais alta (padrão: 5 estrelas).
    Use o parâmetro 'min_rating' para definir a nota mínima (ex: 4 ou 5).
    """
    # Filtra livros que tenham o rating igual ou superior ao min_rating
    results = [book for book in DB if book.get('Rating', 0) >= min_rating]
    
    if not results:
        raise HTTPException(status_code=404, detail=f"Nenhum livro encontrado com rating >= {min_rating}")
        
    # Retorna os livros ordenados pelo rating (maior primeiro)
    return sorted(results, key=lambda x: x.get('Rating', 0), reverse=True)

@app.get("/api/v1/books/price-range", tags=["Livros"], response_model=List[Book])
def get_books_by_price_range(
    min_price: float = Query(0.0, ge=0),
    max_price: float = Query(9999.0, ge=0)
):
    """
    Filtra livros dentro de uma faixa de preço específica (em £).
    """
    if min_price > max_price:
        raise HTTPException(status_code=400, detail="O 'min_price' não pode ser maior que o 'max_price'")
        
    results = []
    for book in DB:
        price = parse_price(book.get('Preco'))
        if price is not None and min_price <= price <= max_price:
            results.append(book)
            
    if not results:
        raise HTTPException(status_code=404, detail="Nenhum livro encontrado nessa faixa de preço")

    # Retorna os livros ordenados pelo preço (menor primeiro)
    return sorted(results, key=lambda x: parse_price(x.get('Preco')) or 0.0)

# --- FIM DOS ENDPOINTS OPCIONAIS (Livros) ---

# 5. Obter um livro por ID (DEVE SER O ÚLTIMO dos /books/...)
@app.get("/api/v1/books/{id}", tags=["Livros"], response_model=Book)
def get_book_by_id(id: int):
    """
    Retorna detalhes completos de um livro específico pelo ID.
    """
    result = next((book for book in DB if book['id'] == id), None)
    
    if result is None:
        raise HTTPException(status_code=404, detail=f"Livro com id {id} não encontrado")
    
    return result

# --- INÍCIO DOS ENDPOINTS OPCIONAIS (Estatísticas) ---

@app.get("/api/v1/stats/overview", tags=["Estatísticas"], response_model=StatsOverview)
def get_stats_overview():
    """
    Retorna estatísticas gerais da coleção (total de livros, preço médio, distribuição de ratings).
    """
    if not DB:
        raise HTTPException(status_code=503, detail="Banco de dados não carregado")

    # 1. Total de livros
    total_livros = len(DB)
    
    # 2. Preço médio
    prices = [parse_price(b.get('Preco')) for b in DB]
    valid_prices = [p for p in prices if p is not None]
    preco_medio_geral = round(sum(valid_prices) / len(valid_prices), 2) if valid_prices else None
    
    # 3. Distribuição de ratings
    ratings = [b.get('Rating', 0) for b in DB]
    rating_counts = Counter(ratings)
    
    distribuicao = RatingDistribution(
        rating_1=rating_counts.get(1, 0),
        rating_2=rating_counts.get(2, 0),
        rating_3=rating_counts.get(3, 0),
        rating_4=rating_counts.get(4, 0),
        rating_5=rating_counts.get(5, 0)
    )
    
    return StatsOverview(
        total_livros=total_livros,
        preco_medio_geral=preco_medio_geral,
        distribuicao_ratings=distribuicao
    )

@app.get("/api/v1/stats/categories", tags=["Estatísticas"], response_model=List[CategoryStats])
def get_stats_by_category():
    """
    Retorna estatísticas detalhadas por categoria (quantidade de livros, preços por categoria).
    """
    if not DB:
        raise HTTPException(status_code=503, detail="Banco de dados não carregado")

    # Agrupa os livros por categoria
    # Usamos defaultdict para facilitar a criação de listas
    grouped_books = defaultdict(list)
    for book in DB:
        grouped_books[book.get('Categoria', 'Sem Categoria')].append(book)
        
    final_stats = []
    
    # Calcula estatísticas para cada categoria
    for categoria, livros in grouped_books.items():
        total_livros = len(livros)
        
        # Calcula estatísticas de preço
        prices = [parse_price(b.get('Preco')) for b in livros]
        valid_prices = [p for p in prices if p is not None]
        
        if valid_prices:
            preco_medio = round(sum(valid_prices) / len(valid_prices), 2)
            preco_min = round(min(valid_prices), 2)
            preco_max = round(max(valid_prices), 2)
        else:
            preco_medio = None
            preco_min = None
            preco_max = None
            
        final_stats.append(CategoryStats(
            categoria=categoria,
            total_livros=total_livros,
            preco_medio=preco_medio,
            preco_min=preco_min,
            preco_max=preco_max
        ))

    # Retorna a lista ordenada pelo nome da categoria
    return sorted(final_stats, key=lambda x: x.categoria)

# --- FIM DOS ENDPOINTS OPCIONAIS ---

# --- Execução da API ---

if __name__ == "__main__":
    """
    Este bloco permite executar a API diretamente com 'python api/main.py'
    Para desenvolvimento, é recomendado usar: 'uvicorn api.main:app --reload'
    """
    print("Iniciando a API com uvicorn...")
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)

