from .page_config import PageConfig
from ratroyale.event_tokens.input_token import InputManagerEvent
from ratroyale.coordination_manager import CoordinationManager
from ratroyale.input.page_management.page_name import PageName
from ratroyale.input.interactables_management.interactable import Interactable, TileInteractable, EntityInteractable, AbilityMenuInteractable
from ratroyale.visual.asset_management.visual_component import VisualComponent
from ratroyale.backend.tile import Tile
from ratroyale.backend.board import Board
from ratroyale.backend.hexagon import OddRCoord
from ratroyale.event_tokens.visual_token import *
from ratroyale.event_tokens.page_token import *
from ratroyale.event_tokens.game_token import *
from ratroyale.visual.screen_constants import SCREEN_SIZE
from .base_page import Page

class PauseButton(Page):
  def __init__(self):
    pass