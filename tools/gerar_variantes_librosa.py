import json
import sys
from pathlib import Path

import librosa
import numpy as np


RAIZ_PROJETO = Path(__file__).resolve().parent.parent

MUSICAS = {
    "balaio": {
        "nome": "Balaio de Café",
        "arquivo": "assets/music/balaio_de_cafe.ogg",
    },
    "paranaue": {
        "nome": "Paranauê",
        "arquivo": "assets/music/paranaue.ogg",
    },
    "dandara": {
        "nome": "Dandara",
        "arquivo": "assets/music/dandara.ogg",
    },
}


def converter_para_float(valor):
    array = np.asarray(valor).flatten()

    if array.size == 0:
        return 0.0

    return float(array[0])


def limitar_intervalo_minimo(tempos, intervalo_minimo):
    filtrados = []
    ultimo = -999.0

    for tempo in tempos:
        if tempo - ultimo >= intervalo_minimo:
            filtrados.append(float(tempo))
            ultimo = tempo

    return filtrados


def detectar_beats(y, sr):
    bpm_bruto, beat_frames = librosa.beat.beat_track(y=y, sr=sr)
    bpm = converter_para_float(bpm_bruto)
    beat_times = librosa.frames_to_time(beat_frames, sr=sr)

    beat_times = limitar_intervalo_minimo(beat_times, intervalo_minimo=0.32)

    return bpm, beat_times


def salvar_mapa(musica_id, nome_musica, arquivo_audio, nome_variante, bpm, duracao, notas):
    caminho_saida = RAIZ_PROJETO / "assets" / "maps" / f"{musica_id}_{nome_variante}.json"

    mapa = {
        "id": musica_id,
        "nome": nome_musica,
        "arquivo": arquivo_audio,
        "offset": 0.0,
        "ferramenta": "librosa",
        "variante": nome_variante,
        "bpm_estimado": round(float(bpm), 2),
        "duracao": round(float(duracao), 3),
        "notas": notas,
    }

    caminho_saida.parent.mkdir(parents=True, exist_ok=True)

    with open(caminho_saida, "w", encoding="utf-8") as arquivo:
        json.dump(mapa, arquivo, indent=2, ensure_ascii=False)

    print()
    print(f"Mapa gerado: {caminho_saida}")
    print(f"Variante: {nome_variante}")
    print(f"BPM estimado: {bpm:.2f}")
    print(f"Notas: {len(notas)}")

    if duracao > 0:
        print(f"Notas por minuto: {len(notas) / (duracao / 60):.1f}")


def gerar_beat_simples(beat_times, inicio_jogavel):
    padrao = [0, 1, 0, 1, 0, 2, 0, 1]

    notas = []

    for i, tempo in enumerate(beat_times):
        if tempo < inicio_jogavel:
            continue

        notas.append({
            "tempo": round(float(tempo), 3),
            "faixa": padrao[i % len(padrao)],
            "origem": "beat",
        })

    return notas


def gerar_beat_pareado(beat_times, inicio_jogavel, duracao):
    atraso_segunda_nota = 0.22
    acento_atabaque_a_cada = 4

    notas = []
    indice_jogavel = 0

    for tempo in beat_times:
        if tempo < inicio_jogavel:
            continue

        # Primeira nota do par: berimbau.
        notas.append({
            "tempo": round(float(tempo), 3),
            "faixa": 0,
            "origem": "beat_par_berimbau",
        })

        tempo_segunda = tempo + atraso_segunda_nota

        if tempo_segunda < duracao:
            if indice_jogavel % acento_atabaque_a_cada == acento_atabaque_a_cada - 1:
                faixa_segunda = 2
                origem = "beat_par_atabaque"
            else:
                faixa_segunda = 1
                origem = "beat_par_pandeiro"

            notas.append({
                "tempo": round(float(tempo_segunda), 3),
                "faixa": faixa_segunda,
                "origem": origem,
            })

        indice_jogavel += 1

    notas.sort(key=lambda nota: nota["tempo"])
    return notas


def gerar_variantes(musica_id, inicio_jogavel):
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
    print(f"Início jogável: {inicio_jogavel:.2f}s")

    y, sr = librosa.load(caminho_audio, sr=None, mono=True)
    duracao = librosa.get_duration(y=y, sr=sr)

    print(f"Duração: {duracao:.2f}s")

    # Variante 1: beat simples no áudio original.
    bpm_original, beats_original = detectar_beats(y, sr)

    notas_beat_simples = gerar_beat_simples(beats_original, inicio_jogavel)

    salvar_mapa(
        musica_id,
        dados["nome"],
        dados["arquivo"],
        "beat_simples",
        bpm_original,
        duracao,
        notas_beat_simples,
    )

    # Variante 2: beat pareado no áudio original.
    notas_beat_pareado = gerar_beat_pareado(beats_original, inicio_jogavel, duracao)

    salvar_mapa(
        musica_id,
        dados["nome"],
        dados["arquivo"],
        "beat_pareado",
        bpm_original,
        duracao,
        notas_beat_pareado,
    )

    # Variante 3: separa componente percussiva e detecta beat nela.
    print()
    print("Separando componente percussiva com HPSS...")

    _, y_percussivo = librosa.effects.hpss(y)

    bpm_percussivo, beats_percussivo = detectar_beats(y_percussivo, sr)

    notas_percussivo_pareado = gerar_beat_pareado(
        beats_percussivo,
        inicio_jogavel,
        duracao,
    )

    salvar_mapa(
        musica_id,
        dados["nome"],
        dados["arquivo"],
        "percussivo_pareado",
        bpm_percussivo,
        duracao,
        notas_percussivo_pareado,
    )


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso:")
        print("python tools/gerar_variantes_librosa.py balaio")
        print("python tools/gerar_variantes_librosa.py balaio 8.0")
        sys.exit(0)

    musica_id = sys.argv[1]

    if len(sys.argv) >= 3:
        inicio_jogavel = float(sys.argv[2])
    else:
        inicio_jogavel = 0.0

    gerar_variantes(musica_id, inicio_jogavel)