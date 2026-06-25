import glfw

# Janela

LARGURA_JANELA = 1100
ALTURA_JANELA = 800
TITULO_JANELA = "BerimBeat"

# Câmera / cena 3D

CAMERA_POS = (0.0, 5.0, 8.5)
CAMERA_ALVO = (0.0, 0.0, -3.5)
CAMERA_UP = (0.0, 1.0, 0.0)

FOV = 45.0
PLANO_PERTO = 0.1
PLANO_LONGE = 100.0

COR_FUNDO = (0.05, 0.045, 0.04, 1.0)

# Faixas jogáveis

FAIXAS = [
    {
        "nome": "Base",
        "tecla": "A",
        "glfw_key": glfw.KEY_A,
        "x": -1.2,
        "cor": (0.95, 0.65, 0.20),
    },
    {
        "nome": "Resposta",
        "tecla": "S",
        "glfw_key": glfw.KEY_S,
        "x": 0.0,
        "cor": (0.25, 0.85, 0.35),
    },
    {
        "nome": "Acento",
        "tecla": "D",
        "glfw_key": glfw.KEY_D,
        "x": 1.2,
        "cor": (0.85, 0.35, 0.25),
    },
]

# Pista / chão

ALTURA_PISTA = 0.0
LARGURA_FAIXA = 0.85

Z_INICIO_PISTA = -12.0
Z_FIM_PISTA = 2.8
Z_ALVO = 2.2

MARGEM_CHAO_X = 5.8
MARGEM_CHAO_FRENTE = 1.5
MARGEM_CHAO_FUNDO = 2.0

COR_CHAO = (0.13, 0.09, 0.055)
COR_LINHAS_PISTA = (0.85, 0.75, 0.55)

# Notas

VELOCIDADE_NOTA = 5.0
TAMANHO_NOTA = 0.32
ALTURA_NOTA = 0.18


# Zona de acerto

LARGURA_RECEPTOR = 0.85
PROFUNDIDADE_RECEPTOR = 0.28
ALTURA_RECEPTOR = 0.035

AUMENTO_RECEPTOR_PULSO = 0.22
INTENSIDADE_RECEPTOR_BASE = 0.72
INTENSIDADE_RECEPTOR_PULSO = 0.45

# Jogabilidade

JANELA_PERFEITO = 0.16
JANELA_BOM = 0.32
TEMPO_APOS_ALVO_PARA_ERRO = JANELA_BOM

PONTOS_PERFEITO = 100
PONTOS_BOM = 60

VELOCIDADE_FEEDBACK = 3.5

# Instrumentos / efeitos visuais

ESCALA_INSTRUMENTOS = 1.45
ESCALA_PULSO_INSTRUMENTO = 0.25
ALTURA_PULSO_INSTRUMENTO = 0.18

# Instrumentos da cena
POSICOES_INSTRUMENTOS = [
    (-4.10, 0.70, -0.85),   # Berimbau
    (4.25, 0.60, 0.10),     # Pandeiro
    (4.55, 0.55, -2.40),    # Atabaque
]

# Iluminação

LUZ_POSICAO = (0.0, 6.0, 4.0, 1.0)
LUZ_DIFUSA = (1.0, 0.92, 0.78, 1.0)
LUZ_AMBIENTE = (0.22, 0.18, 0.15, 1.0)
LUZ_ESPECULAR = (1.0, 1.0, 1.0, 1.0)
BRILHO_MATERIAL = 45

# Áudio / músicas

AUDIO_ATIVO = True

VOLUME_MUSICA = 0.55
VOLUME_EFEITOS = 0.70

# Balaio fica como inicial porque é mais curta
MUSICA_INICIAL = "balaio"

MUSICAS = {
    "balaio": {
        "nome": "Balaio de Café",
        "arquivo": "assets/music/balaio_de_cafe.ogg",
        "mapa": "assets/maps/balaio_bpm152_grade.json",
        "offset": 0.0,
        "repetir": False,
    },

    "demo_facil": {
        "nome": "Demo Fácil",
        "arquivo": None,
        "mapa": "assets/maps/demo_facil.json",
        "offset": 0.0,
        "repetir": False,
    },

    "demo_medio": {
        "nome": "Demo Média",
        "arquivo": None,
        "mapa": "assets/maps/demo_medio.json",
        "offset": 0.0,
        "repetir": False,
    },

    "demo_dificil": {
        "nome": "Demo Difícil",
        "arquivo": None,
        "mapa": "assets/maps/demo_dificil.json",
        "offset": 0.0,
        "repetir": False,
    },
}

# Debug / testes

MOSTRAR_EIXOS = False
MOSTRAR_TITULO_DEBUG = False