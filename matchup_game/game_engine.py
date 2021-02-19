"""Engine class for running a matchup game.

Handles player input and manages game state.
"""

import random

class GameEngine():
  """Game Engine.

  Runs the game using the game model for data and interacts with the player
  through the game console.

  Attributes:
      model: Data model for the game.
      console: Console for player input/output.
      worlds: Worlds visited during the game.
      progress: Choices made in each visited world.
      summary: Textual indication of player's progression through worlds.
      tiebreaker: Helper engine to manage tiebreaks.
  """
  def __init__(self, model, console):
    """Creates GameEngine instance.

    Args:
        model: The data model for the game.
        console: Console for player input/output.
    """
    self.model = model
    self.console = console

    self.worlds = []
    self.progress = {}
    self.summary = "? > ? > ? > ?"
    self.tiebreaker = Tiebreaker(self)

  def play(self):
    """Runs the game.

    Progression: Welcome > (Select & Play World)* > Summary > Final World
    """
    self.console.out(self.model.text["welcome"], style="heading")
    self.console.out(self.model.text["instructions"])

    while len(self.worlds) < self.model.max_worlds:
      self.console.out("%s: %s" %
          (self.model.text["worlds_prefix"], self.summary), style="heading")
      self.play_world(self.select_world())

    self.show_summary()
    self.play_world(self.model.final_world)
    self.console.out("Fin")

  def select_world(self):
    """Handles selection of the next world by the player.

    Returns:
        The World object selected.
    """
    self.console.out(self.model.text["world_selection"])

    worlds = filter(lambda w: w not in self.worlds, self.model.worlds.values())
    return self.vote(dict(enumerate(worlds, 1)))

  def play_world(self, world):
    """Plays through the choices in the provided world.

    Args:
        world: The world to play.
    """
    self.worlds.append(world)
    self.summary = self.summary.replace("?", world.name, 1)
    self.progress[world.key] = []

    self.console.out()
    if world.transition:
      self.console.out(world.transition, style="event")

    current = world.start
    while current:
      option = self.select_option(current)
      current = self.play_option(world, current, option)

  def select_option(self, choice):
    """Handles selection of an option for a given choice.

    Args:
        choice: The choice for the player to make.

    Returns:
        Option object selected.
    """
    self.console.out(choice.prompt)

    return self.vote(dict(enumerate(choice.options.values(), 1)))

  def play_option(self, world, choice, option):
    """Plays the consequences of an option selected by the player.

    Args:
        world: The current world.
        choice: The current choice.
        option: The option selected by the player.

    Returns:
        Choice object for the player's next choice.
    """
    choice.selection = option
    self.progress[world.key].append(choice)

    self.console.out()
    if option.transition:
      self.console.out(option.transition, style="event")

    return option.next_choice

  def show_summary(self):
    """Presents a summary of the worlds visited and choices made.
    """
    self.console.out(self.model.text["summary"], style="heading")
    for world in self.worlds:
      self.console.out(world.name)
      for choice in self.progress[world.key]:
        self.console.out(f"  {choice.name}: {choice.selection.name}")

  def vote(self, options):
    """Handles the player's selection of an option.

    Args:
        options: {i: value} map to present to the player.

    Returns:
        The value selected by the player.
    """
    winners = self.do_vote(options)
    while len(winners) > 1:
      winners = self.tiebreaker.break_tie(options, winners)

    self.console.out(f"{options[winners[0]].name} won")
    return options[winners[0]]

  def do_vote(self, options, indent=""):
    """Presents a vote to the player and gets their choice(s).

    Args:
        options: {i: value} map to present to the player.
        indent: Prefix string for player interactions during this vote.

    Returns:
        A list of each option selected, where multiple indicates a tie.
    """
    for i, val in options.items():
      self.console.out("%s  %s. %s" % (indent, i, getattr(val, "name", val)))

    winners = []
    while not winners or not all(k in options for k in winners):
      self.console.out(indent, end="")
      reply = self.console.get_input("Vote!", style="alert")
      try:
        winners = list(map(int, reply.split()))
      except ValueError:
        winners = []

    return winners

class Tiebreaker():
  """Tiebreaker.

  Helper engine to manage tiebreaks throughout the game.

  Attributes:
      config: Data model for tiebreakers.
      console: Console for player input/output.
      do_vote: Function that handles voting.
      tiebreakers: Available tiebreaker questions.
  """
  def __init__(self, engine):
    """Creates GameEngine instance.

    Args:
        engine: The main game engine.
    """
    self.config = engine.model.tiebreakers
    self.console = engine.console
    self.do_vote = engine.do_vote

    self.tiebreakers = list(self.config.keys())
    random.shuffle(self.tiebreakers)

  def break_tie(self, options, tied_keys):
    """Breaks a tie.

    Args:
        options: {i: value} map for the tied vote.
        tied_keys: The keys which tied.

    Returns:
        The values selected via tiebreak. More than one if another tie.
    """
    self.console.out("\tTiebreak: ", style="event", end="")

    if self.tiebreakers:
      return self.vote_break(options, tied_keys)

    return self.random_break(options, tied_keys)

  @staticmethod
  def tiebreaker_to_keys(tiebreaker, tied_keys):
    """Helper to map tiebreaker values to the tied keys.

    Args:
        tiebreaker: Tiebreaker config to use for this tiebreak.
        tied_keys: The keys which tied.

    Returns:
        {value: tied_keys} map from tiebreaker options.
    """
    values = tiebreaker["options"].copy()
    random.shuffle(values)
    return dict(zip(values, tied_keys))

  @staticmethod
  def vote_options(to_keys):
    """Helper to build vote options for values corresponding to tied keys.

    Args:
        to_keys: {value: tied_keys} map from tiebreaker options.

    Returns:
        {i: value} map for the tiebreaker vote.
    """
    keys = list(to_keys.keys())
    random.shuffle(keys)
    return dict(enumerate(keys, 1))

  def vote_break(self, options, tied_keys):
    """Breaks a tie with another, unrelated vote.

    Args:
        options: {i: value} map for the tied vote.
        tied_keys: The keys which tied.

    Returns:
        The values selected via tiebreak. More than one if another tie.
    """
    tiebreaker = self.config[self.tiebreakers.pop()]
    self.console.out(tiebreaker["prompt"])

    to_keys = self.tiebreaker_to_keys(tiebreaker, tied_keys)
    vote_options = self.vote_options(to_keys)
    reply = [vote_options[r] for r in self.do_vote(vote_options, indent="\t")]
    for winner in reply:
      self.console.out(f"\t{winner} > {options[to_keys[winner]].name}")

    return [to_keys[winner] for winner in reply]

  def random_break(self, options, tied_keys):
    """Breaks a tie by picking a random option.

    Args:
        options: {i: value} map for the tied vote.
        tied_keys: The keys which tied.

    Returns:
        The random value selected to break the tie.
    """
    reply = random.choice(tied_keys)
    self.console.out("Random...\n\t...%s" % options[reply].name)
    return [reply]
