from typing import Tuple, Optional, Union

import pygame
from pygame.rect import Rect

from coordinate import Coordinate
from opengl_support.drawable import Drawable
from opengl_support.texture import Texture


class TileSet(Texture):
    """
    Represents a tile set in OpenGL
    """
    def __init__(self, surface: pygame.SurfaceType, tile_size: Tuple[int, int],
                 tiles_wide: Optional[int] = None, tiles_high: Optional[int] = None):
        """
        Load a tile set from a given surface
        :param surface: the tile set as a surface
        :param tile_size: the size of each tile
        :param tiles_wide: the number of tiles wide the picture is. Leave as None to calculate this from the image size
        :param tiles_high: the number of tiles high the picture is. Leave as None to calculate this from the image size
        :return: the loaded tile set as a dictionary from x,y tile coordinates to the tile
        """
        super().__init__(surface)
        self.__tile_size = tile_size
        self.__tiles_wide = tiles_wide
        self.__tiles_high = tiles_high

        if not self.__tiles_wide:
            self.__tiles_wide = self.width // self.tile_size[0]
            self.__tiles_high = self.height // self.tile_size[1]

    @property
    def tile_size(self) -> Tuple[int, int]:
        return self.__tile_size

    def tile_coordinate_to_rect(self, tile_coordinate: Coordinate):
        """
        Convert a tile coordinate to its rectangle
        :param tile_coordinate: the coordinate for the tile
        :return: the sub-surface rectangle
        """
        return Rect((self.tile_size[0] * tile_coordinate.x, self.tile_size[1] * tile_coordinate.y), self.tile_size)

    def draw_tile(self, rect: Rect, tile_coordinate: Coordinate):
        """
        Draw a specific tile from the tile set
        :param rect: the rectangle in which to draw the tile
        :param tile_coordinate: the coordinate of the tile
        :return: nothing
        """
        sub_rect = self.tile_coordinate_to_rect(tile_coordinate)
        super().draw_sub_rectangle(rect, sub_rect)


class Tile(Drawable):
    """
    A singled out tile from a tile set to draw.
    """
    def __init__(self, tile_set: TileSet, tile: Union[Coordinate, Rect]):
        self.__tile_set = tile_set
        if isinstance(tile, Coordinate):
            self.__tile_rect = tile_set.tile_coordinate_to_rect(tile)
        else:
            self.__tile_rect = tile

    @property
    def tile_set(self):
        return self.__tile_set

    def reload(self):
        """
        Reload the tile. Generally, it is better to reload the underlying tile set to avoid reloading
        the whole tile set excessively.
        """
        self.__tile_set.reload()

    def draw(self, rect: Rect):
        """
        Draw this tile to fill the given rectangle
        :param rect: the rectangle to fill
        :return: nothing
        """
        self.__tile_set.draw_sub_rectangle(rect, self.__tile_rect)
