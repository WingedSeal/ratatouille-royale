from ratroyale.coordination_manager import CoordinationManager
from ratroyale.event_tokens.input_token import InputManagerEvent
from ratroyale.event_tokens.visual_token import *
from ratroyale.event_tokens.page_token import *
from ratroyale.event_tokens.game_token import *
from ratroyale.event_tokens.game_action import GameAction

from ratroyale.frontend.gesture.gesture_data import GestureType, to_event

from ..page_managers.base_page import Page
from ratroyale.frontend.pages.page_managers.event_binder import input_event_bind, callback_event_bind
from ratroyale.frontend.pages.page_managers.page_registry import register_page
from ratroyale.frontend.pages.page_managers.backend_adapter import get_name_from_entity, get_name_from_tile

from ratroyale.frontend.pages.page_elements.element_builder import ElementConfig, ElementType, ParentIdentity

from ratroyale.backend.board import Board
from ratroyale.backend.tile import Tile
from ratroyale.backend.entity import Entity

from ratroyale.frontend.visual.asset_management.sprite_registry import TYPICAL_TILE_SIZE

@register_page
class GameBoard(Page):
  def __init__(self, coordination_manager: CoordinationManager) -> None:
    super().__init__(coordination_manager)
    self.setup_elements([])

    self.selected_element_id: tuple[ElementType, str] | None = None
    self.ability_menu_elements_id: list[str] = []
    self.board: Board | None = None

  def on_create(self) -> None:
    self.coordination_manager.put_message(GameManagerEvent(
        game_action=GameAction.START_GAME
    ))

  # region Input Bindings

  @callback_event_bind(GameAction.START_GAME)
  def _start_game(self, msg: PageCallbackEvent[Board]) -> None:
    """Handle the response from starting a game."""
    print("GameBoard received START_GAME response")
    if msg.success and msg.payload:
      self.board = msg.payload
      element_configs: list[ElementConfig] = []
      tiles = self.board.tiles
      entities = self.board.cache.entities

      for tile_list in tiles:
        for tile in tile_list:
          if tile:
            tile_element = ElementConfig[Tile](
              element_type=ElementType.TILE,
              id=get_name_from_tile(tile),
              rect=self._define_tile_rect(tile),
              payload=tile
            )
            element_configs.append(tile_element)
      
      for entity in entities:
        entity_element = ElementConfig(
          element_type=ElementType.ENTITY,
          id=get_name_from_entity(entity),
          rect=self._define_entity_rect(entity),
          payload=entity,
          z_order=1  # Ensure entities are rendered above tiles
        )
        element_configs.append(entity_element)

      self.setup_elements(element_configs)
    else:
      raise RuntimeError(f"Failed to start game: {msg.error_msg}")
    
  @input_event_bind("tile", to_event(GestureType.CLICK))
  @input_event_bind("tile", to_event(GestureType.DOUBLE_CLICK))
  @input_event_bind("tile", to_event(GestureType.HOLD))
  def _on_tile_click(self, msg: InputManagerEvent[Tile]) -> None:
    self._select_element(ElementType.TILE, msg.element_id)
    self._close_ability_menu()

  @input_event_bind("entity", to_event(GestureType.CLICK))
  @input_event_bind("entity", to_event(GestureType.DOUBLE_CLICK))
  def _on_entity_click(self, msg: InputManagerEvent[Entity]) -> None:
    self._select_element(ElementType.ENTITY, msg.element_id)
    self._close_ability_menu()

  @input_event_bind("entity", to_event(GestureType.HOLD))
  def _display_ability_menu(self, msg: InputManagerEvent[Entity]) -> None:
    """Display the ability menu for the selected entity."""
    entity = msg.payload
    if not entity:
        return

    self._select_element(ElementType.ENTITY, msg.element_id)

    ability_menu_elements = []
    self.ability_menu_elements_id = []

    for i, skill in enumerate(entity.skills):
        element_id = f"ability_{i}_from_{msg.element_id}"
        self.ability_menu_elements_id.append(element_id)
        ability_menu_elements.append(
            ElementConfig(
                element_type=ElementType.BUTTON,
                id=element_id,
                rect=(0, 0, 150, 20),
                text=skill.name,
                z_order=2,
                parent_identity=ParentIdentity(
                  parent_id=msg.element_id,
                  parent_type=ElementType.ENTITY,
                  offset=(50, i * 20)
                )
            )
        )

    self.setup_elements(ability_menu_elements)
    self._select_element(ElementType.ENTITY, msg.element_id, False)

  @input_event_bind("ability", to_event(GestureType.CLICK))
  def _activate_ability(self, msg: InputManagerEvent) -> None:
    """ Activate selected ability. """
    print(f"Activated ability: {msg.element_id}")
    self._close_ability_menu()
    self._select_element(ElementType.ENTITY, msg.element_id)

  # endregion

  # region Utilities

  def _close_ability_menu(self) -> None:
    """Close the ability menu if open."""
    for ability_menu_element in self.ability_menu_elements_id:
      self._element_manager.remove_element(ElementType.BUTTON, ability_menu_element)

  def _select_element(self, element_type: ElementType, element_id: str, toggle: bool = True) -> None:
    """
    Handles single-selection logic for both tiles and entities.
    Only one element can be selected at a time.
    """
    # Un-highlight previous selection
    if self.selected_element_id:
        prev_type, prev_id = self.selected_element_id
        prev_element = self.get_element(prev_type, prev_id)
        if prev_element and prev_element.visual:
            prev_element.visual.set_highlighted(False)

    # Deselect if same element clicked
    if self.selected_element_id == (element_type, element_id) and toggle:
        self.selected_element_id = None
        return

    # Highlight new element
    element = self.get_element(element_type, element_id)
    if element and element.visual:
        element.visual.set_highlighted(True)

    # Update selection
    self.selected_element_id = (element_type, element_id)

  # TODO: could be moved to elsewhere
  def _define_tile_rect(self, tile: Tile) -> tuple[float, float, float, float]:
    """Given a Tile, return its bounding rectangle as (x, y, width, height)."""
    pixel_x, pixel_y = tile.coord.to_pixel(*TYPICAL_TILE_SIZE, is_bounding_box=True)
    width, height = TYPICAL_TILE_SIZE
    return (pixel_x, pixel_y, width, height)
  
  def _define_entity_rect(self, entity: Entity) -> tuple[float, float, float, float]:
    """Given an Entity, return its bounding rectangle as (x, y, width, height)."""
    pixel_x, pixel_y = entity.pos.to_pixel(*TYPICAL_TILE_SIZE, is_bounding_box=True)
    width, height = (40, 40)  # Placeholder size for entity
    return (pixel_x, pixel_y, width, height)
  
  # endregion