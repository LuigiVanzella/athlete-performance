
from getpass import getpass
from supabase_client import conectar_supabase

supabase = conectar_supabase()

email = input("Digite seu e-mail do Supabase: ").strip()
senha = getpass("Digite sua senha: ")

try:
    resposta = supabase.auth.sign_in_with_password({
        "email": email,
        "password": senha
    })

    usuario = resposta.user

    print("\nLogin realizado com sucesso!")
    print("ID do atleta:", usuario.id)

    perfil = (
        supabase.table("athletes")
        .select("nome")
        .eq("id", usuario.id)
        .single()
        .execute()
    )

    print("Perfil encontrado:", perfil.data)

except Exception as erro:
    print("\nErro ao realizar login:", erro)
