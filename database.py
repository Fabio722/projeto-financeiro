import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def conectar():
    db_url = os.getenv("DB_URL")
    if not db_url:
        raise ValueError("ERRO: DB_URL não configurada no ambiente.")
    return psycopg2.connect(db_url)

def init_db():
    """Inicializa todas as tabelas necessárias para o seu bot financeiro."""
    conn = conectar()
    cursor = conn.cursor()
    
    # 1. Tabela de Categorias (ex: Alimentação, Transporte, Salário)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS categorias (
            id SERIAL PRIMARY KEY,
            nome VARCHAR(50) UNIQUE NOT NULL,
            tipo VARCHAR(10) NOT NULL -- 'ganho' ou 'gasto'
        )
    ''')
    
    # 2. Tabela de Movimentações
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS movimentacoes (
            id SERIAL PRIMARY KEY,
            categoria_id INTEGER REFERENCES categorias(id),
            valor REAL NOT NULL,
            descricao TEXT,
            data TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    cursor.close()
    conn.close()
    print("Tabelas configuradas com sucesso!")

def inserir_movimentacao(categoria_id, valor, descricao):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO movimentacoes (categoria_id, valor, descricao) VALUES (%s, %s, %s)",
        (categoria_id, valor, descricao)
    )
    conn.commit()
    cursor.close()
    conn.close()