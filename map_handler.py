import os
import googlemaps
import pygame
from PIL import Image
import requests
from io import BytesIO
import math
from typing import Tuple, Dict

class MapHandler:
    def __init__(self, api_key: str, width: int, height: int):
        """Initialize the map handler with Google Maps API"""
        self.gmaps = googlemaps.Client(key=api_key)
        self.width = width
        self.height = height
        
        # Pacific Ocean bounds (approximate)
        self.bounds = {
            'north': 50,     # Northern latitude
            'south': -50,    # Southern latitude
            'east': 180,     # Eastern longitude
            'west': 100,     # Western longitude
        }
        
        # Important locations
        self.locations = {
            'USA_HAWAII': {'lat': 21.3069, 'lng': -157.8583},
            'NORTH_KOREA': {'lat': 40.3399, 'lng': 127.5101},
            'SOUTH_KOREA': {'lat': 35.9078, 'lng': 127.7669},
            'JAPAN': {'lat': 36.2048, 'lng': 138.2529},
            'GUAM': {'lat': 13.4443, 'lng': 144.7937}
        }
        
        # Initialize map surface
        self.map_surface = None
        self.fetch_map()
        
    def fetch_map(self):
        """Fetch the map from Google Maps Static API"""
        try:
            # Calculate center point
            center_lat = (self.bounds['north'] + self.bounds['south']) / 2
            center_lng = (self.bounds['east'] + self.bounds['west']) / 2
            
            # Construct the static map URL
            base_url = "https://maps.googleapis.com/maps/api/staticmap?"
            
            # Create markers for important locations
            markers = []
            for name, loc in self.locations.items():
                markers.append(f"markers=size:mid|label:{name[0]}|{loc['lat']},{loc['lng']}")
            
            # Parameters for the map
            params = [
                f"center={center_lat},{center_lng}",
                f"size={self.width}x{self.height}",
                "scale=2",  # High resolution
                "maptype=terrain",
                "style=feature:water|color:0x000032",  # Dark blue water
                "style=feature:landscape|color:0x2F4F4F",  # Dark green land
                "style=feature:administrative|element:geometry.stroke|color:0xFFFFFF|weight:1",  # White borders
                f"key={self.gmaps.key}"
            ]
            
            # Combine URL
            url = base_url + "&".join(params + markers)
            
            # Fetch the map image
            response = requests.get(url)
            response.raise_for_status()  # Raise exception for bad status codes
            
            image = Image.open(BytesIO(response.content))
            
            # Convert to pygame surface
            mode = image.mode
            size = image.size
            data = image.tobytes()
            
            # Create pygame surface
            self.map_surface = pygame.image.fromstring(data, size, mode).convert()
            
        except Exception as e:
            print(f"Error fetching map: {e}")
            # Create fallback surface
            self.map_surface = pygame.Surface((self.width, self.height))
            self.map_surface.fill((0, 32, 64))  # Dark blue fallback
            
    def lat_lng_to_pixel(self, lat: float, lng: float) -> Tuple[int, int]:
        """Convert latitude and longitude to pixel coordinates"""
        # Normalize coordinates to [0, 1] range
        x = (lng - self.bounds['west']) / (self.bounds['east'] - self.bounds['west'])
        y = 1 - (lat - self.bounds['south']) / (self.bounds['north'] - self.bounds['south'])
        
        # Convert to pixels
        px = int(x * self.width)
        py = int(y * self.height)
        
        return (px, py)
        
    def get_location_pixels(self) -> Dict[str, Tuple[int, int]]:
        """Get pixel coordinates for all important locations"""
        return {
            name: self.lat_lng_to_pixel(loc['lat'], loc['lng'])
            for name, loc in self.locations.items()
        }
        
    def render(self, screen: pygame.Surface, x: int, y: int):
        """Render the map to the screen at the specified position"""
        if self.map_surface:
            # Create a subsurface for the map area
            map_rect = pygame.Rect(x, y, self.width, self.height)
            screen_rect = screen.get_rect()
            
            # Only render if the map area intersects with the screen
            if map_rect.colliderect(screen_rect):
                screen.blit(self.map_surface, (x, y))
            
    def update_size(self, width: int, height: int):
        """Update the map size and refetch"""
        if width != self.width or height != self.height:
            self.width = width
            self.height = height
            self.fetch_map()
