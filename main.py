import pygame
from sys import exit
import random
import math
import os
from typing import List, Tuple

# Initialize pygame and mixer
pygame.init()
pygame.mixer.init()

# Enhanced screen setup with a wider display
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 576
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Epic Runner Deluxe")
clock = pygame.time.Clock()
background_image = pygame.image.load("/Users/shivamsahu/Kabir Session 4/graphics/bg.png").convert()
background_image = pygame.transform.scale(background_image, (SCREEN_WIDTH, SCREEN_HEIGHT))

screen.blit(background_image, (0, 0))


# Enhanced color palette with more vibrant colors
COLORS = {
    'sky': (135, 206, 235),
    'ground': (00, 00, 00),  # More vibrant green
    'player': (255, 69, 0),   # Bright orange-red
    'obstacle': (139, 0, 139), # Purple
    'flying': (255, 215, 0),  # Gold
    'bullet': (0, 191, 255),  # Deep sky blue
    'powerup': (255, 140, 0), # Dark orange
    'health': (220, 20, 60),  # Crimson
    'shield': (147, 112, 219),# Medium purple
    'menu_bg': (25, 25, 35),  # Dark blue-grey
    'button_active': (46, 204, 113),  # Emerald green
    'button_inactive': (39, 174, 96), # Less bright emerald
    'text': (236, 240, 241)   # Almost white
}

# Enhanced visual elements
def create_player_surface() -> pygame.Surface:
    surface = pygame.Surface((50, 50), pygame.SRCALPHA)
    # Create a more detailed player character
    pygame.draw.rect(surface, COLORS['player'], (10, 0, 30, 40))  # Body
    pygame.draw.circle(surface, COLORS['player'], (25, 10), 10)   # Head
    pygame.draw.rect(surface, COLORS['player'], (15, 40, 8, 10))  # Left leg
    pygame.draw.rect(surface, COLORS['player'], (27, 40, 8, 10))  # Right leg
    return surface

def create_particle_effect(pos: Tuple[int, int], color: Tuple[int, int, int]) -> List[dict]:
    particles = []
    for _ in range(10):
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(2, 5)
        particle = {
            'pos': list(pos),
            'vel': [math.cos(angle) * speed, math.sin(angle) * speed],
            'timer': 30,
            'color': color
        }
        particles.append(particle)
    return particles

# Enhanced game assets
PLAYER_IMAGE = create_player_surface()
FONTS = {
    'main': pygame.font.Font(None, 74),
    'ui': pygame.font.Font(None, 36),
    'title': pygame.font.Font(None, 100)
}

# Enhanced sound effects
def create_enhanced_sound(duration_ms: int = 100, frequency: int = 440, volume: float = 0.3) -> pygame.mixer.Sound:
    sample_rate = 44100
    duration = duration_ms / 1000.0
    num_samples = int(sample_rate * duration)
    samples = []
    
    for i in range(num_samples):
        t = i / sample_rate
        sample = int(127 * volume * (
            math.sin(2 * math.pi * frequency * t) +
            0.5 * math.sin(4 * math.pi * frequency * t)
        ))
        samples.append(max(-127, min(127, sample)) + 127)
    
    return pygame.mixer.Sound(buffer=bytes(samples))

# Enhanced sound effects
SOUNDS = {
    'jump': create_enhanced_sound(150, 523, 0.4),  # C5
    'shoot': create_enhanced_sound(100, 784, 0.3), # G5
    'hit': create_enhanced_sound(300, 165, 0.5),   # E3
    'powerup': create_enhanced_sound(200, 988, 0.4),# B5
    'button': create_enhanced_sound(50, 659, 0.2)  # E5
}

class EnhancedParticleSystem:
    def __init__(self):
        self.particles: List[dict] = []
    
    def add_particles(self, pos: Tuple[int, int], color: Tuple[int, int, int]):
        self.particles.extend(create_particle_effect(pos, color))
    
    def update(self):
        for particle in self.particles[:]:
            particle['pos'][0] += particle['vel'][0]
            particle['pos'][1] += particle['vel'][1]
            particle['timer'] -= 1
            if particle['timer'] <= 0:
                self.particles.remove(particle)
    
    def draw(self, surface: pygame.Surface):
        for particle in self.particles:
            alpha = min(255, particle['timer'] * 8)
            color = (*particle['color'], alpha)
            pos = [int(particle['pos'][0]), int(particle['pos'][1])]
            pygame.draw.circle(surface, color, pos, 2)

class EnhancedPlayer(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        path = os.path.join("/Users/shivamsahu", "Kabir Session 4", "graphics", "dragon.png")
        self.image = pygame.image.load(path).convert_alpha()
        self.image = pygame.transform.scale(self.image, (50, 50))  # Scale to desired size
        self.rect = self.image.get_rect(midbottom=(80, 550))
        self.gravity = 0
        self.bullet_count = 15
        self.health = 100
        self.shield = 0
        self.shield_active = False
        self.double_jump_available = True
        self.particle_system = EnhancedParticleSystem()
        self.invincible = False
        self.invincible_timer = 0
        self.powerup_effects = []
        
    def apply_gravity(self):
        self.gravity += 1
        self.rect.y += self.gravity
        if self.rect.bottom >= SCREEN_HEIGHT - 100:
            self.rect.bottom = SCREEN_HEIGHT - 100
            self.gravity = 0
            self.double_jump_available = True
            
    def jump(self) -> bool:
        if self.rect.bottom >= SCREEN_HEIGHT - 100:
            self.gravity = -22
            self.particle_system.add_particles((self.rect.centerx, self.rect.bottom), COLORS['player'])
            return True
        elif self.double_jump_available:
            self.gravity = -20
            self.double_jump_available = False
            self.particle_system.add_particles((self.rect.centerx, self.rect.bottom), COLORS['player'])
            return True
        return False

    def update(self):
        self.apply_gravity()
        if self.shield_active:
            self.shield = max(0, self.shield - 0.2)
            if self.shield <= 0:
                self.shield_active = False
        
        if self.invincible:
            self.invincible_timer -= 1
            if self.invincible_timer <= 0:
                self.invincible = False
        
        self.particle_system.update()
        
        # Update powerup effects
        for effect in self.powerup_effects[:]:
            effect['duration'] -= 1
            if effect['duration'] <= 0:
                self.powerup_effects.remove(effect)
                effect['end_func']()

class EnhancedObstacle(pygame.sprite.Sprite):
    def __init__(self, type='ground'):
        super().__init__()
        self.type = type
        size = (40, 40) if type == 'ground' else (30, 30)
        self.image = pygame.Surface(size, pygame.SRCALPHA)
        
        if type == 'ground':
            pygame.draw.rect(self.image, COLORS['obstacle'], (0, 0, *size))
            self.rect = self.image.get_rect(midbottom=(SCREEN_WIDTH, SCREEN_HEIGHT - 100))
        else:
            pygame.draw.polygon(self.image, COLORS['flying'],
                              [(15, 0), (30, 30), (0, 30)])
            self.rect = self.image.get_rect(midbottom=(SCREEN_WIDTH, random.randint(200, 400)))
        
        self.speed = random.randint(5, 8)
        
    def update(self):
        self.rect.x -= self.speed
        if self.rect.right < 0:
            self.kill()

class EnhancedPowerUp(pygame.sprite.Sprite):
    TYPES = {
        'health': {'color': COLORS['health'], 'shape': 'circle'},
        'shield': {'color': COLORS['shield'], 'shape': 'diamond'},
        'bullet': {'color': COLORS['bullet'], 'shape': 'square'},
        'speed': {'color': COLORS['player'], 'shape': 'triangle'}
    }
    
    def __init__(self):
        super().__init__()
        self.type = random.choice(list(self.TYPES.keys()))
        self.image = pygame.Surface((30, 30), pygame.SRCALPHA)
        
        style = self.TYPES[self.type]
        if style['shape'] == 'circle':
            pygame.draw.circle(self.image, style['color'], (15, 15), 15)
        elif style['shape'] == 'diamond':
            pygame.draw.polygon(self.image, style['color'],
                              [(15, 0), (30, 15), (15, 30), (0, 15)])
        elif style['shape'] == 'square':
            pygame.draw.rect(self.image, style['color'], (0, 0, 30, 30))
        elif style['shape'] == 'triangle':
            pygame.draw.polygon(self.image, style['color'],
                              [(15, 0), (30, 30), (0, 30)])
        
        self.rect = self.image.get_rect(midbottom=(SCREEN_WIDTH, random.randint(200, 400)))
        self.speed = 3
        
    def update(self):
        self.rect.x -= self.speed
        if self.rect.right < 0:
            self.kill()

class EnhancedGame:
    def __init__(self):
        self.game_state = "level_select"
        self.score = 0
        self.high_score = 0
        self.difficulty = "Medium"
        self.player = pygame.sprite.GroupSingle()
        self.obstacles = pygame.sprite.Group()
        self.bullets = pygame.sprite.Group()
        self.power_ups = pygame.sprite.Group()
        self.particle_system = EnhancedParticleSystem()
        
        # Initialize timers
        pygame.time.set_timer(pygame.USEREVENT + 1, 2000)  # Obstacle timer
        pygame.time.set_timer(pygame.USEREVENT + 2, 3000)  # Flying obstacle timer
        pygame.time.set_timer(pygame.USEREVENT + 3, 5000)  # Powerup timer
        pygame.time.set_timer(pygame.USEREVENT + 4, 1000)  # Score timer
        
    def reset_game(self):
        self.score = 0
        self.player.sprite = EnhancedPlayer()
        self.obstacles.empty()
        self.bullets.empty()
        self.power_ups.empty()
        self.particle_system = EnhancedParticleSystem()
    
    def draw_ui(self):
        # Background panel for UI
        pygame.draw.rect(screen, (*COLORS['menu_bg'], 180), (5, 5, 250, 100), border_radius=10)
        
        # Health bar with gradient
        health_width = 200
        health_height = 20
        health_rect = pygame.Rect(20, 20, health_width, health_height)
        health_amount = (self.player.sprite.health / 100) * health_width
        
        # Background
        pygame.draw.rect(screen, (50, 50, 50), health_rect, border_radius=5)
        # Health bar with gradient effect
        if health_amount > 0:
            health_surface = pygame.Surface((health_amount, health_height))
            for x in range(int(health_amount)):
                progress = x / health_width
                color = pygame.Color(220, 20, 60)  # Start with red
                color.hsla = (120 * progress, 100, 50, 100)  # Transition to green
                pygame.draw.line(health_surface, color, (x, 0), (x, health_height))
            screen.blit(health_surface, health_rect)
        pygame.draw.rect(screen, (200, 200, 200), health_rect, 2, border_radius=5)
        
        # Shield bar
        if self.player.sprite.shield_active:
            shield_amount = (self.player.sprite.shield / 100) * health_width
            shield_rect = pygame.Rect(20, 45, shield_amount, health_height)
            pygame.draw.rect(screen, COLORS['shield'], shield_rect, border_radius=5)
            pygame.draw.rect(screen, (200, 200, 200), (20, 45, health_width, health_height), 2, border_radius=5)
        
        # Score and bullets
        score_text = FONTS['ui'].render(f"Score: {self.score}", True, COLORS['text'])
        bullets_text = FONTS['ui'].render(f"Bullets: {self.player.sprite.bullet_count}", True, COLORS['text'])
        screen.blit(score_text, (20, 70))
        screen.blit(bullets_text, (150, 70))
    
    def run(self):
        while True:
            if self.game_state == "level_select":
                self.level_selection_screen()
            elif self.game_state == "active_game":
                self.main_game_loop()
            elif self.game_state == "game_over":
                self.game_over_screen()
    
    def level_selection_screen(self):
        while self.game_state == "level_select":
            screen.fill(COLORS['menu_bg'])
            
            # Title with shadow effect
            title_shadow = FONTS['title'].render("Epic Runner", True, (0, 0, 0))
            title_text = FONTS['title'].render("Epic Runner", True, COLORS['text'])
            screen.blit(title_shadow, (SCREEN_WIDTH//2 - title_shadow.get_width()//2 + 2, 52))
            screen.blit(title_text, (SCREEN_WIDTH//2 - title_text.get_width()//2, 50))
            
            mouse_pos = pygame.mouse.get_pos()
            
            # Create animated buttons
            button_width, button_height = 250, 60
            buttons = {
                'Easy': pygame.Rect((SCREEN_WIDTH - button_width) // 2, 200, button_width, button_height),
                'Medium': pygame.Rect((SCREEN_WIDTH - button_width) // 2, 280, button_width, button_height),
                'Hard': pygame.Rect((SCREEN_WIDTH - button_width) // 2, 360, button_width, button_height)
            }
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    for difficulty, button in buttons.items():
                        if button.collidepoint(mouse_pos):
                            SOUNDS['button'].play()
                            self.difficulty = difficulty
                            self.game_state = "active_game"
                            self.reset_game()
            
            # Draw animated buttons with hover effects
            for difficulty, button in buttons.items():
                hover = button.collidepoint(mouse_pos)
                color = COLORS['button_active'] if hover else COLORS['button_inactive']
                
                # Button shadow
                shadow = pygame.Rect(button.x + 2, button.y + 2, button.width, button.height)
                pygame.draw.rect(screen, (0, 0, 0, 128), shadow, border_radius=15)
                
                # Main button
                pygame.draw.rect(screen, color, button, border_radius=15)
                if hover:  # Add highlight effect on hover
                    pygame.draw.rect(screen, (*color, 128), button, 4, border_radius=15)
                
                # Button text
                text = FONTS['main'].render(difficulty, True, COLORS['text'])
                text_rect = text.get_rect(center=button.center)
                screen.blit(text, text_rect)
            
            # Add instructions
            inst_text = FONTS['ui'].render("Press SPACE to jump, F to shoot", True, COLORS['text'])
            screen.blit(inst_text, (SCREEN_WIDTH//2 - inst_text.get_width()//2, SCREEN_HEIGHT - 100))
            
            pygame.display.update()
            clock.tick(60)

    def game_over_screen(self):
        self.high_score = max(self.score, self.high_score)
        button_width, button_height = 250, 60
        
        while self.game_state == "game_over":
            screen.fill(COLORS['menu_bg'])
            mouse_pos = pygame.mouse.get_pos()
            
            # Create buttons
            restart_button = pygame.Rect((SCREEN_WIDTH - button_width) // 2, 300, button_width, button_height)
            menu_button = pygame.Rect((SCREEN_WIDTH - button_width) // 2, 380, button_width, button_height)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if restart_button.collidepoint(mouse_pos):
                        SOUNDS['button'].play()
                        self.game_state = "active_game"
                        self.reset_game()
                    elif menu_button.collidepoint(mouse_pos):
                        SOUNDS['button'].play()
                        self.game_state = "level_select"
            
            # Draw game over text with animation
            game_over_text = FONTS['title'].render("GAME OVER", True, COLORS['health'])
            pulse = abs(math.sin(pygame.time.get_ticks() * 0.003)) * 10
            text_rect = game_over_text.get_rect(center=(SCREEN_WIDTH//2, 150 + pulse))
            screen.blit(game_over_text, text_rect)
            
            # Draw score information
            score_text = FONTS['main'].render(f"Score: {self.score}", True, COLORS['text'])
            high_score_text = FONTS['main'].render(f"High Score: {self.high_score}", True, COLORS['flying'])
            screen.blit(score_text, (SCREEN_WIDTH//2 - score_text.get_width()//2, 220))
            screen.blit(high_score_text, (SCREEN_WIDTH//2 - high_score_text.get_width()//2, 260))
            
            # Draw buttons with hover effects
            for button, text in [(restart_button, "Restart"), (menu_button, "Main Menu")]:
                hover = button.collidepoint(mouse_pos)
                color = COLORS['button_active'] if hover else COLORS['button_inactive']
                
                # Button shadow
                shadow = pygame.Rect(button.x + 2, button.y + 2, button.width, button.height)
                pygame.draw.rect(screen, (0, 0, 0, 128), shadow, border_radius=15)
                
                pygame.draw.rect(screen, color, button, border_radius=15)
                if hover:
                    pygame.draw.rect(screen, (*color, 128), button, 4, border_radius=15)
                
                text_surf = FONTS['main'].render(text, True, COLORS['text'])
                text_rect = text_surf.get_rect(center=button.center)
                screen.blit(text_surf, text_rect)
            
            pygame.display.update()
            clock.tick(60)

    def main_game_loop(self):
        bullet_cooldown = 0
        background_pos = 0

        background_image = pygame.image.load("/Users/shivamsahu/Kabir Session 4/graphics/bg.png").convert()
        # Create parallax background layers
        background_layers = [
            pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT)),
            pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        ]
        # Fill background layers with different colors
        background_layers[0].fill(COLORS['sky'])
        background_layers[1].fill((*COLORS['ground'], 128))
        
        
        if not self.player.sprite:
            self.player.add(EnhancedPlayer())
        
        while self.game_state == "active_game":
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        if self.player.sprite.jump():
                            SOUNDS['jump'].play()
                    if event.key == pygame.K_f and bullet_cooldown == 0 and self.player.sprite.bullet_count > 0:
                        self.bullets.add(EnhancedBullet(self.player.sprite.rect.right, 
                                                      self.player.sprite.rect.centery))
                        self.player.sprite.bullet_count -= 1
                        bullet_cooldown = 20
                        SOUNDS['shoot'].play()
                
                # Spawn obstacles and power-ups based on difficulty
                if event.type == pygame.USEREVENT + 1:  # Ground obstacle timer
                    spawn_chance = {'Easy': 0.5, 'Medium': 0.7, 'Hard': 0.9}[self.difficulty]
                    if random.random() < spawn_chance:
                        self.obstacles.add(EnhancedObstacle('ground'))
                
                if event.type == pygame.USEREVENT + 2:  # Flying obstacle timer
                    spawn_chance = {'Easy': 0.4, 'Medium': 0.6, 'Hard': 0.8}[self.difficulty]
                    if random.random() < spawn_chance:
                        self.obstacles.add(EnhancedObstacle('flying'))
                
                if event.type == pygame.USEREVENT + 3:  # Power-up timer
                    if random.random() < 0.3:
                        self.power_ups.add(EnhancedPowerUp())
                
                if event.type == pygame.USEREVENT + 4:  # Score timer
                    self.score += 1
            
            if bullet_cooldown > 0:
                bullet_cooldown -= 1
            
            # Update background position for parallax effect
            background_pos = (background_pos + 2) % SCREEN_WIDTH
            
            # Draw background layers with parallax effect
            screen.blit(background_layers[0], (0, 0))
            screen.blit(background_layers[1], (-background_pos, 0))
            screen.blit(background_layers[1], (SCREEN_WIDTH - background_pos, 0))
            
            # Draw ground
            pygame.draw.rect(screen, COLORS['sky'], 
                           (0, SCREEN_HEIGHT - 100, SCREEN_WIDTH, 100))
            
            # Update and draw game objects
            self.player.update()
            self.obstacles.update()
            self.bullets.update()
            self.power_ups.update()
            
            # Update particle systems
            self.particle_system.update()

            screen.blit(background_image, (0, 0))
            GROUND_HEIGHT = 100
            pygame.draw.rect(screen, COLORS['ground'], (0, SCREEN_HEIGHT - GROUND_HEIGHT, SCREEN_WIDTH, GROUND_HEIGHT))
            
            # Draw all game objects
            self.player.draw(screen)
            self.obstacles.draw(screen)
            self.bullets.draw(screen)
            self.power_ups.draw(screen)
            
            # Draw particle effects
            self.particle_system.draw(screen)
            self.player.sprite.particle_system.draw(screen)
            
            # Collision detection
            if not self.player.sprite.shield_active and not self.player.sprite.invincible:
                if pygame.sprite.spritecollide(self.player.sprite, self.obstacles, False):
                    self.player.sprite.health -= 20
                    self.player.sprite.invincible = True
                    self.player.sprite.invincible_timer = 60
                    SOUNDS['hit'].play()
                    if self.player.sprite.health <= 0:
                        self.game_state = "game_over"
            
            # Power-up collection
            for power_up in pygame.sprite.spritecollide(self.player.sprite, self.power_ups, True):
                SOUNDS['powerup'].play()
                if power_up.type == 'health':
                    self.player.sprite.health = min(100, self.player.sprite.health + 30)
                elif power_up.type == 'shield':
                    self.player.sprite.shield = 100
                    self.player.sprite.shield_active = True
                elif power_up.type == 'bullet':
                    self.player.sprite.bullet_count += 5
                elif power_up.type == 'speed':
                    # Add speed boost effect
                    def start_speed():
                        for obstacle in self.obstacles:
                            obstacle.speed *= 0.75
                    
                    def end_speed():
                        for obstacle in self.obstacles:
                            obstacle.speed /= 0.75
                    
                    self.player.sprite.powerup_effects.append({
                        'duration': 300,  # 5 seconds at 60 FPS
                        'end_func': end_speed
                    })
                    start_speed()
            
            # Bullet-obstacle collision
            for bullet in self.bullets:
                hit_obstacles = pygame.sprite.spritecollide(bullet, self.obstacles, True)
                if hit_obstacles:
                    self.particle_system.add_particles(
                        (bullet.rect.centerx, bullet.rect.centery),
                        COLORS['obstacle']
                    )
                    bullet.kill()
                    self.score += 5
            
            # Draw UI
            self.draw_ui()
            
            # Draw difficulty indicator
            diff_text = FONTS['ui'].render(f"Difficulty: {self.difficulty}", True, COLORS['text'])
            screen.blit(diff_text, (SCREEN_WIDTH - diff_text.get_width() - 20, 20))
            
            pygame.display.update()
            clock.tick(60)

class EnhancedBullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        # Load the bullet image
        self.image = pygame.image.load("/Users/shivamsahu/Downloads/fire.png").convert_alpha()

        # Optional: Scale the image if it's too large or small
        self.image = pygame.transform.scale(self.image, (20, 8))  # Adjust (20, 8) to desired size

        # Set the rect to position the bullet correctly
        self.rect = self.image.get_rect(midleft=(x, y))

        # Bullet speed
        self.speed = 15
        
    def update(self):
        self.rect.x += self.speed
        if self.rect.left > SCREEN_WIDTH:
            self.kill()

if __name__ == "__main__":
    game = EnhancedGame()
    game.run()
