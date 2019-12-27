from animator import Animator
from layouts.grid_layout import GridLayout
from layouts.layout import BasicLayout
from music_player import MusicPlayer
from navigator import Navigator
from resources import Resources
from undo import UndoManager
from views.view import ViewModel, View


class StartViewParameters:
    pass


class StartViewModel(ViewModel[StartViewParameters]):
    pass


class StartView(View[StartViewParameters, StartViewModel]):
    def __init__(self, undo_manager: UndoManager, animator: Animator, music_player: MusicPlayer, resources: Resources,
                 navigator: Navigator, layout: BasicLayout):
        super().__init__(undo_manager, animator, music_player, resources, navigator, layout)

    def init(self):
        title_layout = BasicLayout()


        # Build the layout for the page as a grid
        grid_layout = GridLayout(width=20, height=13)

