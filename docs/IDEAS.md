# Ideas

## 🎯 Core Roguelike Mechanics That Fit Well
1. Items/Pickups (Easy to add)
    - Spawned randomly on the map
    - Mine Detector: Reveals adjacent mines permanently
    - Shield: Survive one mine hit
    - Teleport Scroll: Jump to random safe position
    - Vision Potion: Temporarily show all mines (3 moves)
    - Lucky Charm: Double score for this level
    - Compass: Shows direction to exit

2. Permanent Upgrades (Roguelite style)
    - Unlock with accumulated score
    - Wider Proximity: See mines 2 tiles away instead of 1
    - Extra Life: Start with 4 lives instead of 3
    - Better Scoring: 2.0× max efficiency bonus instead of 1.5×
    - Death Insurance: Only lose 25 points instead of 50
    - Starting Shield: Begin each life with 1-hit protection

3. Per-Run Abilities (Choose at start or find)
    - Cautious: See proximity in 8 directions (diagonals too)
    - Reckless: Move 2 tiles at once, higher score multiplier
    - Archaeologist: Can mark suspected mine positions
    - Ghost: First 5 moves can't hit mines
    - Speedrunner: Bonus points for fast completion

4. Environmental Hazards (Not just mines)
    - Fog tiles: Can't see proximity until you step there
    - Cracked floor: Breaks after stepping (one-way paths)
    - Teleport tiles: Warp you to another location
    - Ice patches: Slide until you hit wall/obstacle
    - Locked doors: Need keys to pass

## 🗺️ Map/Exploration Mechanics

5. Minimap (Top corner) shows:
    - Visited tiles (dim)
    - Current position
    - Exit location (?)
    - Found items
    - Marked suspicious tiles

6. FOV/Vision System
    - Only see 3-5 tiles around you
    - Visited tiles remembered
    - Makes navigation more challenging
    - Items/hazards discovered gradually

7. Procedural Room Layouts
    - Corridors and chambers
    - Multiple paths to exit
    - Dead ends with treasures
    - Secret passages

## 👾 Enemies/NPCs (Bigger change)

8. Neutral Entities
    - Minesweeper Ally: Shows safe path if you reach them
    - Merchant: Trade score for items
    - Oracle: Reveals mine count in regions
    - Ghost: Shows optimal path briefly

9. Active Threats (Roguelike-style)
    - Patrolling Guards: Move on their turns, force you to time moves
    - Chasing Enemies: Hunt you, force risky decisions
    - Mine Layers: Add new mines as you play
    - Trap Setters: Block paths behind you

## 🎲 Roguelike Meta-Progression

10. Daily Challenges
    - Same seed for all players
    - Special constraints (limited moves, no items, etc.)
    - Leaderboard
    - Unique rewards

11. Character Classes
    - Engineer: Disarm 3 mines per level
    - Scout: +2 vision range
    - Lucky: 10% fewer mines
    - Brute: Takes 2 hits to die
    - Speedster: Bonus for <optimal moves

12. Meta Unlocks
    - New tilesets/themes
    - Alt game modes
    - Character skins
    - Starting items
    - Score multipliers
