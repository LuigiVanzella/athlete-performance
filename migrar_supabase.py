
import sqlite3
import json
from datetime import datetime
from getpass import getpass
from supabase_client import conectar_supabase

BANCO_LOCAL = "athlete_performance.db"

supabase = conectar_supabase()

email = input("E-mail do Supabase: ").strip()
senha = getpass("Senha do Supabase: ")

resposta = supabase.auth.sign_in_with_password({
    "email": email,
    "password": senha
})

athlete_id = resposta.user.id

print("\nAutenticado com sucesso!")

conexao = sqlite3.connect(BANCO_LOCAL)
conexao.row_factory = sqlite3.Row

try:
    atividades = conexao.execute(
        "SELECT * FROM activities"
    ).fetchall()

    recuperacao = conexao.execute(
        "SELECT * FROM wellness"
    ).fetchall()

    print(f"Atividades encontradas: {len(atividades)}")
    print(f"Registros de recuperação: {len(recuperacao)}")

    confirmar = input(
        "\nDeseja iniciar a migração? (s/n): "
    ).strip().lower()

    if confirmar != "s":
        print("Migração cancelada.")
        raise SystemExit

    print("\nMigrando atividades...")

    for atividade in atividades:
        dados = dict(atividade)

        data = dados["data"]

        # As datas do SQLite não possuem fuso horário.
        # Interpretamos como horário local de São Carlos.
        data_convertida = (
            datetime.fromisoformat(data)
            .replace(
                tzinfo=__import__("datetime").timezone(
                    __import__("datetime").timedelta(hours=-3)
                )
            )
            .isoformat()
        )

        registro = {
            "athlete_id": athlete_id,
            "intervals_id": dados["id"],
            "data": data_convertida,
            "nome": dados["nome"],
            "esporte": dados["esporte"],
            "duracao": dados["duracao"],
            "distancia": dados["distancia"],
            "dados_json": (
                json.loads(dados["dados_json"])
                if dados["dados_json"]
                else None
            )
        }

        supabase.table("activities").upsert(
            registro,
            on_conflict="athlete_id,intervals_id"
        ).execute()

    print("Atividades migradas!")

    print("\nMigrando recuperação...")

    for item in recuperacao:
        dados = dict(item)

        registro = {
            "athlete_id": athlete_id,
            "data": dados["data"],
            "hrv": dados["hrv"],
            "resting_hr": dados["resting_hr"],
            "sleep_seconds": dados["sleep_seconds"],
            "sleep_score": dados["sleep_score"],
            "weight": dados["weight"],
            "ctl": dados["ctl"],
            "atl": dados["atl"]
        }

        supabase.table("wellness").upsert(
            registro,
            on_conflict="athlete_id,data"
        ).execute()

    print("Recuperação migrada!")
    print("\nMigração concluída com sucesso!")

finally:
    conexao.close()
