from typing import TYPE_CHECKING

from app_container import AppContainer
from pieces.static import StaticPiece

if TYPE_CHECKING:
    from grid import Grid


class FloorPiece(StaticPiece):
    """
    A piece representing the floor.
    """

    def __init__(self, grid: "Grid", app_container: AppContainer):
        super().__init__(grid, app_container, app_container.resources.floor, True)
