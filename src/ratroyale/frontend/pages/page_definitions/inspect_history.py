import pygame
import pygame_gui

from ratroyale.coordination_manager import CoordinationManager
from ratroyale.event_tokens.visual_token import *
from ratroyale.event_tokens.page_token import *
from ratroyale.event_tokens.game_token import *
from ratroyale.event_tokens.payloads import MoveHistoryPayload


from ..page_managers.base_page import Page
from ratroyale.frontend.pages.page_managers.event_binder import (
    input_event_bind,
    callback_event_bind,
    SpecialInputScope,
)
from ratroyale.frontend.pages.page_managers.page_registry import register_page

from ratroyale.frontend.pages.page_elements.element import (
    ElementWrapper,
    ui_element_wrapper,
)
from ratroyale.frontend.pages.page_elements.spatial_component import Camera
from ratroyale.frontend.gesture.gesture_data import GestureType
from ratroyale.frontend.visual.screen_constants import SCREEN_SIZE


@register_page
class InspectHistory(Page):
    def __init__(
        self, coordination_manager: "CoordinationManager", camera: Camera
    ) -> None:
        super().__init__(
            coordination_manager,
            is_blocking=True,
            theme_name="inspect_history",
            camera=camera,
        )
        self.current_move_data: MoveHistoryPayload | None = None
        self.map_surface: pygame.Surface | None = None
        self.map_panel_element: pygame_gui.elements.UIPanel | None = None

    def define_initial_gui(self) -> list[ElementWrapper]:
        elements: list[ElementWrapper] = []

        panel_w, panel_h = 500, 420
        panel_x = (SCREEN_SIZE[0] - panel_w) // 2
        panel_y = (SCREEN_SIZE[1] - panel_h) // 2
        panel = ui_element_wrapper(
            pygame_gui.elements.UIPanel(
                relative_rect=pygame.Rect(panel_x, panel_y, panel_w, panel_h),
                manager=self.gui_manager,
                object_id=pygame_gui.core.ObjectID(
                    class_id="InspectHistoryPanel", object_id="inspect_history_panel"
                ),
                anchors={"left": "left", "top": "top"},
            ),
            registered_name="inspect_history_panel",
            grouping_name="inspect_history",
            camera=self.camera,
        )
        elements.append(panel)

        portrait_area = ui_element_wrapper(
            pygame_gui.elements.UIPanel(
                relative_rect=pygame.Rect(10, 10, 120, 120),
                manager=self.gui_manager,
                container=panel.get_interactable(pygame_gui.elements.UIPanel),
                object_id=pygame_gui.core.ObjectID(
                    class_id="PortraitArea", object_id="history_portrait"
                ),
                anchors={
                    "left": "left",
                    "top": "top",
                },
            ),
            registered_name="history_portrait",
            grouping_name="inspect_history",
            camera=self.camera,
        )
        elements.append(portrait_area)

        history_title = ui_element_wrapper(
            pygame_gui.elements.UILabel(
                relative_rect=pygame.Rect(140, 10, 350, 30),
                text="History Event",
                manager=self.gui_manager,
                container=panel.get_interactable(pygame_gui.elements.UIPanel),
                object_id=pygame_gui.core.ObjectID(
                    class_id="InspectHistoryLabel", object_id="history_title"
                ),
                anchors={
                    "left": "left",
                    "top": "top",
                },
            ),
            registered_name="history_title",
            grouping_name="inspect_history",
            camera=self.camera,
        )
        elements.append(history_title)

        history_desc = ui_element_wrapper(
            pygame_gui.elements.UILabel(
                relative_rect=pygame.Rect(140, 44, 350, 86),
                text="Clanker moves from (xx, xx) to (xx, xx).",
                manager=self.gui_manager,
                container=panel.get_interactable(pygame_gui.elements.UIPanel),
                object_id=pygame_gui.core.ObjectID(
                    class_id="InspectHistoryLabel", object_id="history_desc"
                ),
                anchors={
                    "left": "left",
                    "top": "top",
                },
            ),
            registered_name="history_desc",
            grouping_name="inspect_history",
            camera=self.camera,
        )
        elements.append(history_desc)

        map_panel = ui_element_wrapper(
            pygame_gui.elements.UIPanel(
                relative_rect=pygame.Rect(10, 140, 480, 260),
                manager=self.gui_manager,
                container=panel.get_interactable(pygame_gui.elements.UIPanel),
                object_id=pygame_gui.core.ObjectID(
                    class_id="HistoryMap", object_id="history_map"
                ),
                anchors={
                    "left": "left",
                    "top": "top",
                },
            ),
            registered_name="history_map",
            grouping_name="inspect_history",
            camera=self.camera,
        )
        elements.append(map_panel)

        exit_button = ui_element_wrapper(
            pygame_gui.elements.UIButton(
                relative_rect=pygame.Rect(-90, 10, 80, 30),
                text="exit",
                manager=self.gui_manager,
                container=panel.get_interactable(pygame_gui.elements.UIPanel),
                object_id=pygame_gui.core.ObjectID(
                    class_id="InspectHistoryButton", object_id="exit_button"
                ),
                anchors={
                    "right": "right",
                    "top": "top",
                },
            ),
            registered_name="exit_button",
            grouping_name="inspect_history",
            camera=self.camera,
        )
        elements.append(exit_button)

        return elements

    def render(self, time_delta: float) -> pygame.Surface:
        """Override render to draw the map surface onto the panel."""
        # Get the normal rendering first
        canvas = super().render(time_delta)

        # If we have a map surface to draw, blit it onto the panel area
        if self.map_surface and self.map_panel_element:
            try:
                map_panel = self.map_panel_element
                # Blit the map surface onto the panel
                canvas.blit(
                    self.map_surface, (map_panel.rect.x + 2, map_panel.rect.y + 2)
                )
            except Exception:
                pass  # Silently fail if panel is not available

        return canvas

    @callback_event_bind("move_history_data")
    def on_move_history_data(self, msg: PageCallbackEvent) -> None:
        if msg.success and msg.payload:
            payload = msg.payload
            assert isinstance(payload, MoveHistoryPayload)
            self.current_move_data = payload

            # Update title with entity name
            title_element = self._element_manager.get_element("history_title")
            title_label = title_element.get_interactable(pygame_gui.elements.UILabel)
            title_label.set_text(payload.entity_name)

            # Update description with move details
            desc_element = self._element_manager.get_element("history_desc")
            desc_label = desc_element.get_interactable(pygame_gui.elements.UILabel)
            move_direction = f"from {payload.from_pos} to {payload.to_pos}"
            move_text = f"{payload.entity_name} moves {move_direction}"
            desc_label.set_text(move_text)
            # Draw the map with movement path
            self._draw_map_with_movement(payload)

    def _draw_map_with_movement(self, payload: MoveHistoryPayload) -> None:
        """Draw a simple map visualization showing the movement path."""
        # Parse coordinates from strings like "(9, 8)"
        from_str = payload.from_pos.strip("()")
        to_str = payload.to_pos.strip("()")
        from_coords_list = list(map(int, from_str.split(",")))
        to_coords_list = list(map(int, to_str.split(",")))
        from_coords = (from_coords_list[0], from_coords_list[1])
        to_coords = (to_coords_list[0], to_coords_list[1])

        # Get panel element
        map_panel_element = self._element_manager.get_element("history_map")
        map_panel = map_panel_element.get_interactable(pygame_gui.elements.UIPanel)

        # Get panel dimensions
        panel_rect = map_panel.rect
        panel_width = int(panel_rect.width - 4)
        panel_height = int(panel_rect.height - 4)

        # Create a new surface for drawing
        self.map_surface = pygame.Surface((panel_width, panel_height))
        self.map_surface.fill((30, 35, 40))

        # Calculate tile size - use larger radius for better visibility
        tile_radius = 35
        padding = 10

        # Draw grid of tiles
        self._draw_hexagon_grid(
            self.map_surface, tile_radius, padding, from_coords, to_coords
        )

        # Store reference to panel for later drawing
        self.map_panel_element = map_panel

    def _draw_hexagon_grid(
        self,
        surface: pygame.Surface,
        hex_radius: int,
        padding: int,
        from_coords: tuple[int, int],
        to_coords: tuple[int, int],
    ) -> None:
        """Draw a grid of square tiles showing the actual movement area at real scale."""
        # Show tiles in a smaller range around the movement for better visibility
        min_q = min(from_coords[0], to_coords[0]) - 1
        max_q = max(from_coords[0], to_coords[0]) + 1
        min_r = min(from_coords[1], to_coords[1]) - 1
        max_r = max(from_coords[1], to_coords[1]) + 1

        grid_width = max_q - min_q + 1
        grid_height = max_r - min_r + 1

        # Calculate tile size - make smaller to fit in panel
        tile_size = hex_radius

        # Center the grid in the surface
        total_width = grid_width * tile_size
        total_height = grid_height * tile_size

        start_x = (surface.get_width() - total_width) / 2
        start_y = (surface.get_height() - total_height) / 2

        # Draw all tiles in the grid
        for q in range(min_q, max_q + 1):
            for r in range(min_r, max_r + 1):
                # Calculate tile position
                x = start_x + (q - min_q) * tile_size
                y = start_y + (r - min_r) * tile_size

                # Determine color based on position
                if (q, r) == from_coords:
                    color = (100, 255, 100)  # Bright green for start
                    border_width = 3
                elif (q, r) == to_coords:
                    color = (255, 100, 100)  # Bright red for end
                    border_width = 3
                else:
                    color = (120, 130, 140)  # Light gray for other tiles
                    border_width = 1

                self._draw_square(surface, x, y, tile_size, color, border_width)

                # Draw coordinate label
                font = pygame.font.Font(None, 14)
                text = font.render(f"{q},{r}", True, (50, 50, 50))
                text_rect = text.get_rect(center=(x + tile_size / 2, y + tile_size / 2))
                surface.blit(text, text_rect)

        # Draw arrow showing movement direction
        from_q = from_coords[0]
        from_r = from_coords[1]
        to_q = to_coords[0]
        to_r = to_coords[1]

        # Calculate tile center positions for arrow
        from_x = start_x + (from_q - min_q) * tile_size + tile_size / 2
        from_y = start_y + (from_r - min_r) * tile_size + tile_size / 2

        to_x = start_x + (to_q - min_q) * tile_size + tile_size / 2
        to_y = start_y + (to_r - min_r) * tile_size + tile_size / 2

        # Draw directional arrow
        import math as m

        dx = to_x - from_x
        dy = to_y - from_y
        distance = m.sqrt(dx * dx + dy * dy)

        if distance > 0:
            # Normalize and scale
            dx = dx / distance
            dy = dy / distance

            # Start arrow from edge of from_tile
            arrow_start_x = from_x + dx * tile_size / 2
            arrow_start_y = from_y + dy * tile_size / 2

            # End arrow at edge of to_tile
            arrow_end_x = to_x - dx * tile_size / 2
            arrow_end_y = to_y - dy * tile_size / 2

            # Draw arrow line
            pygame.draw.line(
                surface,
                (255, 200, 100),
                (arrow_start_x, arrow_start_y),
                (arrow_end_x, arrow_end_y),
                2,
            )

            # Draw arrow head
            arrow_size = 8
            angle = m.atan2(dy, dx)

            left_x = arrow_end_x - arrow_size * m.cos(angle - m.pi / 6)
            left_y = arrow_end_y - arrow_size * m.sin(angle - m.pi / 6)
            right_x = arrow_end_x - arrow_size * m.cos(angle + m.pi / 6)
            right_y = arrow_end_y - arrow_size * m.sin(angle + m.pi / 6)

            pygame.draw.polygon(
                surface,
                (255, 200, 100),
                [(arrow_end_x, arrow_end_y), (left_x, left_y), (right_x, right_y)],
            )

    def _draw_square(
        self,
        surface: pygame.Surface,
        x: float,
        y: float,
        size: float,
        color: tuple[int, int, int],
        border_width: int = 1,
    ) -> None:
        """Draw a square tile - filled with color."""
        # Create rectangle for the square
        rect = pygame.Rect(x, y, size, size)

        # Fill the square with the color
        pygame.draw.rect(surface, color, rect)

        # Draw border with darker color
        border_color = tuple(max(0, c - 50) for c in color)
        pygame.draw.rect(surface, border_color, rect, border_width)

    @input_event_bind("exit_button", pygame_gui.UI_BUTTON_PRESSED)
    def on_exit_click(self, msg: pygame.event.Event) -> None:
        self.post(PageNavigationEvent(action_list=[(PageNavigation.CLOSE_TOP, None)]))

    @input_event_bind(SpecialInputScope.GLOBAL, GestureType.CLICK.to_pygame_event())
    def on_click_outside(self, msg: pygame.event.Event) -> None:
        if hasattr(msg, "ui_element"):
            return

        panel = self._element_manager.get_element("inspect_history_panel")

        if panel and hasattr(msg, "pos"):
            click_pos = msg.pos
            panel_rect = panel.spatial_component.get_screen_rect(self.camera)

            if not panel_rect.collidepoint(click_pos):
                self.post(
                    PageNavigationEvent(action_list=[(PageNavigation.CLOSE_TOP, None)])
                )
