"""Manage configuration steps"""
import os, sys, json
from utils.paths import Pathmanagement

class Config():
    def __init__(self):
        pass
    
    @staticmethod
    def load_config(config_path):
        """Load configuration from a file

        Args:
            config_path (string): Path to the configuration file
        """
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
                return config
        except FileNotFoundError:
            print(f"Configuration file not found: {config_path}")
            return {}
        except json.JSONDecodeError as e:
            print(f"Error parsing configuration file: {e}")
            return {}
