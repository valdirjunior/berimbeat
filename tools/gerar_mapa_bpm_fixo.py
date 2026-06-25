import json
import sys
from pathlib import Path

import librosa


RAIZ_PROJETO = Path(__file__).resolve().parent.parent

MUSICAS = {
    "balaio": {
        "nome": "Balaio de Café",
        "arquivo": "assets/music/balaio_de_cafe.ogg",
        "bpm": 76.0,
    },
    "paranaue": {
        "nome": "Paranauê",
        "arquivo": "assets/music/paranaue.ogg",
        "bpm": 117.45,
    },
    "dandara": {
        "nome": "Dandara",
        "arquivo": "assets/music/dandara.ogg",
        "bpm": 76.0,
    },
}


def salvar_mapa(musica_id, dados_musica, nome_variante, bpm, duracao, inicio_jogavel, notas):
    caminho_saida = (
        RAIZ_PROJETO
        / "assets"
        / "maps"
        / f"{musica_id}_{nome_variante}.json"
    )

    mapa = {
        "id": musica_id,
        "nome": dados_musica["nome"],
        "arquivo": dados_musica["arquivo"],
        "offset": 0.0,
        "ferramenta": "bpm_fixo",
        "variante": nome_variante,
        "bpm": round(float(bpm), 3),
        "inicio_jogavel": round(float(inicio_jogavel), 3),
        "duracao": round(float(duracao), 3),
        "notas": notas,
    }

    caminho_saida.parent.mkdir(parents=True, exist_ok=True)

    with open(caminho_saida, "w", encoding="utf-8") as arquivo:
        json.dump(mapa, arquivo, indent=2, ensure_ascii=False)

    print()
    print(f"Mapa gerado: {caminho_saida}")
    print(f"Variante: {nome_variante}")
    print(f"BPM usado: {bpm}")
    print(f"Início jogável: {inicio_jogavel:.3f}s")
    print(f"Total de notas: {len(notas)}")

    if duracao > 0:
        print(f"Notas por minuto: {len(notas) / (duracao / 60):.1f}")


def gerar_76_pareado(bpm, inicio_jogavel, duracao):
    """
    Usa o BPM base de 76.

    Cada beat principal gera:
    - Berimbau no tempo do beat
    - Pandeiro um pouco depois
    - Atabaque no lugar do pandeiro a cada 4 beats

    Sensação:
    0,1... 0,1... 0,1... 0,2...
    """

    duracao_beat = 60.0 / bpm

    atraso_segunda_nota = 0.24
    acento_atabaque_a_cada = 4

    notas = []

    tempo = inicio_jogavel
    indice_beat = 0

    while tempo < duracao:
        notas.append({
            "tempo": round(tempo, 3),
            "faixa": 0,
            "origem": "bpm76_berimbau",
        })

        tempo_segunda = tempo + atraso_segunda_nota

        if tempo_segunda < duracao:
            if indice_beat % acento_atabaque_a_cada == acento_atabaque_a_cada - 1:
                faixa_segunda = 2
                origem = "bpm76_atabaque"
            else:
                faixa_segunda = 1
                origem = "bpm76_pandeiro"

            notas.append({
                "tempo": round(tempo_segunda, 3),
                "faixa": faixa_segunda,
                "origem": origem,
            })

        tempo += duracao_beat
        indice_beat += 1

    return notas


def gerar_152_grade(bpm_base, inicio_jogavel, duracao):
    """
    Usa o double-time: 152 BPM.

    Como 76 BPM tem 4 beats por compasso,
    usamos 8 subdivisões por compasso no double-time.

    Padrão:
    0, 1, pausa, 0, 1, pausa, 0, 2
    """

    bpm_double = bpm_base * 2.0
    duracao_slot = 60.0 / bpm_double

    padrao = [
        0,
        1,
        None,
        0,
        1,
        None,
        0,
        2,
    ]

    notas = []

    tempo = inicio_jogavel
    indice_slot = 0

    while tempo < duracao:
        faixa = padrao[indice_slot % len(padrao)]

        if faixa is not None:
            notas.append({
                "tempo": round(tempo, 3),
                "faixa": faixa,
                "origem": "bpm152_grade",
            })

        tempo += duracao_slot
        indice_slot += 1

    return notas


def gerar_mapas(musica_id, inicio_jogavel):
    if musica_id not in MUSICAS:
        print(f"Música desconhecida: {musica_id}")
        print(f"Opções: {', '.join(MUSICAS.keys())}")
        return

    dados = MUSICAS[musica_id]
    caminho_audio = RAIZ_PROJETO / dados["arquivo"]

    if not caminho_audio.exists():
        print(f"Arquivo de áudio não encontrado: {caminho_audio}")
        return

    print(f"Lendo áudio: {caminho_audio}")

    y, sr = librosa.load(caminho_audio, sr=None, mono=True)
    duracao = librosa.get_duration(y=y, sr=sr)

    bpm = dados["bpm"]

    print(f"Duração: {duracao:.3f}s")
    print(f"BPM base: {bpm}")
    print(f"Double-time: {bpm * 2.0}")
    print(f"Início jogável: {inicio_jogavel:.3f}s")

    notas_76_pareado = gerar_76_pareado(
        bpm=bpm,
        inicio_jogavel=inicio_jogavel,
        duracao=duracao,
    )

    salvar_mapa(
        musica_id=musica_id,
        dados_musica=dados,
        nome_variante="bpm76_pareado",
        bpm=bpm,
        duracao=duracao,
        inicio_jogavel=inicio_jogavel,
        notas=notas_76_pareado,
    )

    notas_152_grade = gerar_152_grade(
        bpm_base=bpm,
        inicio_jogavel=inicio_jogavel,
        duracao=duracao,
    )

    salvar_mapa(
        musica_id=musica_id,
        dados_musica=dados,
        nome_variante="bpm152_grade",
        bpm=bpm * 2.0,
        duracao=duracao,
        inicio_jogavel=inicio_jogavel,
        notas=notas_152_grade,
    )


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso:")
        print("python tools/gerar_mapa_bpm_fixo.py balaio")
        print("python tools/gerar_mapa_bpm_fixo.py balaio 2.8")
        print("python tools/gerar_mapa_bpm_fixo.py balaio 3.32")
        sys.exit(0)

    musica_id = sys.argv[1]

    if len(sys.argv) >= 3:
        inicio_jogavel = float(sys.argv[2])
    else:
        inicio_jogavel = 2.8

    gerar_mapas(musica_id, inicio_jogavel)