import pygame
from ratroyale.input.page.page_creator import Page, GameBoardPage
from ratroyale.coordination_manager import CoordinationManager
from ratroyale.input.page.page_config import PageName
from ratroyale.input.page.gesture_reader import GestureReader
from ratroyale.backend.board import Board
from ratroyale.event_tokens.page_token import *

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

  # region basic Page Management Methods

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
  
  # endregion

  # region Event Handling
  
  """ This method propagates gestures downwards through the page stack, until all
      events are consumed, or no pages remain.
      Additionally, this function stops propagating an event if it hits a page 
      with a 'blocking' flag set to true. """
  def handle_events(self) -> None:
    raw_events = pygame.event.get()
    gestures = self.gesture_reader.read_events(raw_events)  # converts to list[GestureData]

    if gestures:
       for gesture in gestures:
          print(gesture.gesture_key)

    # Propagate gestures through the page stack (top-most first)
    for page in reversed(self.page_stack):
        if not gestures:
            break  # nothing left to propagate

        # Let the page handle gestures
        gestures = page.handle_gestures(gestures)

        # Stop propagation if the page is blocking
        if page.blocking:
            break
        
  # endregion

  # region Drawing

  def update(self, dt: float) -> None:
    for page in self.page_stack:
      page.gui_manager.update(dt)

  def draw(self) -> None:
    for page in self.page_stack:
      page.draw()
      self.screen.blit(page.canvas, (0, 0))  

      page.draw_ui()   

  # endregion

  # region Message Processing

  def execute_callbacks(self) -> None:
    page_event_queue = self.coordination_manager.mailboxes[PageManagerEvent]

    while not page_event_queue.empty():
        token = page_event_queue.get()

        match token:
            case AddPageEvent_PageManagerEvent(page_name=page_name):
                self.push_page(page_name)
            case RemovePageEvent_PageManagerEvent(page_name=page_name):
                self.pop_page(page_name)
            case ReplaceTopPage_PageManagerEvent(page_name=page_name):
                self.replace_top(page_name)
            case ConfirmStartGame_PageManagerEvent(board=board):
                self.push_game_board_page(board)
            case EndGame_PageManagerEvent():
                self.end_game_return_to_menu()

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