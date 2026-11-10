
import sqlite3
import json
from statistics import mean, stdev
from datetime import date, timedelta

conexao = sqlite3.connect("athlete_performance.db")
cursor = conexao.cursor()

# Usamos a data mais recente disponível no banco.
cursor.execute("SELECT MAX(data) FROM wellness")
data_atual = cursor.fetchone()[0]

if data_atual is None:
    print("Nenhum registro de recuperação encontrado.")
    raise SystemExit

inicio = (date.fromisoformat(data_atual) - timedelta(days=28)).isoformat()

# Recuperação do dia
cursor.execute("""
SELECT hrv, resting_hr, sleep_seconds, sleep_score
FROM wellness
WHERE data = ?
""", (data_atual,))

hrv, fc, sono, score = cursor.fetchone()

# Histórico anterior ao dia analisado
cursor.execute("""
SELECT hrv, resting_hr
FROM wellness
WHERE data >= ? AND data < ?
ORDER BY data
""", (inicio, data_atual))

historico = cursor.fetchall()

def comparar(valor, valores):
    valores = [v for v in valores if v is not None]

    if valor is None or len(valores) < 7:
        return "Dados insuficientes"

    media = mean(valores)
    desvio = stdev(valores)

    if desvio == 0:
        return "Sem variabilidade histórica"

    z = (valor - media) / desvio

    if abs(z) <= 1:
        return f"Dentro da faixa histórica (z={z:+.2f})"

    return f"Fora da faixa de 1 desvio (z={z:+.2f})"

# Carga diária de todas as modalidades
cursor.execute("""
SELECT dados_json
FROM activities
WHERE substr(data, 1, 10) = ?
""", (data_atual,))

atividades = cursor.fetchall()

cargas = []
for (dados_json,) in atividades:
    treino = json.loads(dados_json)
    carga = treino.get("icu_training_load")
    if carga is not None:
        cargas.append(carga)

print("\n========== ATHLETE PERFORMANCE AI ==========")
print("RELATÓRIO DIÁRIO:", data_atual)

print("\nTREINAMENTO")
print("Atividades:", len(atividades))
print("Carga total registrada:", sum(cargas))
if len(cargas) < len(atividades):
    print("Aviso: existem atividades sem carga disponível.")

print("\nRECUPERAÇÃO")

print("VFC:", hrv, "ms")
print("Análise:", comparar(hrv, [r[0] for r in historico]))

print("\nFC repouso:", fc, "bpm")
print("Análise:", comparar(fc, [r[1] for r in historico]))

if sono is not None:
    horas, resto = divmod(int(sono), 3600)
    minutos = resto // 60
    print(f"\nSono: {horas}h{minutos:02d}")
else:
    print("\nSono: sem dados")

print("Score do sono:", score if score is not None else "Sem dados")

print("\n============================================")

conexao.close()
