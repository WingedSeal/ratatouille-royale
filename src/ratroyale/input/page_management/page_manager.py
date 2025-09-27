import pygame
from ratroyale.input.page_management.page_creator import Page, GameBoardPage
from ratroyale.coordination_manager import CoordinationManager
from ratroyale.input.page_management.page_config import PageName
from ratroyale.input.gesture_management.gesture_reader import GestureReader
from ratroyale.backend.board import Board
from ratroyale.event_tokens.page_token import *
from ratroyale.event_tokens.visual_token import *
from typing import Callable

class PageManager:
  def __init__(self, screen: pygame.surface.Surface, coordination_manager: CoordinationManager) -> None:
    self.screen = screen
    self.is_hovering_ui = False

    self.coordination_manager = coordination_manager

    self.gesture_reader = GestureReader()
    """Highest level gesture reader. Outputs a gesture to be decorated by the pipeline."""

    self.page_factory = PageFactory(self, self.screen.get_size(), coordination_manager)
    """Dictionary of pages, each page is a list of interactables and visuals"""

    self.page_stack: dict[PageName, Page] = {}
    """Active page stack"""

    self.event_handlers: dict[type[PageManagerEvent], Callable] = {
       StartGameConfirmation_PageManagerEvent: lambda tkn: self.push_game_board_page(tkn.board),
       EndGame_PageManagerEvent: lambda tkn: self.end_game_return_to_menu(),
       PauseGame_PageManagerEvent: lambda tkn: self.pause_game(),
       ResumeGame_PageManagerEvent: lambda tkn: self.resume_game()
    }

  # region Basic Page Management Methods

  def push_page(self, page_name: PageName, page: Page | None = None) -> None:
    """ Push page by name or by the given page object, create if it doesn’t exist yet """
    if self.get_page(page_name):
      return
    else: 
      self.page_stack[page_name] = self.page_factory.create_page(page_name) if not page else page
  
  def pop_page(self, page_name: PageName | None = None) -> None:
    """ Remove topmost page, or first page that matches the given name"""
    if page_name is None:
        self.page_stack.popitem()[1]._unregister_self()
    else:
        self.page_stack.pop(page_name)._unregister_self()
  
  def get_page(self, page_name: PageName) -> Page | None:
    return self.page_stack.get(page_name)

  def replace_top(self, page_option: PageName, page: Page | None) -> None:
    """ Switch topmost page for a different one """
    if self.page_stack:
      self.pop_page()
    self.push_page(page_option, page)

  # endregion

  # region Composite Page Management Methods

  def push_game_board_page(self, board: Board | None) -> None:
     self.replace_top(PageName.GAME_BOARD, self.page_factory.create_game_board_page(board))
     self.push_page(PageName.PAUSE_BUTTON)
     
  def end_game_return_to_menu(self) -> None:
     self.pop_page(PageName.PAUSE_BUTTON)
     self.pop_page(PageName.PAUSE_MENU)
     self.pop_page(PageName.GAME_BOARD)

     self.push_page(PageName.MAIN_MENU)

  def pause_game(self) -> None:
     self.push_page(PageName.PAUSE_MENU)

  def resume_game(self) -> None:
     self.pop_page(PageName.PAUSE_MENU)
  
  # endregion

  # region Event Handling
  
  
  def handle_events(self) -> None:
    """ This method propagates gestures downwards through the page stack, until all
      events are consumed, or no pages remain.
      Additionally, this function stops propagating an event if it hits a page 
      with a 'blocking' flag set to true. """
    raw_events = pygame.event.get()
    gestures = self.gesture_reader.read_events(raw_events) 

    for page in reversed(self.page_stack.values()):
        if not gestures:
            break  

        gestures = page.handle_gestures(gestures)

        if page.blocking:
            break
        
  # endregion

  # region Message Processing

  def execute_callbacks(self) -> None:
    page_event_queue = self.coordination_manager.mailboxes[PageManagerEvent]

    while not page_event_queue.empty():
        token = page_event_queue.get()
        handler = self.event_handlers.get(type(token))
        if handler:
            handler(token)
        else:
            self._delegate(token)

  def _delegate(self, token: PageManagerEvent) -> None:
    page = self.get_page(token.page_name)
    if page:
       page.execute_callback(token)
    else:
       print("No pages to handle this callback")


  # endregion

# ====================================
# region Page Factory 
# ====================================

class PageFactory:
    def __init__(self, page_manager: PageManager, screen_size: tuple[int, int], coordination_manager: CoordinationManager) -> None:
        self.page_manager = page_manager
        self.screen_size = screen_size
        self.coordination_manager = coordination_manager

    # Used for creating non-specialized page classes.
    def create_page(self, page_option: PageName) -> Page:
        return Page(page_option, self.coordination_manager)
    
    def create_game_board_page(self, board: Board | None) -> GameBoardPage:
        return GameBoardPage(self.coordination_manager, board)
    
# endregion