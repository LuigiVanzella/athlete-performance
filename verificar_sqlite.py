
import sqlite3

conexao = sqlite3.connect("athlete_performance.db")
conexao.row_factory = sqlite3.Row

try:
    for tabela in ["activities", "wellness"]:
        print(f"\n--- {tabela.upper()} ---")

        total = conexao.execute(
            f"SELECT COUNT(*) FROM {tabela}"
        ).fetchone()[0]

        print("Total de registros:", total)

        colunas = conexao.execute(
            f"PRAGMA table_info({tabela})"
        ).fetchall()

        print("Colunas:")
        for coluna in colunas:
            print(" -", coluna["name"], coluna["type"])

        exemplo = conexao.execute(
            f"SELECT * FROM {tabela} LIMIT 1"
        ).fetchone()

        if exemplo:
            print("Exemplo (campos principais):")
            for campo in ["id", "data", "nome", "esporte",
                          "duracao", "distancia", "hrv",
                          "resting_hr", "sleep_seconds",
                          "sleep_score", "weight", "ctl", "atl"]:
                if campo in exemplo.keys():
                    print(f" {campo}: {exemplo[campo]}")
finally:
    conexao.close()
