"""CLI for running a matchup game.

Command-line tool whose primary purpose is to interactively manage a
matchup-based competitive game.
"""

import atexit
from cmd import Cmd
from contextlib import contextmanager
from pathlib import Path
import readline

from matchup_game.colored import colored
from matchup_game.game_engine import GameEngine

# pylint: disable=no-self-use
class GameConsole(Cmd):
  """Game CLI.

  Derives from cmd.Cmd and defines commands.

  Attributes:
      STYLES: Convenience packaging of options to format output.
      prompt: String to precede CLI input. Configurable by game.
      history: Path to CLI history file.
      engine: Engine that runs the game.
  """
  STYLES = {
      "alert": {
          "color": "red",
          "attrs": ["bold"],
        },
      "event": {
          "color": "magenta"
        },
      "heading": {
          "color": "green"
        },
      "info": {
          "color": "white"
        },
      "prompt": {
          "color": "cyan",
          "attrs": ["bold"],
          "escape": True
        }
    }

  @staticmethod
  def style_text(*objects, **styles):
    """Styles objects with an interface similar to print.

    Args:
        objects: Objects to print.
        styles: Keyword args used by the colored library.

    Returns:
        A collection of styled objects that can be directly printed.
    """
    return tuple(colored(obj, **styles) for obj in objects)

  @staticmethod
  def out(*objects, style=None, end="\n"):
    """Prints objects to console with an applied style.

    Args:
        objects: Objects to print.
        style: One of STYLES to apply to all objects.
        end: Text to follow the printed objects.
    """
    styles = GameConsole.STYLES[style or "info"]
    print(*GameConsole.style_text(*objects, **styles), end=end)

  @staticmethod
  @contextmanager
  def readline_disabled():
    """Context manager to temporarily disable readline features.
    """
    readline.set_auto_history(False)
    try:
      yield
    finally:
      readline.set_auto_history(True)

  @staticmethod
  def get_input(prompt, style=None):
    """Prompts the user for input and handles interrupts.

    Args:
        prompt: Text to display before user input.
        style: One of STYLES to apply to the prompt.

    Returns:
        The user's input as a String.
    """
    styles = GameConsole.STYLES[style or "prompt"]
    styles["escape"] = True
    with GameConsole.readline_disabled():
      try:
        return input("%s " % GameConsole.style_text(prompt, **styles))
      except KeyboardInterrupt:
        GameConsole.out()
        return ""

  def __init__(self, model):
    """Creates GameConsole instance.

    Args:
        model: The data model of the game to play.
    """
    super().__init__()

    self.prompt = "%s " % GameConsole.style_text("<%s>" %
        model.text["console_prompt"], **GameConsole.STYLES["prompt"])

    if model.history_file:
      self.history = Path(f"~/.{model.history_file}").expanduser()
    else:
      self.history = None

    self.engine = GameEngine(model, self)

  def cmdloop(self):
    """Runs the main loop.

    Handles CLI history and restarting the command prompt.
    """
    readline.set_history_length(1000)
    if self.history:
      atexit.register(readline.write_history_file, self.history)
      if self.history.exists():
        readline.read_history_file(self.history)

    while True:
      try:
        super().cmdloop()
        break
      except KeyboardInterrupt:
        self.out()
        self.emptyline()

  def onecmd(self, line):
    """Executes one command.

    Returns:
        True to stop processing commands; else False.
    """
    try:
      return super().onecmd(line)
    except ValueError as ex:
      self.out(f"command failed: {ex}")
      return False

  def emptyline(self):
    """Processes an empty command.

    Returns:
        False to continue processing commands.
    """
    return False

  # pylint: disable=invalid-name
  def do_EOF(self, _):
    """Handles end of line.

    Returns:
        True to stop processing commands.
    """
    self.out()
    return self.onecmd("quit")

  def do_quit(self, _):
    """Handles quitting the CLI.

    Returns:
        True to stop processing commands.
    """
    return True

  def do_play(self, _):
    """Starts the game.
    """
    self.engine.play()
