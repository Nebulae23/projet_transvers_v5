#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Skill Tree UI for Nightfall Defenders
Implements a visual interface for the skill tree system
"""

from direct.gui.DirectGui import (
    DirectFrame, DirectButton, DirectLabel, 
    DirectScrolledFrame, DGG
)
from panda3d.core import (
    NodePath, TextNode, LVector3f, 
    LineSegs, TransparencyAttrib, Vec4
)
import math

class SkillTreeUI:
    """UI for displaying and interacting with the skill tree"""
    
    def __init__(self, game, player, skill_tree):
        """
        Initialize the skill tree UI
        
        Args:
            game: The main game instance
            player: The player entity
            skill_tree: The SkillTree instance
        """
        self.game = game
        self.player = player
        self.skill_tree = skill_tree
        self.node_size = 64  # Size of node icons in pixels
        self.zoom = 1.0
        self.is_dragging = False
        self.drag_start = (0, 0)
        self.offset = (0, 0)
        
        # UI elements
        self.root_frame = None
        self.scroll_frame = None
        self.content_frame = None
        self.title_label = None
        self.close_button = None
        self.zoom_in_button = None
        self.zoom_out_button = None
        self.reset_view_button = None
        self.node_frames = {}  # Mapping of node_id to UI elements
        self.connection_lines = None
        self.tooltip = None
        
        # Node visualization 
        self.question_mark_icon = "src/assets/generated/ui/question_mark.png"
        self.locked_icon = "src/assets/generated/ui/locked.png"
        self.fusion_icon_overlay = "src/assets/generated/ui/fusion_overlay.png"
        self.pulse_animations = {}  # Store pulse animation data for nodes
        self.animation_time = 0.0
        
        # Create the UI
        self.create_ui()
        
        # Initially hide the UI
        self.hide()
    
    def create_ui(self):
        """Create the skill tree UI elements"""
        # Root frame that covers the whole screen
        self.root_frame = DirectFrame(
            frameColor=(0.1, 0.1, 0.15, 0.9),
            frameSize=(-1, 1, -1, 1),
            parent=self.game.aspect2d
        )
        
        # Title
        self.title_label = DirectLabel(
            text="Skill Tree",
            text_fg=(1, 1, 1, 1),
            text_scale=0.08,
            frameColor=(0, 0, 0, 0),
            pos=(0, 0, 0.9),
            parent=self.root_frame
        )
        
        # Close button
        self.close_button = DirectButton(
            text="X",
            text_fg=(1, 1, 1, 1),
            text_scale=0.08,
            frameColor=(0.5, 0.0, 0.0, 0.8),
            relief=DGG.FLAT,
            frameSize=(-0.05, 0.05, -0.05, 0.05),
            pos=(0.9, 0, 0.9),
            command=self.hide,
            parent=self.root_frame
        )
        
        # Zoom controls
        self.zoom_in_button = DirectButton(
            text="+",
            text_fg=(1, 1, 1, 1),
            text_scale=0.08,
            frameColor=(0.2, 0.2, 0.2, 0.8),
            relief=DGG.FLAT,
            frameSize=(-0.05, 0.05, -0.05, 0.05),
            pos=(0.7, 0, 0.9),
            command=self.zoom_in,
            parent=self.root_frame
        )
        
        self.zoom_out_button = DirectButton(
            text="-",
            text_fg=(1, 1, 1, 1),
            text_scale=0.08,
            frameColor=(0.2, 0.2, 0.2, 0.8),
            relief=DGG.FLAT,
            frameSize=(-0.05, 0.05, -0.05, 0.05),
            pos=(0.6, 0, 0.9),
            command=self.zoom_out,
            parent=self.root_frame
        )
        
        self.reset_view_button = DirectButton(
            text="Reset",
            text_fg=(1, 1, 1, 1),
            text_scale=0.05,
            frameColor=(0.2, 0.2, 0.2, 0.8),
            relief=DGG.FLAT,
            frameSize=(-0.1, 0.1, -0.04, 0.04),
            pos=(0.45, 0, 0.9),
            command=self.reset_view,
            parent=self.root_frame
        )
        
        # Create a scrolled frame for the skill tree content
        self.scroll_frame = DirectScrolledFrame(
            frameColor=(0.15, 0.15, 0.2, 0.8),
            frameSize=(-0.9, 0.9, -0.8, 0.8),
            canvasSize=(-2, 2, -2, 2),  # Will be adjusted based on content
            scrollBarWidth=0.04,
            verticalScroll_relief=DGG.FLAT,
            horizontalScroll_relief=DGG.FLAT,
            parent=self.root_frame
        )
        
        # Content frame within the scrolled frame
        self.content_frame = DirectFrame(
            frameColor=(0, 0, 0, 0),
            state=DGG.NORMAL,  # Make it clickable for drag functionality
            parent=self.scroll_frame.getCanvas()
        )
        
        # Tooltip for hovering over nodes
        self.tooltip = DirectFrame(
            frameColor=(0.2, 0.2, 0.2, 0.9),
            frameSize=(-0.3, 0.3, -0.2, 0.2),
            pos=(0, 0, 0),
            parent=self.game.aspect2d,
            sortOrder=2
        )
        
        self.tooltip_title = DirectLabel(
            text="",
            text_fg=(1, 0.8, 0.2, 1),
            text_scale=0.05,
            frameColor=(0, 0, 0, 0),
            pos=(0, 0, 0.15),
            parent=self.tooltip
        )
        
        self.tooltip_desc = DirectLabel(
            text="",
            text_fg=(1, 1, 1, 1),
            text_scale=0.035,
            frameColor=(0, 0, 0, 0),
            pos=(0, 0, 0.05),
            text_wordwrap=12,
            text_align=TextNode.ACenter,
            parent=self.tooltip
        )
        
        self.tooltip_cost = DirectLabel(
            text="",
            text_fg=(0.2, 0.8, 0.2, 1),
            text_scale=0.035,
            frameColor=(0, 0, 0, 0),
            pos=(0, 0, -0.1),
            parent=self.tooltip
        )
        
        # Hide tooltip initially
        self.tooltip.hide()
        
        # Set up drag handling
        self.content_frame.bind(DGG.B1PRESS, self.start_drag)
        self.content_frame.bind(DGG.B1RELEASE, self.end_drag)
        self.content_frame.bind(DGG.WITHIN, self.update_drag)
        
        # Add skill points indicator
        self.skill_points_label = DirectLabel(
            text="Available Skill Points: 0",
            text_fg=(0.2, 1, 0.2, 1),
            text_scale=0.05,
            frameColor=(0, 0, 0, 0),
            pos=(-0.7, 0, 0.9),
            parent=self.root_frame
        )
        
        # Add monster essence indicator
        self.monster_essence_label = DirectLabel(
            text="Monster Essence: 0",
            text_fg=(0.8, 0.6, 1, 1),
            text_scale=0.05,
            frameColor=(0, 0, 0, 0),
            pos=(-0.7, 0, 0.8),
            parent=self.root_frame
        )
    
    def show(self):
        """Show the skill tree UI"""
        if self.root_frame:
            self.root_frame.show()
            self.refresh()
            
            # Update skill points and monster essence display
            if hasattr(self.player, 'skill_points'):
                self.skill_points_label['text'] = f"Available Skill Points: {self.player.skill_points}"
            
            if hasattr(self.player, 'inventory') and 'monster_essence' in self.player.inventory:
                self.monster_essence_label['text'] = f"Monster Essence: {self.player.inventory['monster_essence']}"
            
            # Pause game while skill tree is open
            if hasattr(self.game, 'set_paused'):
                self.game.set_paused(True)
            
            # Bind escape key to close
            self.game.accept("escape", self.hide)
    
    def hide(self):
        """Hide the skill tree UI"""
        if self.root_frame:
            self.root_frame.hide()
            self.tooltip.hide()
            
            # Resume game
            if hasattr(self.game, 'set_paused'):
                self.game.set_paused(False)
            
            # Unbind escape key
            self.game.ignore("escape")
    
    def refresh(self):
        """Refresh the skill tree display"""
        # Clear existing nodes
        for node_id, node_ui in self.node_frames.items():
            node_ui.destroy()
        self.node_frames = {}
        
        # Remove connection lines
        if self.connection_lines:
            self.connection_lines.removeNode()
        
        # Create connection lines
        self.connection_lines = self.create_connection_lines()
        self.connection_lines.reparentTo(self.content_frame)
        
        # Create node frames for each visible node
        visible_nodes = self.skill_tree.get_visible_nodes(self.player)
        for node in visible_nodes:
            self.create_node_frame(node)
            
        # Reset animation time
        self.animation_time = 0.0
        self.pulse_animations = {}
    
    def create_connection_lines(self):
        """Create connection lines between nodes with enhanced visuals"""
        lines = LineSegs()
        lines.setThickness(3.0)
        
        # First pass - draw connection background lines (wider, darker)
        for node_id, node in self.skill_tree.nodes.items():
            if not node.is_visible:
                continue
                
            for child in node.children:
                if not child.is_visible:
                    continue
                
                # Draw background line (wider, darker)
                lines.setColor(0.1, 0.1, 0.1, 0.7)
                lines.setThickness(5.0)
                
                # Calculate positions
                start_x, start_y = node.position
                end_x, end_y = child.position
                
                lines.moveTo(start_x, 0, start_y)
                lines.drawTo(end_x, 0, end_y)
        
        # Create the background lines node
        background_node = NodePath(lines.create())
        
        # Reset for foreground lines
        lines = LineSegs()
        lines.setThickness(3.0)
        
        # Second pass - draw foreground lines with appropriate colors
        for node_id, node in self.skill_tree.nodes.items():
            if not node.is_visible:
                continue
                
            for child in node.children:
                if not child.is_visible:
                    continue
                
                # Set color based on unlock status
                if node.is_unlocked and child.is_unlocked:
                    # Both nodes unlocked - bright green
                    lines.setColor(0.4, 1.0, 0.4, 0.9)
                elif node.is_unlocked:
                    # Parent unlocked, child locked - yellow (available)
                    lines.setColor(1.0, 0.9, 0.2, 0.8)
                else:
                    # Both locked - gray (unavailable)
                    lines.setColor(0.5, 0.5, 0.5, 0.5)
                
                # Fusion paths get special visual treatment
                if hasattr(child, 'skill_type') and str(child.skill_type).endswith('FUSION'):
                    # Fusion paths get a pulsing effect (implemented in update)
                    lines.setColor(0.7, 0.4, 1.0, 0.8)  # Purple for fusion paths
                
                # Calculate positions
                start_x, start_y = node.position
                end_x, end_y = child.position
                
                lines.moveTo(start_x, 0, start_y)
                lines.drawTo(end_x, 0, end_y)
        
        # Create a node for the foreground lines
        foreground_node = NodePath(lines.create())
        
        # Create a parent node for both line sets
        combined_node = NodePath("connection_lines")
        background_node.reparentTo(combined_node)
        foreground_node.reparentTo(combined_node)
        
        return combined_node
    
    def create_node_frame(self, node):
        """Create a UI element for a skill tree node with enhanced visuals"""
        # Determine the node's appearance based on its state and type
        if node.is_unlocked:
            # Unlocked node - show normal icon
            icon_path = node.icon if node.icon else "src/assets/generated/ui/default_node.png"
            frame_color = (0.3, 0.7, 0.3, 0.9)  # Green for unlocked
        elif self.can_unlock_node(node):
            # Can be unlocked - show normal icon with yellow frame
            icon_path = node.icon if node.icon else "src/assets/generated/ui/default_node.png"
            frame_color = (0.9, 0.8, 0.2, 0.9)  # Yellow for available
        elif node.is_visible:
            # Visible but not unlockable - show normal icon with locked overlay
            icon_path = node.icon if node.icon else "src/assets/generated/ui/default_node.png"
            frame_color = (0.5, 0.5, 0.5, 0.8)  # Gray for visible but locked
        else:
            # Not yet visible - show question mark
            icon_path = self.question_mark_icon
            frame_color = (0.4, 0.4, 0.5, 0.7)  # Dark gray for unknown
        
        # Create frame
        x, y = node.position
        node_frame = DirectButton(
            frameSize=(-0.05, 0.05, -0.05, 0.05),
            frameColor=frame_color,
            frameTexture=icon_path,
            relief=DGG.FLAT,
            pos=(x, 0, y),
            parent=self.content_frame,
            command=self.on_node_click,
            extraArgs=[node]
        )
        
        # Handle hover events
        node_frame.bind(DGG.ENTER, self.on_node_hover, [node])
        node_frame.bind(DGG.EXIT, self.on_node_hover_exit)
        
        # Add node name label
        node_label = DirectLabel(
            text=node.name if node.is_visible else "???",
            text_fg=(1, 1, 1, 1),
            text_scale=0.02,
            frameColor=(0.1, 0.1, 0.1, 0.7),
            pos=(0, 0, -0.07),
            parent=node_frame
        )
        
        # Add fusion overlay for fusion nodes
        if hasattr(node, 'skill_type') and str(node.skill_type).endswith('FUSION'):
            fusion_overlay = DirectFrame(
                frameSize=(-0.05, 0.05, -0.05, 0.05),
                frameColor=(1, 1, 1, 0.8),
                frameTexture=self.fusion_icon_overlay,
                parent=node_frame,
                pos=(0, 0, 0)
            )
            # Store reference to animate the overlay
            self.pulse_animations[node.node_id] = {
                'overlay': fusion_overlay,
                'base_scale': 1.0,
                'phase': 0.0
            }
        
        # Add locked overlay for visible but locked nodes
        if not node.is_unlocked and node.is_visible and not self.can_unlock_node(node):
            locked_overlay = DirectFrame(
                frameSize=(-0.05, 0.05, -0.05, 0.05),
                frameColor=(1, 1, 1, 0.5),
                frameTexture=self.locked_icon,
                parent=node_frame,
                pos=(0, 0, 0)
            )
        
        # Store frame reference
        self.node_frames[node.node_id] = node_frame
        
        return node_frame
    
    def can_unlock_node(self, node):
        """Check if a node can be unlocked by the player"""
        can_unlock, _ = node.can_unlock(self.player)
        return can_unlock
    
    def on_node_click(self, node):
        """Handle node click events"""
        if not node.is_unlocked:
            # Try to unlock
            if node.unlock(self.player):
                # Success - refresh the UI
                self.refresh()
                
                # Apply node effects
                node.apply_effects(self.player)
                
                # Update skill points and monster essence display
                if hasattr(self.player, 'skill_points'):
                    self.skill_points_label['text'] = f"Available Skill Points: {self.player.skill_points}"
                
                if hasattr(self.player, 'inventory') and 'monster_essence' in self.player.inventory:
                    self.monster_essence_label['text'] = f"Monster Essence: {self.player.inventory['monster_essence']}"
            else:
                # Failed - show detailed reason in tooltip
                can_unlock, reason = node.can_unlock(self.player)
                self.show_tooltip(node, reason)
        else:
            # Already unlocked - show effects
            self.show_tooltip(node, "Already unlocked")
    
    def on_node_hover(self, node, event=None):
        """Handle node hover events"""
        # Show tooltip with info
        self.show_tooltip(node)
        
        # Highlight the node
        if node.node_id in self.node_frames:
            frame = self.node_frames[node.node_id]
            original_color = frame['frameColor']
            # Brighten the frame color
            frame['frameColor'] = (
                min(original_color[0] + 0.2, 1.0),
                min(original_color[1] + 0.2, 1.0),
                min(original_color[2] + 0.2, 1.0),
                original_color[3]
            )
    
    def show_tooltip(self, node, extra_info=None):
        """Show tooltip with node information"""
        if not node.is_visible and not extra_info:
            # Don't show tooltip for invisible nodes
            self.tooltip.hide()
            return
            
        # Set tooltip position near the mouse
        mouse_x = self.game.mouseWatcherNode.getMouseX()
        mouse_y = self.game.mouseWatcherNode.getMouseY()
        self.tooltip.setPos(mouse_x + 0.3, 0, mouse_y)
        
        # Set tooltip content
        if node.is_visible:
            self.tooltip_title['text'] = node.name
            self.tooltip_desc['text'] = node.description
            
            # Format cost
            cost_text = "Cost: "
            for resource, amount in node.cost.items():
                cost_text += f"{amount} {resource.replace('_', ' ')}, "
            cost_text = cost_text.rstrip(", ")
            
            self.tooltip_cost['text'] = cost_text
        else:
            self.tooltip_title['text'] = "Unknown Skill"
            self.tooltip_desc['text'] = "This skill is not yet visible."
            self.tooltip_cost['text'] = ""
        
        # Add extra info if provided
        if extra_info:
            self.tooltip_desc['text'] += f"\n\n{extra_info}"
        
        # Show the tooltip
        self.tooltip.show()
    
    def on_node_hover_exit(self, event=None):
        """Handle node hover exit events"""
        self.tooltip.hide()
        
        # Reset frame colors for all nodes
        self.refresh()
    
    def zoom_in(self):
        """Zoom in the skill tree view"""
        self.zoom = min(2.0, self.zoom + 0.25)
        self.content_frame.setScale(self.zoom)
    
    def zoom_out(self):
        """Zoom out the skill tree view"""
        self.zoom = max(0.5, self.zoom - 0.25)
        self.content_frame.setScale(self.zoom)
    
    def reset_view(self):
        """Reset the view to default position and zoom"""
        self.zoom = 1.0
        self.content_frame.setScale(1.0)
        self.content_frame.setPos(0, 0, 0)
        
        # Reset scroll bars
        self.scroll_frame.verticalScroll['value'] = 0.5
        self.scroll_frame.horizontalScroll['value'] = 0.5
    
    def start_drag(self, event):
        """Start dragging the skill tree view"""
        self.is_dragging = True
        self.drag_start = (event.getMouse()[0], event.getMouse()[1])
        
        # Store current position
        curr_pos = self.content_frame.getPos()
        self.offset = (curr_pos[0], curr_pos[2])
    
    def end_drag(self, event):
        """End dragging the skill tree view"""
        self.is_dragging = False
    
    def update_drag(self, event):
        """Update dragging of the skill tree view"""
        if self.is_dragging:
            # Calculate mouse movement
            curr_x, curr_y = event.getMouse()
            dx = curr_x - self.drag_start[0]
            dy = curr_y - self.drag_start[1]
            
            # Scale by zoom factor
            dx *= self.zoom * 2
            dy *= self.zoom * 2
            
            # Update position
            new_x = self.offset[0] + dx
            new_y = self.offset[1] + dy
            self.content_frame.setPos(new_x, 0, new_y)
    
    def update(self, dt):
        """Update animations and effects"""
        # Update animation time
        self.animation_time += dt
        
        # Update pulse animations for fusion nodes
        for node_id, anim_data in self.pulse_animations.items():
            # Calculate pulse effect (sine wave)
            pulse = math.sin(self.animation_time * 2.0 + anim_data['phase']) * 0.1 + 1.0
            
            # Apply to overlay
            if 'overlay' in anim_data:
                anim_data['overlay'].setScale(pulse * anim_data['base_scale'])
        
        # Optionally, animate connection lines for fusion paths
        if self.connection_lines:
            # Could implement line animations here
            pass 