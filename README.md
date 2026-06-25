# BerimBeat

BerimBeat é um jogo rítmico 3D desenvolvido em Python para a disciplina de Computação Gráfica.

O projeto usa OpenGL para renderizar a cena 3D, GLFW para criação da janela e entrada de teclado, pygame para áudio e textos da interface, e arquivos JSON para definir os mapas de notas.

## Tecnologias

* Python
* GLFW
* PyOpenGL
* pygame

## Estrutura do projeto

```text
berimbeat/
  audio.py
  config.py
  game.py
  map_loader.py
  notes.py
  renderer.py

assets/
  maps/
  music/

tools/
  gerar_mapa_audio.py
  gerar_mapa_bpm_fixo.py
  gerar_variantes_librosa.py

main.py
requirements.txt
requirements-dev.txt
```

## Como executar

Crie um ambiente virtual na raiz do projeto:

```bash
python -m venv .venv
```

Ative o ambiente virtual no Windows PowerShell:

```bash
.\.venv\Scripts\Activate.ps1
```

Ou no Git Bash:

```bash
source .venv/Scripts/activate
```

Instale as dependências principais:

```bash
pip install -r requirements.txt
```

Execute o jogo:

```bash
python main.py
```

No Windows, se o comando `python` não funcionar, use:

```bash
py main.py
```

## Controles

* `A`, `S`, `D`: acionar as faixas
* `ENTER`: iniciar o mapa selecionado
* `R`: reiniciar a partida
* `BACKSPACE`: voltar ao menu
* `ESC`: sair

## Mapas

As notas do jogo são carregadas a partir de arquivos JSON. Cada nota possui um tempo e uma faixa:

```json
{
  "tempo": 1.5,
  "faixa": 0
}
```

Durante a execução, o jogo converte esses dados em notas que se deslocam pela pista até a zona de acerto.

## Interface e HUD

A interface é desenhada sobre a cena 3D. O pygame renderiza o texto em uma superfície 2D, essa superfície é convertida para textura, e o OpenGL aplica a textura sobre um retângulo 2D. Por isso, o HUD fica fixo na tela e não acompanha a câmera 3D.

## Scripts experimentais

A pasta `tools/` contém scripts usados em testes de geração automática de mapas a partir de áudio, BPM fixo e análise com librosa. Esses scripts foram mantidos como registro das tentativas realizadas, mas não são necessários para executar o jogo principal.

Para usar esses scripts, instale as dependências extras:

```bash
pip install -r requirements-dev.txt
```

## Observação

A música real foi mantida como parte da proposta temática do projeto. Como o sincronismo automático com áudio orgânico de capoeira apresentou limitações, os mapas demonstrativos foram utilizados para validar a jogabilidade, a movimentação das notas, o sistema de pontuação e a renderização da cena.
