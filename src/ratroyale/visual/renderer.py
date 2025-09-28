import pygame
from ratroyale.visual.asset_management.visual_component import VisualComponent
from ratroyale.input.interactables_management.interactable import Interactable
from pygame_gui.ui_manager import UIManager
from ratroyale.event_tokens.visual_token import *
from ratroyale.backend.tile import Tile
from ratroyale.backend.entity import Entity
from ratroyale.visual.asset_management.visual_component import TileVisual, EntityVisual, AbilityMenuVisual
from typing import cast
from ratroyale.backend.hexagon import OddRCoord
from ratroyale.input.interactables_management.interaction_type import InteractionType

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
        print("Unhandled management event on basic renderer")
    pass


# TODO: Revise the draw order to align with the isometric style.
# TODO: implement unit selection & path preview highlight.
# TODO: implement SHOW HITBOX trigger
# FIXME: would it be cleaner for each visual/interactable objects to reference via UUID instead of directly holding obj?
class GameBoardPageRenderer(PageRenderer):
  def __init__(self, screen_size: tuple[int,int], ui_manager: UIManager) -> None:
      super().__init__(screen_size, ui_manager)

      self.tile_visuals: dict[OddRCoord, list[TileVisual]] = {} 
      self.selected_tile: OddRCoord | None = None

      self.entity_visuals: dict[OddRCoord, list[EntityVisual]] = {}
      self.selected_entity: OddRCoord | None = None

      self.ability_menu_visuals_list: list[list[AbilityMenuVisual]] = []

  def execute_callback(self, tkn: VisualManagerEvent) -> None:
    super().execute_callback(tkn)

    match tkn:
      case TileInteraction_VisualManagerEvent(tile=tile, interaction_type=type):
        self._tile_interaction(tile, type)
      case EntityInteraction_VisualManagerEvent(entity=entity, interaction_type=type):
        self._entity_interaction(entity, type)
      case EntityMovementConfirmation_VisualManagerEvent(success=s, error_msg=e, new_coord=c):
        self._move_entity(s, e, c)
      case _:
        print("Unhandled management event")
  
  def draw(self) -> None:
    self.canvas.fill((0,0,0,0))

    for visuals in self.tile_visuals.values():
      for v in visuals:
          v.render(self.canvas, highlighted=(v.tile.coord is self.selected_tile))

    for visuals in self.entity_visuals.values():
      for v in visuals:
          v.render(self.canvas, highlighted=(v.entity.pos is self.selected_entity))

    for visuals in self.ability_menu_visuals_list:
      for v in visuals:
        v.render(self.canvas)

    self.ui_manager.draw_ui(self.canvas)

  def _register_component(self, interactable: Interactable, visual_components: list[VisualComponent]) -> None:
    if all(isinstance(v, TileVisual) for v in visual_components):
      self._register_tile_visuals(cast(list[TileVisual], visual_components), cast(TileVisual, visual_components[0]).tile)
    elif all(isinstance(v, EntityVisual) for v in visual_components):
      self._register_entity_visuals(cast(list[EntityVisual], visual_components), cast(EntityVisual, visual_components[0]).entity)
    elif all(isinstance(v, AbilityMenuVisual) for v in visual_components):
      self._register_ability_menu_visuals(cast(list[AbilityMenuVisual], visual_components))
    
  def _register_tile_visuals(self, visual_components: list[TileVisual], tile: Tile) -> None:
    self.tile_visuals[tile.coord] = visual_components

  def _register_entity_visuals(self, visual_components: list[EntityVisual], entity: Entity) -> None:
    self.entity_visuals[entity.pos] = visual_components

  def _register_ability_menu_visuals(self, visual_components: list[AbilityMenuVisual]) -> None:
    self.ability_menu_visuals_list.append(visual_components)

  def _tile_interaction(self, tile: Tile, tile_interaction_type: InteractionType) -> None:
    match tile_interaction_type:
      case InteractionType.HOVER:
        pass # self._hover_tile(tile)
      case InteractionType.SELECT:
        self._select_tile(tile)
      case _:
        print("Unhandled tile interaction type")

  def _entity_interaction(self, entity: Entity, interaction_type: InteractionType) -> None:
    match interaction_type:
      case InteractionType.HOVER:
        pass
      case InteractionType.SELECT:
        self._select_entity(entity)
      case _:
        print("Unhandled entity interaction type")

  def _select_tile(self, tile: Tile) -> None:
    self.selected_tile = tile.coord if tile.coord is not self.selected_tile and not self.selected_entity else None

  def _select_entity(self, entity: Entity) -> None:
    self.selected_entity = entity.pos if entity.pos is not self.selected_entity else None
    self.selected_tile = None

  def _move_entity(self, success: bool, error_msg: str | None, coord: tuple[float, float] | None):
    if self.selected_entity is not None and coord is not None:
      entity_visuals = self.entity_visuals.get(self.selected_entity)
      if entity_visuals:
        for v in entity_visuals:
          v.moveto(coord)

          self.selected_tile = None
          self.selected_entity = None
