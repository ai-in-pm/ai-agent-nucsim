from enum import Enum
from dataclasses import dataclass
from typing import List, Dict, Optional
import random

class ActionType(Enum):
    MILITARY = "military"
    DIPLOMATIC = "diplomatic"
    ECONOMIC = "economic"
    CYBER = "cyber"
    PROPAGANDA = "propaganda"

class DecisionFactor(Enum):
    MILITARY_STRENGTH = "military_strength"
    PUBLIC_SUPPORT = "public_support"
    INTERNATIONAL_PRESSURE = "international_pressure"
    ECONOMIC_STATUS = "economic_status"
    THREAT_LEVEL = "threat_level"

@dataclass
class Action:
    action_type: ActionType
    description: str
    severity: int  # 1-10
    success_probability: float
    consequences: Dict[str, float]

class AIPresident:
    def __init__(self, nation: str, personality_traits: Dict[str, float]):
        self.nation = nation
        self.personality_traits = personality_traits
        self.available_actions: List[Action] = []
        self.decision_history: List[Action] = []
        self.current_state: Dict[DecisionFactor, float] = {
            factor: 5.0 for factor in DecisionFactor
        }
        
    def initialize_actions(self):
        """Initialize available actions based on nation and personality"""
        if self.nation == "United States":
            self.available_actions.extend([
                Action(
                    ActionType.MILITARY,
                    "Deploy carrier group to South China Sea",
                    severity=7,
                    success_probability=0.8,
                    consequences={
                        "tension": 0.3,
                        "deterrence": 0.4,
                        "international_support": -0.2
                    }
                ),
                Action(
                    ActionType.DIPLOMATIC,
                    "Propose emergency UN Security Council meeting",
                    severity=3,
                    success_probability=0.9,
                    consequences={
                        "tension": -0.2,
                        "international_support": 0.3,
                        "negotiation_power": 0.2
                    }
                ),
                # Add more US-specific actions
            ])
        elif self.nation == "North Korea":
            self.available_actions.extend([
                Action(
                    ActionType.MILITARY,
                    "Conduct missile test over Japan",
                    severity=8,
                    success_probability=0.7,
                    consequences={
                        "tension": 0.5,
                        "deterrence": 0.3,
                        "international_support": -0.4
                    }
                ),
                Action(
                    ActionType.PROPAGANDA,
                    "Release statement condemning US aggression",
                    severity=4,
                    success_probability=0.95,
                    consequences={
                        "domestic_support": 0.3,
                        "international_support": -0.2,
                        "negotiation_power": 0.1
                    }
                ),
                # Add more NK-specific actions
            ])
    
    def evaluate_situation(self, map_state: Dict) -> Dict[DecisionFactor, float]:
        """Evaluate current situation based on map state and other factors"""
        evaluation = {}
        for factor in DecisionFactor:
            # Calculate factor value based on map_state and personality
            base_value = self.current_state[factor]
            modifier = self.calculate_situation_modifier(factor, map_state)
            evaluation[factor] = min(max(base_value + modifier, 0), 10)
        return evaluation
    
    def calculate_situation_modifier(self, factor: DecisionFactor, map_state: Dict) -> float:
        """Calculate modifier for situation evaluation based on personality and map state"""
        modifier = 0.0
        
        if factor == DecisionFactor.THREAT_LEVEL:
            # Calculate threat based on enemy units proximity and activity
            enemy_presence = map_state.get("enemy_units_proximity", 0)
            modifier += enemy_presence * self.personality_traits.get("aggression", 1.0)
            
        elif factor == DecisionFactor.PUBLIC_SUPPORT:
            # Modify based on recent actions and propaganda effectiveness
            recent_success = map_state.get("recent_action_success", 0)
            modifier += recent_success * self.personality_traits.get("populist_tendency", 1.0)
            
        return modifier
    
    def make_decision(self, map_state: Dict) -> Optional[Action]:
        """Make a decision based on current situation and personality"""
        situation = self.evaluate_situation(map_state)
        
        # Calculate action scores based on situation and personality
        action_scores = []
        for action in self.available_actions:
            score = self.calculate_action_score(action, situation)
            action_scores.append((score, action))
            
        if not action_scores:
            return None
            
        # Sort by score and add some randomness based on personality
        action_scores.sort(reverse=True)
        randomness = self.personality_traits.get("impulsiveness", 0.1)
        
        if random.random() < randomness:
            # Make a potentially irrational decision
            return random.choice(self.available_actions)
        
        # Return the highest-scored action
        return action_scores[0][1]
    
    def calculate_action_score(self, action: Action, situation: Dict[DecisionFactor, float]) -> float:
        """Calculate score for an action based on current situation"""
        score = 0.0
        
        # Factor in personality traits
        aggression_weight = self.personality_traits.get("aggression", 0.5)
        caution_weight = self.personality_traits.get("caution", 0.5)
        
        # Calculate base score
        if action.action_type == ActionType.MILITARY:
            score += situation[DecisionFactor.MILITARY_STRENGTH] * aggression_weight
            score -= situation[DecisionFactor.INTERNATIONAL_PRESSURE] * caution_weight
            
        elif action.action_type == ActionType.DIPLOMATIC:
            score += situation[DecisionFactor.INTERNATIONAL_PRESSURE] * caution_weight
            score += situation[DecisionFactor.PUBLIC_SUPPORT] * 0.5
            
        # Adjust for severity and success probability
        score *= action.success_probability
        score *= (11 - action.severity) / 10  # Higher severity reduces score
        
        return score
    
    def update_state(self, action: Action, outcome: Dict):
        """Update internal state based on action outcome"""
        self.decision_history.append(action)
        
        # Update current state based on action consequences and outcome
        for factor in DecisionFactor:
            modifier = outcome.get(factor.value, 0)
            self.current_state[factor] = min(max(
                self.current_state[factor] + modifier,
                0
            ), 10)
