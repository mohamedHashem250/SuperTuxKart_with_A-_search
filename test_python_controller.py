
import time
import pystk2

# ==========================================
# 1. Initialize the game
# ==========================================

graphics = pystk2.GraphicsConfig.sd()
graphics.screen_width = 800
graphics.screen_height = 600
graphics.render = True
graphics.display = True

pystk2.init(graphics)


# ==========================================
# 2. Configure the race
# ==========================================

config = pystk2.RaceConfig(
    track="lighthouse",
    num_kart=4
)
config.laps = 1

# Our Python code will control kart 0
config.players[0].controller = (
    pystk2.PlayerConfig.Controller.PLAYER_CONTROL
)

config.players[0].camera_mode = (
    pystk2.PlayerConfig.CameraMode.ON
)
config.num_cameras = 1


# ==========================================
# 3. Start the race
# ==========================================

race = pystk2.Race(config)

try:
    race.start()
    world = pystk2.WorldState()

    # ======================================
    # 4. Python-controlled game loop
    # ======================================

    for step in range(1200):

        # Create a driving action
        action = pystk2.Action()

        # Apply acceleration
        action.acceleration = 0.7
        action.brake = False

        # Apply simple steering commands
        if step < 240:
            action.steer = 0.0

        elif step < 300:
            action.steer = -0.45

        elif step < 360:
            action.steer = 0.45

        else:
            action.steer = 0.0

        # Execute our Python-generated action
        running = race.step(action)

        # Read the new state
        world.update()

        if step % 60 == 0:
            kart = world.players[0].kart

            print(
                f"Step: {step} | "
                f"Speed: {kart.speed:.2f} | "
                f"Steering: {action.steer:.2f} | "
                f"Position: {kart.location}"
            )

        if not running:
            print("Race finished!")
            break

        time.sleep(1 / 60)

except KeyboardInterrupt:
    print("Simulation interrupted.")

finally:
    race.stop()
    del race
    pystk2.clean()
    print("Simulation closed.")

