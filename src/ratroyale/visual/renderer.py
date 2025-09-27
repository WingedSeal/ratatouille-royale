import pygame
from ratroyale.visual.asset_management.visual_component import VisualComponent
from ratroyale.input.page_management.interactable import Interactable
from pygame_gui.ui_manager import UIManager
from ratroyale.event_tokens.visual_token import *
from ratroyale.backend.tile import Tile
from ratroyale.visual.asset_management.visual_component import TileVisual, EntityVisual
from typing import cast

class PageRenderer:
  def __init__(self, screen_size: tuple[int, int], ui_manager: UIManager) -> None:
    self.canvas: pygame.Surface = pygame.Surface(screen_size, pygame.SRCALPHA)
    self.ui_manager: UIManager = ui_manager
    self.interactable_visuals: dict[Interactable, list[VisualComponent]] = {}
    # TODO: non-interactable visuals (e.g. particles)

  def update(self, dt: float) -> None:
    self.ui_manager.update(dt)

  # TODO: layer order-based drawing
  def draw(self) -> None:
    self.canvas.fill((0,0,0,0))

    for visual_list in self.interactable_visuals.values():
      for visuals in visual_list:
        visuals.render(self.canvas)

    self.render_hitbox()

    self.ui_manager.draw_ui(self.canvas)

  def _register_component(self, interactable: Interactable, visual: list[VisualComponent]) -> None:
    self.interactable_visuals.setdefault(interactable, []).extend(visual)

  def _unregister_component(self, interactable: Interactable) -> None:
    self.interactable_visuals.pop(interactable, None)

  def render_hitbox(self) -> None:
    for interactable in self.interactable_visuals:
        interactable.hitbox.draw(self.canvas)

  def execute_callback(self, tkn: VisualManagerEvent) -> None:
    match tkn:
      case RegisterVisualComponent_VisualManagerEvent(visual_component=vc, interactable=i):
        self._register_component(i, vc)
      case UnregisterVisualComponent_VisualManagerEvent(interactable=i):
        self._unregister_component(i)
      case _:
        print("Unhandled management event")
    pass


# TODO: Revise the draw order to align with the isometric style.
# TODO: implement unit selection & path preview highlight.
# TODO: implement SHOW HITBOX trigger
# FIXME: would it be cleaner for each visual/interactable objects to reference via UUID instead of directly holding obj?
class GameBoardPageRenderer(PageRenderer):
  def __init__(self, screen_size: tuple[int,int], ui_manager: UIManager) -> None:
      super().__init__(screen_size, ui_manager)

      self.tile_visuals: dict[Tile, list[TileVisual]] = {} 

  def execute_callback(self, tkn: VisualManagerEvent) -> None:
    super().execute_callback(tkn)

    match tkn:
      case RegisterVisualComponent_VisualManagerEvent(visual_component=vc, interactable=i):
        pass
      case TileInteraction_VisualManagerEvent(tile=tile, tile_interaction_type=type):
        self._tile_interaction(tile, type)
      case _:
        print("Unhandled management event")

  def _register_component(self, visual_components: list[VisualComponent]) -> None:
    if all(isinstance(v, TileVisual) for v in visual_components):
      self._register_tile_visuals(cast(list[TileVisual], visual_components), cast(TileVisual, visual_components[1]).tile)
    
  def _register_tile_visuals(self, visual_components: list[TileVisual], tile: Tile) -> None:
    self.tile_visuals[tile] = visual_components

  def _tile_interaction(self, tile: Tile, tile_interaction_type: TileInteractionType) -> None:
    match tile_interaction_type:
      case TileInteractionType.HOVER:
        self._hover_tile(tile)
      case TileInteractionType.SELECT:
        self._select_tile(tile)
      case _:
        print("Unhandled tile interaction type")

  def _hover_tile(self, tile: Tile) -> None:
    pass

  def _select_tile(self, tile: Tile) -> None:
    pass
