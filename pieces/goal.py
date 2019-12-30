from app_container import AppContainer
from grid import Grid
from pieces.static import StaticPiece


class GoalPiece(StaticPiece):
    """
    A piece representing a goal, which is where a crate needs to be pushed to.
    """

    def __init__(self, grid: "Grid", app_container: AppContainer):
        super().__init__(grid, app_container, app_container.resources.goal, True)
