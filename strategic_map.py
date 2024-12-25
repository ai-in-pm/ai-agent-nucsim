import pygame
import numpy as np
from enum import Enum
from dataclasses import dataclass
from typing import Dict, List, Tuple
import json
from datetime import datetime
import random
import os
from dotenv import load_dotenv
from neural_viz import NeuralActivity, BrainRegion

class Nation(Enum):
    USA = "United States"
    DPRK = "North Korea"
    SOUTH_KOREA = "South Korea"
    JAPAN = "Japan"
    CHINA = "China"
    RUSSIA = "Russia"

class UnitType(Enum):
    CARRIER = "Aircraft Carrier"
    SUBMARINE = "Submarine"
    AIRBASE = "Air Base"
    MISSILE_SITE = "Missile Site"

@dataclass
class MilitaryUnit:
    unit_type: UnitType
    position: Tuple[float, float]
    nation: Nation
    status: str = "active"

class StrategicMap:
    def __init__(self, width: int = 1200, height: int = 800):
        pygame.init()
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)
        pygame.display.set_caption("Nuclear Crisis Simulation")
        
        # Initialize colors
        self.COLORS = {
            'background': (0, 0, 32),  # Dark blue
            'text': (255, 255, 255),   # White
            'usa_blue': (0, 82, 165),  # USA Blue
            'dprk_red': (200, 16, 46), # DPRK Red
            'unit': (255, 255, 0),     # Yellow for units
            'alert': (255, 0, 0, 128), # Semi-transparent red
            'button': (100, 100, 100), # Gray
            'button_hover': (150, 150, 150), # Light gray
            'panel': (47, 79, 79),     # Dark slate gray
        }
        
        # Initialize fonts
        pygame.font.init()
        self.update_fonts()
        
        # Initialize neural visualizations
        self.neural_viz_usa = NeuralActivity(
            width=(self.width - 250 - 250 - 40) // 2,
            height=self.height - 40
        )
        self.neural_viz_dprk = NeuralActivity(
            width=(self.width - 250 - 250 - 40) // 2,
            height=self.height - 40
        )
        
        # Layout constants
        self.PADDING = 10
        self.update_layout()
        
        # Load environment variables
        load_dotenv()
        
        # Initialize other components
        self.military_units = []
        self.alert_zones = []
        self.event_log = []
        self.tension_level = 50
        self.button_states = {
            'pause': False,
            'speed': 1.0
        }
        
        # AI Presidents' states
        self.usa_president = {
            'name': 'Donald Trump',
            'current_action': 'Evaluating situation',
            'next_action': 'Pending',
            'approval': 45,
            'decisions': []
        }
        
        self.dprk_president = {
            'name': 'Kim Jong Un',
            'current_action': 'Monitoring developments',
            'next_action': 'Pending',
            'approval': 100,
            'decisions': []
        }
        
    def update_fonts(self):
        """Update font sizes based on window size"""
        base_size = min(self.width, self.height) // 50
        self.font = pygame.font.SysFont('Arial', base_size)
        self.title_font = pygame.font.SysFont('Arial', int(base_size * 1.5), bold=True)
        self.president_font = pygame.font.SysFont('Arial', int(base_size * 1.2), bold=True)
        
    def update_layout(self):
        """Update layout dimensions based on window size"""
        # Padding and minimum sizes
        self.PADDING = 10
        min_panel_width = 250
        
        # Left panel (Event log)
        self.left_panel_width = max(min_panel_width, self.width // 4)
        
        # Right panel (AI Presidents)
        self.right_panel_width = max(min_panel_width, self.width // 4)
        
        # Neural network visualization areas
        neural_width = (self.width - self.left_panel_width - self.right_panel_width - self.PADDING * 4) // 2
        neural_height = self.height - self.PADDING * 2
        
        self.neural_areas = {
            'usa': {
                'x': self.left_panel_width + self.PADDING,
                'y': self.PADDING,
                'width': neural_width,
                'height': neural_height
            },
            'dprk': {
                'x': self.left_panel_width + neural_width + self.PADDING * 2,
                'y': self.PADDING,
                'width': neural_width,
                'height': neural_height
            }
        }
        
        # Update neural visualizations
        self.neural_viz_usa = NeuralActivity(neural_width, neural_height)
        self.neural_viz_dprk = NeuralActivity(neural_width, neural_height)
        
        # President panels positioning
        self.president_panel = {
            'width': self.right_panel_width - (self.PADDING * 2),
            'height': 200,
            'x': self.width - self.right_panel_width + self.PADDING,
            'spacing': 20  # Space between president panels
        }
        
        # Control buttons
        button_width = min(100, self.right_panel_width - self.PADDING * 2)
        button_height = 30
        button_x = self.width - self.right_panel_width + self.PADDING
        
        self.buttons = {
            'pause': pygame.Rect(button_x, self.height - (button_height + self.PADDING) * 3,
                               button_width, button_height),
            'speed_up': pygame.Rect(button_x, self.height - (button_height + self.PADDING) * 2,
                                  button_width, button_height),
            'speed_down': pygame.Rect(button_x, self.height - (button_height + self.PADDING),
                                    button_width, button_height)
        }
        
    def draw_military_unit(self, unit: MilitaryUnit, position: Tuple[float, float]):
        """Draw a military unit icon"""
        x, y = position
        pygame.draw.circle(self.screen, self.COLORS['unit'], (int(x), int(y)), 5)
        text = self.font.render(unit.unit_type.value, True, self.COLORS['text'])
        self.screen.blit(text, (int(x) + 10, int(y) - 10))
        
    def draw_alert_zone(self, alert: dict):
        """Draw an alert zone"""
        pos = alert['position']
        pygame.draw.circle(self.screen, self.COLORS['alert'], 
                         (int(pos[0]), int(pos[1])), 
                         int(alert['radius']), 1)
        
    def draw_event_log(self):
        """Draw the event log panel"""
        # Draw event log background
        log_rect = pygame.Rect(self.PADDING, self.PADDING,
                             self.left_panel_width - (self.PADDING * 2),
                             self.height - (self.PADDING * 2))
        pygame.draw.rect(self.screen, self.COLORS['panel'], log_rect)
        
        # Draw title
        text = self.title_font.render("Event Log", True, self.COLORS['text'])
        self.screen.blit(text, (self.PADDING * 2, self.PADDING * 2))
        
        # Draw events
        y_offset = self.PADDING * 4
        for event in self.event_log[-10:]:  # Show last 10 events
            text = self.font.render(event, True, self.COLORS['text'])
            text_rect = text.get_rect()
            
            # Word wrap if text is too long
            if text_rect.width > self.left_panel_width - (self.PADDING * 4):
                words = event.split()
                lines = []
                current_line = []
                
                for word in words:
                    test_line = ' '.join(current_line + [word])
                    test_text = self.font.render(test_line, True, self.COLORS['text'])
                    if test_text.get_rect().width <= self.left_panel_width - (self.PADDING * 4):
                        current_line.append(word)
                    else:
                        lines.append(' '.join(current_line))
                        current_line = [word]
                
                if current_line:
                    lines.append(' '.join(current_line))
                
                for line in lines:
                    text = self.font.render(line, True, self.COLORS['text'])
                    self.screen.blit(text, (self.PADDING * 2, y_offset))
                    y_offset += 20
            else:
                self.screen.blit(text, (self.PADDING * 2, y_offset))
                y_offset += 20

    def draw_president_panel(self, president, y_offset, color):
        """Draw an AI President panel"""
        x = self.president_panel['x']
        width = self.president_panel['width']
        height = self.president_panel['height']
        
        # Draw panel background
        panel_rect = pygame.Rect(x, y_offset, width, height)
        pygame.draw.rect(self.screen, self.COLORS['panel'], panel_rect)
        
        # Draw header
        header_rect = pygame.Rect(x, y_offset, width, 30)
        pygame.draw.rect(self.screen, color, header_rect)
        
        # Draw president name
        name_text = self.title_font.render(president['name'], True, self.COLORS['text'])
        self.screen.blit(name_text, (x + 5, y_offset + 5))
        
        # Draw approval rating
        y_pos = y_offset + 35
        approval_text = self.font.render(f"Approval: {president['approval']}%", 
                                       True, self.COLORS['text'])
        self.screen.blit(approval_text, (x + 5, y_pos))
        
        # Draw current action
        y_pos += 25
        current_text = self.font.render(f"Current: {president['current_action']}", 
                                      True, self.COLORS['text'])
        self.screen.blit(current_text, (x + 5, y_pos))
        
        # Draw next action
        y_pos += 25
        next_text = self.font.render(f"Next: {president['next_action']}", 
                                   True, self.COLORS['text'])
        self.screen.blit(next_text, (x + 5, y_pos))
        
        # Draw recent decisions
        y_pos += 25
        decisions_text = self.font.render("Recent Decisions:", True, self.COLORS['text'])
        self.screen.blit(decisions_text, (x + 5, y_pos))
        
        for decision in president['decisions'][-3:]:  # Show last 3 decisions
            y_pos += 20
            text = self.font.render(f"- {decision}", True, self.COLORS['text'])
            self.screen.blit(text, (x + 5, y_pos))

    def draw_control_panel(self):
        """Draw simulation control buttons"""
        for button_name, button_rect in self.buttons.items():
            color = self.COLORS['button_hover'] if button_rect.collidepoint(pygame.mouse.get_pos()) else self.COLORS['button']
            pygame.draw.rect(self.screen, color, button_rect)
            text = self.font.render(button_name.replace('_', ' ').title(), True, self.COLORS['text'])
            text_rect = text.get_rect(center=button_rect.center)
            self.screen.blit(text, text_rect)
            
    def add_military_unit(self, unit: MilitaryUnit):
        """Add a new military unit to the map"""
        self.military_units.append(unit)
        self.log_event(f"{unit.nation.value} deployed {unit.unit_type.value}")
        
    def create_alert_zone(self, position: Tuple[float, float], radius: float, severity: str):
        """Create a new alert zone on the map"""
        self.alert_zones.append({
            "position": position,
            "radius": radius,
            "severity": severity,
            "timestamp": datetime.now()
        })
        
    def log_event(self, event: str):
        """Add an event to the log with timestamp"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.event_log.append(f"[{timestamp}] {event}")
        
    def handle_input(self):
        """Handle user input and interface interactions"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.VIDEORESIZE:
                self.width, self.height = event.size
                self.screen = pygame.display.set_mode((self.width, self.height), pygame.RESIZABLE)
                self.update_fonts()
                self.update_layout()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    pos = pygame.mouse.get_pos()
                    for name, rect in self.buttons.items():
                        if rect.collidepoint(pos):
                            self.handle_button_click(name)
            else:
                self.handle_event(event)
        return True
        
    def handle_event(self, event):
        """Handle pygame events"""
        if event.type == pygame.QUIT:
            return False
            
        elif event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP, pygame.MOUSEMOTION):
            # Pass mouse events to neural visualizations with correct offsets
            usa_offset = (self.neural_areas['usa']['x'], self.neural_areas['usa']['y'])
            dprk_offset = (self.neural_areas['dprk']['x'], self.neural_areas['dprk']['y'])
            
            # Check if mouse is in USA neural area
            if (self.neural_areas['usa']['x'] <= event.pos[0] <= 
                self.neural_areas['usa']['x'] + self.neural_areas['usa']['width'] and
                self.neural_areas['usa']['y'] <= event.pos[1] <= 
                self.neural_areas['usa']['y'] + self.neural_areas['usa']['height']):
                self.neural_viz_usa.handle_event(event, usa_offset[0], usa_offset[1])
                
            # Check if mouse is in DPRK neural area
            elif (self.neural_areas['dprk']['x'] <= event.pos[0] <= 
                  self.neural_areas['dprk']['x'] + self.neural_areas['dprk']['width'] and
                  self.neural_areas['dprk']['y'] <= event.pos[1] <= 
                  self.neural_areas['dprk']['y'] + self.neural_areas['dprk']['height']):
                self.neural_viz_dprk.handle_event(event, dprk_offset[0], dprk_offset[1])
            
        elif event.type == pygame.VIDEORESIZE:
            self.width = event.w
            self.height = event.h
            self.screen = pygame.display.set_mode((self.width, self.height), pygame.RESIZABLE)
            self.update_layout()
            
        return True
        
    def handle_button_click(self, button_name: str):
        """Handle button clicks"""
        if button_name == 'pause':
            self.button_states['pause'] = not self.button_states['pause']
        elif button_name == 'speed_up':
            self.button_states['speed'] = min(2.0, self.button_states['speed'] + 0.25)
        elif button_name == 'speed_down':
            self.button_states['speed'] = max(0.25, self.button_states['speed'] - 0.25)
            
    def update(self):
        """Update the simulation state"""
        if self.button_states['pause']:
            return
            
        # Update simulation at current speed
        speed = self.button_states['speed']
        
        # Simulate AI President decisions
        if random.random() < 0.02 * speed:  # Random chance for new decisions
            self.update_president_decisions()
            
    def update_president_decisions(self):
        """Update AI Presidents' decisions and actions"""
        # Simulate USA President decision
        if random.random() < 0.5:
            action = random.choice([
                "Consulting with military advisors",
                "Calling emergency security meeting",
                "Reviewing intelligence reports",
                "Coordinating with allies",
                "Preparing diplomatic response"
            ])
            self.usa_president['current_action'] = action
            self.usa_president['decisions'].append(action)
            if len(self.usa_president['decisions']) > 5:
                self.usa_president['decisions'].pop(0)
                
        # Simulate DPRK President decision
        if random.random() < 0.5:
            action = random.choice([
                "Meeting with military command",
                "Inspecting missile facilities",
                "Issuing diplomatic statement",
                "Conducting military exercises",
                "Monitoring US movements"
            ])
            self.dprk_president['current_action'] = action
            self.dprk_president['decisions'].append(action)
            if len(self.dprk_president['decisions']) > 5:
                self.dprk_president['decisions'].pop(0)

    def render(self):
        """Render the current state of the simulation"""
        # Clear screen
        self.screen.fill(self.COLORS['background'])
        
        # Draw neural network visualizations
        usa_decision = "diplomatic" if self.usa_president['approval'] > 50 else "aggressive"
        dprk_decision = "aggressive" if self.dprk_president['approval'] > 50 else "defensive"
        
        # Calculate stress levels based on tension
        usa_stress = self.tension_level / 100.0
        dprk_stress = min(1.0, self.tension_level / 80.0)  # DPRK gets stressed faster
        
        # Render USA neural network
        usa_surface = self.neural_viz_usa.render(usa_stress, usa_decision)
        self.screen.blit(usa_surface, 
                        (self.neural_areas['usa']['x'],
                         self.neural_areas['usa']['y']))
        
        # Render DPRK neural network
        dprk_surface = self.neural_viz_dprk.render(dprk_stress, dprk_decision)
        self.screen.blit(dprk_surface,
                        (self.neural_areas['dprk']['x'],
                         self.neural_areas['dprk']['y']))
        
        # Draw labels for neural networks
        usa_label = self.title_font.render("USA Neural Activity", True, self.COLORS['text'])
        dprk_label = self.title_font.render("DPRK Neural Activity", True, self.COLORS['text'])
        
        self.screen.blit(usa_label, 
                        (self.neural_areas['usa']['x'], 
                         self.neural_areas['usa']['y'] - 30))
        self.screen.blit(dprk_label,
                        (self.neural_areas['dprk']['x'],
                         self.neural_areas['dprk']['y'] - 30))
        
        # Draw event log panel
        self.draw_event_log()
        
        # Draw AI President panels with proper spacing
        first_panel_y = self.PADDING
        second_panel_y = first_panel_y + self.president_panel['height'] + self.president_panel['spacing']
        
        self.draw_president_panel(self.usa_president, first_panel_y, self.COLORS['usa_blue'])
        self.draw_president_panel(self.dprk_president, second_panel_y, self.COLORS['dprk_red'])
        
        # Draw control buttons
        self.draw_control_panel()
        
        # Update display
        pygame.display.flip()
        
if __name__ == "__main__":
    strategic_map = StrategicMap()
    running = True
    
    # Add some initial units
    strategic_map.add_military_unit(
        MilitaryUnit(UnitType.CARRIER, (150, 320), Nation.USA)
    )
    strategic_map.add_military_unit(
        MilitaryUnit(UnitType.SUBMARINE, (820, 220), Nation.DPRK)
    )
    strategic_map.add_military_unit(
        MilitaryUnit(UnitType.AIRBASE, (880, 250), Nation.JAPAN)
    )
    
    # Add some initial events
    strategic_map.log_event("US Carrier Group deployed to Pacific")
    strategic_map.log_event("DPRK submarine activity detected")
    strategic_map.log_event("Japan increases air defense readiness")
    
    # Add an initial alert zone
    strategic_map.create_alert_zone((820, 220), 30, "high")
    
    clock = pygame.time.Clock()
    
    while running:
        running = strategic_map.handle_input()
        strategic_map.update()
        strategic_map.render()
        clock.tick(60)  # Limit to 60 FPS
        
    pygame.quit()
