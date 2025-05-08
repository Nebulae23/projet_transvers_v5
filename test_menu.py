#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Test script for debugging menu UI issues
"""

import sys
import os

# Add src directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, "src")
sys.path.insert(0, src_dir)

from direct.showbase.ShowBase import ShowBase
from direct.gui.DirectGui import DirectButton, DirectFrame, DGG
from direct.gui.OnscreenText import OnscreenText
from direct.gui.OnscreenImage import OnscreenImage
from panda3d.core import TextNode, TransparencyAttrib, WindowProperties

class TestMenuApp(ShowBase):
    """Test application for menu debugging"""
    
    def __init__(self):
        """Initialize the test app"""
        ShowBase.__init__(self)
        
        # Set window title
        props = WindowProperties()
        props.setTitle("Menu Test")
        self.win.requestProperties(props)
        
        # Create a background
        try:
            self.background = OnscreenImage(
                image="src/assets/generated/ui/main_menu_bg.png",
                pos=(0, 0, 0),
                scale=(1.33, 1, 1)  # Adjusted for 16:9 aspect ratio
            )
            self.background.setTransparency(TransparencyAttrib.MAlpha)
        except Exception as e:
            print(f"Background image error: {e}")
            print("Using colored background")
            self.background = DirectFrame(
                frameColor=(0.1, 0.1, 0.2, 1),
                frameSize=(-1.33, 1.33, -1, 1)
            )
        
        # Create a title
        self.title = OnscreenText(
            text="Menu Test",
            pos=(0, 0.7),
            scale=0.12,
            fg=(1, 0.9, 0.7, 1),
            shadow=(0.1, 0.1, 0.1, 0.5),
            shadowOffset=(0.04, 0.04),
            align=TextNode.ACenter
        )
        
        # Create direct buttons
        button_spacing = 0.15
        start_y = 0.2
        
        # New Game button
        self.new_game_button = DirectButton(
            text="New Game",
            scale=0.07,
            pos=(0, 0, start_y),
            frameSize=(-4, 4, -0.8, 0.8),
            frameColor=(0.3, 0.3, 0.3, 0.8),
            text_fg=(1, 1, 1, 1),
            relief=DGG.FLAT,
            command=self.on_new_game
        )
        
        # Options button
        self.options_button = DirectButton(
            text="Options",
            scale=0.07,
            pos=(0, 0, start_y - button_spacing),
            frameSize=(-4, 4, -0.8, 0.8),
            frameColor=(0.3, 0.3, 0.3, 0.8),
            text_fg=(1, 1, 1, 1),
            relief=DGG.FLAT,
            command=self.on_options
        )
        
        # Quit button
        self.quit_button = DirectButton(
            text="Quit",
            scale=0.07,
            pos=(0, 0, start_y - button_spacing * 2),
            frameSize=(-4, 4, -0.8, 0.8),
            frameColor=(0.3, 0.3, 0.3, 0.8),
            text_fg=(1, 1, 1, 1),
            relief=DGG.FLAT,
            command=self.on_quit
        )
        
        print("Menu test initialized")
        
    def on_new_game(self):
        """Handle new game button click"""
        print("New Game clicked")
        
    def on_options(self):
        """Handle options button click"""
        print("Options clicked")
        
    def on_quit(self):
        """Handle quit button click"""
        print("Quit clicked")
        self.userExit()

def main():
    """Main entry point"""
    app = TestMenuApp()
    app.run()

if __name__ == "__main__":
    main() 