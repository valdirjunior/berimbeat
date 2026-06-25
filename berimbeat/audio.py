from pathlib import Path

import pygame

from berimbeat.config import (
    AUDIO_ATIVO,
    VOLUME_MUSICA,
    VOLUME_EFEITOS,
)


class AudioManager:
    def __init__(self):
        self.inicializado = False
        self.musica_carregada = False
        self.caminho_musica_atual = None

        if AUDIO_ATIVO:
            self.inicializar()

    def inicializar(self):
        try:
            pygame.mixer.init()
            pygame.mixer.music.set_volume(VOLUME_MUSICA)
            self.inicializado = True

        except pygame.error as erro:
            print(f"[AUDIO] Não foi possível iniciar o mixer: {erro}")
            self.inicializado = False

    def carregar_musica(self, caminho):
        if not self.inicializado:
            return False

        caminho_completo = self.resolver_caminho(caminho)

        if not caminho_completo.exists():
            print(f"[AUDIO] Música não encontrada: {caminho_completo}")
            self.musica_carregada = False
            return False

        try:
            pygame.mixer.music.load(str(caminho_completo))
            pygame.mixer.music.set_volume(VOLUME_MUSICA)

            self.caminho_musica_atual = caminho_completo
            self.musica_carregada = True

            return True

        except pygame.error as erro:
            print(f"[AUDIO] Erro ao carregar música: {erro}")
            self.musica_carregada = False
            return False

    def tocar_musica(self, repetir=True):
        if not self.inicializado or not self.musica_carregada:
            return

        loops = -1 if repetir else 0
        pygame.mixer.music.play(loops=loops)

    def parar_musica(self):
        if self.inicializado:
            pygame.mixer.music.stop()

    def pausar_musica(self):
        if self.inicializado:
            pygame.mixer.music.pause()

    def retomar_musica(self):
        if self.inicializado:
            pygame.mixer.music.unpause()

    def musica_tocando(self):
        if not self.inicializado:
            return False

        return pygame.mixer.music.get_busy()

    def carregar_efeito(self, caminho):
        if not self.inicializado:
            return None

        caminho_completo = self.resolver_caminho(caminho)

        if not caminho_completo.exists():
            print(f"[AUDIO] Efeito não encontrado: {caminho_completo}")
            return None

        try:
            efeito = pygame.mixer.Sound(str(caminho_completo))
            efeito.set_volume(VOLUME_EFEITOS)
            return efeito

        except pygame.error as erro:
            print(f"[AUDIO] Erro ao carregar efeito: {erro}")
            return None

    def encerrar(self):
        if self.inicializado:
            pygame.mixer.music.stop()
            pygame.mixer.quit()
            self.inicializado = False

    def resolver_caminho(self, caminho):
        raiz_projeto = Path(__file__).resolve().parent.parent
        return raiz_projeto / caminho