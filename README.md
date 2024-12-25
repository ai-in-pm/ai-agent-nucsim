# Nuclear Crisis Simulation with AI Presidents

A real-time simulation of nuclear crisis decision-making, featuring AI-driven representations of world leaders and their cognitive processes during high-stakes scenarios.

## Overview

This simulation provides a unique insight into the decision-making processes of AI-driven world leaders during a potential nuclear crisis. The system visualizes neural activity patterns and cognitive processes that influence critical decisions in real-time.

## Features

### Neural Network Visualization
- Real-time visualization of AI presidents' brain activity
- Key brain regions monitored:
  - Amygdala (Fear & Threat Response)
  - Prefrontal Cortex (Decision Making)
  - Hippocampus (Memory)
  - Anterior Cingulate (Conflict Resolution)
  - Insula (Risk Assessment)
  - Striatum (Reward & Consequences)
  - Thalamus (Information Processing)
  - Hypothalamus (Stress Response)

### AI Presidents
- Donald Trump (USA)
  - Decision patterns based on approval ratings
  - Stress response visualization
  - Real-time cognitive process display

- Kim Jong Un (DPRK)
  - Aggressive vs. defensive decision making
  - Stress threshold monitoring
  - Neural activity patterns during crisis

### Crisis Simulation
- Dynamic tension level system
- Real-time event generation
- Military unit deployment tracking
- International incident simulation

### Interactive Interface
- Event log tracking all actions and decisions
- Control panel for simulation speed
- Real-time approval ratings
- Decision history tracking

## Technical Details

### Dependencies
pygame==2.5.2
numpy==1.24.3
pandas==2.0.3
folium==0.14.0
geopy==2.4.1
python-dotenv==1.0.0
colorama==0.4.6
googlemaps==4.10.0
pillow==10.0.0
requests==2.31.0

### Key Components
- `strategic_map.py`: Main simulation controller
- `neural_viz.py`: Neural network visualization
- `ai_president.py`: AI decision-making logic

## Installation

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv .venv
   ```
3. Activate the virtual environment:
   - Windows: `.venv\Scripts\activate`
   - Unix/MacOS: `source .venv/bin/activate`
4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

Run the simulation:
```bash
python strategic_map.py
```

### Controls
- Pause/Resume: Toggle simulation
- Speed +/-: Adjust simulation speed
- Window is resizable for better visualization

## Neural Activity Interpretation

The neural visualization shows:
- Red regions: High activity/stress
- Blue regions: Low activity/normal function
- Connection brightness: Information flow strength
- Percentage indicators: Regional activation levels

### Decision Patterns
- Diplomatic decisions: High prefrontal cortex activity
- Aggressive decisions: High amygdala activity
- Defensive decisions: Balanced activation across regions

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Thanks to all contributors and testers
- Special thanks to the pygame community for their excellent graphics library
- Inspired by real-world geopolitical simulations and crisis management scenarios
