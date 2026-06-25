from berimbeat.config import (
    Z_INICIO_PISTA,
    Z_ALVO,
    VELOCIDADE_NOTA,
    JANELA_PERFEITO,
    JANELA_BOM,
    TEMPO_APOS_ALVO_PARA_ERRO,
    PONTOS_PERFEITO,
    PONTOS_BOM,
)


def criar_notas(mapa):
    notas = []

    for item in mapa:
        notas.append({
            "tempo": item["tempo"],
            "faixa": item["faixa"],
            "z": Z_INICIO_PISTA,
            "ativa": True,
            "acertada": False,
        })

    return notas


def atualizar_notas(notas, tempo_jogo):
    erros = 0

    for nota in notas:
        if not nota["ativa"]:
            continue

        tempo_restante = nota["tempo"] - tempo_jogo
        nota["z"] = Z_ALVO - tempo_restante * VELOCIDADE_NOTA

        passou_da_janela = tempo_jogo - nota["tempo"] > TEMPO_APOS_ALVO_PARA_ERRO

        if passou_da_janela:
            nota["ativa"] = False
            erros += 1

    return erros


def tentar_acertar(notas, indice_faixa, tempo_jogo):
    melhor_nota = None
    menor_diferenca = None

    for nota in notas:
        if not nota["ativa"]:
            continue

        if nota["faixa"] != indice_faixa:
            continue

        diferenca = abs(tempo_jogo - nota["tempo"])

        if menor_diferenca is None or diferenca < menor_diferenca:
            menor_diferenca = diferenca
            melhor_nota = nota

    if melhor_nota is None:
        return "vazio", 0

    if menor_diferenca <= JANELA_PERFEITO:
        melhor_nota["ativa"] = False
        melhor_nota["acertada"] = True
        return "perfeito", PONTOS_PERFEITO

    if menor_diferenca <= JANELA_BOM:
        melhor_nota["ativa"] = False
        melhor_nota["acertada"] = True
        return "bom", PONTOS_BOM

    return "fora", 0
