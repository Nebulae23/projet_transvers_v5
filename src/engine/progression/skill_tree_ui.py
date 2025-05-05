# src/engine/progression/skill_tree_ui.py
import pygame
from typing import Dict, List, Optional, Tuple
from ..ui.ui_base import UIElement, UIElementType, TextElement
from .skills import SkillTree, SkillNode

class SkillNodeUI(UIElement):
    def __init__(self,
                position: Tuple[int, int],
                size: Tuple[int, int],
                node: SkillNode,
                skill_tree: SkillTree):
        super().__init__(position, size, UIElementType.CONTAINER)
        self.node = node
        self.skill_tree = skill_tree
        self.selected = False
        
        # Set up visual properties
        self.normal_color = (64, 64, 64)
        self.hover_color = (96, 96, 96)
        self.selected_color = (128, 128, 0)
        self.unlocked_color = (0, 128, 0)
        self.set_background(self.normal_color)
        
        # Create icon and text
        self.icon = pygame.image.load(node.icon_path)
        self.icon = pygame.transform.scale(self.icon, (size[0]-8, size[0]-8))
        
        self.name_text = TextElement(
            (position[0], position[1] + size[1] - 20),
            node.name,
            16
        )
        self.add_child(self.name_text)
        
    def draw(self, surface: pygame.Surface):
        # Draw connection lines to prerequisites
        if not self.node.prerequisites:
            return
            
        for prereq_id in self.node.prerequisites:
            if prereq_id in self.skill_tree.nodes:
                prereq = self.skill_tree.nodes[prereq_id]
                start_pos = (
                    prereq.position[0] * self.size[0] + self.size[0]//2,
                    prereq.position[1] * self.size[1] + self.size[1]//2
                )
                end_pos = (
                    self.position[0] + self.size[0]//2,
                    self.position[1] + self.size[1]//2
                )
                
                # Draw line
                color = (0, 128, 0) if (prereq_id in self.skill_tree.unlocked_skills and 
                                      self.node.id in self.skill_tree.unlocked_skills) else (64, 64, 64)
                pygame.draw.line(surface, color, start_pos, end_pos, 2)
                
        super().draw(surface)
        
        # Draw icon
        surface.blit(self.icon, (self.position[0]+4, self.position[1]+4))
        
        # Draw unlock status
        if self.node.id in self.skill_tree.unlocked_skills:
            self.set_background(self.unlocked_color)
        elif self.selected:
            self.set_background(self.selected_color)
        else:
            self.set_background(self.normal_color)

class SkillTreeUI(UIElement):
    def __init__(self,
                position: Tuple[int, int],
                size: Tuple[int, int],
                skill_tree: SkillTree):
        super().__init__(position, size, UIElementType.CONTAINER)
        self.skill_tree = skill_tree
        self.node_size = (80, 100)
        self.selected_node: Optional[SkillNodeUI] = None
        
        # Create title
        self.title = TextElement(
            (position[0], position[1] - 40),
            "Skill Tree",
            32
        )
        self.add_child(self.title)
        
        # Create points display
        self.points_text = TextElement(
            (position[0] + size[0] - 150, position[1] - 40),
            f"Points: {skill_tree.available_points}",
            24
        )
        self.add_child(self.points_text)
        
        # Create skill node UIs
        self.node_uis: Dict[str, SkillNodeUI] = {}
        self._create_node_uis()
        
        # Create description panel
        self.description_panel = TextElement(
            (position[0], position[1] + size[1] + 10),
            "Select a skill to view details",
            20
        )
        self.add_child(self.description_panel)
        
    def _create_node_uis(self):
        for node_id, node in self.skill_tree.nodes.items():
            ui_pos = (
                self.position[0] + node.position[0] * (self.node_size[0] + 40),
                self.position[1] + node.position[1] * (self.node_size[1] + 40)
            )
            
            node_ui = SkillNodeUI(
                ui_pos,
                self.node_size,
                node,
                self.skill_tree
            )
            node_ui.set_click_handler(lambda n=node_ui: self._on_node_click(n))
            
            self.node_uis[node_id] = node_ui
            self.add_child(node_ui)
            
    def _on_node_click(self, node_ui: SkillNodeUI):
        # Deselect previous node
        if self.selected_node:
            self.selected_node.selected = False
            
        # Select new node
        self.selected_node = node_ui
        node_ui.selected = True
        
        # Update description
        desc_text = (f"{node_ui.node.name}\n\n"
                    f"{node_ui.node.description}\n\n"
                    f"Cost: {node_ui.node.cost} skill points\n"
                    f"Effects: {', '.join(f'{k}: +{v}' for k,v in node_ui.node.effects.items())}")
        self.description_panel.set_text(desc_text)
        
        # Try to unlock if possible
        if self.skill_tree.unlock_skill(node_ui.node.id):
            self.points_text.set_text(f"Points: {self.skill_tree.available_points}")
            
    def update(self):
        self.points_text.set_text(f"Points: {self.skill_tree.available_points}")
        for node_ui in self.node_uis.values():
            node_ui.draw_surface = None  # Force redraw