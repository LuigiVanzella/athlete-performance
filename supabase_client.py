
import os

from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")


def conectar_supabase() -> Client:
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise ValueError(
            "Configure SUPABASE_URL e SUPABASE_KEY no arquivo .env"
        )

    return create_client(SUPABASE_URL, SUPABASE_KEY)


if __name__ == "__main__":
    supabase = conectar_supabase()

    resposta = (
        supabase.table("athletes")
        .select("id")
        .limit(1)
        .execute()
    )

    print("Conexão com Supabase realizada com sucesso!")
    print("Consulta executada:", resposta.data)
