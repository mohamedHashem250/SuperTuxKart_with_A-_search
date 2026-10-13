
import time
import pygame
import pystk2

# ======================================
# 1. Settings
# ======================================

WIDTH, HEIGHT = 640, 480
TARGET_FPS = 60
NUM_KARTS = 4  # Only our player for now

# ======================================
# 2. Initialize SuperTuxKart
# ======================================

graphics = pystk2.GraphicsConfig.ld()
graphics.screen_width = WIDTH
graphics.screen_height = HEIGHT
graphics.render = True
graphics.display = False

pystk2.init(graphics)

config = pystk2.RaceConfig(
    track="lighthouse",
    num_kart=NUM_KARTS
)

config.laps = 1
config.step_size = 1 / 60

# Python controls the player
config.players[0].controller = (
    pystk2.PlayerConfig.Controller.PLAYER_CONTROL
)

# Identify our kart
config.players[0].name = "MY KART"

available_karts = pystk2.list_karts()
if "tux" in available_karts:
    config.players[0].kart = "tux"

config.players[0].camera_mode = (
    pystk2.PlayerConfig.CameraMode.ON
)
config.num_cameras = 1

# ======================================
# 3. Initialize Pygame
# ======================================

pygame.init()

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("SuperTuxKart - Manual Test")

font = pygame.font.SysFont("Arial", 22, bold=True)
small_font = pygame.font.SysFont("Arial", 17)

clock = pygame.time.Clock()

# ======================================
# 4. Start simulation
# ======================================

race = pystk2.Race(config)

try:
    race.start()

    world = pystk2.WorldState()
    running = True
    step = 0

    print("Manual control started")
    print("Arrow UP: Accelerate")
    print("Arrow DOWN: Brake")
    print("Arrow LEFT/RIGHT: Steering")
    print("SPACE: Drift")
    print("ESC: Exit")

    # ==================================
    # 5. Main game loop
    # ==================================

    while running:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

        if not running:
            break

        keys = pygame.key.get_pressed()

        action = pystk2.Action()

        # Acceleration and braking
        action.acceleration = (
            1.0 if keys[pygame.K_UP] else 0.0
        )
        action.brake = bool(keys[pygame.K_DOWN])

        # Full steering range for testing
        if keys[pygame.K_LEFT] and not keys[pygame.K_RIGHT]:
            action.steer = -1.0
        elif keys[pygame.K_RIGHT] and not keys[pygame.K_LEFT]:
            action.steer = 1.0
        else:
            action.steer = 0.0

        action.drift = bool(keys[pygame.K_SPACE])

        # Execute our command
        race_continues = race.step(action)

        # Read actual kart state
        world.update()
        kart = world.players[0].kart
        my_kart = world.players[0].kart
        print("\n========== RACING STATE ==========")
        print(
            f"MY PLAYER: {my_kart.name} | "
            f"ID: {my_kart.id} | "
            f"Race position: {my_kart.position}"
        )

        for other in world.karts:
            if other.id == my_kart.id:
                continue

            print(
                f"OPPONENT: {other.name} | "
                f"ID: {other.id} | "
                f"Speed: {other.speed:.2f} | "
                f"Position: {other.location}"
            )
        # ==================================
        # 6. Display game image
        # ==================================

        if race.render_data:
            image = race.render_data[0].image
            h, w = image.shape[:2]

            frame = pygame.image.frombuffer(
                image.tobytes(), (w, h), "RGB"
            )

            screen.blit(frame, (0, 0))

        # ==================================
        # 7. Display information
        # ==================================

        pygame.draw.rect(
            screen, (15, 20, 30),
            (0, 0, WIDTH, 100)
        )

        title = font.render(
            "PLAYER 1 - MANUAL CONTROL",
            True, (255, 220, 40)
        )
        screen.blit(title, (12, 7))

        fps = clock.get_fps()

        info1 = small_font.render(
            f"Speed: {kart.speed:.1f} m/s"
            f"   Steering: {action.steer:+.1f}"
            f"   FPS: {fps:.1f}",
            True, (255, 255, 255)
        )

        screen.blit(info1, (12, 41))

        road_status = (
            "ON ROAD" if kart.is_on_road
            else "OFF ROAD"
        )

        road_color = (
            (60, 240, 100) if kart.is_on_road
            else (255, 75, 75)
        )

        info2 = small_font.render(
            f"Track: {road_status}"
            f"   Game time: {world.time:.1f}s",
            True, road_color
        )

        screen.blit(info2, (12, 68))

        pygame.display.flip()

        # Debug output
        if step % 120 == 0:
            print(
                f"Step={step} | "
                f"Speed={kart.speed:.2f} | "
                f"Steer={action.steer:+.1f} | "
                f"OnRoad={kart.is_on_road} | "
                f"FPS={fps:.1f}"
            )

        if not race_continues:
            print("Race finished.")
            break

        step += 1
        clock.tick(TARGET_FPS)

except KeyboardInterrupt:
    print("Interrupted.")

finally:
    race.stop()
    del race
    pystk2.clean()
    pygame.quit()
    print("Game closed.")
