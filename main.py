#!/usr/bin/env python3
"""
Zelda-like 2D Game
Main entry point for the game
"""
import sys
import os

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from core.game import Game


def main():
    """Main function to start the game."""
    try:
        # Create and run the game
        game = Game()
        game.run()
        
    except KeyboardInterrupt:
        print("\nGame interrupted by user.")
    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)


if __name__ == "__main__":
    print("Zelda-like 2D Game - Starting...")
    main()