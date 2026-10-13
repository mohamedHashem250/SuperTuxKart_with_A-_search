
import pygame
import pystk2

# ======================================
# 1. Configure SuperTuxKart graphics
# ======================================

WIDTH, HEIGHT = 800, 600

graphics = pystk2.GraphicsConfig.sd()
graphics.screen_width = WIDTH
graphics.screen_height = HEIGHT
graphics.render = True

# Render game images, but let Pygame display them
graphics.display = False

pystk2.init(graphics)

# ======================================
# 2. Configure the race
# ======================================

config = pystk2.RaceConfig(
    track="lighthouse",
    num_kart=4
)

config.laps = 1
config.step_size = 1 / 60

# Manually control kart 0
config.players[0].controller = (
    pystk2.PlayerConfig.Controller.PLAYER_CONTROL
)

config.players[0].camera_mode = (
    pystk2.PlayerConfig.CameraMode.ON
)
config.num_cameras = 1

# ======================================
# 3. Initialize Pygame
# ======================================

pygame.init()

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("SuperTuxKart - Manual Driving")

clock = pygame.time.Clock()

# ======================================
# 4. Start the race
# ======================================

race = pystk2.Race(config)

try:
    race.start()

    world = pystk2.WorldState()

    running = True
    step = 0

    # ==================================
    # 5. Main game loop
    # ==================================

    while running:

        # Check for window close or ESC
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

        if not running:
            break

        # Read the keyboard
        keys = pygame.key.get_pressed()

        # Create manual driving commands
        action = pystk2.Action()

        # Acceleration and braking
        action.acceleration = (
            1.0 if keys[pygame.K_UP] else 0.0
        )

        action.brake = bool(keys[pygame.K_DOWN])

        # Steering
        if keys[pygame.K_LEFT]:
            action.steer = -0.7

        elif keys[pygame.K_RIGHT]:
            action.steer = 0.7

        else:
            action.steer = 0.0

        # Optional drifting
        action.drift = bool(keys[pygame.K_SPACE])

        # Execute the action inside the game
        race_continues = race.step(action)

        # Read the updated game state
        world.update()

        # ==================================
        # 6. Display the rendered game
        # ==================================

        if race.render_data:

            image = race.render_data[0].image

            height, width, _ = image.shape

            frame = pygame.image.frombuffer(
                image.tobytes(),
                (width, height),
                "RGB"
            )

            screen.blit(frame, (0, 0))
            pygame.display.flip()

        # Display kart information
        if step % 120 == 0 and world.players:

            kart = world.players[0].kart

            print(
                f"Step: {step} | "
                f"Speed: {kart.speed:.2f} | "
                f"Steering: {action.steer:.2f} | "
                f"Position: {kart.location}"
            )

        if not race_continues:
            print("Race finished!")
            break

        step += 1

        # Limit execution to approximately 60 FPS
        clock.tick(60)

except KeyboardInterrupt:
    print("Game interrupted.")

finally:
    race.stop()
    del race

    pystk2.clean()
    pygame.quit()

    print("Game closed successfully.")
