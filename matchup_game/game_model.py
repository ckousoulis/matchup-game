"""Model classes representing a matchup game.

Read/Write game config from file and provide convenient data models.
"""

from contextlib import contextmanager
from pathlib import Path
import yaml

class Schema():
  """Schema mixin class.

  Validates game config files and safely loads them into models.
  """
  @classmethod
  def from_file(cls, path):
    """Loads YAML from a file.

    Args:
        cls: Schema class or derivative.
        path: The file containing the game data.

    Returns:
        Representation of YAML schema with built-in objects.

    Raises:
        ValueError: Invalid file or malformed YAML.
    """
    if not path.is_file():
      raise ValueError(f"{path} is not a {cls.__name__} file.")

    try:
      return yaml.safe_load(path.read_text())
    except yaml.YAMLError as ex:
      raise ValueError(f"{path} is not valid YAML.") from ex

  @classmethod
  def factory(cls, path):
    """Creates a data model from config schema.

    Args:
        cls: Schema class or derivative.
        path: The file containing the game data.

    Returns:
        Instance of cls loaded with data from file.

    Raises:
        ValueError: Schema does not conform with data model requirements.
    """
    try:
      return cls(path.parent, cls.from_file(path))
    except KeyError as ex:
      raise ValueError(f"{path} is not valid {cls.__name__} schema.") from ex

class Resolveable():
  """Resolveable mixin class.

  Resolves references contained within self to their loaded data models.

  Attributes:
      _properties: List of members expected to be references.
      _children: Data models contained within that need resolving.
  """
  def __init__(self, properties, children):
    """Resolveable base constructor.

    Args:
        properties: Members to resolve.
        children: Helper objects to resolve.
    """
    self._properties = properties
    self._children = children

  def resolve(self, game_model):
    """Resolves references to other game objects.

    Args:
        game_model: Main data model to look for existing objects.
    """
    for prop in self._properties:
      ref = getattr(self, prop)
      if ref:
        world, choice = tuple(ref["$ref"].split("/"))
        setattr(self, prop, game_model.worlds[world].choices[choice])

    for child in self._children:
      child.resolve(game_model)

class Option(Resolveable):
  """Option model.

  Represents an option contained within a choice.

  Attributes:
      key: Identifier unique to the choice.
      name: Presentation name of this option.
      next_choice: The choice to follow if this option is selected.
      transition: Optional text to present when playing this option.
  """
  def __init__(self, key, config):
    """Option constructor.

    Args:
        key: Identifier.
        config: Loaded schema.
    """
    self.key = key
    self.name = config["name"]
    self.next_choice = config["next_choice"]
    self.transition = config.get("transition")

    super().__init__(["next_choice"], [])

class Choice(Resolveable):
  """Choice model.

  Represents a choice for a player to make in a world.

  Attributes:
      key: Identifier unique to the world.
      name: Presentation name of this choice.
      prompt: Description of the choice to present when voting.
      options: Options the player selects from.
      selected: The option selected during a run of the game.
  """
  def __init__(self, key, config):
    """Choice constructor.

    Args:
        key: Identifier.
        config: Loaded schema.
    """
    self.key = key
    self.name = config["name"]
    self.prompt = config["prompt"]
    self.options = {k: Option(k, v) for k, v in config["options"].items()}
    self.selected = None

    super().__init__([], self.options.values())

class World(Resolveable, Schema):
  """World model.

  Represents a world which hosts choices in the game.

  Attributes:
      key: Identifier unique to the game.
      name: Presentation name of this world.
      transition: Optional text to present when entering this world.
      start: The choice that starts this world.
      choices: Choices for the player to make.
  """
  def __init__(self, _, config):
    """World constructor.

    Args:
        _: Directory containing this world's config.
        config: Loaded schema.
    """
    self.key = config["key"]
    self.name = config["name"]
    self.transition = config["transition"]
    self.start = config["start"]
    self.choices = {k: Choice(k, v) for k, v in config["choices"].items()}

    super().__init__(["start"], self.choices.values())

class GameModel(Resolveable, Schema):
  """Models a game.

  Loads configuration from file and manages state.

  Attributes:
      name: Name of the game.
      text: Dictionary of text to display to the player during the game.
      history_file: Optional file in which to remember player input.
      tiebreakers: Tiebreaker config to use during this game.
      worlds: The worlds available to play in this game.
      final_world: The designated final world in this game.
      max_worlds: How many worlds the player is allowed to visit.
  """
  @classmethod
  def from_user(cls, filepath, ex_cls=ValueError):
    """Creates a GameModel instance from user-provided filepath.

    Args:
        cls: GameModel class.
        filepath: The relative path given by the user as the configuration.
        ex_cls: Exception class to raise on error.

    Returns:
        A GameModel object loaded with config from file.

    Raises:
        ex_cls: The provided configuration is not valid.
    """
    try:
      return cls.factory(Path(filepath).resolve())
    except ValueError as ex:
      raise ex_cls(ex) from ex

  def __init__(self, path, config):
    """GameModel constructor.

    Args:
        path: Directory containing this game's config.
        config: Loaded schema.
    """
    self.name = config["name"]
    self.text = config["text"]
    self.history_file = config.get("history_file")
    self.tiebreakers = Schema.from_file(path / config["tiebreakers"])
    self.worlds = {}
    for file in config["worlds"]:
      world = World.factory(path / file)
      self.worlds[world.key] = world

    self.final_world = World.factory(path / config["final_world"])
    self.max_worlds = config.get("max_worlds", len(self.worlds))

    with self.worlds_joined([self.final_world]):
      super().__init__([], self.worlds.values())
      self.resolve(self)

  @contextmanager
  def worlds_joined(self, temp_worlds):
    """Context manager to temporarily join worlds to resolve references.

    Args:
        temp_worlds: Worlds to temporarily add to selectable list.
    """
    self.worlds.update((temp.key, temp) for temp in temp_worlds)
    try:
      yield
    finally:
      all(map(lambda temp: self.worlds.pop(temp.key), temp_worlds))
