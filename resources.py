import os
import sys
from typing import Dict, List, Tuple, Optional

import pygame
from pygame import SurfaceType, Rect
from pygame.mixer import SoundType

from constants.direction import Direction
from coordinate import Coordinate
from opengl_support.font import Font
from opengl_support.helpers import load_texture_to_surface
from opengl_support.tilesets import TileSet, Tile


def find_resource(path):
    if getattr(sys, 'frozen', False):
        base_path = os.path.dirname(sys.executable)
    else:
        base_path = os.path.dirname(__file__)
    return os.path.join(base_path, path)


def load_tile_set(file_path: str, tile_size: int,
                  width: Optional[int] = None,
                  height: Optional[int] = None) -> Dict[Tuple[int, int], pygame.SurfaceType]:
    """
    Load a tile set from a given file
    :param file_path: the path to the file
    :param tile_size: the size of each tile
    :param width: the number of tiles wide the picture is. Leave as None to calculate this from the image size
    :param height: the number of tiles high the picture is. Leave as None to calculate this from the image size
    :return: the loaded tile set as a dictionary from x,y tile coordinates to the tile
    """
    image = pygame.image.load(file_path).convert_alpha()
    image_width, image_height = image.get_size()
    tile_width, tile_height = tile_size, tile_size
    tiles: Dict[Tuple[int, int], pygame.SurfaceType] = dict()
    for tile_x in range(0, int(image_width / tile_width) if width is None else width):
        for tile_y in range(0, int(image_height / tile_height) if height is None else height):
            rect = (tile_x * tile_width, tile_y * tile_height, tile_width, tile_height)
            tiles[tile_x, tile_y] = image.subsurface(rect)
    return tiles


class Resources:
    """
    A collection for all the games resources
    """
    def __init__(self, display: SurfaceType):
        # Tile sets
        self.__tiles1 = TileSet(load_texture_to_surface(find_resource("resources/sokoban_tilesheet.png")), (128, 128))
        self.__tiles2 = TileSet(load_texture_to_surface(find_resource("resources/sokoban_tilesheet2.png")), (64, 64),
                                tiles_wide=6, tiles_high=6)
        self.__tiles3 = TileSet(load_texture_to_surface(find_resource("resources/sokoban_tilesheet3.png")), (128, 128))
        self.__keyboard_tiles = TileSet(load_texture_to_surface(find_resource("resources/keys.png")), (1, 1))

        # Tiles
        self.__crate = Tile(self.tiles1, Coordinate(1, 0))
        self.__floor = Tile(self.tiles2, Coordinate(1, 3))
        self.__goal = Tile(self.tiles1, Coordinate(1, 3))
        self.__wall = Tile(self.tiles2, Coordinate(1, 1))
        self.__menu_background = Tile(self.tiles2, Coordinate(0, 0))
        self.__player = self.__get_player_tiles()
        self.__keyboard_key = self.__get_keyboard_tiles()

        # Sounds
        self.__crate_sound = pygame.mixer.Sound(find_resource("resources/crate_sound.wav"))
        self.__coin_sound = pygame.mixer.Sound(find_resource("resources/mario coin.wav"))
        self.__crate_success_sound = self.__coin_sound
        self.__win_sound = pygame.mixer.Sound(find_resource("resources/Ta Da-SoundBible.com-1884170640.wav"))

        # Fonts
        self.__title_font = Font(pygame.font.Font(find_resource("resources/heygorgeous.ttf"), 128))
        self.__menu_font = Font(pygame.font.Font(find_resource("resources/heygorgeous.ttf"), 24))
        self.__wall_text_font = Font(pygame.font.Font(find_resource("resources/heygorgeous.ttf"), 32))
        self.__you_win_font = self.__wall_text_font
        self.__key_font = self.__wall_text_font
        self.__keyboard_text_font = self.__wall_text_font
        self.__arrows_font = Font(pygame.font.Font(find_resource("resources/M2PBold-XJDa.ttf"), 24))
        self.__symbols_font = Font(pygame.font.Font(find_resource("resources/Quivira-A8VL.ttf"), 24))

        # Display
        self.display = display

    def reload(self):
        """
        On some events such as a window resize, the textures must be reloaded.
        This method reloads all textures immediately.
        """
        # Tiles
        self.tiles1.reload()
        self.tiles2.reload()
        self.tiles3.reload()
        self.__keyboard_tiles.reload()

        # Fonts
        self.title_font.reload()
        self.menu_font.reload()
        self.wall_text_font.reload()
        self.arrows_font.reload()
        self.symbols_font.reload()

    @property
    def tiles1(self) -> TileSet:
        return self.__tiles1

    @property
    def tiles2(self) -> TileSet:
        return self.__tiles2

    @property
    def tiles3(self) -> TileSet:
        return self.__tiles3

    @property
    def keyboard_tiles(self) -> TileSet:
        return self.__keyboard_tiles

    @property
    def title_font(self):
        return self.__title_font

    @property
    def menu_font(self):
        return self.__menu_font

    @property
    def wall_text_font(self):
        return self.__wall_text_font

    @property
    def you_win_font(self) -> Font:
        return self.__you_win_font

    @property
    def keyboard_text_font(self) -> Font:
        return self.__keyboard_text_font

    @property
    def arrows_font(self) -> Font:
        return self.__arrows_font

    @property
    def symbols_font(self) -> Font:
        return self.__symbols_font

    @property
    def crate_sound(self) -> SoundType:
        return self.__crate_sound

    @property
    def menu_background(self) -> Tile:
        return self.__menu_background

    @property
    def crate_success_sound(self) -> SoundType:
        return self.__crate_success_sound

    @property
    def coin_sound(self) -> SoundType:
        return self.__coin_sound

    @property
    def win_sound(self) -> SoundType:
        return self.__win_sound

    @property
    def crate(self) -> Tile:
        return self.__crate

    @property
    def floor(self) -> Tile:
        return self.__floor

    @property
    def goal(self) -> Tile:
        return self.__goal

    @property
    def wall(self) -> Tile:
        return self.__wall

    @property
    def player(self) -> Dict[Direction, List[Tile]]:
        return self.__player

    @property
    def keyboard_key(self) -> Dict[int, Tile]:
        return self.__keyboard_key

    def __get_keyboard_tiles(self) -> Dict[int, Tile]:
        # Load all the keyboard tiles into a dictionary based on width
        return {
            1: Tile(self.keyboard_tiles, Rect((0, 0), (128, 128))),
            2: Tile(self.keyboard_tiles, Rect((128, 0), (256, 128))),
            3: Tile(self.keyboard_tiles, Rect((384, 0), (384, 128))),
        }

    def __get_player_tiles(self) -> Dict[Direction, List[Tile]]:
        # Load all the player tiles into a dictionary based on direction
        player_tiles = {Direction.left: [], Direction.right: [], Direction.down: [], Direction.up: []}
        for phase in range(0, 3):
            player_tiles[Direction.left].append(Tile(self.tiles3, Coordinate(3 + phase, 6)))
            player_tiles[Direction.right].append(Tile(self.tiles3, Coordinate(phase, 6)))
            player_tiles[Direction.up].append(Tile(self.tiles3, Coordinate(3 + phase, 4)))
            player_tiles[Direction.down].append(Tile(self.tiles3, Coordinate(phase, 4)))
        return player_tiles
