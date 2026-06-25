import json
from pathlib import Path

from berimbeat.config import FAIXAS


def resolver_caminho(caminho):
    raiz_projeto = Path(__file__).resolve().parent.parent
    return raiz_projeto / caminho


def carregar_mapa_json(caminho):
    caminho_completo = resolver_caminho(caminho)

    if not caminho_completo.exists():
        print(f"[MAPA] Arquivo não encontrado: {caminho_completo}")

        return {
            "id": "vazio",
            "nome": "Mapa vazio",
            "arquivo": "",
            "offset": 0.0,
            "notas": [],
        }

    with open(caminho_completo, "r", encoding="utf-8") as arquivo:
        dados = json.load(arquivo)

    notas_validas = []

    for item in dados.get("notas", []):
        try:
            tempo = float(item["tempo"])
            faixa = int(item["faixa"])

        except (KeyError, TypeError, ValueError):
            continue

        if faixa < 0 or faixa >= len(FAIXAS):
            continue

        notas_validas.append({
            "tempo": tempo,
            "faixa": faixa,
        })

    notas_validas.sort(key=lambda nota: nota["tempo"])

    print()
    print("[MAPA] Mapa carregado")
    print(f"[MAPA] Nome: {dados.get('nome', 'sem nome')}")
    print(f"[MAPA] Variante: {dados.get('variante', 'sem variante')}")
    print(f"[MAPA] Arquivo: {caminho_completo}")
    print(f"[MAPA] Notas válidas: {len(notas_validas)}")

    return {
        "id": dados.get("id", "sem_id"),
        "nome": dados.get("nome", "Mapa sem nome"),
        "arquivo": dados.get("arquivo", ""),
        "offset": float(dados.get("offset", 0.0)),
        "variante": dados.get("variante", "sem variante"),
        "notas": notas_validas,
    }