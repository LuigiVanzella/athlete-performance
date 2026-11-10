
import sqlite3
from statistics import mean

conexao = sqlite3.connect("athlete_performance.db")
cursor = conexao.cursor()

cursor.execute("""
SELECT data, hrv, resting_hr, sleep_seconds, sleep_score
FROM wellness
ORDER BY data DESC
LIMIT 28
""")

registros = cursor.fetchall()

hrvs = [r[1] for r in registros if r[1] is not None]
fcs = [r[2] for r in registros if r[2] is not None]
sonos = [r[3] for r in registros if r[3] is not None]
scores = [r[4] for r in registros if r[4] is not None]

print("\n===== LINHA DE BASE DE RECUPERAÇÃO =====\n")

def mostrar_media(nome, valores, unidade=""):
    if valores:
        print(
            f"{nome}: {mean(valores):.1f} {unidade}"
            f" ({len(valores)} registros)"
        )
    else:
        print(f"{nome}: dados insuficientes")

mostrar_media("VFC média", hrvs, "ms")
mostrar_media("FC repouso média", fcs, "bpm")

if sonos:
    media_sono = mean(sonos)
    horas = int(media_sono // 3600)
    minutos = int((media_sono % 3600) // 60)
    print(f"Sono médio: {horas}h{minutos:02d}")

mostrar_media("Score médio do sono", scores)

print("\n===== ÚLTIMO REGISTRO =====")

data, hrv, fc, sono, score = registros[0]

print("Data:", data)
print("VFC:", hrv)
print("FC repouso:", fc)
print("Score do sono:", score)

conexao.close()
