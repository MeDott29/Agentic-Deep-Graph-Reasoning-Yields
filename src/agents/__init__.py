"""
Agent module initialization.
"""
from src.agents.base import Agent
from src.agents.trend_spotter import TrendSpotterAgent
from src.agents.deep_dive import DeepDiveAgent
from src.agents.entertainer import EntertainerAgent

__all__ = ['Agent', 'TrendSpotterAgent', 'DeepDiveAgent', 'EntertainerAgent'] 