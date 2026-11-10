
import sqlite3
import json
from collections import defaultdict

conexao = sqlite3.connect("athlete_performance.db")
cursor = conexao.cursor()

cursor.execute("""
SELECT data, esporte, dados_json
FROM activities
ORDER BY data
""")

atividades = cursor.fetchall()

dias = defaultdict(lambda: {
    "carga": 0,
    "quantidade": 0,
    "esportes": set()
})

for data, esporte, dados_json in atividades:
    treino = json.loads(dados_json)

    dia = data[:10]
    carga = treino.get("icu_training_load")

    dias[dia]["quantidade"] += 1
    dias[dia]["esportes"].add(esporte)

    if carga is not None:
        dias[dia]["carga"] += carga

print("\n===== CARGA DIÁRIA TOTAL =====\n")

for dia in sorted(dias):
    info = dias[dia]

    print(f"Data: {dia}")
    print(f"Treinos: {info['quantidade']}")
    print(f"Modalidades: {', '.join(sorted(info['esportes']))}")
    print(f"Carga total: {info['carga']:.1f}")
    print("-" * 35)

conexao.close()
