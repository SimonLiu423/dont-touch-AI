import Box2D
import pygame

WIDTH = 360  # width of our game window
HEIGHT = 480 # height of our game window
FPS = 30 # frames per second

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("My Game")
clock = pygame.time.Clock()
world = Box2D.b2World(gravity=(0, 0), doSleep=False)

class Car(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((30, 40))
        self.image.fill((255, 0, 0))
        self.rect = self.image.get_rect()
        self.rect.center = (WIDTH / 2, HEIGHT / 2)
        self.speedx = 10
        self.speedy = 0
        self.body = world.CreateDynamicBody(position=(WIDTH/2, HEIGHT/2))
        self.box = self.body.CreatePolygonFixture(box=(1, 1), density=1, friction=0.1, restitution=0.3, isSensor = True)

    def update(self):
        self.speedx = 0
        keystate = pygame.key.get_pressed()
        if keystate[pygame.K_LEFT]:
            self.body.position[0] -= 10
        if keystate[pygame.K_RIGHT]:
            self.body.position[0] += 10
        self.rect.center = (self.body.position.x, self.body.position.y)


all_sprites = pygame.sprite.Group()
car = Car()
all_sprites.add(car)


# Game Loop
running = True
while running:
    # keep loop running at the right speed
    clock.tick(FPS)
    # Process input (events)
    for event in pygame.event.get():
        # check for closing window
        if event.type == pygame.QUIT:
            running = False
    # Update
    all_sprites.update()
    # Draw / render
    screen.fill((255, 255, 255))
    all_sprites.draw(screen)
    # *after* drawing everything, flip the display
    pygame.display.flip()

pygame.quit()