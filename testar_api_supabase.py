
import requests
from getpass import getpass
from supabase_client import conectar_supabase

supabase = conectar_supabase()

email = input("E-mail do Supabase: ").strip()
senha = getpass("Senha do Supabase: ")

try:
    # Realiza o login
    resposta = supabase.auth.sign_in_with_password({
        "email": email,
        "password": senha
    })

    token = resposta.session.access_token

    # Consulta nossa API FastAPI
    url = "http://127.0.0.1:8000/api/supabase/recuperacao"

    resultado = requests.get(
        url,
        headers={
            "Authorization": f"Bearer {token}"
        },
        timeout=15
    )

    print("\nStatus HTTP:", resultado.status_code)

    dados = resultado.json()

    
    if resultado.status_code == 200:
        print("Total de registros:", dados["total"])

        print("\nÚltimos 3 registros:")
        for registro in dados["recuperacao"][:3]:
            print(
                "Data:", registro["data"],
                "| HRV:", registro["hrv"],
                "| FC repouso:", registro["resting_hr"],
                "| CTL:", registro["ctl"],
                "| ATL:", registro["atl"]
            )
    else:
        print("Erro:", dados)


except Exception as erro:
    print("\nErro:", erro)
