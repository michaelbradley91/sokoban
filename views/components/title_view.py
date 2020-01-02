from app_container import AppContainer
from constants.colours import TITLE_COLOUR, TITLE_SHADOW_COLOUR
from constants.text import START_VIEW_TITLE, draw_text_with_border
from layouts.aspect_layout import AspectLayout
from layouts.layout import Layout, BasicLayout
from layouts.margin_layout import MarginLayout
from views.components.component_view import ComponentView


class TitleView(ComponentView):
    """
    A view for drawing the title text.
    """

    def __init__(self, app_container: AppContainer, layout: BasicLayout):
        super().__init__(app_container, layout)

        self.title_layout = BasicLayout()

        surface = self.resources.title_font.get_surface(START_VIEW_TITLE, TITLE_COLOUR)
        aspect_layout = AspectLayout((surface.get_width(), surface.get_height()))
        aspect_layout.set_layout(self.title_layout)

        margin_layout = MarginLayout(1 / 20, identifier="title_margin")
        margin_layout.set_layout(aspect_layout)

        self.layout.set_layout(margin_layout)

    def draw(self):
        draw_text_with_border(self.resources.title_font, START_VIEW_TITLE, TITLE_COLOUR,
                              self.title_layout.bounding_rect, TITLE_SHADOW_COLOUR,
                              self.title_layout.bounding_rect.width / 120)
