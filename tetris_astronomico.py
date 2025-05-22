import pygame
import random
import requests
from datetime import datetime
import pytz

# Inicializa o Pygame
pygame.init()

# Configurações gerais
WIDTH, HEIGHT = 500, 620  # Tamanho da janela
GRID_WIDTH, GRID_HEIGHT = 10, 20  # Tamanho da grade (10 colunas, 20 linhas)
CELL_SIZE = 30  # Tamanho de cada célula (30x30 pixels)
GOIANIA_TZ = pytz.timezone('America/Sao_Paulo')  # Fuso horário de Goiânia (UTC-3)
NASA_API_KEY = "snngNMZnw1hqXpKEndt1Ggodg7Ld3FgthI9XlwpJ" 

# Cores (RGB) para o tema astronômico
COLORS = {
    0: (26, 31, 40),  # Cinza escuro (fundo da grade)
    1: (47, 230, 23),  # Verde (bloco)
    2: (232, 18, 18),  # Vermelho (bloco)
    3: (226, 116, 17),  # Laranja (bloco)
    4: (237, 234, 4),  # Amarelo (bloco)
    5: (166, 0, 247),  # Roxo (bloco)
    6: (21, 204, 209),  # Ciano (bloco)
    7: (13, 64, 216),  # Azul (bloco)
    'white': (255, 255, 255),  # Branco (texto)
    'dark_blue': (44, 44, 127),  # Azul escuro (fundo da tela)
    'light_blue': (59, 85, 162)  # Azul claro (bordas)
}

# Formas dos blocos (cada bloco tem uma forma inicial)
BLOCK_SHAPES = [
    [[(0, 2), (1, 0), (1, 1), (1, 2)]],  # L
    [[(0, 0), (1, 0), (1, 1), (1, 2)]],  # J
    [[(1, 0), (1, 1), (1, 2), (1, 3)]],  # I
    [[(0, 0), (0, 1), (1, 0), (1, 1)]],  # O
    [[(0, 1), (0, 2), (1, 0), (1, 1)]],  # S
    [[(0, 1), (1, 0), (1, 1), (1, 2)]],  # T
    [[(0, 0), (0, 1), (1, 1), (1, 2)]]   # Z
]

# Função para buscar dados da NASA APOD
def fetch_nasa_data():
    try:
        response = requests.get(f"https://api.nasa.gov/planetary/apod?api_key={NASA_API_KEY}")  # Chama API
        response.raise_for_status()  # Verifica erros
        apod = response.json()  # Converte para JSON
        return {
            "title": apod.get("title", "Imagem Astronômica"),  # Título da imagem
            "date": apod.get("date", "Desconhecida")  # Data da imagem
        }
    except requests.exceptions.RequestException:
        return {
            "title": "NGC 1234 (Galáxia Espiral)",  # Fallback
            "date": datetime.now(GOIANIA_TZ).strftime("%Y-%m-%d")  # Data atual
        }

# Configuração da tela e fonte
screen = pygame.display.set_mode((WIDTH, HEIGHT))  # Cria janela
pygame.display.set_caption("Tetris Astronômico")  # Define título
font = pygame.font.Font(None, 40)  # Fonte para textos
clock = pygame.time.Clock()  # Controle de FPS

# Estado inicial do jogo
grid = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]  # Grade 20x10
current_block = None  # Bloco atual
next_block = None  # Próximo bloco
block_pos = [0, 0]  # Posição do bloco (linha, coluna)
game_over = False  # Estado de fim de jogo
score = 0  # Pontuação
nasa_data = fetch_nasa_data()  # Busca dados da NASA

# Função para criar um novo bloco
def new_block():
    global current_block, next_block, block_pos
    if next_block is None:
        current_block = random.choice(BLOCK_SHAPES)  # Escolhe forma aleatória
        next_block = random.choice(BLOCK_SHAPES)  # Escolhe próximo bloco
    else:
        current_block = next_block  # Usa o próximo bloco
        next_block = random.choice(BLOCK_SHAPES)  # Escolhe novo próximo
    block_pos = [0, 3]  # Começa no topo, coluna 3
    if not block_fits():  # Verifica se o bloco cabe
        return False  # Retorna False se não couber
    return True

# Verifica se o bloco cabe na grade
def block_fits():
    for row, col in current_block[0]:  # Itera sobre as células do bloco
        new_row, new_col = row + block_pos[0], col + block_pos[1]  # Posição na grade
        if (new_row >= GRID_HEIGHT or new_col < 0 or new_col >= GRID_WIDTH or
                (new_row >= 0 and grid[new_row][new_col] != 0)):  # Verifica limites e colisão
            return False  # Não cabe
    return True  # Cabe

# Move o bloco
def move_block(dx, dy):
    global block_pos
    block_pos[1] += dx  # Move horizontalmente
    block_pos[0] += dy  # Move verticalmente
    if not block_fits():  # Verifica se a nova posição é válida
        block_pos[1] -= dx  # Desfaz movimento horizontal
        block_pos[0] -= dy  # Desfaz movimento vertical
        return False  # Movimento inválido
    return True  # Movimento válido

# Trava o bloco na grade
def lock_block():
    global score
    for row, col in current_block[0]:  # Itera sobre as células do bloco
        new_row, new_col = row + block_pos[0], col + block_pos[1]  # Posição na grade
        if new_row >= 0:
            grid[new_row][new_col] = current_block[0][0][0] % 7 + 1  # Marca com ID do bloco
    lines_cleared = 0  # Contador de linhas limpas
    for row in range(GRID_HEIGHT - 1, -1, -1):  # Itera de baixo para cima
        if all(grid[row]):  # Verifica se a linha está cheia
            lines_cleared += 1  # Incrementa contador
            grid.pop(row)  # Remove linha
            grid.insert(0, [0] * GRID_WIDTH)  # Adiciona linha vazia no topo
    if lines_cleared == 1:
        score += 100  # 100 pontos por 1 linha
    elif lines_cleared == 2:
        score += 300  # 300 pontos por 2 linhas
    elif lines_cleared == 3:
        score += 500  # 500 pontos por 3 linhas
    return new_block()  # Cria novo bloco

# Desenha a grade e os blocos
def draw():
    screen.fill(COLORS['dark_blue'])  # Preenche fundo com azul escuro
    # Desenha grade
    for row in range(GRID_HEIGHT):
        for col in range(GRID_WIDTH):
            rect = pygame.Rect(col * CELL_SIZE + 11, row * CELL_SIZE + 11,
                              CELL_SIZE - 1, CELL_SIZE - 1)  # Retângulo da célula
            pygame.draw.rect(screen, COLORS[grid[row][col]], rect)  # Desenha célula
    # Desenha bloco atual
    if current_block and not game_over:
        for row, col in current_block[0]:
            new_row, new_col = row + block_pos[0], col + block_pos[1]
            if new_row >= 0:
                rect = pygame.Rect(new_col * CELL_SIZE + 11, new_row * CELL_SIZE + 11,
                                  CELL_SIZE - 1, CELL_SIZE - 1)  # Retângulo da célula
                pygame.draw.rect(screen, COLORS[current_block[0][0][0] % 7 + 1], rect)  # Desenha célula
    # Desenha próximo bloco
    if next_block:
        for row, col in next_block[0]:
            rect = pygame.Rect((col + 9) * CELL_SIZE, (row + 7) * CELL_SIZE,
                              CELL_SIZE - 1, CELL_SIZE - 1)  # Posição ajustada
            pygame.draw.rect(screen, COLORS[next_block[0][0][0] % 7 + 1], rect)  # Desenha célula
    # Desenha textos
    score_text = font.render(f"Pontuação: {score}", True, COLORS['white'])  # Texto da pontuação
    screen.blit(score_text, (320, 20))  # Desenha pontuação
    next_text = font.render("Próximo:", True, COLORS['white'])  # Texto "Próximo"
    screen.blit(next_text, (320, 180))  # Desenha "Próximo"
    nasa_title = font.render(f"NASA: {nasa_data['title']}", True, COLORS['white'])  # Título da APOD
    screen.blit(nasa_title, (320, 360))  # Desenha título
    nasa_date = font.render(f"Data: {nasa_data['date']}", True, COLORS['white'])  # Data da APOD
    screen.blit(nasa_date, (320, 390))  # Desenha data
    time_text = font.render(datetime.now(GOIANIA_TZ).strftime("%H:%M:%S -03"), True, COLORS['white'])  # Hora atual
    screen.blit(time_text, (320, 420))  # Desenha hora
    if game_over:
        game_over_text = font.render("FIM DE JOGO", True, COLORS['white'])  # Texto de fim de jogo
        screen.blit(game_over_text, (320, 450))  # Desenha "FIM DE JOGO"

# Inicia o primeiro bloco
if not new_block():
    game_over = True

# Loop principal do jogo
last_drop = pygame.time.get_ticks()  # Última queda automática
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:  # Fecha o jogo
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if game_over:  # Reseta o jogo se terminado
                grid = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]  # Reseta grade
                score = 0  # Zera pontuação
                game_over = False  # Reseta fim de jogo
                nasa_data = fetch_nasa_data()  # Busca novos dados da NASA
                new_block()  # Cria novo bloco
            if not game_over:
                if event.key == pygame.K_LEFT:  # Move esquerda
                    move_block(-1, 0)
                if event.key == pygame.K_RIGHT:  # Move direita
                    move_block(1, 0)
                if event.key == pygame.K_DOWN:  # Move baixo
                    if move_block(0, 1):
                        score += 1  # Adiciona 1 ponto
                    else:
                        if not lock_block():
                            game_over = True  # Fim de jogo se não couber
    # Faz o bloco cair automaticamente a cada 200ms
    if not game_over and pygame.time.get_ticks() - last_drop > 200:
        if not move_block(0, 1):  # Tenta mover para baixo
            if not lock_block():  # Trava bloco se não puder descer
                game_over = True  # Fim de jogo se não couber
        last_drop = pygame.time.get_ticks()  # Atualiza tempo da última queda
    draw()  # Desenha tudo na tela
    pygame.display.update()  # Atualiza a tela
    clock.tick(60)  # Limita a 60 FPS
