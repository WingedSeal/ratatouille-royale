import pygame
from ratroyale.input.page.page_creator import Page, PageFactory
from ratroyale.coordination_manager import CoordinationManager
from ratroyale.input.page.page_config import PageName
from ratroyale.input.page.gesture_reader import GestureReader
# from ratroyale.visual.dummy_game_objects import DummyTile, DummyEntity, DummyCoord, DummyPos
from ratroyale.backend.board import Board
from ratroyale.event_tokens import *

class PageManager:
  def __init__(self, screen: pygame.surface.Surface, coordination_manager: CoordinationManager):
    self.screen = screen
    self.is_hovering_ui = False

    self.coordination_manager = coordination_manager

    # Highest level gesture reader. Outputs a gesture to be decorated by the pipeline.
    self.gesture_reader = GestureReader()

    # Dictionary of pages, each page is a list of UI elements
    self.page_factory = PageFactory(self, self.screen.get_size(), coordination_manager)

    # Active page stack
    self.page_stack: list[Page] = []

  # region Page Creation & Deletion

  """ Push page by name, create if it doesn’t exist yet """
  def push_page(self, page_option: PageName) -> Page:
    # Check if the page already exists in stack
    for page in self.page_stack:
      if page.name == page_option:
        self.page_stack.append(page)
        return page

    # Otherwise, create it on demand
    page = self.page_factory.create_page(page_option)
    self.page_stack.append(page)
    return page
  
  """ Remove topmost page """
  def pop_page(self, page_option: PageName | None = None):
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

  """ Switch topmost page for a different one """
  def replace_top(self, page_option: PageName):
    if self.page_stack:
      self.page_stack.pop()
    self.push_page(page_option)

  def push_game_board_page(self, board: Board | None):
     self.pop_page(None)

     page = self.page_factory.create_game_board_page(board)
     self.page_stack.append(page)

     self.push_page(PageName.PAUSE_BUTTON)
     
  def end_game_return_to_menu(self):
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
  def handle_events(self):
    raw_events = pygame.event.get()
    gestures = self.gesture_reader.read_events(raw_events)  # converts to List[GestureData]

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

  def update(self, dt):
    for page in self.page_stack:
      page.gui_manager.update(dt)

  def draw(self):
    for page in self.page_stack:
      page.draw()
      self.screen.blit(page.canvas, (0, 0))  # draw canvas first

      page.draw_ui()   # then draw UI elements on top

  # endregion

  # region Message Processing

  def execute_callbacks(self):
    while not self.coordination_manager.page_domain_mailbox.empty():
        token = self.coordination_manager.page_domain_mailbox.get()

        if isinstance(token, AddPageEvent_PageManagerEvent):
          self.push_page(token.page_name)
        elif isinstance(token, RemovePageEvent_PageManagerEvent):
          self.pop_page(getattr(token, "page_name", None))  # remove top if no page_name
        elif isinstance(token, ReplaceTopPage_PageManagerEvent):
          self.replace_top(token.page_name)
        elif isinstance(token, ConfirmStartGame_PageManagerEvent):
          self.push_game_board_page(token.board)
        elif isinstance(token, EndGame_PageManagerEvent):
          self.end_game_return_to_menu()

  # endregion