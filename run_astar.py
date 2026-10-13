"""Run our A* planning agent on the Lighthouse track.

Usage: python run_astar.py            # one kart, simpler first test
       python run_astar.py --karts 4  # add 3 built-in-AI opponents

Pygame is only a display window. All racing physics run in PySuperTuxKart2.
"""
import argparse
import csv
from pathlib import Path
import pygame
import pystk2
from agents.astar_agent import AStarRacingAgent


def run(num_karts=1, max_steps=9000):
    width, height = 640, 480
    graphics = pystk2.GraphicsConfig.ld()
    graphics.screen_width, graphics.screen_height = width, height
    graphics.render, graphics.display = True, False
    pystk2.init(graphics)

    config = pystk2.RaceConfig(track='lighthouse', num_kart=num_karts)
    config.laps = 1
    config.step_size = 1 / 60
    config.players[0].controller = pystk2.PlayerConfig.Controller.PLAYER_CONTROL
    config.players[0].name = 'A-STAR AGENT'
    config.players[0].camera_mode = pystk2.PlayerConfig.CameraMode.ON
    config.num_cameras = 1

    pygame.init()
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption('SuperTuxKart — Our A* Agent')
    font = pygame.font.SysFont(None, 23)
    clock = pygame.time.Clock()
    race = pystk2.Race(config)

    output = Path(__file__).parent / 'results' / 'astar_log.csv'
    output.parent.mkdir(parents=True, exist_ok=True)
    try:
        race.start()
        world, track = pystk2.WorldState(), pystk2.Track()
        track.update()
        agent = AStarRacingAgent(track)
        print('Loaded', agent.graph.n, 'track segments; 3 lanes per segment.')

        with output.open('w', newline='') as handle:
            writer = csv.DictWriter(handle, fieldnames=[
                'step', 'game_time', 'speed', 'steer', 'acceleration', 'brake',
                'on_road', 'current_segment', 'goal_segment', 'expanded', 'path_cost'])
            writer.writeheader()

            for step in range(max_steps):
                for event in pygame.event.get():
                    if event.type == pygame.QUIT or (
                        event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE
                    ):
                        return

                # Initial state may not exist until the first physics step.
                world.update()
                if world.players:
                    my_kart = world.players[0].kart
                    commands, details = agent.choose_action(my_kart, world, step)
                else:
                    commands = {'steer': 0.0, 'acceleration': 0.0, 'brake': False}
                    details = {'segment': -1, 'goal': -1, 'expanded': 0, 'path_cost': float('nan')}

                action = pystk2.Action()
                action.steer = commands['steer']
                action.acceleration = commands['acceleration']
                action.brake = commands['brake']
                continuing = race.step(action)
                world.update()

                if race.render_data:
                    image = race.render_data[0].image
                    h, w = image.shape[:2]
                    frame = pygame.image.frombuffer(image.tobytes(), (w, h), 'RGB')
                    screen.blit(frame, (0, 0))

                if world.players:
                    my_kart = world.players[0].kart
                    hud = (f'A* PLAYER | speed {my_kart.speed:.1f} | '
                           f'steer {action.steer:+.2f} | '
                           f'road {"YES" if my_kart.is_on_road else "NO"} | '
                           f'nodes expanded {details["expanded"]}')
                    pygame.draw.rect(screen, (10, 17, 28), (0, 0, width, 32))
                    screen.blit(font.render(hud, True, (255, 255, 255)), (10, 7))
                    writer.writerow({
                        'step': step, 'game_time': float(world.time),
                        'speed': float(my_kart.speed), 'steer': action.steer,
                        'acceleration': action.acceleration, 'brake': action.brake,
                        'on_road': bool(my_kart.is_on_road),
                        'current_segment': details['segment'],
                        'goal_segment': details['goal'],
                        'expanded': details['expanded'],
                        'path_cost': details['path_cost'],
                    })
                    if step % 120 == 0:
                        print(f'step={step} t={world.time:.1f} speed={my_kart.speed:.1f} '
                              f'node={details["segment"]} expanded={details["expanded"]} '
                              f'onroad={my_kart.is_on_road} fps={clock.get_fps():.1f}')

                pygame.display.flip()
                if not continuing:
                    print('Race completed or ended.')
                    break
                clock.tick(60)
    except KeyboardInterrupt:
        print('Interrupted by user.')
    finally:
        race.stop()
        del race
        pystk2.clean()
        pygame.quit()
        print('Saved experiment log to', output)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--karts', type=int, default=1)
    parser.add_argument('--steps', type=int, default=9000)
    args = parser.parse_args()
    if args.karts < 1:
        parser.error('--karts must be >= 1')
    run(args.karts, args.steps)
