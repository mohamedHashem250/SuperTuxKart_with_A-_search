
import time
import pystk2

# ==========================================
# 1. Initialize SuperTuxKart graphics
# ==========================================

graphics = pystk2.GraphicsConfig.sd()

graphics.screen_width = 800
graphics.screen_height = 600

# Use the game's native display (no OpenCV)
graphics.render = True
graphics.display = True

pystk2.init(graphics)


# ==========================================
# 2. Configure the racing environment
# ==========================================

config = pystk2.RaceConfig()

config.track = "lighthouse"
config.num_kart = 4
config.laps = 1

# Use the built-in AI to drive the first kart
config.players[0].controller = (
    pystk2.PlayerConfig.Controller.AI_CONTROL
)

# Enable the camera for our AI-controlled kart
config.players[0].camera_mode = (
    pystk2.PlayerConfig.CameraMode.ON
)

config.num_cameras = 1


# ==========================================
# 3. Create the race
# ==========================================

race = pystk2.Race(config)

try:
    race.start()

    # Initialize the game state
    world = pystk2.WorldState()

    # Initialize the track information
    track = pystk2.Track()
    track.update()

    print("\n========== TRACK INFORMATION ==========")

    print("Track:", config.track)
    print("Track length:", track.length)
    print("Track segments:", len(track.path_nodes))
    print("Track widths:", track.path_width.shape)
    print("Track graph nodes:", len(track.successors))

    print("=======================================\n")


    # ==========================================
    # 4. Run the simulation
    # ==========================================

    max_steps = 10000

    for step in range(max_steps):

        # Advance the game by one simulation step
        # True means the race can continue
        race_continues = race.step()

        # Retrieve the updated game state
        world.update()

        # Display information every 100 steps
        if step % 100 == 0 and world.players:

            kart = world.players[0].kart

            print(
                f"Step: {step} | "
                f"Time: {world.time:.2f} | "
                f"Position: {kart.location} | "
                f"Speed: {kart.speed:.2f} | "
                f"Laps: {kart.finished_laps} | "
                f"Opponents: {len(world.karts)-1} | "
                f"Items: {len(world.items)}"
            )

        # Slow down execution for viewing
        time.sleep(1 / 60)

        # Correct race-ending condition
        if not race_continues:
            print("\nRace finished or stopped!")
            break

    else:
        print("\nMaximum simulation steps reached.")

except KeyboardInterrupt:
    print("\nSimulation interrupted by user.")

finally:

    # ==========================================
    # 5. Clean up the game
    # ==========================================

    print("\nCleaning up SuperTuxKart...")

    race.stop()
    del race

    pystk2.clean()

    print("Simulation closed successfully.")
