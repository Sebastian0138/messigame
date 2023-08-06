import pygame
import math

pygame.init()
clock = pygame.time.Clock()

# Configura la ventana y crea una pantalla
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Mi Juego 2D")

background_image = pygame.image.load("./background.png")
# Carga la imagen del personaje
character_image = pygame.image.load("./messi.png")

# Carga la imagen del proyectil
projectile_image = pygame.image.load("./ball.png")

# Carga la imagen del arco
arc_image = pygame.image.load("./arc.png")

# Posición inicial del personaje
character_x = 100
character_y = 100

# Escala inicial del personaje, proyectil y arco (porcentaje del tamaño original)
character_scale = 20
projectile_scale = 1
arc_scale = 100

# Velocidad del personaje
character_speed = 5

# Velocidad del proyectil
projectile_speed = 5

# Velocidad del arco
global speed
speed = 1
arc_speed = speed

# Almacena los proyectiles y sus direcciones
projectiles = []
font = pygame.font.Font(None, 36)  # Puedes ajustar el tamaño de la fuente aquí


class Arc:
    def __init__(self):
        self.x = WIDTH - 25  # Fijo en el máximo eje X
        self.y = HEIGHT // 2  # Inicializa el arco en el centro vertical de la ventana
        self.direction = 1  # Dirección inicial del arco (1 = abajo, -1 = arriba)
        # Carga la imagen del arco sin rotar
        self.arc_image = pygame.image.load("./arc.png")
        # Obtener las dimensiones del arco sin rotar
        self.arc_width = int(self.arc_image.get_width() * arc_scale / 100)
        self.arc_height = int(self.arc_image.get_height() * arc_scale / 100)

    def update(self):
        self.y += self.direction * arc_speed

        # Verifica si el arco ha llegado a los extremos de la ventana
        if self.y <= 0 or self.y >= HEIGHT - self.arc_height:
            self.direction *= -1

    def draw(self):
        # Rota la imagen del arco 180 grados verticalmente
        rotated_arc_image = pygame.transform.flip(self.arc_image, False, True)
        screen.blit(pygame.transform.scale(rotated_arc_image, (self.arc_width, self.arc_height)), (self.x, self.y))


class Projectile:
    def __init__(self, x, y, direction):
        self.x = x
        self.y = y
        self.direction = direction


# Crea un arco
arc = Arc()


def calculate_score_multiplier(character_x, character_y, character_width, character_height, arc_x, arc_y, arc_width,
                               arc_height):
    # Calcula la posición vertical del personaje en relación con la posición del arco
    # 0.0: personaje arriba del arco, 1.0: personaje abajo del arco
    vertical_position = (character_y + character_height / 2 - arc_y) / arc_height

    # Calcula la posición horizontal del personaje en relación con el arco
    # 0.0: personaje a la izquierda del arco, 1.0: personaje a la derecha del arco
    horizontal_position = (character_x + character_width / 2 - arc_x) / arc_width

    # Calcula el puntaje según la posición del personaje en el eje X y el eje Y
    # 0% en ambos ejes da puntaje máximo, 100% en ambos ejes da puntaje mínimo
    score_percentage = (1 - abs(horizontal_position)) * (1 - abs(vertical_position))

    # Asegurarse de que el puntaje sea siempre mayor o igual a cero
    score_percentage = max(score_percentage, 0)

    return score_percentage


# Variables para controlar el delay del disparo
last_shot_time = 0
shoot_delay = 1000  # Tiempo en milisegundos entre cada disparo


def fire_projectile(x, y, direction):
    global projectiles, last_shot_time
    current_time = pygame.time.get_ticks()
    if current_time - last_shot_time > shoot_delay:
        projectiles.append(Projectile(x, y, direction))
        last_shot_time = current_time


running = True
goal_counter = 0

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Lógica del juego y actualizaciones aquí
    keys = pygame.key.get_pressed()

    # Mueve el personaje
    move_direction = (0, 0)
    if keys[pygame.K_w]:  # Tecla W para mover arriba
        character_y -= character_speed
        move_direction = (0, -1)
    if keys[pygame.K_s]:  # Tecla S para mover abajo
        character_y += character_speed
        move_direction = (0, 1)
    if keys[pygame.K_a]:  # Tecla A para mover izquierda
        character_x -= character_speed
        move_direction = (-1, 0)
    if keys[pygame.K_d]:  # Tecla D para mover derecha
        character_x += character_speed
        move_direction = (1, 0)

    # Limita el movimiento del personaje dentro de la pantalla
    character_x = max(0, min(character_x, WIDTH - int(character_image.get_width() * character_scale / 100)))
    character_y = max(0, min(character_y, HEIGHT - int(character_image.get_height() * character_scale / 100)))

    # Detecta las flechas presionadas para disparar los proyectiles
    if keys[pygame.K_UP]:
        fire_projectile(character_x, character_y, (0, -1))
    if keys[pygame.K_DOWN]:
        fire_projectile(character_x, character_y, (0, 1))
    if keys[pygame.K_LEFT]:
        fire_projectile(character_x, character_y, (-1, 0))
    if keys[pygame.K_RIGHT]:
        fire_projectile(character_x, character_y, (1, 0))

    # Mueve los proyectiles
    for projectile in projectiles:
        projectile.x += projectile.direction[0] * projectile_speed
        projectile.y += projectile.direction[1] * projectile_speed

    # Limpia la lista de proyectiles que están fuera de la pantalla
    projectiles = [projectile for projectile in projectiles if
                   0 <= projectile.x <= WIDTH and 0 <= projectile.y <= HEIGHT]

    # Actualiza el arco
    arc.update()

    # Detecta colisiones entre los proyectiles y el arco
    for projectile in projectiles:
        projectile_width = int(projectile_image.get_width() * projectile_scale / 100)
        projectile_height = int(projectile_image.get_height() * projectile_scale / 100)
        projectile_rect = pygame.Rect(projectile.x, projectile.y, projectile_width, projectile_height)

        arc_rect = pygame.Rect(arc.x, arc.y, arc.arc_width, arc.arc_height)

        if projectile_rect.colliderect(arc_rect):
            # Elimina el proyectil de la lista
            projectiles.remove(projectile)

            # Calcula el puntaje según la posición del personaje y el arco
            score_multiplier = calculate_score_multiplier(character_x, character_y, character_width, character_height,
                                                          arc.x, arc.y, arc.arc_width, arc.arc_height)

            # Incrementa el contador de goles según el puntaje calculado
            goal_counter += score_multiplier
            speed += 1
            arc_speed += 1

            # Mostrar el mensaje de "Gol" y el contador de goles
            

    # Limpia la pantalla y dibuja los proyectiles, el personaje y el arco
    screen.blit(pygame.transform.scale(background_image, (WIDTH, HEIGHT)), (0, 0))
    character_width = int(character_image.get_width() * character_scale / 100)
    character_height = int(character_image.get_height() * character_scale / 100)
    screen.blit(pygame.transform.scale(character_image, (character_width, character_height)), (character_x, character_y))

    for projectile in projectiles:
        projectile_width = int(projectile_image.get_width() * projectile_scale / 100)
        projectile_height = int(projectile_image.get_height() * projectile_scale / 100)
        screen.blit(pygame.transform.scale(projectile_image, (projectile_width, projectile_height)),
                    (projectile.x, projectile.y))

    arc.draw()
    score_text = font.render("Score: {:.2f}".format(goal_counter ), True, (255, 255, 255))  # Color verde
    screen.blit(score_text, (10, 10))  # Posición del texto

    pygame.display.update()
    clock.tick(60)

# Fuera del bucle principal, cierra Pygame
pygame.quit()
