
import sqlite3
import json

conexao = sqlite3.connect("athlete_performance.db")
cursor = conexao.cursor()

cursor.execute("""
SELECT
    a.data,
    a.dados_json,
    w.hrv,
    w.resting_hr,
    w.sleep_seconds,
    w.sleep_score
FROM activities a
LEFT JOIN wellness w
    ON substr(a.data, 1, 10) = w.data
WHERE a.esporte IN ('Ride', 'VirtualRide')
ORDER BY a.data DESC
LIMIT 10
""")

resultados = cursor.fetchall()

print("\n===== TREINO + RECUPERAÇÃO =====")

for data, dados_json, hrv, fc_repouso, sono, score in resultados:
    treino = json.loads(dados_json)

    print(f"\nData: {data[:10]}")
    print("Treino:", treino.get("name"))
    print("Carga:", treino.get("icu_training_load"))

    print("VFC:", f"{hrv} ms" if hrv is not None else "Sem dados")

    print(
        "FC repouso:",
        f"{fc_repouso} bpm"
        if fc_repouso is not None else "Sem dados"
    )

    if sono is not None:
        horas = int(sono // 3600)
        minutos = int((sono % 3600) // 60)
        print(f"Sono: {horas}h{minutos:02d}")
    else:
        print("Sono: Sem dados")

    print(
        "Score do sono:",
        score if score is not None else "Sem dados"
    )

    print("-" * 35)

conexao.close()
