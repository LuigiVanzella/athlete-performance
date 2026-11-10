
import sqlite3
import json

conexao = sqlite3.connect("athlete_performance.db")
cursor = conexao.cursor()

ids = {
    "CICLISMO": "i207995181",
    "CORRIDA": "i207846302"
}

palavras_chave = [
    "power", "watts", "ftp", "load",
    "threshold", "zone", "pace",
    "heartrate", "decoupling", "intensity"
]

for modalidade, activity_id in ids.items():
    cursor.execute(
        "SELECT dados_json FROM activities WHERE id = ?",
        (activity_id,)
    )

    resultado = cursor.fetchone()

    if resultado is None:
        print(f"{modalidade}: não encontrada")
        continue

    dados = json.loads(resultado[0])

    print(f"\n===== {modalidade} =====")

    for campo, valor in dados.items():
        if any(p in campo.lower() for p in palavras_chave):
            print(f"{campo}: {str(valor)[:150]}")

conexao.close()
