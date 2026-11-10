import json
import sqlite3
from pathlib import Path
from fastapi import FastAPI
from fastapi.responses import FileResponse
from datetime import date, timedelta


app = FastAPI(
    title="Athlete Performance AI",
    description="Dashboard de desempenho e recuperação para triathlon",
    version="1.0.0"
)

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "athlete_performance.db"


@app.get("/")
def inicio():
    return FileResponse(BASE_DIR / "static" / "index.html")


@app.get("/api/resumo")
def resumo():
    conexao = sqlite3.connect(DB_PATH)
    cursor = conexao.cursor()

    cursor.execute("SELECT COUNT(*) FROM activities")
    total_atividades = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM wellness")
    total_wellness = cursor.fetchone()[0]

    cursor.execute("""
        SELECT data, hrv, resting_hr, sleep_seconds, sleep_score
        FROM wellness
        ORDER BY data DESC
        LIMIT 1
    """)


    ultimo = cursor.fetchone()
    conexao.close()

    return {
        "total_atividades": total_atividades,
        "total_registros_recuperacao": total_wellness,
        "ultima_recuperacao": {
            "data": ultimo[0],
            "hrv": ultimo[1],
            "fc_repouso": ultimo[2],
            "sono_segundos": ultimo[3],
            "score_sono": ultimo[4]
        } if ultimo else None
    }



@app.get("/api/carga-diaria")
def carga_diaria():
    conexao = sqlite3.connect(DB_PATH)
    cursor = conexao.cursor()

    cursor.execute("""
        SELECT MAX(substr(data, 1, 10))
        FROM activities
    """)

    ultima_data = cursor.fetchone()[0]

    if ultima_data is None:
        conexao.close()
        return []

    fim = date.fromisoformat(ultima_data)
    inicio = fim - timedelta(days=13)

    cursor.execute("""
        SELECT data, dados_json
        FROM activities
        WHERE substr(data, 1, 10) BETWEEN ? AND ?
    """, (inicio.isoformat(), fim.isoformat()))

    atividades = cursor.fetchall()
    conexao.close()

    cargas = {}

    for data, dados_json in atividades:
        dia = data[:10]
        treino = json.loads(dados_json)

        carga = treino.get("icu_training_load")

        if carga is not None:
            cargas[dia] = cargas.get(dia, 0) + carga

    resultado = []

    for i in range(14):
        dia = inicio + timedelta(days=i)
        data_formatada = dia.isoformat()

        resultado.append({
            "data": data_formatada,
            "carga": cargas.get(data_formatada, 0)
        })

    return resultado



@app.get("/api/historico-recuperacao")
def historico_recuperacao():
    conexao = sqlite3.connect(DB_PATH)
    cursor = conexao.cursor()

    cursor.execute("""
        SELECT MAX(data)
        FROM wellness
    """)

    ultima_data = cursor.fetchone()[0]

    if ultima_data is None:
        conexao.close()
        return []

    fim = date.fromisoformat(ultima_data)
    inicio = fim - timedelta(days=13)

    cursor.execute("""
        SELECT data, hrv, resting_hr, sleep_seconds, sleep_score
        FROM wellness
        WHERE data BETWEEN ? AND ?
        ORDER BY data
    """, (inicio.isoformat(), fim.isoformat()))

    registros = cursor.fetchall()
    conexao.close()

    registros_por_data = {
        registro[0]: registro
        for registro in registros
    }

    resultado = []

    for i in range(14):
        dia = inicio + timedelta(days=i)
        data_formatada = dia.isoformat()

        registro = registros_por_data.get(data_formatada)

        resultado.append({
            "data": data_formatada,
            "hrv": registro[1] if registro else None,
            "fc_repouso": registro[2] if registro else None,
            "sono_segundos": registro[3] if registro else None,
            "score_sono": registro[4] if registro else None
        })

    return resultado



@app.get("/api/carga-recuperacao")
def carga_recuperacao():
    conexao = sqlite3.connect(DB_PATH)
    cursor = conexao.cursor()

    cursor.execute("SELECT MAX(data) FROM wellness")
    ultima_data = cursor.fetchone()[0]

    if ultima_data is None:
        conexao.close()
        return []

    fim = date.fromisoformat(ultima_data)
    inicio = fim - timedelta(days=13)

    cursor.execute("""
        SELECT data, hrv, resting_hr
        FROM wellness
        WHERE data BETWEEN ? AND ?
    """, (inicio.isoformat(), fim.isoformat()))

    recuperacao = {
        data: {"hrv": hrv, "fc_repouso": fc}
        for data, hrv, fc in cursor.fetchall()
    }

    cursor.execute("""
        SELECT data, dados_json
        FROM activities
        WHERE substr(data, 1, 10) BETWEEN ? AND ?
    """, (inicio.isoformat(), fim.isoformat()))

    atividades = cursor.fetchall()
    conexao.close()

    cargas = {}
    quantidades = {}

    for data, dados_json in atividades:
        dia = data[:10]
        treino = json.loads(dados_json)
        carga = treino.get("icu_training_load")

        quantidades[dia] = quantidades.get(dia, 0) + 1

        if carga is not None:
            cargas[dia] = cargas.get(dia, 0) + carga

    resultado = []

    for i in range(14):
        dia = (inicio + timedelta(days=i)).isoformat()
        dados_recuperacao = recuperacao.get(dia, {})

        resultado.append({
            "data": dia,
            "carga": cargas.get(dia),
            "atividades": quantidades.get(dia, 0),
            "hrv": dados_recuperacao.get("hrv"),
            "fc_repouso": dados_recuperacao.get("fc_repouso")
        })

    return resultado



@app.get("/api/carga-acumulada")
def carga_acumulada():
    conexao = sqlite3.connect(DB_PATH)
    cursor = conexao.cursor()

    cursor.execute("""
        SELECT MAX(substr(data, 1, 10))
        FROM activities
    """)

    ultima_data = cursor.fetchone()[0]

    if ultima_data is None:
        conexao.close()
        return []

    fim = date.fromisoformat(ultima_data)

    # Precisamos de 20 dias para calcular
    # 14 pontos com janelas de 7 dias.
    inicio = fim - timedelta(days=19)

    cursor.execute("""
        SELECT data, dados_json
        FROM activities
        WHERE substr(data, 1, 10) BETWEEN ? AND ?
    """, (inicio.isoformat(), fim.isoformat()))

    atividades = cursor.fetchall()
    conexao.close()

    cargas = {}
    atividades_por_dia = {}

    for data, dados_json in atividades:
        dia = data[:10]
        treino = json.loads(dados_json)

        carga = treino.get("icu_training_load")

        atividades_por_dia[dia] = (
            atividades_por_dia.get(dia, 0) + 1
        )

        if carga is not None:
            cargas[dia] = cargas.get(dia, 0) + carga

    resultado = []

    for i in range(14):
        dia = fim - timedelta(days=13 - i)

        carga_7d = 0
        dias_com_treino = 0

        for j in range(7):
            data_janela = (
                dia - timedelta(days=j)
            ).isoformat()

            carga_7d += cargas.get(data_janela, 0)

            if atividades_por_dia.get(data_janela, 0) > 0:
                dias_com_treino += 1

        resultado.append({
            "data": dia.isoformat(),
            "carga_7d": round(carga_7d, 1),
            "dias_com_treino": dias_com_treino
        })

    return resultado


@app.get("/api/fitness-fatigue")
def fitness_fatigue():
    conexao = sqlite3.connect(DB_PATH)
    cursor = conexao.cursor()

    cursor.execute("""
        SELECT data, ctl, atl
        FROM wellness
        ORDER BY data DESC
        LIMIT 30
    """)

    registros = cursor.fetchall()
    conexao.close()

    resultado = []

    for data, ctl, atl in reversed(registros):
        # Diferença simples entre os valores
        # do mesmo registro, não necessariamente
        # o TSB oficial do Intervals.icu.
        diferenca = (
            round(ctl - atl, 1)
            if ctl is not None and atl is not None
            else None
        )

        resultado.append({
            "data": data,
            "fitness": ctl,
            "fatigue": atl,
            "diferenca_ctl_atl": diferenca
        })

    return resultado


@app.get("/api/athlete-insights")
def athlete_insights():
    conexao = sqlite3.connect(DB_PATH)
    cursor = conexao.cursor()

    cursor.execute("""
        SELECT data, ctl, atl, hrv, resting_hr
        FROM wellness
        WHERE ctl IS NOT NULL
          AND atl IS NOT NULL
        ORDER BY data DESC
        LIMIT 1
    """)

    registro = cursor.fetchone()
    conexao.close()

    if registro is None:
        return {
            "mensagem": "Dados insuficientes para análise."
        }

    data, ctl, atl, hrv, resting_hr = registro

    balanco = round(ctl - atl, 1)

    if balanco < 0:
        interpretacao = (
            "A carga aguda está acima da carga crônica. "
            "Isso pode ser esperado em blocos intensos. "
            "Acompanhe também os indicadores de recuperação."
        )
    elif balanco > 0:
        interpretacao = (
            "A carga aguda está abaixo da carga crônica. "
            "Isso pode ocorrer em períodos de redução "
            "de carga ou recuperação."
        )
    else:
        interpretacao = (
            "A carga aguda está próxima da carga crônica."
        )

    return {
        "data": data,
        "fitness": round(ctl, 1),
        "fatigue": round(atl, 1),
        "balanco": balanco,
        "hrv": hrv,
        "fc_repouso": resting_hr,
        "interpretacao": interpretacao
    }


@app.get("/api/tendencia-recuperacao")
def tendencia_recuperacao():
    conexao = sqlite3.connect(DB_PATH)
    cursor = conexao.cursor()

    cursor.execute("""
        SELECT data, hrv, resting_hr
        FROM wellness
        ORDER BY data DESC
        LIMIT 14
    """)

    registros = cursor.fetchall()
    conexao.close()

    if len(registros) < 14:
        return {
            "mensagem": "Histórico insuficiente para comparação."
        }

    recentes = registros[:7]
    anteriores = registros[7:14]

    
    def calcular_media(registros, indice):
        valores = [
            registro[indice]
            for registro in registros
            if registro[indice] is not None
        ]

        quantidade = len(valores)

        if quantidade == 0:
            return None, 0

        media = sum(valores) / quantidade

        return media, quantidade


    hrv_recente, qtd_hrv_recente = calcular_media(recentes, 1)
    hrv_anterior, qtd_hrv_anterior = calcular_media(anteriores, 1)

    fc_recente, qtd_fc_recente = calcular_media(recentes, 2)
    fc_anterior, qtd_fc_anterior = calcular_media(anteriores, 2)


    def calcular_variacao(atual, anterior):
        if atual is None or anterior is None or anterior == 0:
            return None

        return round(((atual - anterior) / anterior) * 100, 1)

    return {
        "periodo_recente": {
            "inicio": recentes[-1][0],
            "fim": recentes[0][0]
        },
        "periodo_anterior": {
            "inicio": anteriores[-1][0],
            "fim": anteriores[0][0]
        },
        "hrv": {
            "quantidade_recente": qtd_hrv_recente,
            "quantidade_anterior": qtd_hrv_anterior,
            "media_recente": round(hrv_recente, 1) if hrv_recente is not None else None,
            "media_anterior": round(hrv_anterior, 1) if hrv_anterior is not None else None,
            "variacao_percentual": calcular_variacao(
                hrv_recente, hrv_anterior
            )
        },
        "fc_repouso": {
            "quantidade_recente": qtd_fc_recente,
            "quantidade_anterior": qtd_fc_anterior,
            "media_recente": round(fc_recente, 1) if fc_recente is not None else None,
            "media_anterior": round(fc_anterior, 1) if fc_anterior is not None else None,
            "variacao_percentual": calcular_variacao(
                fc_recente, fc_anterior
            )
        }
    }



@app.get("/api/analise-recuperacao")
def analise_recuperacao():
    dados = tendencia_recuperacao()

    if "mensagem" in dados:
        return {
            "status": "dados_insuficientes",
            "interpretacao": dados["mensagem"]
        }

    hrv = dados["hrv"]
    fc = dados["fc_repouso"]

    # Exigimos pelo menos 5 medições por semana
    # para cada indicador analisado.
    hrv_confiavel = (
        hrv["quantidade_recente"] >= 5
        and hrv["quantidade_anterior"] >= 5
    )

    fc_confiavel = (
        fc["quantidade_recente"] >= 5
        and fc["quantidade_anterior"] >= 5
    )

    observacoes = []

    if hrv_confiavel:
        variacao = hrv["variacao_percentual"]

        if variacao is not None:
            if variacao <= -10:
                observacoes.append(
                    "A VFC média apresentou redução "
                    "de pelo menos 10% entre as semanas."
                )
            elif variacao >= 10:
                observacoes.append(
                    "A VFC média apresentou aumento "
                    "de pelo menos 10% entre as semanas."
                )
            else:
                observacoes.append(
                    "A VFC média apresentou variação "
                    "inferior a 10% entre as semanas."
                )
    else:
        observacoes.append(
            "A comparação da VFC possui poucas "
            "medições e deve ser interpretada "
            "com cautela."
        )

    if fc_confiavel:
        variacao = fc["variacao_percentual"]

        if variacao is not None:
            if variacao >= 5:
                observacoes.append(
                    "A frequência cardíaca de repouso "
                    "apresentou aumento de pelo menos 5%."
                )
            elif variacao <= -5:
                observacoes.append(
                    "A frequência cardíaca de repouso "
                    "apresentou redução de pelo menos 5%."
                )
            else:
                observacoes.append(
                    "A frequência cardíaca de repouso "
                    "apresentou variação inferior a 5%."
                )
    else:
        observacoes.append(
            "A comparação da frequência cardíaca "
            "de repouso possui poucas medições."
        )

    return {
        "status": (
            "comparacao_completa"
            if hrv_confiavel and fc_confiavel
            else "comparacao_parcial"
        ),
        "hrv_confiavel": hrv_confiavel,
        "fc_confiavel": fc_confiavel,
        "observacoes": observacoes,
        "aviso": (
            "Os limites utilizados são regras "
            "exploratórias, não critérios clínicos "
            "ou recomendações de treinamento."
        )
    }


@app.get("/api/analise-integrada")
def analise_integrada():
    treinamento = athlete_insights()
    recuperacao = analise_recuperacao()
    tendencia = tendencia_recuperacao()

    if "fitness" not in treinamento:
        return {
            "status": "dados_insuficientes",
            "mensagem": "Sem dados de treinamento suficientes."
        }

    balanco = treinamento["balanco"]
    observacoes = []

    # Verificar a relação entre carga aguda e crônica
    if balanco < 0:
        observacoes.append(
            "A carga aguda está acima da carga crônica."
        )
    elif balanco > 0:
        observacoes.append(
            "A carga aguda está abaixo da carga crônica."
        )
    else:
        observacoes.append(
            "A carga aguda está próxima da carga crônica."
        )

    # Avaliar VFC apenas com cobertura suficiente
    hrv_confiavel = recuperacao.get(
        "hrv_confiavel", False
    )

    if hrv_confiavel and "hrv" in tendencia:
        variacao_hrv = tendencia["hrv"]["variacao_percentual"]

        if variacao_hrv is not None and variacao_hrv <= -10:
            observacoes.append(
                "A VFC média apresentou redução de pelo "
                "menos 10% em relação à semana anterior."
            )
    else:
        observacoes.append(
            "A cobertura da VFC é insuficiente para "
            "uma comparação semanal mais consistente."
        )

    # Avaliar frequência cardíaca de repouso
    fc_confiavel = recuperacao.get(
        "fc_confiavel", False
    )

    if fc_confiavel and "fc_repouso" in tendencia:
        variacao_fc = tendencia[
            "fc_repouso"
        ]["variacao_percentual"]

        if variacao_fc is not None and variacao_fc >= 5:
            observacoes.append(
                "A FC de repouso média apresentou aumento "
                "de pelo menos 5%."
            )
        elif variacao_fc is not None:
            observacoes.append(
                "A FC de repouso não apresentou aumento "
                "igual ou superior a 5%."
            )

    # Classificação da qualidade dos dados
    qualidade = (
        "completa"
        if hrv_confiavel and fc_confiavel
        else "parcial"
    )

    return {
        "data": treinamento["data"],
        "fitness": treinamento["fitness"],
        "fatigue": treinamento["fatigue"],
        "balanco": balanco,
        "qualidade_dados": qualidade,
        "observacoes": observacoes,
        "conclusao": (
            "Os indicadores devem ser interpretados "
            "em conjunto com sono, percepção de esforço "
            "e contexto dos treinamentos. Esta análise "
            "não determina prontidão para treinar."
        )
    }



from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from supabase_client import conectar_supabase

seguranca = HTTPBearer()

@app.get("/api/supabase/status")
def status_supabase(
    credenciais: HTTPAuthorizationCredentials = Depends(seguranca)
):
    try:
        supabase = conectar_supabase()

        # Valida o token de autenticação recebido
        token = credenciais.credentials
        usuario = supabase.auth.get_user(token).user

        if not usuario:
            raise HTTPException(
                status_code=401,
                detail="Usuário não autenticado"
            )

        # Faz as consultas usando o token do usuário,
        # para respeitar as políticas RLS.
        supabase.postgrest.auth(token)

        atividades = (
            supabase.table("activities")
            .select("id", count="exact")
            .eq("athlete_id", usuario.id)
            .limit(0)
            .execute()
        )

        recuperacao = (
            supabase.table("wellness")
            .select("id", count="exact")
            .eq("athlete_id", usuario.id)
            .limit(0)
            .execute()
        )

        return {
            "status": "conectado",
            "athlete_id": usuario.id,
            "atividades": atividades.count,
            "recuperacao": recuperacao.count
        }

    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=401,
            detail="Não foi possível validar a autenticação"
        )


@app.get("/api/supabase/atividades")
def listar_atividades_supabase(
    credenciais: HTTPAuthorizationCredentials = Depends(seguranca)
):
    token = credenciais.credentials

    try:
        supabase = conectar_supabase()

        # Identifica o atleta autenticado
        usuario = supabase.auth.get_user(token).user

        if not usuario:
            raise HTTPException(
                status_code=401,
                detail="Usuário não autenticado"
            )

        # Aplica o token às consultas do banco
        supabase.postgrest.auth(token)

        resposta = (
            supabase.table("activities")
            .select(
                "intervals_id,data,nome,esporte,duracao,distancia"
            )
            .eq("athlete_id", usuario.id)
            .order("data", desc=True)
            .execute()
        )

        return {
            "total": len(resposta.data),
            "atividades": resposta.data
        }

    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Erro ao consultar atividades"
        )


@app.get("/api/supabase/recuperacao")
def listar_recuperacao_supabase(
    credenciais: HTTPAuthorizationCredentials = Depends(seguranca)
):
    token = credenciais.credentials

    try:
        supabase = conectar_supabase()

        usuario = supabase.auth.get_user(token).user

        if not usuario:
            raise HTTPException(
                status_code=401,
                detail="Usuário não autenticado"
            )

        supabase.postgrest.auth(token)

        resposta = (
            supabase.table("wellness")
            .select(
                "data,hrv,resting_hr,sleep_seconds,"
                "sleep_score,weight,ctl,atl"
            )
            .eq("athlete_id", usuario.id)
            .order("data", desc=True)
            .execute()
        )

        return {
            "total": len(resposta.data),
            "recuperacao": resposta.data
        }

    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Erro ao consultar recuperação"
        )
