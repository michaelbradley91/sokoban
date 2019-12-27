# Sokoban

A simple puzzle game.

All the art is sourced from various places online.

## How to run
Install Python 3.6 + and run the following in the base of the repository:
```sh
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

The app can now be run after activating the venv (`source venv/bin/activate`) with:
```sh
python app.py
```

## How to package
To build an executable for the game run:
```sh
source venv/bin/activate
python setup.py build
```

This will drop an executable inside the `build` directory somewhere.

To build an MSI installer, just run:
```sh
python setup.py bdist_msi
```

When installed you should be able to just search for "Sokoban".
Currently you will need to add the Desktop shortcut manually if you would like one.

## Art
Thanks to Kenney and 1001com on Open Game Art for the free Sokoban tilesets:

* https://opengameart.org/content/sokoban-100-tiles
* https://opengameart.org/content/sokoban-pack

## Fonts
* https://www.ffonts.net/Hey-Gorgeous.font

## Sound

* https://soundbible.com/1003-Ta-Da.html
* https://www.zapsplat.com/sound-effect-category/cardboard/ - Zapslat
* https://www.findsounds.com/ISAPI/search.dll?keywords=ding+dinging&keywords=ding+dinging
* https://soundimage.org/puzzle-music/

