import requests
from bs4 import BeautifulSoup
import pandas as pd
from urllib.parse import urljoin # Para montar URLs completas
import os # Importa 'os' para manipulação de pastas

# --- Seu código inicial (um pouco modificado) ---
# ... existing code ...
# ... existing code ...
    'Five': 5
}

while current_page_url:
# ... existing code ...
# ... existing code ...
    except Exception as e:
        print(f"Erro crítico ao processar a página {current_page_url}: {e}")
        break

# --- Fim do scraping ---

if all_books_data:
# ... existing code ...
    print(df.head())
    
    # 5. Salvar em um arquivo CSV
    try:
        # --- INÍCIO DA MUDANÇA ---
        # Definir o diretório raiz (um nível acima de 'scripts/')
        ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        # Criar a pasta 'data' se ela não existir
        DATA_DIR = os.path.join(ROOT_DIR, "data")
        os.makedirs(DATA_DIR, exist_ok=True)
        
        # Salvar o CSV dentro da pasta 'data'
        csv_path = os.path.join(DATA_DIR, "books_scrape_data.csv")
        
        # Usamos utf-8-sig para garantir compatibilidade com acentos no Excel
        df.to_csv(csv_path, index=False, encoding='utf-8-sig')
        print(f"\nDados salvos com sucesso em '{csv_path}'")
        # --- FIM DA MUDANÇA ---
    except Exception as e:
        print(f"Erro ao salvar CSV: {e}")
else:
# ... existing code ...
