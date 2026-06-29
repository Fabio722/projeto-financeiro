from datetime import datetime, date

# Import psycopg2 lazily inside conectar() to avoid import-time errors in editors
# that don't have the package installed.

# URL de conexão com o banco de dados
DB_URL = "postgresql://postgres:A1980F2350pq@db.pmargckbnntqnjcjigxu.supabase.co:5432/postgres"


def conectar():
    try:
        import importlib
        psycopg2 = importlib.import_module("psycopg2")
    except ModuleNotFoundError:
        raise ImportError("psycopg2 is required but not installed. Install with: pip install psycopg2-binary")
    return psycopg2.connect(DB_URL)


def init_db():
    conn = conectar()
    cursor = conn.cursor()
    # Criar a tabela de movimentacoes
    cursor.execute("""
                   CREATE TABLE IF NOT EXISTS movimentacoes (
                       id SERIAL PRIMARY KEY,
                       tipo VARCHAR(10),   -- 'ganho' ou 'gasto'
                       categoria VARCHAR(50),  -- 'Emprego', 'Moto 99', 'Boletos', 'Investimentos', 'Dia a Dia', etc.
                       valor NUMERIC(10, 2),
                       descricao TEXT,
                       data DATE             -- Salva a data correta
                   )
                   """)
    conn.commit()
    cursor.close()
    conn.close()


def registrar_fluxo(tipo, categoria, valor, descricao, data=None):
    """Registra um fluxo de caixa. Se data for None, usa a data atual."""
    conn = conectar()
    cursor = conn.cursor()

    if data is None:
        data = date.today()
    elif isinstance(data, str):
        # tenta converter string YYYY-MM-DD
        data = datetime.fromisoformat(data).date()

    cursor.execute("""
                   INSERT INTO movimentacoes (tipo, categoria, valor, descricao, data)
                   VALUES (%s, %s, %s, %s, %s)
                   """, (tipo, categoria, valor, descricao, data))
    conn.commit()
    cursor.close()
    conn.close()


# Garantir criação da tabela ao importar o módulo
init_db()

def buscar_resumo_hoje():
    conn = conectar()
    cursor = conn.cursor()
    # Buscar todas as movimentacoes de hoje
    cursor.execute("SELECT tipo, categoria, valor, descricao FROM movimentacoes Where data = CURRENT_DATE")
    resultados = cursor.fetchall()
    cursor.close()
    conn.close()
    return resultados