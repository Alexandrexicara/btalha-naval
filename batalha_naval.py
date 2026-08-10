import pygame
import sys
import random

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
GRID_SIZE = 10
CELL_SIZE = 40
GRID_OFFSET_X = 50
GRID_OFFSET_Y = 150
ENEMY_GRID_OFFSET_X = 650

# Colors
COLOR_BG = (10, 22, 40)
COLOR_GRID = (26, 58, 95)
COLOR_GRID_BORDER = (42, 74, 106)
COLOR_WATER = (30, 58, 95)
COLOR_SHIP = (45, 90, 63)
COLOR_SHIP_HOVER = (58, 122, 85)
COLOR_HIT = (139, 46, 46)
COLOR_MISS = (42, 58, 74)
COLOR_HIDDEN = (30, 58, 95)
COLOR_HIDDEN_HOVER = (58, 106, 170)
COLOR_TEXT = (224, 224, 224)
COLOR_ACCENT = (78, 205, 196)
COLOR_ORANGE = (255, 107, 53)
COLOR_BUTTON = (26, 42, 64)
COLOR_BUTTON_HOVER = (42, 74, 106)
COLOR_BUTTON_ACTIVE = (42, 26, 16)

# Ship types
SHIPS = {
    'porta-aviões': 5,
    'navio-tanque': 4,
    'cruzador': 3,
    'submarino': 3,
    'destróier': 2
}

class BattleshipGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("⚓ Batalha Naval")
        self.clock = pygame.time.Clock()
        self.font_title = pygame.font.Font(None, 48)
        self.font_large = pygame.font.Font(None, 36)
        self.font_medium = pygame.font.Font(None, 28)
        self.font_small = pygame.font.Font(None, 20)
        
        # Game state
        self.phase = 'placement'  # 'placement', 'battle', 'game_over'
        self.player_board = self.create_board()
        self.enemy_board = self.create_board()
        self.player_shots = [[False for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        self.enemy_shots = [[False for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        
        # Ship placement
        self.current_ship = None
        self.ship_orientation = 'horizontal'
        self.placed_ships = []
        self.selected_cell = None
        
        # Place enemy ships randomly
        self.place_enemy_ships()
        
        # UI elements
        self.message = "Posicione seus navios!"
        self.selected_ship_name = None
        
    def create_board(self):
        return [[None for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
    
    def place_enemy_ships(self):
        for ship_name, ship_size in SHIPS.items():
            placed = False
            while not placed:
                orientation = random.choice(['horizontal', 'vertical'])
                if orientation == 'horizontal':
                    row = random.randint(0, GRID_SIZE - 1)
                    col = random.randint(0, GRID_SIZE - ship_size)
                    if self.can_place_ship(self.enemy_board, row, col, ship_size, orientation):
                        for i in range(ship_size):
                            self.enemy_board[row][col + i] = ship_name
                        placed = True
                else:
                    row = random.randint(0, GRID_SIZE - ship_size)
                    col = random.randint(0, GRID_SIZE - 1)
                    if self.can_place_ship(self.enemy_board, row, col, ship_size, orientation):
                        for i in range(ship_size):
                            self.enemy_board[row + i][col] = ship_name
                        placed = True
    
    def can_place_ship(self, board, row, col, size, orientation):
        if orientation == 'horizontal':
            if col + size > GRID_SIZE:
                return False
            for i in range(size):
                if board[row][col + i] is not None:
                    return False
        else:
            if row + size > GRID_SIZE:
                return False
            for i in range(size):
                if board[row + i][col] is not None:
                    return False
        return True
    
    def place_ship(self, row, col, ship_name, orientation):
        size = SHIPS[ship_name]
        if self.can_place_ship(self.player_board, row, col, size, orientation):
            if orientation == 'horizontal':
                for i in range(size):
                    self.player_board[row][col + i] = ship_name
            else:
                for i in range(size):
                    self.player_board[row + i][col] = ship_name
            self.placed_ships.append(ship_name)
            return True
        return False
    
    def get_next_ship(self):
        for ship_name in SHIPS.keys():
            if ship_name not in self.placed_ships:
                return ship_name
        return None
    
    def fire_at_enemy(self, row, col):
        if self.player_shots[row][col]:
            return False  # Already fired here
        
        self.player_shots[row][col] = True
        if self.enemy_board[row][col] is not None:
            return True  # Hit
        return False  # Miss
    
    def enemy_fire(self):
        # Simple AI: random firing
        available = []
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                if not self.enemy_shots[row][col]:
                    available.append((row, col))
        
        if available:
            row, col = random.choice(available)
            self.enemy_shots[row][col] = True
            return row, col, self.player_board[row][col] is not None
        return None
    
    def check_winner(self):
        # Check if all enemy ships are sunk
        enemy_ships_left = False
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                if self.enemy_board[row][col] is not None:
                    if not self.player_shots[row][col]:
                        enemy_ships_left = True
                        break
        
        if not enemy_ships_left:
            return 'player'
        
        # Check if all player ships are sunk
        player_ships_left = False
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                if self.player_board[row][col] is not None:
                    if not self.enemy_shots[row][col]:
                        player_ships_left = True
                        break
        
        if not player_ships_left:
            return 'enemy'
        
        return None
    
    def draw_board(self, board, shots, offset_x, offset_y, is_enemy=False):
        # Draw grid background
        grid_width = GRID_SIZE * CELL_SIZE + 20
        grid_height = GRID_SIZE * CELL_SIZE + 20
        pygame.draw.rect(self.screen, COLOR_GRID, (offset_x - 10, offset_y - 10, grid_width, grid_height), border_radius=10)
        pygame.draw.rect(self.screen, COLOR_GRID_BORDER, (offset_x - 10, offset_y - 10, grid_width, grid_height), 2, border_radius=10)
        
        # Draw column headers (A-J)
        for col in range(GRID_SIZE):
            header = chr(65 + col)
            text = self.font_small.render(header, True, (136, 153, 170))
            text_rect = text.get_rect(center=(offset_x + col * CELL_SIZE + CELL_SIZE // 2, offset_y - 20))
            self.screen.blit(text, text_rect)
        
        # Draw row headers (1-10)
        for row in range(GRID_SIZE):
            text = self.font_small.render(str(row + 1), True, (136, 153, 170))
            text_rect = text.get_rect(center=(offset_x - 20, offset_y + row * CELL_SIZE + CELL_SIZE // 2))
            self.screen.blit(text, text_rect)
        
        # Draw cells
        mouse_pos = pygame.mouse.get_pos()
        
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                x = offset_x + col * CELL_SIZE
                y = offset_y + row * CELL_SIZE
                rect = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)
                
                # Determine cell color
                color = COLOR_WATER
                if board[row][col] is not None:
                    color = COLOR_SHIP
                
                # Check for shots
                if shots[row][col]:
                    if board[row][col] is not None:
                        color = COLOR_HIT
                    else:
                        color = COLOR_MISS
                
                # Hover effect
                if rect.collidepoint(mouse_pos):
                    if is_enemy and not shots[row][col]:
                        color = COLOR_HIDDEN_HOVER
                    elif not is_enemy and board[row][col] is not None:
                        color = COLOR_SHIP_HOVER
                
                # Draw cell
                pygame.draw.rect(self.screen, color, rect, border_radius=4)
                
                # Draw ship indicator (for player board or when hit)
                if board[row][col] is not None and (not is_enemy or shots[row][col]):
                    if shots[row][col]:
                        # Draw hit marker
                        pygame.draw.circle(self.screen, COLOR_ORANGE, rect.center, 8)
                    else:
                        # Draw ship indicator
                        pygame.draw.rect(self.screen, COLOR_ACCENT, (x + 8, y + 8, CELL_SIZE - 16, CELL_SIZE - 16), border_radius=2)
                
                # Draw miss marker
                if shots[row][col] and board[row][col] is None:
                    pygame.draw.circle(self.screen, (102, 119, 136), rect.center, 5)
    
    def draw_ui(self):
        # Title
        title = self.font_title.render("⚓ Batalha Naval", True, COLOR_ORANGE)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 40))
        self.screen.blit(title, title_rect)
        
        # Phase indicator
        phase_text = f"Fase: {'Posicionamento' if self.phase == 'placement' else 'Batalha'}"
        phase = self.font_medium.render(phase_text, True, COLOR_ACCENT)
        phase_rect = phase.get_rect(center=(SCREEN_WIDTH // 2, 80))
        self.screen.blit(phase, phase_rect)
        
        # Board labels
        player_label = self.font_medium.render("Seu Tabuleiro", True, COLOR_ACCENT)
        player_label_rect = player_label.get_rect(center=(GRID_OFFSET_X + GRID_SIZE * CELL_SIZE // 2, 120))
        self.screen.blit(player_label, player_label_rect)
        
        enemy_label = self.font_medium.render("Tabuleiro Inimigo", True, COLOR_ACCENT)
        enemy_label_rect = enemy_label.get_rect(center=(ENEMY_GRID_OFFSET_X + GRID_SIZE * CELL_SIZE // 2, 120))
        self.screen.blit(enemy_label, enemy_label_rect)
        
        # Message
        message = self.font_medium.render(self.message, True, COLOR_ORANGE)
        message_rect = message.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100))
        self.screen.blit(message, message_rect)
        
        # Ship selection during placement
        if self.phase == 'placement':
            self.draw_ship_selection()
        
        # Controls help
        help_text = "Clique para posicionar/disparar | R para rotacionar navio"
        help = self.font_small.render(help_text, True, (136, 153, 170))
        help_rect = help.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50))
        self.screen.blit(help, help_rect)
    
    def draw_ship_selection(self):
        next_ship = self.get_next_ship()
        if next_ship:
            ship_info = f"Navio atual: {next_ship} (tamanho {SHIPS[next_ship]})"
            ship_text = self.font_medium.render(ship_info, True, COLOR_ACCENT)
            ship_rect = ship_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 140))
            self.screen.blit(ship_text, ship_rect)
            
            orientation_text = f"Orientação: {'Horizontal' if self.ship_orientation == 'horizontal' else 'Vertical'} (Pressione R)"
            orientation = self.font_small.render(orientation_text, True, (136, 153, 170))
            orientation_rect = orientation.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 170))
            self.screen.blit(orientation, orientation_rect)
        else:
            # All ships placed, show start battle button
            start_text = self.font_large.render("Pressione ESPAÇO para começar a batalha!", True, COLOR_ORANGE)
            start_rect = start_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 140))
            self.screen.blit(start_text, start_rect)
    
    def draw_game_over(self, winner):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        self.screen.blit(overlay, (0, 0))
        
        if winner == 'player':
            text = "🎉 VOCÊ VENCEU! 🎉"
            color = COLOR_ACCENT
        else:
            text = "💀 VOCÊ PERDEU! 💀"
            color = (255, 68, 68)
        
        game_over_text = self.font_title.render(text, True, color)
        text_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        self.screen.blit(game_over_text, text_rect)
        
        restart_text = self.font_large.render("Pressione R para reiniciar", True, COLOR_TEXT)
        restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
        self.screen.blit(restart_text, restart_rect)
    
    def handle_click(self, pos):
        if self.phase == 'game_over':
            return
        
        # Check if click is on player board (placement phase)
        if self.phase == 'placement':
            player_grid_x = GRID_OFFSET_X
            player_grid_y = GRID_OFFSET_Y
            
            if (player_grid_x <= pos[0] <= player_grid_x + GRID_SIZE * CELL_SIZE and
                player_grid_y <= pos[1] <= player_grid_y + GRID_SIZE * CELL_SIZE):
                
                col = (pos[0] - player_grid_x) // CELL_SIZE
                row = (pos[1] - player_grid_y) // CELL_SIZE
                
                next_ship = self.get_next_ship()
                if next_ship:
                    if self.place_ship(row, col, next_ship, self.ship_orientation):
                        self.message = f"{next_ship} posicionado!"
                        if not self.get_next_ship():
                            self.message = "Todos os navios posicionados! Pressione ESPAÇO para começar."
                    else:
                        self.message = "Não é possível posicionar o navio aqui!"
        
        # Check if click is on enemy board (battle phase)
        elif self.phase == 'battle':
            enemy_grid_x = ENEMY_GRID_OFFSET_X
            enemy_grid_y = GRID_OFFSET_Y
            
            if (enemy_grid_x <= pos[0] <= enemy_grid_x + GRID_SIZE * CELL_SIZE and
                enemy_grid_y <= pos[1] <= enemy_grid_y + GRID_SIZE * CELL_SIZE):
                
                col = (pos[0] - enemy_grid_x) // CELL_SIZE
                row = (pos[1] - enemy_grid_y) // CELL_SIZE
                
                if not self.player_shots[row][col]:
                    hit = self.fire_at_enemy(row, col)
                    if hit:
                        self.message = "ACERTOU! 🎯"
                    else:
                        self.message = "Errou! 💧"
                    
                    # Enemy's turn
                    enemy_result = self.enemy_fire()
                    if enemy_result:
                        enemy_row, enemy_col, enemy_hit = enemy_result
                        if enemy_hit:
                            self.message += " | Inimigo acertou seu navio!"
                        else:
                            self.message += " | Inimigo errou!"
                    
                    # Check for winner
                    winner = self.check_winner()
                    if winner:
                        self.phase = 'game_over'
    
    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Left click
                        self.handle_click(event.pos)
                
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        if self.phase == 'placement':
                            self.ship_orientation = 'vertical' if self.ship_orientation == 'horizontal' else 'horizontal'
                        elif self.phase == 'game_over':
                            # Restart game
                            self.__init__()
                    
                    elif event.key == pygame.K_SPACE:
                        if self.phase == 'placement' and not self.get_next_ship():
                            self.phase = 'battle'
                            self.message = "Batalha iniciada! Clique no tabuleiro inimigo para disparar."
            
            # Draw everything
            self.screen.fill(COLOR_BG)
            
            # Draw boards
            self.draw_board(self.player_board, self.enemy_shots, GRID_OFFSET_X, GRID_OFFSET_Y, is_enemy=False)
            self.draw_board(self.enemy_board, self.player_shots, ENEMY_GRID_OFFSET_X, GRID_OFFSET_Y, is_enemy=True)
            
            # Draw UI
            self.draw_ui()
            
            # Draw game over screen if needed
            if self.phase == 'game_over':
                winner = self.check_winner()
                self.draw_game_over(winner)
            
            pygame.display.flip()
            self.clock.tick(60)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = BattleshipGame()
    game.run()