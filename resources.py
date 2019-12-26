from typing import Dict, Tuple, Optional, List

import pygame
from pygame.font import FontType, Font
from pygame.mixer import SoundType
from undo import UndoManager
from direction import Direction
from music_player import MusicPlayer


def scale(size, surface: pygame.SurfaceType) -> pygame.SurfaceType:
    return pygame.transform.scale(surface, size)


def dim(surface: pygame.SurfaceType, amount: int):
    dark = pygame.Surface(surface.get_size(), flags=pygame.SRCALPHA)
    dark.fill((amount, amount, amount, 0))
    surface.blit(dark, (0, 0), special_flags=pygame.BLEND_RGBA_SUB)
    return surface


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
    def __init__(self, display: pygame.SurfaceType):
        self.display: pygame.SurfaceType = display
        self.tiles1 = load_tile_set("resources/sokoban_tilesheet.png", 128)
        self.tiles2 = load_tile_set("resources/sokoban_tilesheet2.png", 64, width=6, height=6)
        self.tiles3 = load_tile_set("resources/sokoban_tilesheet3.png", 128)
        self.__crate_sound = pygame.mixer.Sound('resources/crate_sound.wav')
        self.__you_win_font = Font("resources/heygorgeous.ttf", 48)
        self.__coin_sound = pygame.mixer.Sound('resources/mario coin.wav')
        self.__crate_success_sound = self.__coin_sound
        self.__win_sound = pygame.mixer.Sound('resources/Ta Da-SoundBible.com-1884170640.wav')

    @property
    def you_win_font(self) -> FontType:
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
    def crate_image(self) -> pygame.SurfaceType:
        return self.tiles1[1, 0]

    @property
    def floor_image(self) -> pygame.SurfaceType:
        return self.tiles2[1, 3]

    @property
    def goal_image(self) -> pygame.SurfaceType:
        return self.tiles1[1, 3]

    @property
    def wall_image(self) -> pygame.SurfaceType:
        return self.tiles2[1, 1]

    def get_player_images(self, facing_direction: Direction) -> List[pygame.SurfaceType]:
        if facing_direction == Direction.left:
            return [self.tiles3[3 + i, 6] for i in range(0, 3)]
        if facing_direction == Direction.right:
            return [self.tiles3[i, 6] for i in range(0, 3)]
        if facing_direction == Direction.up:
            return [self.tiles3[3 + i, 4] for i in range(0, 3)]
        if facing_direction == Direction.down:
            return [self.tiles3[i, 4] for i in range(0, 3)]
        raise ValueError("Unknown direction")
