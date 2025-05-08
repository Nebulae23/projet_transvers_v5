#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Simple test of Panda3D setup
"""

import sys
import os
from direct.showbase.ShowBase import ShowBase
from panda3d.core import loadPrcFileData, WindowProperties, Vec3

# Configure Panda3D settings
loadPrcFileData("", "window-title Nightfall Defenders - Test")
loadPrcFileData("", "win-size 800 600")
loadPrcFileData("", "fullscreen 0")
loadPrcFileData("", "sync-video 1")

class SimpleTest(ShowBase):
    def __init__(self):
        super().__init__()
        
        # Set up window
        wp = WindowProperties()
        wp.setTitle("Nightfall Defenders - Test")
        self.win.requestProperties(wp)
        
        # Add a simple box
        self.box = self.loader.loadModel("models/box")
        self.box.setPos(0, 5, 0)
        self.box.reparentTo(self.render)
        
        # Set up camera
        self.camera.setPos(0, -10, 3)
        self.camera.lookAt(0, 0, 0)
        
        # Add a simple task to rotate the box
        self.taskMgr.add(self.spin_box_task, "spin_box_task")
        
        print("Simple test initialized!")
    
    def spin_box_task(self, task):
        # Rotate the box
        self.box.setH(self.box.getH() + 1)
        return task.cont

def main():
    try:
        app = SimpleTest()
        app.run()
    except Exception as e:
        import traceback
        print(f"ERROR: Test crashed: {e}")
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 