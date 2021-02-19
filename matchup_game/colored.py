"""Library for coloring text and setting display attributes.

Applies ANSI escape codes for SGR (Select Graphic Rendition) parameters.
"""

import itertools

_FG_COLORS = dict(itertools.chain(
    zip(("black",
         "red",
         "green",
         "yellow",
         "blue",
         "magenta",
         "cyan",
         "white",
        ), range(30, 38)),
    zip(("bright_black",
         "bright_red",
         "bright_green",
         "bright_yellow",
         "bright_blue",
         "bright_magenta",
         "bright_cyan",
         "bright_white",
        ), range(90, 98))))

_BG_COLORS = dict((f"on_{key}", val + 10) for key, val in _FG_COLORS.items())

_ATTRIBUTES = dict(
    zip(("bold",
         "faint",
         "italic",
         "underline",
         "slow_blink",
         "rapid_blink",
         "reverse",
         "conceal",
         "strikethrough",
        ), range(1, 10)))

def colored(text, color=None, on_color=None, attrs=None, escape=False):
  """Wraps text with ANSI escape codes to achieve the desired look.

  Args:
      color: The foreground color.
      on_color: The background color.
      attrs: A list of effects.
      escape: True to escape invisibles (for readline); else False.

  Returns:
      A string with the original text wrapped by escape codes.
  """
  def sgr(*codes):
    return "\x1b[%sm" % ";".join(map(str, codes))
  def esc(text):
    return "\x01%s\x02" % text

  codes = []
  if color:
    codes.append(_FG_COLORS[color])
  if on_color:
    codes.append(_BG_COLORS[on_color])
  if attrs:
    codes.extend(_ATTRIBUTES[attr] for attr in attrs)

  if not escape:
    esc = lambda n: n

  return "%s%s%s" % (esc(sgr(*codes)), text, esc(sgr(0)))
