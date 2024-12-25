import pygame
import numpy as np
from enum import Enum
import math
import random
from typing import Dict, List, Tuple, Optional
import pygame.mixer

class BrainRegion(Enum):
    AMYGDALA = ("Amygdala", "Fear & Threat", "Emotional processing and threat response")
    PREFRONTAL = ("Prefrontal Cortex", "Decision", "Strategic planning and control")
    HIPPOCAMPUS = ("Hippocampus", "Memory", "Experience and context processing")
    ANTERIOR = ("Anterior Cingulate", "Conflict", "Error detection and correction")
    INSULA = ("Insula", "Risk", "Risk and consequence evaluation")
    STRIATUM = ("Striatum", "Reward", "Action selection and motivation")
    THALAMUS = ("Thalamus", "Processing", "Information filtering and relay")
    HYPOTHALAMUS = ("Hypothalamus", "Stress", "Stress response and regulation")

class VisualizationMode(Enum):
    CIRCULAR = "Circular Layout"
    HIERARCHICAL = "Hierarchical Layout"
    CLUSTERED = "Clustered Layout"
    FORCE_DIRECTED = "Force-Directed Layout"

class SoundEffects:
    def __init__(self):
        self.enabled = False
        try:
            pygame.mixer.init()
            self.sounds = {}
            sound_files = {
                'click': 'sounds/click.wav',
                'hover': 'sounds/hover.wav',
                'connect': 'sounds/connect.wav',
                'alert': 'sounds/alert.wav'
            }
            
            # Try to load sounds, skip if files don't exist
            for name, path in sound_files.items():
                try:
                    self.sounds[name] = pygame.mixer.Sound(path)
                except FileNotFoundError:
                    pass  # Skip missing sound files
                    
            self.enabled = len(self.sounds) > 0
        except Exception:
            # Fallback if sound initialization fails
            self.sounds = {}
            self.enabled = False
        
    def play(self, sound_name: str, volume: float = 0.5):
        if self.enabled and sound_name in self.sounds:
            self.sounds[sound_name].set_volume(volume)
            self.sounds[sound_name].play()

class NeuralActivity:
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.surface = pygame.Surface((width, height), pygame.SRCALPHA)
        self.visualization_mode = VisualizationMode.CIRCULAR
        
        # Initialize sound effects
        self.sounds = SoundEffects()
        
        # Layout configurations
        self.layouts = {
            VisualizationMode.CIRCULAR: {
                BrainRegion.AMYGDALA: (0.5, 0.4),  # Moved up
                BrainRegion.PREFRONTAL: (0.5, 0.15),  # Higher up
                BrainRegion.HIPPOCAMPUS: (0.25, 0.4),  # Adjusted left
                BrainRegion.ANTERIOR: (0.75, 0.4),  # Adjusted right
                BrainRegion.INSULA: (0.5, 0.65),  # Lower
                BrainRegion.STRIATUM: (0.3, 0.25),  # Upper left
                BrainRegion.THALAMUS: (0.7, 0.25),  # Upper right
                BrainRegion.HYPOTHALAMUS: (0.5, 0.85)  # Bottom
            },
            VisualizationMode.HIERARCHICAL: {
                BrainRegion.PREFRONTAL: (0.5, 0.15),  # Top
                BrainRegion.ANTERIOR: (0.3, 0.35),
                BrainRegion.THALAMUS: (0.7, 0.35),
                BrainRegion.AMYGDALA: (0.2, 0.55),
                BrainRegion.INSULA: (0.5, 0.55),
                BrainRegion.HIPPOCAMPUS: (0.8, 0.55),
                BrainRegion.HYPOTHALAMUS: (0.3, 0.75),
                BrainRegion.STRIATUM: (0.7, 0.75)
            }
        }
        
        # Add other layouts...
        
        self.current_layout = self.layouts[self.visualization_mode]
        
        # Colors with alpha channel support
        self.COLORS = {
            'background': (10, 10, 30, 255),
            'inactive': (40, 40, 60, 255),
            'low': (60, 100, 200, 255),
            'medium': (200, 60, 60, 255),
            'high': (255, 60, 60, 255),
            'text': (255, 255, 255, 255),
            'connection': (100, 100, 140, 50),
            'selected': (255, 255, 0, 255),
            'hover': (200, 200, 100, 255),
            'pulse': (255, 255, 255, 0),
            'tooltip_bg': (0, 0, 0, 180),
            'graph_bg': (30, 30, 50, 200)
        }
        
        # Initialize brain regions with animation states
        self.regions = {region: {
            'pos': self.current_layout[region],
            'target_pos': self.current_layout[region],
            'size': 30,  # Reduced base size
            'activation': 0.0,
            'velocity': (0, 0),
            'history': [(0.0, 0)] * 50,
            'pulse_phase': 0.0,
            'scale': 1.0,
            'tooltip_alpha': 0,
            'highlight': 0.0
        } for region in BrainRegion}
        
        # Neural connections with reduced set for clarity
        self.connections = [
            (BrainRegion.AMYGDALA, BrainRegion.PREFRONTAL),
            (BrainRegion.PREFRONTAL, BrainRegion.ANTERIOR),
            (BrainRegion.ANTERIOR, BrainRegion.INSULA),
            (BrainRegion.INSULA, BrainRegion.HYPOTHALAMUS),
            (BrainRegion.HYPOTHALAMUS, BrainRegion.AMYGDALA),
            (BrainRegion.THALAMUS, BrainRegion.PREFRONTAL)
        ]
        
        # Animation timing
        self.current_time = pygame.time.get_ticks()
        self.last_update = self.current_time
        
        # Interactive state
        self.selected_region = None
        self.hovered_region = None
        self.dragging = False
        self.show_details = False
        self.last_clicked_region = None
        self.last_click_time = 0
        self.offset_x = 0
        self.offset_y = 0
        
        # Fonts
        self.font = pygame.font.Font(None, 18)  # Smaller font
        self.detail_font = pygame.font.Font(None, 16)
        
    def cycle_visualization_mode(self):
        """Cycle through different visualization layouts"""
        modes = list(VisualizationMode)
        current_index = modes.index(self.visualization_mode)
        next_index = (current_index + 1) % len(modes)
        self.visualization_mode = modes[next_index]
        self.current_layout = self.layouts[self.visualization_mode]
        
        # Animate transition to new layout
        for region in self.regions:
            self.regions[region]['target_pos'] = self.current_layout[region]
        
        self.sounds.play('connect')
        
    def update_physics(self, dt: float):
        """Enhanced physics simulation"""
        spring_constant = 0.8
        damping = 0.7
        
        for region, data in self.regions.items():
            if region != self.selected_region:
                # Spring force towards target position
                target_x, target_y = data['target_pos']
                current_x, current_y = data['pos']
                
                dx = target_x - current_x
                dy = target_y - current_y
                
                # Apply spring force
                force_x = dx * spring_constant
                force_y = dy * spring_constant
                
                # Update velocity
                vx, vy = data['velocity']
                vx = (vx + force_x * dt) * damping
                vy = (vy + force_y * dt) * damping
                
                # Update position
                new_x = current_x + vx * dt
                new_y = current_y + vy * dt
                
                # Boundary collision with bounce
                if new_x < 0.1 or new_x > 0.9:
                    vx *= -0.5
                    new_x = max(0.1, min(0.9, new_x))
                
                if new_y < 0.1 or new_y > 0.9:
                    vy *= -0.5
                    new_y = max(0.1, min(0.9, new_y))
                
                data['velocity'] = (vx, vy)
                data['pos'] = (new_x, new_y)
                
                # Update animations
                data['pulse_phase'] = (data['pulse_phase'] + dt * 2) % (2 * math.pi)
                data['scale'] += (1.0 + data['activation'] * 0.2 - data['scale']) * dt * 5
                
                # Smooth tooltip fade
                if region == self.hovered_region:
                    data['tooltip_alpha'] = min(255, data['tooltip_alpha'] + dt * 510)
                else:
                    data['tooltip_alpha'] = max(0, data['tooltip_alpha'] - dt * 510)
    
    def draw_connection_flow(self, start: Tuple[int, int], end: Tuple[int, int],
                           activation: float, phase: float):
        """Draw animated connection with particle flow"""
        dx = end[0] - start[0]
        dy = end[1] - start[1]
        length = math.sqrt(dx * dx + dy * dy)
        
        # Base connection
        color = (*self.COLORS['connection'][:3], 
                int(128 * activation))
        pygame.draw.line(self.surface, color, start, end, 
                        max(1, int(activation * 2)))
        
        # Particle flow
        num_particles = int(length / 30 * (activation + 0.5))
        for i in range(num_particles):
            pos = ((i + phase) % num_particles) / num_particles
            x = start[0] + dx * pos
            y = start[1] + dy * pos
            
            size = max(1, int(activation * 3))
            alpha = int(255 * (0.5 + 0.5 * math.sin(pos * math.pi * 2)))
            color = (*self.COLORS['high'][:3], alpha)
            
            pygame.draw.circle(self.surface, color, (int(x), int(y)), size)
    
    def draw_detailed_view(self):
        """Draw detailed information panel"""
        if self.show_details and self.hovered_region:
            panel_width = 180  # Slightly narrower
            panel_height = 120  # Slightly shorter
            padding = 8  # Reduced padding
            
            # Create panel surface
            panel = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
            pygame.draw.rect(panel, self.COLORS['tooltip_bg'],
                           (0, 0, panel_width, panel_height), border_radius=8)
            
            # Draw region information
            region = self.hovered_region
            data = self.regions[region]
            name, function, description = region.value
            
            y = padding
            # Truncate long descriptions
            max_chars = 30
            if len(description) > max_chars:
                description = description[:max_chars] + "..."
            
            for text in [name, function, description]:
                surface = self.detail_font.render(text, True, self.COLORS['text'])
                panel.blit(surface, (padding, y))
                y += 18  # Reduced spacing
            
            # Draw activation history graph
            graph_height = 35  # Slightly smaller graph
            graph_width = panel_width - padding * 2
            graph_rect = pygame.Rect(padding, y, graph_width, graph_height)
            
            pygame.draw.rect(panel, self.COLORS['graph_bg'], graph_rect)
            
            # Plot activation history
            points = [(i * graph_width / 49, 
                      graph_height * (1 - activation))
                     for i, (activation, _) in enumerate(data['history'])]
            
            if len(points) > 1:
                pygame.draw.lines(panel, self.COLORS['high'],
                                False,
                                [(x + padding, y + y_offset) 
                                 for x, y_offset in points], 2)
            
            # Position panel - ensure it stays within bounds
            mouse_x, mouse_y = pygame.mouse.get_pos()
            panel_x = min(self.width - panel_width - 10,
                         max(10, mouse_x - panel_width // 2))
            panel_y = min(self.height - panel_height - 10,
                         max(10, mouse_y - panel_height - 20))
            
            self.surface.blit(panel, (panel_x, panel_y))
    
    def handle_event(self, event: pygame.event.Event, offset_x: int, offset_y: int) -> None:
        """Handle mouse events for interactivity"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                mouse_x, mouse_y = event.pos
                mouse_x -= offset_x
                mouse_y -= offset_y
                
                # Check for double click
                current_time = pygame.time.get_ticks()
                for region, data in self.regions.items():
                    pos = (int(data['pos'][0] * self.width),
                          int(data['pos'][1] * self.height))
                    size = data['size']
                    
                    distance = ((mouse_x - pos[0]) ** 2 + (mouse_y - pos[1]) ** 2) ** 0.5
                    if distance <= size:
                        if (region == self.last_clicked_region and 
                            current_time - self.last_click_time < 500):  # Double click threshold
                            # Reset position on double click
                            data['target_pos'] = self.current_layout[region]
                            self.sounds.play('click')
                        else:
                            self.selected_region = region
                            self.dragging = True
                            self.offset_x = mouse_x - pos[0]
                            self.offset_y = mouse_y - pos[1]
                            self.sounds.play('click', 0.3)
                            
                        self.last_clicked_region = region
                        self.last_click_time = current_time
                        break
                        
            elif event.button == 4:  # Mouse wheel up
                if self.hovered_region:
                    self.regions[self.hovered_region]['size'] = min(
                        50, self.regions[self.hovered_region]['size'] + 2)
                    self.sounds.play('hover', 0.2)
            elif event.button == 5:  # Mouse wheel down
                if self.hovered_region:
                    self.regions[self.hovered_region]['size'] = max(
                        20, self.regions[self.hovered_region]['size'] - 2)
                    self.sounds.play('hover', 0.2)
                    
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                if self.dragging:
                    self.dragging = False
                    if self.selected_region:
                        # Add momentum when releasing
                        velocity = (random.uniform(-0.5, 0.5), random.uniform(-0.5, 0.5))
                        self.regions[self.selected_region]['velocity'] = velocity
                        self.sounds.play('connect', 0.3)
                
        elif event.type == pygame.MOUSEMOTION:
            mouse_x, mouse_y = event.pos
            mouse_x -= offset_x
            mouse_y -= offset_y
            
            if self.dragging and self.selected_region:
                new_x = (mouse_x - self.offset_x) / self.width
                new_y = (mouse_y - self.offset_y) / self.height
                
                # Elastic boundary behavior
                new_x = max(0.1, min(0.9, new_x))
                new_y = max(0.1, min(0.9, new_y))
                
                self.regions[self.selected_region]['pos'] = (new_x, new_y)
                # Reset velocity when dragging
                self.regions[self.selected_region]['velocity'] = (0, 0)
            
            # Update hover state
            prev_hovered = self.hovered_region
            self.hovered_region = None
            for region, data in self.regions.items():
                pos = (int(data['pos'][0] * self.width),
                      int(data['pos'][1] * self.height))
                size = data['size']
                
                distance = ((mouse_x - pos[0]) ** 2 + (mouse_y - pos[1]) ** 2) ** 0.5
                if distance <= size:
                    self.hovered_region = region
                    if prev_hovered != region:
                        self.sounds.play('hover', 0.1)
                    break
        
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                self.cycle_visualization_mode()
                self.sounds.play('connect')
            elif event.key == pygame.K_TAB:
                self.show_details = not self.show_details
                self.sounds.play('click')

    def render(self, stress_level: float, decision_type: str) -> pygame.Surface:
        """Render enhanced neural visualization"""
        self.surface.fill((0, 0, 0, 0))
        
        # Update timing
        current_time = pygame.time.get_ticks()
        dt = (current_time - self.last_update) / 1000.0
        self.last_update = current_time
        
        # Update physics and animations
        self.update_physics(dt)
        self.update_activity(stress_level, decision_type)
        
        # Draw connections with flow
        connection_phase = (current_time / 2000.0) % 1.0  # Slower connection animation
        
        for start_region, end_region in self.connections:
            start_data = self.regions[start_region]
            end_data = self.regions[end_region]
            
            start_pos = (int(start_data['pos'][0] * self.width),
                        int(start_data['pos'][1] * self.height))
            end_pos = (int(end_data['pos'][0] * self.width),
                      int(end_data['pos'][1] * self.height))
            
            avg_activation = (start_data['activation'] + 
                            end_data['activation']) / 2
            
            self.draw_connection_flow(start_pos, end_pos,
                                   avg_activation, connection_phase)
        
        # Draw regions
        for region, data in self.regions.items():
            pos = (int(data['pos'][0] * self.width),
                  int(data['pos'][1] * self.height))
            
            # Calculate size with slower pulse
            base_size = data['size'] * data['scale']
            pulse = math.sin(data['pulse_phase'] * 0.5) * 2  # Slower pulse
            size = int(base_size + pulse * data['activation'])
            
            # Draw node glow
            if data['activation'] > 0.5:
                glow_size = size + 4
                glow_alpha = int(128 * data['activation'])
                glow_color = (*self.COLORS['high'][:3], glow_alpha)
                pygame.draw.circle(self.surface, glow_color, pos, glow_size)
            
            # Draw node
            color = self.get_color_for_activation(data['activation'], region)
            pygame.draw.circle(self.surface, color, pos, size)
            
            # Draw label with better positioning and background
            name = region.value[0]
            text = self.font.render(name, True, self.COLORS['text'])
            
            # Add background for better readability
            text_rect = text.get_rect(center=(pos[0], pos[1] + size + 12))
            bg_rect = text_rect.copy()
            bg_rect.inflate_ip(8, 4)  # Make background slightly larger
            pygame.draw.rect(self.surface, self.COLORS['tooltip_bg'], bg_rect, border_radius=4)
            
            # Draw text
            self.surface.blit(text, text_rect)
            
            # Draw activation percentage with background
            if data['activation'] > 0.1:
                pct_text = f"{int(data['activation'] * 100)}%"
                pct_surface = self.font.render(pct_text, True, self.COLORS['text'])
                pct_rect = pct_surface.get_rect(center=pos)
                
                # Add background for percentage
                pct_bg_rect = pct_rect.copy()
                pct_bg_rect.inflate_ip(8, 4)
                pygame.draw.rect(self.surface, self.COLORS['tooltip_bg'], pct_bg_rect, border_radius=4)
                
                self.surface.blit(pct_surface, pct_rect)
        
        # Draw detailed view if enabled
        self.draw_detailed_view()
        
        return self.surface

    def get_color_for_activation(self, activation: float, region: Optional[BrainRegion]) -> Tuple[int, int, int, int]:
        """Get color based on activation level and region state"""
        if region == self.selected_region:
            return self.COLORS['selected']
        elif region == self.hovered_region:
            return self.COLORS['hover']
        elif activation < 0.2:
            return self.COLORS['inactive']
        elif activation < 0.5:
            return self.COLORS['low']
        elif activation < 0.8:
            return self.COLORS['medium']
        else:
            return self.COLORS['high']

    def update_activity(self, stress_level: float, decision_type: str):
        """Update neural activation based on stress and decision type"""
        # Slow down the rate of change with interpolation
        interpolation_speed = 0.05  # Lower value = slower changes
        
        # Store target activations
        target_activations = {region: 0.0 for region in self.regions}
        
        # Set target activation patterns for different scenarios
        if decision_type == "aggressive":
            target_activations[BrainRegion.AMYGDALA] = 0.8 + random.uniform(-0.05, 0.05)
            target_activations[BrainRegion.PREFRONTAL] = 0.3 + random.uniform(-0.05, 0.05)
            target_activations[BrainRegion.STRIATUM] = 0.7 + random.uniform(-0.05, 0.05)
            target_activations[BrainRegion.HYPOTHALAMUS] = 0.6 + random.uniform(-0.05, 0.05)
        elif decision_type == "diplomatic":
            target_activations[BrainRegion.PREFRONTAL] = 0.9 + random.uniform(-0.05, 0.05)
            target_activations[BrainRegion.ANTERIOR] = 0.7 + random.uniform(-0.05, 0.05)
            target_activations[BrainRegion.AMYGDALA] = 0.3 + random.uniform(-0.05, 0.05)
            target_activations[BrainRegion.INSULA] = 0.6 + random.uniform(-0.05, 0.05)
        elif decision_type == "defensive":
            target_activations[BrainRegion.INSULA] = 0.8 + random.uniform(-0.05, 0.05)
            target_activations[BrainRegion.HIPPOCAMPUS] = 0.6 + random.uniform(-0.05, 0.05)
            target_activations[BrainRegion.THALAMUS] = 0.7 + random.uniform(-0.05, 0.05)
            target_activations[BrainRegion.ANTERIOR] = 0.5 + random.uniform(-0.05, 0.05)
        
        # Smoothly interpolate current activations toward target values
        for region, data in self.regions.items():
            target = target_activations[region]
            # Modulate target by stress level
            target = min(1.0, target * (1 + stress_level * 0.5))
            
            # Smooth interpolation
            current = data['activation']
            new_value = current + (target - current) * interpolation_speed
            
            # Add very subtle random fluctuation
            new_value += random.uniform(-0.01, 0.01)
            
            # Clamp value
            data['activation'] = max(0.0, min(1.0, new_value))
            
            # Update activation history
            data['history'].pop(0)
            data['history'].append((data['activation'], pygame.time.get_ticks()))
