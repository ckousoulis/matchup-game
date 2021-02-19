Matchup Game
============

Matchup Game is an open source tool for playing matchup-based games.

With the command-line interface, anyone can run a game with their friends that
involves arguing over competitive options and voting on a winner.

Running
-------

from source
^^^^^^^^^^^

1. Clone the `matchup-game`_ repository.
2. From the repository root directory, run:

  .. code-block:: text

    $ python -m matchup_game games/configuration.yml

from install
^^^^^^^^^^^^

1. ``pip install path/to/tarball``
2. From anywhere within the Python environment, run:

  .. code-block:: text

    $ matchup-game path/to/games/configuration.yml

3. Run ``play`` to start the game.

.. _`matchup-game`: https://github.com/ckousoulis/matchup-game

Commands
--------

* ``play``: Starts the game.
* ``help``: Shows help text with a list of commands.
* ``quit``: Exits the shell, as does ``^d`` for end of file.

Developing
----------

* Install packages: ``pylint``
* Lint the source files in accordance with `Google's Style Guide`_
* Package with ``python setup.py sdist``

.. _`Google's Style Guide`: http://google.github.io/styleguide/pyguide.html