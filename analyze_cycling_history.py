
import sqlite3
import json

conexao = sqlite3.connect("athlete_performance.db")
cursor = conexao.cursor()

cursor.execute("""
SELECT dados_json
FROM activities
WHERE esporte IN ('Ride', 'VirtualRide')
ORDER BY data ASC
""")

atividades = cursor.fetchall()

print("\n===== HISTÓRICO DE CICLISMO =====\n")

for linha in atividades:
    treino = json.loads(linha[0])

    data = treino.get("start_date_local", "")[:10]
    potencia = treino.get("icu_average_watts")
    fc = treino.get("average_heartrate")
    carga = treino.get("icu_training_load")
    duracao = treino.get("moving_time", 0)

    if potencia is None or fc is None or fc == 0:
        continue

    eficiencia = potencia / fc

    print(f"Data: {data}")
    print(f"Duração: {duracao / 60:.0f} min")
    print(f"Potência média: {potencia:.0f} W")
    print(f"FC média: {fc:.0f} bpm")
    print(f"Relação potência/FC: {eficiencia:.2f} W/bpm")
    print(f"Carga: {carga}")
    print("-" * 35)

conexao.close()
