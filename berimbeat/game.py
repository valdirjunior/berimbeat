import sys
import glfw

from berimbeat.config import (
    LARGURA_JANELA,
    ALTURA_JANELA,
    TITULO_JANELA,
    FAIXAS,
    VELOCIDADE_FEEDBACK,
    MUSICAS,
    MUSICA_INICIAL,
)

from berimbeat.audio import AudioManager
from berimbeat.notes import criar_notas, tentar_acertar, atualizar_notas
from berimbeat.renderer import Renderer
from berimbeat.map_loader import carregar_mapa_json


ESTADO_MENU = "menu"
ESTADO_JOGANDO = "jogando"
ESTADO_RESULTADO = "resultado"


class BerimBeatGame:
    def __init__(self):
        self.window = None
        self.renderer = Renderer()
        self.audio = AudioManager()

        self.estado = ESTADO_MENU

        self.musica_atual_id = MUSICA_INICIAL
        self.musica_atual = MUSICAS[self.musica_atual_id]
        self.offset_musica = self.musica_atual.get("offset", 0.0)
        self.mapa_atual = None

        self.notas = []
        self.tempo_inicio = 0.0
        self.tempo_anterior = 0.0

        self.pontos = 0
        self.combo = 0
        self.maior_combo = 0

        self.acertos = 0
        self.erros = 0
        self.notas_perdidas = 0
        self.teclas_erradas = 0

        self.feedbacks = {i: 0.0 for i in range(len(FAIXAS))}
        self.ultimo_resultado = ""

    # Janela GLFW
    def iniciar_janela(self):
        if not glfw.init():
            sys.exit("Erro ao inicializar GLFW")

        self.window = glfw.create_window(
            LARGURA_JANELA,
            ALTURA_JANELA,
            TITULO_JANELA,
            None,
            None,
        )

        if not self.window:
            glfw.terminate()
            sys.exit("Erro ao criar janela")

        glfw.make_context_current(self.window)

        glfw.set_key_callback(self.window, self.teclado)
        glfw.set_framebuffer_size_callback(self.window, self.redimensionar)

        self.renderer.configurar_opengl(LARGURA_JANELA, ALTURA_JANELA)

    def redimensionar(self, window, largura, altura):
        self.renderer.redimensionar(largura, altura)

    # Tempo usado para sincronizar notas e mapa
    def tempo_jogo(self):
        tempo = glfw.get_time() - self.tempo_inicio + self.offset_musica
        return max(0.0, tempo)

    # Seleção no menu
    def selecionar_musica(self, musica_id):
        if musica_id not in MUSICAS:
            return

        self.musica_atual_id = musica_id
        self.musica_atual = MUSICAS[musica_id]
        self.offset_musica = self.musica_atual.get("offset", 0.0)

    def selecionar_musica_por_numero(self, numero):
        ids_musicas = list(MUSICAS.keys())
        indice = numero - 1

        if indice < 0 or indice >= len(ids_musicas):
            return

        self.selecionar_musica(ids_musicas[indice])

    # Início/reinício da partida
    def iniciar_partida(self):
        self.audio.parar_musica()

        self.musica_atual = MUSICAS[self.musica_atual_id]
        self.offset_musica = self.musica_atual.get("offset", 0.0)

        caminho_mapa = self.musica_atual.get("mapa")

        if not caminho_mapa:
            print("[MAPA] Música/mapa sem campo 'mapa' configurado.")
            return

        self.mapa_atual = carregar_mapa_json(caminho_mapa)
        self.offset_musica += self.mapa_atual.get("offset", 0.0)

        self.notas = criar_notas(self.mapa_atual["notas"])

        self.pontos = 0
        self.combo = 0
        self.maior_combo = 0

        self.acertos = 0
        self.erros = 0
        self.notas_perdidas = 0
        self.teclas_erradas = 0

        self.feedbacks = {i: 0.0 for i in range(len(FAIXAS))}
        self.ultimo_resultado = ""

        arquivo_musica = self.musica_atual.get("arquivo")

        if arquivo_musica:
            musica_carregou = self.audio.carregar_musica(arquivo_musica)

            if musica_carregou:
                self.audio.tocar_musica(
                    repetir=self.musica_atual.get("repetir", True)
                )
        else:
            print("[AUDIO] Partida sem música. Usando apenas tempo interno do jogo.")

        self.tempo_inicio = glfw.get_time()
        self.tempo_anterior = self.tempo_inicio

        self.estado = ESTADO_JOGANDO

    def voltar_menu(self):
        self.audio.parar_musica()
        self.estado = ESTADO_MENU
        self.ultimo_resultado = ""

    def finalizar_partida(self):
        self.audio.parar_musica()
        self.estado = ESTADO_RESULTADO
        self.combo = 0

    # Entrada de teclado por estado
    def teclado(self, window, key, scancode, action, mods):
        if action != glfw.PRESS:
            return

        if key == glfw.KEY_ESCAPE:
            glfw.set_window_should_close(self.window, True)
            return

        if self.estado == ESTADO_MENU:
            self.teclado_menu(key)
            return

        if self.estado == ESTADO_JOGANDO:
            self.teclado_jogo(key)
            return

        if self.estado == ESTADO_RESULTADO:
            self.teclado_resultado(key)
            return

    def teclado_menu(self, key):
        if glfw.KEY_1 <= key <= glfw.KEY_9:
            numero = key - glfw.KEY_0
            self.selecionar_musica_por_numero(numero)
            return

        if key == glfw.KEY_ENTER:
            self.iniciar_partida()

    def teclado_resultado(self, key):
        if key == glfw.KEY_R:
            self.iniciar_partida()
            return

        if key == glfw.KEY_BACKSPACE:
            self.voltar_menu()
            return

    def teclado_jogo(self, key):
        if key == glfw.KEY_R:
            self.iniciar_partida()
            return

        if key == glfw.KEY_BACKSPACE:
            self.voltar_menu()
            return

        tempo = self.tempo_jogo()

        for indice, faixa in enumerate(FAIXAS):
            if key == faixa["glfw_key"]:
                resultado, pontos = tentar_acertar(self.notas, indice, tempo)
                self.processar_resultado(indice, resultado, pontos)
                return

    # Pontuação, combo e feedback de acerto
    def processar_resultado(self, indice_faixa, resultado, pontos):
        self.ultimo_resultado = resultado

        if pontos > 0:
            self.combo += 1
            self.acertos += 1
            self.maior_combo = max(self.maior_combo, self.combo)

            multiplicador = self.multiplicador_combo()
            self.pontos += pontos * multiplicador

            self.feedbacks[indice_faixa] = 1.0
        else:
            self.combo = 0
            self.teclas_erradas += 1
            self.erros = self.total_erros()

    # Atualização da lógica
    def atualizar(self, delta):
        if self.estado == ESTADO_JOGANDO:
            self.atualizar_jogo(delta)

        self.atualizar_feedbacks(delta)
        self.atualizar_titulo_debug()

    def atualizar_jogo(self, delta):
        tempo = self.tempo_jogo()
        novos_erros = atualizar_notas(self.notas, tempo)

        if novos_erros > 0:
            self.combo = 0
            self.notas_perdidas += novos_erros
            self.erros = self.total_erros()
            self.ultimo_resultado = "perdeu"

        if self.todas_notas_finalizadas():
            self.finalizar_partida()

    def atualizar_feedbacks(self, delta):
        for faixa in self.feedbacks:
            self.feedbacks[faixa] = max(
                0.0,
                self.feedbacks[faixa] - delta * VELOCIDADE_FEEDBACK
            )

    def todas_notas_finalizadas(self):
        if len(self.notas) == 0:
            return False

        for nota in self.notas:
            if nota["ativa"]:
                return False

        return True

    # Estatísticas da partida
    def total_erros(self):
        return self.notas_perdidas + self.teclas_erradas

    def total_tentativas_resultado(self):
        return self.acertos + self.total_erros()

    def precisao_resultado(self):
        total = self.total_tentativas_resultado()

        if total == 0:
            return 0.0

        return (self.acertos / total) * 100.0

    def desempenho_resultado(self):
        precisao = self.precisao_resultado()

        if precisao >= 90:
            return "S"

        if precisao >= 75:
            return "A"

        if precisao >= 60:
            return "B"

        if precisao >= 40:
            return "C"

        return "D"

    def multiplicador_combo(self):
        if self.combo >= 50:
            return 4

        if self.combo >= 25:
            return 3

        if self.combo >= 10:
            return 2

        return 1

    # Informações usadas pelo menu e HUD
    def nome_mapa_atual(self):
        if self.mapa_atual is None:
            return "sem mapa"

        variante = self.mapa_atual.get("variante")

        if variante:
            return variante

        return self.mapa_atual.get("id", "mapa")

    def nome_musica_atual(self):
        return self.musica_atual.get("nome", self.musica_atual_id)

    def opcoes_menu(self):
        opcoes = []

        for indice, musica_id in enumerate(MUSICAS.keys(), start=1):
            nome = MUSICAS[musica_id].get("nome", musica_id)
            opcoes.append(f"{indice} - {nome}")

        return opcoes

    def montar_hud(self):
        tempo = self.tempo_jogo()

        return {
            "pontos": self.pontos,
            "combo": self.combo,
            "multiplicador": self.multiplicador_combo(),
            "acertos": self.acertos,
            "erros": self.total_erros(),
            "notas_perdidas": self.notas_perdidas,
            "teclas_erradas": self.teclas_erradas,
            "maior_combo": self.maior_combo,
            "tempo": tempo,
            "musica": self.musica_atual.get("nome", "Música"),
            "mapa": self.nome_mapa_atual(),
            "resultado": self.ultimo_resultado,
        }

    def atualizar_titulo_debug(self):
        glfw.set_window_title(self.window, TITULO_JANELA)

    # Renderização por estado
    def desenhar(self):
        self.renderer.limpar()

        if self.estado == ESTADO_MENU:
            self.renderer.desenhar_menu(
                self.nome_musica_atual(),
                self.opcoes_menu(),
            )

        elif self.estado == ESTADO_JOGANDO:
            hud = self.montar_hud()

            self.renderer.desenhar_cena(
                self.notas,
                self.tempo_jogo(),
                self.feedbacks,
                hud,
            )

        elif self.estado == ESTADO_RESULTADO:
            self.renderer.desenhar_resultado(
                self.pontos,
                self.acertos,
                self.total_erros(),
                self.maior_combo,
                self.notas_perdidas,
                self.teclas_erradas,
                self.precisao_resultado(),
                self.desempenho_resultado(),
            )

    # Loop principal
    def executar(self):
        self.iniciar_janela()

        self.tempo_anterior = glfw.get_time()

        while not glfw.window_should_close(self.window):
            agora = glfw.get_time()
            delta = agora - self.tempo_anterior
            self.tempo_anterior = agora

            glfw.poll_events()

            self.atualizar(delta)
            self.desenhar()

            glfw.swap_buffers(self.window)

        self.audio.encerrar()
        glfw.terminate()
