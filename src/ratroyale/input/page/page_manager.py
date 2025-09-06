import pygame
from ratroyale.input.page.page import Page, PageFactory
from ratroyale.coordination_manager import CoordinationManager
from ratroyale.input.constants import PageEventAction
from ratroyale.input.page.page_config import PageName
from ratroyale.input.page.gesture_reader import GestureReader

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
  def pop_page(self):
    if self.page_stack:
      page = self.page_stack.pop()

  """ Switch topmost page for a different one """
  def replace_top(self, page_option: PageName):
    if self.page_stack:
      self.page_stack.pop()
    self.push_page(page_option)

  def get_active_page(self) -> Page | None:
    return self.page_stack[-1] if self.page_stack else None
  
  """ This method propagates gestures downwards through the page stack, until all
      events are consumed, or no pages remain.
      Additionally, this function stops propagating an event if it hits a page 
      with a 'blocking' flag set to true. """
  def handle_events(self):
    raw_events = pygame.event.get()
    gestures = self.gesture_reader.read_events(raw_events)  # converts to List[GestureData]

    # Propagate gestures through the page stack (top-most first)
    for page in reversed(self.page_stack):
        if not gestures:
            break  # nothing left to propagate

        # Let the page handle gestures
        gestures = page.handle_gestures(gestures)

        # Stop propagation if the page is blocking
        if page.blocking:
            break

  def update(self, dt):
    for page in reversed(self.page_stack):
      page.gui_manager.update(dt)

  def draw(self):
    for page in reversed(self.page_stack):
      self.screen.blit(page.canvas, (0, 0))  # draw canvas first
      page.draw_ui()   # then draw UI elements on top

  def execute_callbacks(self):
    while not self.coordination_manager.page_domain_mailbox.empty():
      token = self.coordination_manager.page_domain_mailbox.get()
      page_name = token.page_name
      action = token.action

      match action:
        case PageEventAction.ADD:
          self.push_page(page_name)
        case PageEventAction.REMOVE:
          self.pop_page()
        case PageEventAction.REPLACE_TOP:
          self.replace_top(page_name)