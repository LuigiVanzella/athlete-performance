
import sqlite3

conexao = sqlite3.connect("athlete_performance.db")
cursor = conexao.cursor()

cursor.execute("""
SELECT id, nome, esporte, duracao, distancia
FROM activities
ORDER BY data DESC
LIMIT 5
""")

print("ÚLTIMAS 5 ATIVIDADES:\n")

for atividade in cursor.fetchall():
    id, nome, esporte, duracao, distancia = atividade

    print(f"ID: {id}")
    print(f"Nome: {nome}")
    print(f"Esporte: {esporte}")
    print(f"Duração: {duracao / 60:.1f} minutos" if duracao is not None else "Duração: indisponível")
    print(f"Distância: {distancia / 1000:.2f} km" if distancia is not None else "Distância: indisponível")
    print("-" * 40)

conexao.close()
