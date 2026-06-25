import math
import pygame

from OpenGL.GL import *
from OpenGL.GLU import *

from berimbeat.config import (
    FAIXAS,
    CAMERA_POS,
    CAMERA_ALVO,
    CAMERA_UP,
    FOV,
    PLANO_PERTO,
    PLANO_LONGE,
    COR_FUNDO,
    MOSTRAR_EIXOS,

    ALTURA_PISTA,
    LARGURA_FAIXA,
    Z_INICIO_PISTA,
    Z_FIM_PISTA,
    Z_ALVO,

    MARGEM_CHAO_X,
    MARGEM_CHAO_FRENTE,
    MARGEM_CHAO_FUNDO,
    COR_CHAO,
    COR_LINHAS_PISTA,

    TAMANHO_NOTA,
    ALTURA_NOTA,
    LARGURA_RECEPTOR,
    PROFUNDIDADE_RECEPTOR,
    ALTURA_RECEPTOR,
    AUMENTO_RECEPTOR_PULSO,
    INTENSIDADE_RECEPTOR_BASE,
    INTENSIDADE_RECEPTOR_PULSO,

    ESCALA_INSTRUMENTOS,
    ESCALA_PULSO_INSTRUMENTO,
    ALTURA_PULSO_INSTRUMENTO,
    POSICOES_INSTRUMENTOS,

    LUZ_POSICAO,
    LUZ_DIFUSA,
    LUZ_AMBIENTE,
    LUZ_ESPECULAR,
    BRILHO_MATERIAL,
)


class Renderer:
    def __init__(self):
        self.largura = 1
        self.altura = 1

        self.fonte_titulo = None
        self.fonte_grande = None
        self.fonte_media = None
        self.fonte_pequena = None

    # Configuração inicial do OpenGL
    def configurar_opengl(self, largura, altura):
        self.largura = largura
        self.altura = altura

        glClearColor(*COR_FUNDO)

        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glEnable(GL_COLOR_MATERIAL)
        glEnable(GL_NORMALIZE)

        glShadeModel(GL_SMOOTH)

        self.configurar_fontes()
        self.configurar_luz()
        self.redimensionar(largura, altura)

    # Fontes usadas na interface
    def configurar_fontes(self):
        pygame.font.init()

        self.fonte_titulo = pygame.font.SysFont("Arial", 52, bold=True)
        self.fonte_grande = pygame.font.SysFont("Arial", 34, bold=True)
        self.fonte_media = pygame.font.SysFont("Arial", 24, bold=True)
        self.fonte_pequena = pygame.font.SysFont("Arial", 18)

    # Iluminação da cena 3D
    def configurar_luz(self):
        glLightfv(GL_LIGHT0, GL_POSITION, LUZ_POSICAO)
        glLightfv(GL_LIGHT0, GL_DIFFUSE, LUZ_DIFUSA)
        glLightfv(GL_LIGHT0, GL_AMBIENT, LUZ_AMBIENTE)
        glLightfv(GL_LIGHT0, GL_SPECULAR, LUZ_ESPECULAR)

        glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, LUZ_ESPECULAR)
        glMaterialf(GL_FRONT_AND_BACK, GL_SHININESS, BRILHO_MATERIAL)

    # Atualiza viewport e perspectiva
    def redimensionar(self, largura, altura):
        if altura == 0:
            altura = 1

        self.largura = largura
        self.altura = altura

        glViewport(0, 0, largura, altura)

        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(FOV, largura / altura, PLANO_PERTO, PLANO_LONGE)

        glMatrixMode(GL_MODELVIEW)

    def limpar(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()

    # Câmera fixa da cena
    def aplicar_camera(self):
        gluLookAt(
            CAMERA_POS[0], CAMERA_POS[1], CAMERA_POS[2],
            CAMERA_ALVO[0], CAMERA_ALVO[1], CAMERA_ALVO[2],
            CAMERA_UP[0], CAMERA_UP[1], CAMERA_UP[2],
        )

    # Menu principal
    def desenhar_menu(self, nome_selecionado="Balaio de Café", opcoes=None):
        self.aplicar_camera()
        self.desenhar_chao()
        self.desenhar_pista_base()
        self.desenhar_instrumentos({i: 0.15 for i in range(len(FAIXAS))})

        if opcoes is None:
            opcoes = ["1 - Balaio de Café"]

        self.iniciar_desenho_2d()

        painel_largura = 720
        painel_altura = 340
        painel_x = (self.largura - painel_largura) / 2
        painel_y = 75

        self.desenhar_painel_2d(
            painel_x,
            painel_y,
            painel_largura,
            painel_altura,
        )

        self.desenhar_texto_centralizado_2d(
            "BerimBeat",
            105,
            self.fonte_titulo,
            (255, 190, 70),
        )

        self.desenhar_texto_centralizado_2d(
            f"Selecionado: {nome_selecionado}",
            175,
            self.fonte_media,
            (255, 255, 255),
        )

        y_opcao = 225

        for opcao in opcoes:
            cor = (220, 210, 180)

            if nome_selecionado in opcao:
                cor = (255, 210, 90)

            self.desenhar_texto_centralizado_2d(
                opcao,
                y_opcao,
                self.fonte_pequena,
                cor,
            )

            y_opcao += 28

        self.desenhar_texto_centralizado_2d(
            "ENTER - Iniciar",
            350,
            self.fonte_media,
            (255, 255, 255),
        )

        self.desenhar_texto_centralizado_2d(
            "ESC - Sair",
            380,
            self.fonte_pequena,
            (200, 190, 170),
        )

        self.finalizar_desenho_2d()

    # Tela de resultado
    def desenhar_resultado(
        self,
        pontos,
        acertos,
        erros,
        maior_combo,
        notas_perdidas=0,
        teclas_erradas=0,
        precisao=0.0,
        desempenho="D",
    ):
        self.aplicar_camera()
        self.desenhar_chao()
        self.desenhar_pista_base()
        self.desenhar_painel_resultado(pontos, acertos, erros, maior_combo)

        self.iniciar_desenho_2d()

        painel_largura = 740
        painel_altura = 370
        painel_x = (self.largura - painel_largura) / 2
        painel_y = 70

        self.desenhar_painel_2d(
            painel_x,
            painel_y,
            painel_largura,
            painel_altura,
        )

        self.desenhar_texto_centralizado_2d(
            "Resultado",
            95,
            self.fonte_titulo,
            (255, 190, 70),
        )

        self.desenhar_texto_centralizado_2d(
            f"Desempenho: {desempenho}",
            165,
            self.fonte_grande,
            (255, 255, 255),
        )

        self.desenhar_texto_centralizado_2d(
            f"Pontuação: {pontos}",
            220,
            self.fonte_media,
            (255, 230, 160),
        )

        self.desenhar_texto_centralizado_2d(
            f"Precisão: {precisao:.1f}%",
            255,
            self.fonte_media,
            (230, 220, 190),
        )

        self.desenhar_texto_centralizado_2d(
            f"Acertos: {acertos}    Erros: {erros}",
            295,
            self.fonte_pequena,
            (220, 210, 185),
        )

        self.desenhar_texto_centralizado_2d(
            f"Perdidas: {notas_perdidas}    Teclas erradas: {teclas_erradas}",
            322,
            self.fonte_pequena,
            (200, 190, 170),
        )

        self.desenhar_texto_centralizado_2d(
            f"Maior combo: {maior_combo}",
            350,
            self.fonte_pequena,
            (220, 210, 185),
        )

        self.desenhar_texto_centralizado_2d(
            "R - Jogar novamente    |    BACKSPACE - Menu",
            395,
            self.fonte_pequena,
            (210, 200, 180),
        )

        self.finalizar_desenho_2d()

    # Cena principal da partida
    def desenhar_cena(self, notas, tempo_jogo, feedbacks, hud=None):
        self.aplicar_camera()

        if MOSTRAR_EIXOS:
            self.desenhar_eixos()

        self.desenhar_chao()
        self.desenhar_pista_base()
        self.desenhar_zona_acerto(feedbacks)
        self.desenhar_notas(notas, tempo_jogo)
        self.desenhar_instrumentos(feedbacks)

        if hud is not None:
            self.desenhar_hud(hud, feedbacks)

    # HUD da partida
    def desenhar_hud(self, hud, feedbacks):
        pontos = hud.get("pontos", 0)
        combo = hud.get("combo", 0)
        acertos = hud.get("acertos", 0)
        erros = hud.get("erros", 0)
        tempo = hud.get("tempo", 0.0)
        nome_musica = hud.get("musica", "Balaio de Café")
        mapa = hud.get("mapa", "mapa")

        minutos = int(tempo // 60)
        segundos = int(tempo % 60)
        centesimos = int((tempo - int(tempo)) * 100)

        tempo_formatado = f"{minutos:02d}:{segundos:02d}.{centesimos:02d}"

        self.iniciar_desenho_2d()

        self.desenhar_texto_2d(
            f"Pontos: {pontos}",
            25,
            22,
            self.fonte_media,
            (255, 230, 160),
        )

        self.desenhar_texto_2d(
            f"Combo: {combo}",
            25,
            52,
            self.fonte_pequena,
            (230, 230, 230),
        )

        self.desenhar_texto_2d(
            f"Acertos: {acertos}   Erros: {erros}",
            25,
            78,
            self.fonte_pequena,
            (210, 210, 210),
        )

        self.desenhar_texto_2d(
            f"Tempo: {tempo_formatado}",
            self.largura - 220,
            22,
            self.fonte_media,
            (255, 255, 255),
        )

        self.desenhar_texto_2d(
            nome_musica,
            self.largura - 260,
            55,
            self.fonte_pequena,
            (220, 210, 180),
        )

        self.desenhar_texto_2d(
            f"Mapa: {mapa}",
            self.largura - 260,
            78,
            self.fonte_pequena,
            (180, 180, 180),
        )

        self.desenhar_teclas_hud(feedbacks)

        self.desenhar_multiplicador_combo(hud)

        self.finalizar_desenho_2d()

    # Teclas A/S/D no rodapé
    def desenhar_teclas_hud(self, feedbacks):
        y = self.altura - 72
        tamanho = 48

        centro_tela = self.largura / 2

        # Teclas no rodapé
        centros = [
            centro_tela - 170,
            centro_tela,
            centro_tela + 170,
        ]

        for indice, faixa in enumerate(FAIXAS):
            pulso = feedbacks[indice]

            r, g, b = faixa["cor"]

            intensidade = 0.70 + pulso * 0.40
            borda = (r * intensidade, g * intensidade, b * intensidade, 0.95)
            fundo = (0.06, 0.045, 0.035, 0.82)

            crescimento = pulso * 6.0
            tam_caixa = tamanho + crescimento

            x_caixa = centros[indice] - tam_caixa / 2
            y_caixa = y - crescimento / 2

            self.desenhar_painel_2d(
                x_caixa,
                y_caixa,
                tam_caixa,
                tam_caixa,
                cor_fundo=fundo,
                cor_borda=borda,
            )

            self.desenhar_texto_2d(
                faixa["tecla"],
                x_caixa + tam_caixa / 2 - 9,
                y_caixa + tam_caixa / 2 - 17,
                self.fonte_media,
                (255, 255, 255),
            )

    # Multiplicador grande no centro superior
    def desenhar_multiplicador_combo(self, hud):
        multiplicador = hud.get("multiplicador", 1)

        if multiplicador <= 1:
            return

        texto = f"x{multiplicador}"

        y = 118

        if multiplicador == 2:
            cor_principal = (255, 220, 90)
            cor_sombra = (80, 45, 10)

        elif multiplicador == 3:
            cor_principal = (255, 150, 70)
            cor_sombra = (90, 25, 10)

        else:
            cor_principal = (255, 80, 80)
            cor_sombra = (90, 10, 10)

        fonte = self.fonte_titulo

        superficie = fonte.render(texto, True, cor_principal)
        largura_texto, _ = superficie.get_size()
        x = (self.largura - largura_texto) / 2

        self.desenhar_texto_2d(texto, x - 3, y + 3, fonte, cor_sombra)
        self.desenhar_texto_2d(texto, x + 3, y + 3, fonte, cor_sombra)
        self.desenhar_texto_2d(texto, x - 3, y - 3, fonte, cor_sombra)
        self.desenhar_texto_2d(texto, x + 3, y - 3, fonte, cor_sombra)

        self.desenhar_texto_2d(texto, x, y, fonte, cor_principal)

    def definir_cor(self, cor, intensidade=1.0):
        r, g, b = cor
        glColor3f(r * intensidade, g * intensidade, b * intensidade)

    # Troca temporariamente para projeção 2D
    def iniciar_desenho_2d(self):
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        gluOrtho2D(0, self.largura, self.altura, 0)

        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()

        glDisable(GL_DEPTH_TEST)
        glDisable(GL_LIGHTING)

        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    def finalizar_desenho_2d(self):
        glDisable(GL_BLEND)

        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)

        glMatrixMode(GL_MODELVIEW)
        glPopMatrix()

        glMatrixMode(GL_PROJECTION)
        glPopMatrix()

        glMatrixMode(GL_MODELVIEW)


    # Renderiza texto com pygame e aplica como textura em um quad 2D
    def desenhar_texto_2d(self, texto, x, y, fonte=None, cor=(255, 255, 255)):
        if fonte is None:
            fonte = self.fonte_pequena

        superficie = fonte.render(str(texto), True, cor)
        largura_texto, altura_texto = superficie.get_size()

        dados_textura = pygame.image.tostring(superficie, "RGBA", True)

        textura_id = glGenTextures(1)

        glBindTexture(GL_TEXTURE_2D, textura_id)

        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

        glTexImage2D(
            GL_TEXTURE_2D,
            0,
            GL_RGBA,
            largura_texto,
            altura_texto,
            0,
            GL_RGBA,
            GL_UNSIGNED_BYTE,
            dados_textura,
        )

        glEnable(GL_TEXTURE_2D)
        glColor4f(1.0, 1.0, 1.0, 1.0)

        glBegin(GL_QUADS)
        glTexCoord2f(0.0, 1.0)
        glVertex2f(x, y)

        glTexCoord2f(1.0, 1.0)
        glVertex2f(x + largura_texto, y)

        glTexCoord2f(1.0, 0.0)
        glVertex2f(x + largura_texto, y + altura_texto)

        glTexCoord2f(0.0, 0.0)
        glVertex2f(x, y + altura_texto)
        glEnd()

        glDisable(GL_TEXTURE_2D)

        glDeleteTextures([textura_id])

    def desenhar_texto_centralizado_2d(self, texto, y, fonte=None, cor=(255, 255, 255)):
        if fonte is None:
            fonte = self.fonte_pequena

        superficie = fonte.render(str(texto), True, cor)
        largura_texto, _ = superficie.get_size()

        x = (self.largura - largura_texto) / 2

        self.desenhar_texto_2d(texto, x, y, fonte, cor)

    # Painéis semitransparentes da interface
    def desenhar_painel_2d(
        self,
        x,
        y,
        largura,
        altura,
        cor_fundo=(0.08, 0.06, 0.04, 0.82),
        cor_borda=(0.95, 0.75, 0.30, 0.95),
    ):
        glDisable(GL_TEXTURE_2D)

        # Fundo do painel
        glColor4f(*cor_fundo)
        glBegin(GL_QUADS)
        glVertex2f(x, y)
        glVertex2f(x + largura, y)
        glVertex2f(x + largura, y + altura)
        glVertex2f(x, y + altura)
        glEnd()

        # Borda do painel
        glLineWidth(2.0)
        glColor4f(*cor_borda)
        glBegin(GL_LINE_LOOP)
        glVertex2f(x, y)
        glVertex2f(x + largura, y)
        glVertex2f(x + largura, y + altura)
        glVertex2f(x, y + altura)
        glEnd()

    # Chão da cena
    def desenhar_chao(self):
        glDisable(GL_LIGHTING)

        glColor3f(*COR_CHAO)

        glBegin(GL_QUADS)
        glVertex3f(-MARGEM_CHAO_X, -0.04, Z_FIM_PISTA + MARGEM_CHAO_FRENTE)
        glVertex3f(MARGEM_CHAO_X, -0.04, Z_FIM_PISTA + MARGEM_CHAO_FRENTE)
        glVertex3f(MARGEM_CHAO_X, -0.04, Z_INICIO_PISTA - MARGEM_CHAO_FUNDO)
        glVertex3f(-MARGEM_CHAO_X, -0.04, Z_INICIO_PISTA - MARGEM_CHAO_FUNDO)
        glEnd()

        glEnable(GL_LIGHTING)

    # Faixas coloridas da pista
    def desenhar_pista_base(self):
        for faixa in FAIXAS:
            x = faixa["x"]
            cor = faixa["cor"]

            self.definir_cor(cor, 0.35)

            glBegin(GL_QUADS)
            glNormal3f(0.0, 1.0, 0.0)

            glVertex3f(x - LARGURA_FAIXA / 2, ALTURA_PISTA, Z_FIM_PISTA)
            glVertex3f(x + LARGURA_FAIXA / 2, ALTURA_PISTA, Z_FIM_PISTA)
            glVertex3f(x + LARGURA_FAIXA / 2, ALTURA_PISTA, Z_INICIO_PISTA)
            glVertex3f(x - LARGURA_FAIXA / 2, ALTURA_PISTA, Z_INICIO_PISTA)

            glEnd()

        self.desenhar_linhas_pista()

    # Linhas divisórias da pista
    def desenhar_linhas_pista(self):
        glDisable(GL_LIGHTING)

        glColor3f(*COR_LINHAS_PISTA)
        glLineWidth(2.0)

        altura_linha = ALTURA_PISTA + 0.01

        glBegin(GL_LINES)

        for faixa in FAIXAS:
            x = faixa["x"]

            esquerda = x - LARGURA_FAIXA / 2
            direita = x + LARGURA_FAIXA / 2

            # Linha esquerda
            glVertex3f(esquerda, altura_linha, Z_FIM_PISTA)
            glVertex3f(esquerda, altura_linha, Z_INICIO_PISTA)

            # Linha direita
            glVertex3f(direita, altura_linha, Z_FIM_PISTA)
            glVertex3f(direita, altura_linha, Z_INICIO_PISTA)

        glEnd()

        glLineWidth(1.0)
        glEnable(GL_LIGHTING)

    # Receptores e linha de acerto
    def desenhar_zona_acerto(self, feedbacks):
        glDisable(GL_LIGHTING)

        for indice, faixa in enumerate(FAIXAS):
            x = faixa["x"]
            cor = faixa["cor"]
            pulso = feedbacks[indice]

            intensidade = INTENSIDADE_RECEPTOR_BASE + pulso * INTENSIDADE_RECEPTOR_PULSO
            largura = LARGURA_RECEPTOR * (1.0 + pulso * AUMENTO_RECEPTOR_PULSO)
            profundidade = PROFUNDIDADE_RECEPTOR * (1.25 + pulso * AUMENTO_RECEPTOR_PULSO)

            r, g, b = cor

            # Base escura sob o receptor
            glColor4f(0.04, 0.035, 0.03, 0.45)
            glBegin(GL_QUADS)
            glVertex3f(x - largura / 2 - 0.08, ALTURA_RECEPTOR - 0.005, Z_ALVO + profundidade / 2 + 0.08)
            glVertex3f(x + largura / 2 + 0.08, ALTURA_RECEPTOR - 0.005, Z_ALVO + profundidade / 2 + 0.08)
            glVertex3f(x + largura / 2 + 0.08, ALTURA_RECEPTOR - 0.005, Z_ALVO - profundidade / 2 - 0.08)
            glVertex3f(x - largura / 2 - 0.08, ALTURA_RECEPTOR - 0.005, Z_ALVO - profundidade / 2 - 0.08)
            glEnd()

            # Receptor colorido
            glColor4f(r * intensidade, g * intensidade, b * intensidade, 0.90)
            glBegin(GL_QUADS)
            glVertex3f(x - largura / 2, ALTURA_RECEPTOR, Z_ALVO + profundidade / 2)
            glVertex3f(x + largura / 2, ALTURA_RECEPTOR, Z_ALVO + profundidade / 2)
            glVertex3f(x + largura / 2, ALTURA_RECEPTOR, Z_ALVO - profundidade / 2)
            glVertex3f(x - largura / 2, ALTURA_RECEPTOR, Z_ALVO - profundidade / 2)
            glEnd()

            # Contorno do receptor
            glLineWidth(2.5 + pulso * 2.0)
            glColor4f(r * 1.2, g * 1.2, b * 1.2, 1.0)
            glBegin(GL_LINE_LOOP)
            glVertex3f(x - largura / 2, ALTURA_RECEPTOR + 0.012, Z_ALVO + profundidade / 2)
            glVertex3f(x + largura / 2, ALTURA_RECEPTOR + 0.012, Z_ALVO + profundidade / 2)
            glVertex3f(x + largura / 2, ALTURA_RECEPTOR + 0.012, Z_ALVO - profundidade / 2)
            glVertex3f(x - largura / 2, ALTURA_RECEPTOR + 0.012, Z_ALVO - profundidade / 2)
            glEnd()

        # Linha geral de acerto
        glColor3f(*COR_LINHAS_PISTA)
        glLineWidth(3.5)

        limite_esquerdo = FAIXAS[0]["x"] - LARGURA_FAIXA / 2
        limite_direito = FAIXAS[-1]["x"] + LARGURA_FAIXA / 2

        glBegin(GL_LINES)
        glVertex3f(limite_esquerdo, ALTURA_RECEPTOR + 0.025, Z_ALVO)
        glVertex3f(limite_direito, ALTURA_RECEPTOR + 0.025, Z_ALVO)
        glEnd()

        glLineWidth(1.0)
        glEnable(GL_LIGHTING)

    # Notas em movimento
    def desenhar_notas(self, notas, tempo_jogo):
        for nota in notas:
            if not nota["ativa"]:
                continue

            indice_faixa = nota["faixa"]

            if indice_faixa < 0 or indice_faixa >= len(FAIXAS):
                continue

            z = nota["z"]

            if z < Z_INICIO_PISTA or z > Z_FIM_PISTA:
                continue

            faixa = FAIXAS[indice_faixa]
            x = faixa["x"]
            cor_faixa = faixa["cor"]

            cor = (
                min(1.0, cor_faixa[0] * 0.78 + 0.22),
                min(1.0, cor_faixa[1] * 0.78 + 0.22),
                min(1.0, cor_faixa[2] * 0.78 + 0.22),
            )

            fase = tempo_jogo * 6.0 + indice_faixa * 1.7 + z * 0.35

            flutuacao = math.sin(fase) * 0.035
            balanco_z = math.sin(fase * 0.8) * 7.0
            balanco_x = math.cos(fase * 0.7) * 4.0

            glPushMatrix()

            glTranslatef(x, ALTURA_PISTA + ALTURA_NOTA + flutuacao, z)

            glRotatef(10.0, 1.0, 0.0, 0.0)

            glRotatef(balanco_z, 0.0, 0.0, 1.0)
            glRotatef(balanco_x, 1.0, 0.0, 0.0)

            self.desenhar_nota_jogo(cor)

            glPopMatrix()

    # Modelo de uma nota
    def desenhar_nota_jogo(self, cor):
        r, g, b = cor

        # Base escura da nota
        glPushMatrix()
        self.definir_cor((r * 0.45, g * 0.45, b * 0.45), 1.0)
        self.desenhar_cilindro(TAMANHO_NOTA * 0.62, ALTURA_NOTA * 0.85, 32)
        glPopMatrix()

        # Topo colorido
        glPushMatrix()
        glTranslatef(0.0, ALTURA_NOTA * 0.28, 0.0)
        self.definir_cor(cor, 1.25)
        self.desenhar_cilindro(TAMANHO_NOTA * 0.52, ALTURA_NOTA * 0.28, 32)
        glPopMatrix()

        # Pequeno detalhe central claro
        glPushMatrix()
        glTranslatef(0.0, ALTURA_NOTA * 0.48, 0.0)
        self.definir_cor((1.0, 0.92, 0.72), 0.85)
        self.desenhar_cilindro(TAMANHO_NOTA * 0.22, ALTURA_NOTA * 0.08, 24)
        glPopMatrix()

    # Instrumentos laterais com pulso
    def desenhar_instrumentos(self, feedbacks):
        if isinstance(feedbacks, list):
            feedbacks = {i: valor for i, valor in enumerate(feedbacks)}
    
        pulso_berimbau = max(feedbacks.get(0, 0.0), feedbacks.get(1, 0.0))

        pulso_percussao = feedbacks.get(2, 0.0)

        # Berimbau
        x, y, z = POSICOES_INSTRUMENTOS[0]
        escala = ESCALA_INSTRUMENTOS + 0.35 + pulso_berimbau * ESCALA_PULSO_INSTRUMENTO

        glPushMatrix()
        glTranslatef(x, y + pulso_berimbau * ALTURA_PULSO_INSTRUMENTO, z)
        glScalef(escala, escala, escala)
        glRotatef(-8.0 + pulso_berimbau * 10.0, 0.0, 1.0, 0.0)
        self.desenhar_berimbau((0.95, 0.65, 0.20))
        glPopMatrix()

        # Pandeiro
        x, y, z = POSICOES_INSTRUMENTOS[1]
        escala = ESCALA_INSTRUMENTOS + pulso_percussao * ESCALA_PULSO_INSTRUMENTO

        glPushMatrix()
        glTranslatef(x, y + pulso_percussao * ALTURA_PULSO_INSTRUMENTO, z)
        glScalef(escala, escala, escala)

        glRotatef(20.0, 1.0, 0.0, 0.0)
        glRotatef(pulso_percussao * 10.0, 0.0, 0.0, 1.0)

        self.desenhar_pandeiro((0.85, 0.70, 0.45))
        glPopMatrix()

        # Atabaque
        x, y, z = POSICOES_INSTRUMENTOS[2]
        escala = ESCALA_INSTRUMENTOS + pulso_percussao * ESCALA_PULSO_INSTRUMENTO

        glPushMatrix()
        glTranslatef(x, y + pulso_percussao * ALTURA_PULSO_INSTRUMENTO, z)
        glScalef(escala, escala, escala)
        glRotatef(pulso_percussao * 8.0, 0.0, 1.0, 0.0)

        self.desenhar_atabaque((0.85, 0.35, 0.25))
        glPopMatrix()

    # Berimbau
    def desenhar_berimbau(self, cor):
        pontos = [
            (0.00, -0.82),
            (0.03, -0.55),
            (0.07, -0.20),
            (0.11, 0.18),
            (0.14, 0.50),
            (0.16, 0.82),
        ]

        self.definir_cor((0.72, 0.49, 0.24))

        for i in range(len(pontos) - 1):
            x1, y1 = pontos[i]
            x2, y2 = pontos[i + 1]

            dx = x2 - x1
            dy = y2 - y1
            comprimento = math.sqrt(dx * dx + dy * dy)
            angulo = math.degrees(math.atan2(dy, dx)) - 90.0

            glPushMatrix()
            glTranslatef((x1 + x2) / 2, (y1 + y2) / 2, 0.0)
            glRotatef(angulo, 0.0, 0.0, 1.0)
            self.desenhar_cilindro(0.022, comprimento, 12)
            glPopMatrix()

        glDisable(GL_LIGHTING)
        glColor3f(0.92, 0.88, 0.72)
        glLineWidth(2.0)

        glBegin(GL_LINES)
        glVertex3f(0.145, 0.80, 0.0)
        glVertex3f(0.01, -0.79, 0.0)
        glEnd()

        glBegin(GL_LINES)
        glVertex3f(0.03, -0.18, 0.0)
        glVertex3f(-0.14, -0.23, 0.0)
        glEnd()

        glLineWidth(1.0)
        glEnable(GL_LIGHTING)

        glPushMatrix()
        glTranslatef(-0.18, -0.26, 0.0)
        glScalef(1.0, 1.0, 0.82)
        self.definir_cor((0.56, 0.30, 0.14))
        self.desenhar_esfera(0.17, 18, 12)
        glPopMatrix()

        glPushMatrix()
        glTranslatef(-0.12, -0.23, 0.10)
        self.definir_cor((0.42, 0.22, 0.10))
        self.desenhar_cilindro(0.035, 0.05, 12)
        glPopMatrix()

        glPushMatrix()
        glTranslatef(0.10, -0.30, 0.05)
        glRotatef(58.0, 0.0, 0.0, 1.0)
        self.definir_cor((0.84, 0.66, 0.34))
        self.desenhar_cilindro(0.012, 0.28, 10)
        glPopMatrix()

    # Pandeiro
    def desenhar_pandeiro(self, cor):
        # aro externo
        glPushMatrix()
        self.definir_cor((0.62, 0.34, 0.14))
        self.desenhar_cilindro(0.34, 0.07, 32)
        glPopMatrix()

        # pele principal
        glPushMatrix()
        glTranslatef(0.0, 0.04, 0.0)
        self.definir_cor((0.92, 0.82, 0.62))
        self.desenhar_cilindro(0.27, 0.025, 32)
        glPopMatrix()

    # Atabaque
    def desenhar_atabaque(self, cor):
        # Corpo principal de madeira
        glPushMatrix()
        self.definir_cor((0.50, 0.25, 0.10))
        glScalef(0.82, 1.28, 0.82)
        self.desenhar_cilindro(0.25, 0.78, 32)
        glPopMatrix()

        # Base inferior mais escura
        glPushMatrix()
        glTranslatef(0.0, -0.52, 0.0)
        self.definir_cor((0.25, 0.12, 0.05))
        self.desenhar_cilindro(0.24, 0.08, 32)
        glPopMatrix()

        # Aro superior escuro
        glPushMatrix()
        glTranslatef(0.0, 0.52, 0.0)
        self.definir_cor((0.24, 0.12, 0.06))
        self.desenhar_cilindro(0.31, 0.08, 32)
        glPopMatrix()

        # Pele/couro superior claro
        glPushMatrix()
        glTranslatef(0.0, 0.575, 0.0)
        self.definir_cor((0.95, 0.82, 0.58))
        self.desenhar_cilindro(0.25, 0.03, 32)
        glPopMatrix()

        # Faixas decorativas simples no corpo
        glPushMatrix()
        glTranslatef(0.0, 0.18, 0.0)
        self.definir_cor((0.30, 0.14, 0.06))
        self.desenhar_cilindro(0.258, 0.035, 32)
        glPopMatrix()

        glPushMatrix()
        glTranslatef(0.0, -0.18, 0.0)
        self.definir_cor((0.30, 0.14, 0.06))
        self.desenhar_cilindro(0.258, 0.035, 32)
        glPopMatrix()

    def desenhar_logo_simples(self):
        glPushMatrix()

        glTranslatef(0.0, 1.8, -2.0)
        glScalef(2.4, 0.5, 0.12)

        glColor3f(0.95, 0.65, 0.18)
        self.desenhar_cubo(1.0)

        glPopMatrix()

    # Painel 3D ao fundo do resultado
    def desenhar_painel_resultado(self, pontos, acertos, erros, maior_combo):
        glPushMatrix()

        glTranslatef(0.0, 1.5, -2.0)
        glScalef(2.8, 1.4, 0.12)

        glColor3f(0.25, 0.16, 0.08)
        self.desenhar_cubo(1.0)

        glPopMatrix()

    # Primitiva: cubo
    def desenhar_cubo(self, tamanho):
        t = tamanho / 2

        glBegin(GL_QUADS)

        glNormal3f(0.0, 0.0, 1.0)
        glVertex3f(-t, -t, t)
        glVertex3f(t, -t, t)
        glVertex3f(t, t, t)
        glVertex3f(-t, t, t)

        glNormal3f(0.0, 0.0, -1.0)
        glVertex3f(t, -t, -t)
        glVertex3f(-t, -t, -t)
        glVertex3f(-t, t, -t)
        glVertex3f(t, t, -t)

        glNormal3f(0.0, 1.0, 0.0)
        glVertex3f(-t, t, t)
        glVertex3f(t, t, t)
        glVertex3f(t, t, -t)
        glVertex3f(-t, t, -t)

        glNormal3f(0.0, -1.0, 0.0)
        glVertex3f(-t, -t, -t)
        glVertex3f(t, -t, -t)
        glVertex3f(t, -t, t)
        glVertex3f(-t, -t, t)

        glNormal3f(1.0, 0.0, 0.0)
        glVertex3f(t, -t, t)
        glVertex3f(t, -t, -t)
        glVertex3f(t, t, -t)
        glVertex3f(t, t, t)

        glNormal3f(-1.0, 0.0, 0.0)
        glVertex3f(-t, -t, -t)
        glVertex3f(-t, -t, t)
        glVertex3f(-t, t, t)
        glVertex3f(-t, t, -t)

        glEnd()

    # Primitiva: cilindro
    def desenhar_cilindro(self, raio, altura, fatias):
        meio = altura / 2

        glBegin(GL_TRIANGLES)

        for i in range(fatias):
            ang1 = 2 * math.pi * i / fatias
            ang2 = 2 * math.pi * (i + 1) / fatias

            x1 = math.cos(ang1) * raio
            z1 = math.sin(ang1) * raio
            x2 = math.cos(ang2) * raio
            z2 = math.sin(ang2) * raio

            glNormal3f(math.cos(ang1), 0.0, math.sin(ang1))
            glVertex3f(x1, -meio, z1)

            glNormal3f(math.cos(ang2), 0.0, math.sin(ang2))
            glVertex3f(x2, -meio, z2)

            glNormal3f(math.cos(ang2), 0.0, math.sin(ang2))
            glVertex3f(x2, meio, z2)

            glNormal3f(math.cos(ang1), 0.0, math.sin(ang1))
            glVertex3f(x1, -meio, z1)

            glNormal3f(math.cos(ang2), 0.0, math.sin(ang2))
            glVertex3f(x2, meio, z2)

            glNormal3f(math.cos(ang1), 0.0, math.sin(ang1))
            glVertex3f(x1, meio, z1)

        glEnd()

        self.desenhar_tampa_cilindro(raio, meio, fatias, 1)
        self.desenhar_tampa_cilindro(raio, -meio, fatias, -1)

    # Tampas do cilindro
    def desenhar_tampa_cilindro(self, raio, y, fatias, direcao_normal):
        glBegin(GL_TRIANGLES)

        for i in range(fatias):
            ang1 = 2 * math.pi * i / fatias
            ang2 = 2 * math.pi * (i + 1) / fatias

            x1 = math.cos(ang1) * raio
            z1 = math.sin(ang1) * raio
            x2 = math.cos(ang2) * raio
            z2 = math.sin(ang2) * raio

            glNormal3f(0.0, direcao_normal, 0.0)

            if direcao_normal > 0:
                glVertex3f(0.0, y, 0.0)
                glVertex3f(x1, y, z1)
                glVertex3f(x2, y, z2)
            else:
                glVertex3f(0.0, y, 0.0)
                glVertex3f(x2, y, z2)
                glVertex3f(x1, y, z1)

        glEnd()

    # Primitiva: esfera
    def desenhar_esfera(self, raio, fatias, camadas):
        for i in range(camadas):
            lat1 = math.pi * (-0.5 + i / camadas)
            lat2 = math.pi * (-0.5 + (i + 1) / camadas)

            y1 = math.sin(lat1) * raio
            r1 = math.cos(lat1) * raio

            y2 = math.sin(lat2) * raio
            r2 = math.cos(lat2) * raio

            glBegin(GL_QUAD_STRIP)

            for j in range(fatias + 1):
                lon = 2 * math.pi * j / fatias

                x1 = math.cos(lon) * r1
                z1 = math.sin(lon) * r1

                x2 = math.cos(lon) * r2
                z2 = math.sin(lon) * r2

                glNormal3f(x1 / raio, y1 / raio, z1 / raio)
                glVertex3f(x1, y1, z1)

                glNormal3f(x2 / raio, y2 / raio, z2 / raio)
                glVertex3f(x2, y2, z2)

            glEnd()

    # Eixos de debug
    def desenhar_eixos(self):
        glDisable(GL_LIGHTING)

        glLineWidth(2.0)

        glBegin(GL_LINES)

        glColor3f(1.0, 0.0, 0.0)
        glVertex3f(-5, 0.0, 0.0)
        glVertex3f(5, 0.0, 0.0)

        glColor3f(0.0, 1.0, 0.0)
        glVertex3f(0.0, -2, 0.0)
        glVertex3f(0.0, 4, 0.0)

        glColor3f(0.0, 0.4, 1.0)
        glVertex3f(0.0, 0.0, Z_INICIO_PISTA - 1.0)
        glVertex3f(0.0, 0.0, Z_FIM_PISTA + 1.0)

        glEnd()

        glLineWidth(1.0)
        glEnable(GL_LIGHTING)