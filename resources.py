from typing import Dict, List, Tuple, Optional

import pygame
import sys
import os
from direction import Direction
from pygame import SurfaceType
from pygame.mixer import SoundType
from opengl_support.helpers import load_texture_to_surface
from opengl_support.tilesets import TileSet, Tile
from opengl_support.font import Font
from coordinate import Coordinate


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

        # Tiles
        self.__crate = Tile(self.tiles1, Coordinate(1, 0))
        self.__floor = Tile(self.tiles2, Coordinate(1, 3))
        self.__goal = Tile(self.tiles1, Coordinate(1, 3))
        self.__wall = Tile(self.tiles2, Coordinate(1, 1))
        self.__player = self.__get_player_tiles()

        # Sounds
        self.__crate_sound = pygame.mixer.Sound(find_resource("resources/crate_sound.wav"))
        self.__coin_sound = pygame.mixer.Sound(find_resource("resources/mario coin.wav"))
        self.__crate_success_sound = self.__coin_sound
        self.__win_sound = pygame.mixer.Sound(find_resource("resources/Ta Da-SoundBible.com-1884170640.wav"))

        # Fonts
        self.__you_win_font = Font(pygame.font.Font(find_resource("resources/heygorgeous.ttf"), 256))

        # Display
        self.display = display

    def reload(self):
        """
        On some events such as a window resize, the textures must be reloaded.
        This method reloads all textures immediately.
        """
        self.tiles1.reload()
        self.tiles2.reload()
        self.tiles3.reload()
        self.you_win_font.reload()

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
    def you_win_font(self) -> Font:
        return self.__you_win_font

    @property
    def crate_sound(self) -> SoundType:
        return self.__crate_sound

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
        return Tile(self.tiles1, Coordinate(1, 0))

    @property
    def floor(self) -> Tile:
        return Tile(self.tiles2, Coordinate(1, 3))

    @property
    def goal(self) -> Tile:
        return Tile(self.tiles1, Coordinate(1, 3))

    @property
    def wall(self) -> Tile:
        return Tile(self.tiles2, Coordinate(1, 1))

    @property
    def player(self) -> Dict[Direction, List[Tile]]:
        return self.__player

    def __get_player_tiles(self) -> Dict[Direction, List[Tile]]:
        # Load all the player tiles into a dictionary based on direction
        player_tiles = {Direction.left: [], Direction.right: [], Direction.down: [], Direction.up: []}
        for phase in range(0, 3):
            player_tiles[Direction.left].append(Tile(self.tiles3, Coordinate(3 + phase, 6)))
            player_tiles[Direction.right].append(Tile(self.tiles3, Coordinate(phase, 6)))
            player_tiles[Direction.up].append(Tile(self.tiles3, Coordinate(3 + phase, 4)))
            player_tiles[Direction.down].append(Tile(self.tiles3, Coordinate(phase, 4)))
        return player_tiles
