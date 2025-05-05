# Architecture du Système de Combat

## Vue d'Ensemble
Le système de combat est basé sur une architecture ECS (Entity Component System) qui sépare les données (Components) de la logique (Systems) et des entités.

## Composants Principaux
- AbilityStats : Statistiques des capacités
- Cooldown : Gestion des temps de recharge
- Targeting : Système de ciblage

## Flux de Données
1. Input -> InputManager
2. InputManager -> AbilitySystem
3. AbilitySystem -> Components
4. Components -> Effects
5. Effects -> Renderer

## Intégration
- Avec TimeSystem pour le cycle jour/nuit
- Avec RenderSystem pour les effets visuels
- Avec World pour la gestion des entités