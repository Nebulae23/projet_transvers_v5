#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Notification System for Nightfall Defenders
Provides temporary pop-up notifications and messages
"""

from direct.gui.DirectGui import DirectFrame, DirectLabel, DGG
from panda3d.core import TextNode, Vec4
import time

class NotificationSystem:
    """System for displaying temporary notifications"""
    
    def __init__(self, game):
        """
        Initialize the notification system
        
        Args:
            game: The game instance
        """
        self.game = game
        
        # Create container for notifications
        self.container = DirectFrame(
            frameColor=(0, 0, 0, 0),  # Transparent
            frameSize=(-0.8, 0.8, -0.5, 0.5),
            pos=(0, 0, 0.7),  # Top of screen
            parent=game.aspect2d
        )
        
        # List of active notifications
        self.notifications = []
        
        # Maximum number of visible notifications
        self.max_visible = 5
        
        # Add task to update notifications
        self.game.taskMgr.add(self.update_notifications, "update_notifications")
    
    def add_notification(self, message, duration=5.0, type="info"):
        """
        Add a new notification
        
        Args:
            message: Notification message
            duration: Duration in seconds
            type: Type of notification ('info', 'warning', 'error', 'success')
        """
        # Determine color based on type
        colors = {
            "info": (0.2, 0.3, 0.7, 0.8),      # Blue
            "warning": (0.8, 0.6, 0.2, 0.8),   # Orange
            "error": (0.8, 0.2, 0.2, 0.8),     # Red
            "success": (0.2, 0.7, 0.3, 0.8),   # Green
            "quest": (0.6, 0.3, 0.8, 0.8),     # Purple
            "item": (0.3, 0.7, 0.7, 0.8)       # Teal
        }
        
        frame_color = colors.get(type, colors["info"])
        text_color = (1, 1, 1, 1)  # White text
        
        # Create notification frame
        notification = DirectFrame(
            frameColor=frame_color,
            frameSize=(-0.7, 0.7, -0.05, 0.05),
            pos=(0, 0, 0),  # Will be positioned later
            parent=self.container
        )
        
        # Add text
        text = DirectLabel(
            text=message,
            text_scale=0.04,
            text_fg=text_color,
            text_align=TextNode.ACenter,
            frameColor=(0, 0, 0, 0),
            parent=notification
        )
        
        # Add to notifications list with metadata
        self.notifications.append({
            "frame": notification,
            "text": text,
            "created": time.time(),
            "duration": duration,
            "alpha": 1.0,
            "type": type
        })
        
        # Reposition all notifications
        self._reposition_notifications()
        
        # Play sound based on notification type
        self._play_notification_sound(type)
    
    def update_notifications(self, task):
        """
        Update notifications (fade out, remove expired)
        
        Args:
            task: Task instance
        
        Returns:
            Task continuation flag
        """
        current_time = time.time()
        to_remove = []
        
        for i, notification in enumerate(self.notifications):
            # Calculate age of notification
            age = current_time - notification["created"]
            
            # If past duration, start fading out
            if age > notification["duration"]:
                # Calculate fade (1 second fade out)
                fade_time = 1.0
                fade_progress = min(1.0, (age - notification["duration"]) / fade_time)
                
                # Update alpha
                new_alpha = 1.0 - fade_progress
                notification["alpha"] = new_alpha
                
                # Apply alpha to frame
                frame_color = list(notification["frame"]["frameColor"])
                frame_color[3] = new_alpha
                notification["frame"]["frameColor"] = tuple(frame_color)
                
                # For text, we need to recreate it with new alpha since fg is not directly accessible
                old_text = notification["text"]
                text_pos = old_text.getPos()
                
                # Create new text with updated alpha
                new_text = DirectLabel(
                    text=old_text["text"],
                    text_scale=old_text["text_scale"],
                    text_align=TextNode.ACenter,
                    text_fg=(1, 1, 1, new_alpha),  # Use the new alpha here
                    frameColor=(0, 0, 0, 0),
                    parent=notification["frame"]
                )
                new_text.setPos(text_pos)
                
                # Remove old text
                old_text.destroy()
                
                # Update reference
                notification["text"] = new_text
                
                # Mark for removal if completely faded
                if fade_progress >= 1.0:
                    to_remove.append(i)
        
        # Remove expired notifications (in reverse order to maintain indices)
        for i in reversed(to_remove):
            # Clean up the notification
            self.notifications[i]["frame"].destroy()
            # Remove from list
            self.notifications.pop(i)
        
        # Reposition remaining notifications if any were removed
        if to_remove:
            self._reposition_notifications()
        
        return task.cont
    
    def _reposition_notifications(self):
        """Reposition notifications in the container"""
        # Ensure we don't show too many
        visible_count = min(len(self.notifications), self.max_visible)
        
        # Hide excess notifications (oldest first)
        for i in range(visible_count, len(self.notifications)):
            self.notifications[i]["frame"].hide()
        
        # Position visible notifications
        for i in range(visible_count):
            # Start from the newest (bottom of the list)
            index = len(self.notifications) - 1 - i
            if index >= 0:
                notification = self.notifications[index]
                
                # Position from top to bottom
                y_pos = -i * 0.12
                notification["frame"].setPos(0, 0, y_pos)
                notification["frame"].show()
    
    def _play_notification_sound(self, type):
        """
        Play a sound based on notification type
        
        Args:
            type: Notification type
        """
        # If audio manager exists, play appropriate sound
        if hasattr(self.game, 'audio_manager'):
            sound_name = f"ui_notification_{type}"
            self.game.audio_manager.play_sound(sound_name)
    
    def clear_all(self):
        """Clear all notifications"""
        for notification in self.notifications:
            notification["frame"].destroy()
        
        self.notifications = []
    
    def cleanup(self):
        """Clean up resources"""
        self.clear_all()
        self.container.destroy()
        self.game.taskMgr.remove("update_notifications") 