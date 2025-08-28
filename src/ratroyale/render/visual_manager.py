import pygame
import pygame_gui
from ratroyale.render.input_manager import InputManager
from ratroyale.render.page.page_factory import PageFactory
from ratroyale.render.gesture_interpreter import GestureInterpreter
from ratroyale.render.gui_event_constants import CONSUMED_UI_EVENTS

class VisualManager:
    def __init__(self, screen: pygame.display):
        self.screen = screen
        self.is_hovering_ui = False

        # Helping managers
        self.input_manager = InputManager()
        self.gesture_interpreter = GestureInterpreter()

        # Top-level pygame_gui manager
        self.gui_manager = pygame_gui.UIManager(screen.get_size())

        # Dictionary of pages, each page is a list of UI elements
        self.factory = PageFactory(self.gui_manager, self)
        self.pages = self.factory.create_all_pages()
        self.active_page = None

    def add_page(self, name, elements):
        """Add a page with a list of pygame_gui elements"""
        self.pages[name] = elements

    def set_active_page(self, name):
        """Set the active page by name, hiding the previous one"""
        if self.active_page:
            self.pages[self.active_page].hide()
        self.active_page = name
        self.pages[name].show()

    def handle_events(self):
        """Process events and forward unconsumed ones to GestureInterpreter"""
        events = self.input_manager.update()
        unconsumed_events = []

        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            # Determine if event is consumed by pygame_gui
            event_consumed = self.gui_process_event_and_consume(event)
            if event_consumed:
              self.hovering_ui(event) # Update hovering state

              # Call callbacks for buttons
              if event.type == pygame_gui.UI_BUTTON_PRESSED:
                active_page = self.get_active_page()
                if active_page:
                    callback = active_page.get_callback(event.ui_element)
                    if callback:
                        callback()
                    else:
                        print(f"No callback found for button: {event.ui_element}")

            elif not self.is_hovering_ui:
              unconsumed_events.append(event)

            # Determine if event was consumed by a widget
            # Only forward events that are not in our CONSUMED_UI_EVENTS set

        # Forward remaining events to gestures
        if unconsumed_events:
            self.gesture_interpreter.handle_events(unconsumed_events)

    def update(self, dt):
        """Update UI manager and active page elements"""
        self.gui_manager.update(dt)

    def draw(self):
        """Draw active page elements"""
        self.gui_manager.draw_ui(self.screen)

    def gui_process_event_and_consume(self, event):
      consumed_by_gui = self.gui_manager.process_events(event)
      
      # Additionally consider other GUI events as consumed
      if hasattr(event, 'ui_element') or event.type in CONSUMED_UI_EVENTS:
          return True
      return consumed_by_gui
    
    def hovering_ui(self, event: pygame.event.Event):
        if event.type == pygame_gui.UI_BUTTON_ON_HOVERED:
            self.is_hovering_ui = True
        elif event.type == pygame_gui.UI_BUTTON_ON_UNHOVERED:
            self.is_hovering_ui = False

    def get_active_page(self):
        return self.pages.get(self.active_page)
