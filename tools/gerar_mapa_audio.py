import json
import sys
from pathlib import Path

import librosa
import numpy as np


RAIZ_PROJETO = Path(__file__).resolve().parent.parent

MUSICAS = {
    "paranaue": {
        "nome": "Paranauê",
        "arquivo": "assets/music/paranaue.ogg",
        "saida": "assets/maps/paranaue_librosa.json",
    },
    "balaio": {
        "nome": "Balaio de Café",
        "arquivo": "assets/music/balaio_de_cafe.ogg",
        "saida": "assets/maps/balaio_librosa.json",
    },
    "dandara": {
        "nome": "Dandara",
        "arquivo": "assets/music/dandara.ogg",
        "saida": "assets/maps/dandara_librosa.json",
    },
}


def limitar_intervalo_minimo(tempos, intervalo_minimo):
    tempos_filtrados = []
    ultimo_tempo = -999.0

    for tempo in tempos:
        if tempo - ultimo_tempo >= intervalo_minimo:
            tempos_filtrados.append(float(tempo))
            ultimo_tempo = tempo

    return tempos_filtrados

def converter_para_float(valor):
    array = np.asarray(valor).flatten()

    if array.size == 0:
        return 0.0

    return float(array[0])

def faixa_para_beat(indice):
    padrao = [0, 1, 0, 1, 0, 2, 0, 1]
    return padrao[indice % len(padrao)]


def faixa_para_onset(indice, intensidade_normalizada):
    if intensidade_normalizada > 0.78:
        return 2

    if indice % 4 == 0:
        return 3

    return 1


def gerar_mapa(musica_id):
    if musica_id not in MUSICAS:
        print(f"Música desconhecida: {musica_id}")
        print(f"Opções: {', '.join(MUSICAS.keys())}")
        return

    dados_musica = MUSICAS[musica_id]

    caminho_audio = RAIZ_PROJETO / dados_musica["arquivo"]
    caminho_saida = RAIZ_PROJETO / dados_musica["saida"]

    if not caminho_audio.exists():
        print(f"Arquivo de áudio não encontrado: {caminho_audio}")
        return

    print(f"Lendo áudio: {caminho_audio}")

    y, sr = librosa.load(caminho_audio, sr=None, mono=True)

    duracao = librosa.get_duration(y=y, sr=sr)

    print(f"Duração: {duracao:.2f}s")
    print("Detectando batidas principais...")

    tempo_estimado_bruto, beat_frames = librosa.beat.beat_track(y=y, sr=sr)

    tempo_estimado = converter_para_float(tempo_estimado_bruto)
    beat_times = librosa.frames_to_time(beat_frames, sr=sr)

    print(f"BPM estimado: {tempo_estimado:.2f}")
    print(f"Batidas detectadas: {len(beat_times)}")

    print("Detectando ataques sonoros...")

    onset_env = librosa.onset.onset_strength(y=y, sr=sr)
    onset_frames = librosa.onset.onset_detect(
        onset_envelope=onset_env,
        sr=sr,
        backtrack=True,
        units="frames",
    )

    onset_times = librosa.frames_to_time(onset_frames, sr=sr)

    intensidades = onset_env[onset_frames]
    if len(intensidades) > 0:
        intensidades_norm = intensidades / max(np.max(intensidades), 0.0001)
    else:
        intensidades_norm = []

    print(f"Ataques detectados: {len(onset_times)}")

    # Filtragem para não gerar mapa impossível.
    beat_times = limitar_intervalo_minimo(beat_times, intervalo_minimo=0.32)

    notas = []

    # Batidas principais: base do mapa.
    for i, tempo in enumerate(beat_times):
        if tempo < 1.0:
            continue

        notas.append({
            "tempo": round(float(tempo), 3),
            "faixa": faixa_para_beat(i),
            "origem": "beat",
        })

    # Ataques fortes: notas extras, mas com filtro para não virar bagunça.
    onsets_filtrados = []
    ultimo_onset = -999.0

    for i, tempo in enumerate(onset_times):
        if tempo < 1.0:
            continue

        intensidade = float(intensidades_norm[i])

        if intensidade < 0.55:
            continue

        if tempo - ultimo_onset < 0.42:
            continue

        ultimo_onset = tempo

        onsets_filtrados.append((tempo, intensidade))

    for i, (tempo, intensidade) in enumerate(onsets_filtrados):
        # Evita colocar onset grudado em beat já existente.
        muito_perto_de_beat = any(abs(tempo - b) < 0.16 for b in beat_times)

        if muito_perto_de_beat:
            continue

        notas.append({
            "tempo": round(float(tempo), 3),
            "faixa": faixa_para_onset(i, intensidade),
            "origem": "onset",
            "forca": round(float(intensidade), 3),
        })

    notas.sort(key=lambda n: n["tempo"])

    mapa = {
        "id": musica_id,
        "nome": dados_musica["nome"],
        "arquivo": dados_musica["arquivo"],
        "offset": 0.0,
        "bpm_estimado": round(tempo_estimado, 2),
        "duracao": round(float(duracao), 3),
        "notas": notas,
    }

    caminho_saida.parent.mkdir(parents=True, exist_ok=True)

    with open(caminho_saida, "w", encoding="utf-8") as arquivo:
        json.dump(mapa, arquivo, indent=2, ensure_ascii=False)

    print()
    print(f"Mapa gerado: {caminho_saida}")
    print(f"Total de notas finais: {len(notas)}")

    if duracao > 0:
        print(f"Notas por minuto: {len(notas) / (duracao / 60):.1f}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso:")
        print("python tools/gerar_mapa_audio.py paranaue")
        print("python tools/gerar_mapa_audio.py balaio")
        print("python tools/gerar_mapa_audio.py dandara")
        sys.exit(0)

    gerar_mapa(sys.argv[1])