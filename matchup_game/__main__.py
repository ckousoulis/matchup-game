"""Entry point into the Matchup Game application.
"""

import argparse
from functools import partial

from .game_console import GameConsole
from .game_model import GameModel

def main():
  """Runs the Matchup Game CLI main loop.
  """
  parser = argparse.ArgumentParser(description="CLI for Matchup Games.")
  parser.add_argument(
      "game",
      help="Game configuration",
      type=partial(GameModel.from_user, ex_cls=argparse.ArgumentTypeError))
  args = parser.parse_args()
  GameConsole(args.game).cmdloop()

if __name__ == "__main__":
  main()
