import pygame
from ratroyale.input.page_management.page_creator import Page, GameBoardPage
from ratroyale.coordination_manager import CoordinationManager
from ratroyale.input.page_management.page_config import PageName
from ratroyale.input.gesture_management.gesture_reader import GestureReader
from ratroyale.backend.board import Board
from ratroyale.event_tokens.page_token import *
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

    self.page_stack: list[Page] = []
    """Active page stack"""

    self.event_handlers: dict[type[PageManagerEvent], Callable] = {
       ConfirmStartGame_PageManagerEvent: lambda tkn: self.push_game_board_page(tkn.board),
       EndGame_PageManagerEvent: lambda tkn: self.end_game_return_to_menu(),
       PauseGame_PageManagerEvent: lambda tkn: self.pause_game(),
       ResumeGame_PageManagerEvent: lambda tkn: self.resume_game()
    }

  # region Basic Page Management Methods

  def push_page(self, page_option: PageName) -> Page:
    """ Push page by name, create if it doesn’t exist yet """
    # Check if the page already exists in stack
    for page in self.page_stack:
      if page.name == page_option:
        self.page_stack.append(page)
        return page

    # Otherwise, create it on demand
    page = self.page_factory.create_page(page_option)
    self.page_stack.append(page)
    return page
  
  def pop_page(self, page_option: PageName | None = None) -> None:
    """ Remove topmost page """
    if not self.page_stack:
        return  # nothing to remove

    if page_option is None:
        # Remove the topmost page
        self.page_stack.pop()
    else:
        # Remove the first page that matches the name
        for i, page in enumerate(self.page_stack):
            if page.name == page_option:
                self.page_stack.pop(i)
                break

  def replace_top(self, page_option: PageName) -> None:
    """ Switch topmost page for a different one """
    if self.page_stack:
      self.page_stack.pop()
    self.push_page(page_option)

  # endregion

  # region Composite Page Management Methods

  def push_game_board_page(self, board: Board | None) -> None:
     self.pop_page(None)

     page = self.page_factory.create_game_board_page(board)
     self.page_stack.append(page)

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

    if gestures:
       for gesture in gestures:
          print(gesture.gesture_key)

    for page in reversed(self.page_stack):
        if not gestures:
            break  

        gestures = page.handle_gestures(gestures)

        if page.blocking:
            break
        
  # endregion

  # region Drawing

  # def update(self, dt: float) -> None:
  #   for page in self.page_stack:
  #     page.gui_manager.update(dt)

  # def draw(self) -> None:
  #   for page in self.page_stack:
  #     page.draw()
  #     self.screen.blit(page.canvas, (0, 0))  

  #     page.draw_ui()   

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
            print(f"Unhandled page manager event: {token}")


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
        return Page(page_option, self.screen_size, self.coordination_manager)
    
    def create_game_board_page(self, board: Board | None) -> GameBoardPage:
        return GameBoardPage(self.screen_size, self.coordination_manager, board)
    
# endregion