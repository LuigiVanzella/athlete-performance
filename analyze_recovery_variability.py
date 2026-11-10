
import sqlite3
from statistics import mean, stdev

conexao = sqlite3.connect("athlete_performance.db")
cursor = conexao.cursor()

cursor.execute("""
SELECT data, hrv, resting_hr
FROM wellness
ORDER BY data DESC
LIMIT 29
""")

registros = cursor.fetchall()

# O primeiro registro é o dia que queremos avaliar.
atual = registros[0]

# Os 28 dias anteriores formam a referência.
historico = registros[1:]

def analisar(nome, valores, valor_atual, unidade):
    valores = [v for v in valores if v is not None]

    print(f"\n===== {nome} =====")

    if len(valores) < 7:
        print("Histórico insuficiente.")
        return

    media = mean(valores)
    desvio = stdev(valores)

    print(f"Registros: {len(valores)}")
    print(f"Média histórica: {media:.1f} {unidade}")
    print(f"Desvio-padrão: {desvio:.1f} {unidade}")

    if valor_atual is None:
        print("Valor atual indisponível.")
        return

    diferenca = valor_atual - media

    print(f"Valor atual: {valor_atual:.1f} {unidade}")
    print(f"Diferença: {diferenca:+.1f} {unidade}")

    if desvio > 0:
        z_score = diferenca / desvio
        print(f"Distância da média: {z_score:+.2f} desvios")

        if abs(z_score) <= 1:
            print("Dentro de 1 desvio-padrão da média.")
        else:
            print("Fora de 1 desvio-padrão da média.")

analisar(
    "VFC",
    [r[1] for r in historico],
    atual[1],
    "ms"
)

analisar(
    "FC DE REPOUSO",
    [r[2] for r in historico],
    atual[2],
    "bpm"
)

conexao.close()
