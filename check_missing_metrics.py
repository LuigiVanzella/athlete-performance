
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

completos = 0
incompletos = 0

for linha in atividades:
    treino = json.loads(linha[0])

    potencia = treino.get("icu_average_watts")
    fc = treino.get("average_heartrate")

    if potencia is not None and fc is not None and fc > 0:
        completos += 1
        continue

    incompletos += 1

    print("\nATIVIDADE COM DADOS AUSENTES")
    print("Data:", treino.get("start_date_local", "")[:10])
    print("Nome:", treino.get("name"))
    print("Tipo:", treino.get("type"))
    print("Potência:", potencia)
    print("FC:", fc)
    print("Tem medidor:", treino.get("device_watts"))
    print("-" * 35)

print("\n===== RESUMO =====")
print("Total:", len(atividades))
print("Com potência e FC:", completos)
print("Com dados ausentes:", incompletos)

conexao.close()
