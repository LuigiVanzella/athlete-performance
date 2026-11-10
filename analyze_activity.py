
import sqlite3
import json

conexao = sqlite3.connect("athlete_performance.db")
cursor = conexao.cursor()

cursor.execute("""
SELECT dados_json
FROM activities
WHERE id = ?
""", ("i207995181",))

resultado = cursor.fetchone()

if resultado is None:
    print("Atividade não encontrada.")
    conexao.close()
    raise SystemExit

atividade = json.loads(resultado[0])

def formatar_tempo(segundos):
    horas = int(segundos // 3600)
    minutos = int((segundos % 3600) // 60)
    return f"{horas}h{minutos:02d}min"

def analisar_ciclismo(dados):
    potencia = dados.get("icu_average_watts")
    potencia_ponderada = dados.get("icu_weighted_avg_watts")
    ftp = dados.get("icu_ftp")
    fc = dados.get("average_heartrate")
    carga = dados.get("icu_training_load")
    desacoplamento = dados.get("decoupling")

    print("\n===== ANÁLISE DE CICLISMO =====")

    print("Treino:", dados.get("name"))
    print("Duração:", formatar_tempo(dados.get("moving_time", 0)))

    distancia = dados.get("distance")
    if distancia is not None:
        print(f"Distância: {distancia / 1000:.2f} km")

    if potencia is not None:
        print(f"Potência média: {potencia} W")

    if potencia_ponderada is not None:
        print(f"Potência ponderada: {potencia_ponderada} W")

    if ftp and potencia_ponderada is not None:
        intensidade = potencia_ponderada / ftp * 100
        print(f"Intensidade relativa: {intensidade:.1f}%")

    if fc is not None:
        print(f"FC média: {fc} bpm")

    if carga is not None:
        print(f"Carga do treino: {carga}")

    if desacoplamento is not None:
        print(f"Desacoplamento: {desacoplamento:.1f}%")

        if abs(desacoplamento) > 5:
            print(
                "Observação: desacoplamento elevado "
                "em relação ao critério exploratório de 5%. "
                "Interpretar conforme o tipo de treino."
            )

analisar_ciclismo(atividade)

conexao.close()
