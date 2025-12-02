"""
COMP 163 - Project 3: Quest Chronicles
Combat System Module - Starter Code
 
Name: Daylen Hicks

AI Usage: Used an AI assistant to help explain and break down the
          logic, discuss the overall approach, and fix syntactical errors.

Handles combat mechanics
"""

import random
# We need character_manager for healing and for awarding XP
import character_manager
from custom_exceptions import (
    InvalidTargetError,
    CombatNotActiveError,
    CharacterDeadError,
    AbilityOnCooldownError  # We won't implement cooldowns to keep it simple
)

# ============================================================================
# ENEMY DEFINITIONS
# ============================================================================

def create_enemy(enemy_type):
    """
    Create an enemy based on type
    
    Raises: InvalidTargetError if enemy_type not recognized
    """
    if enemy_type == "goblin":
        return {
            'name': 'Goblin', 'health': 50, 'max_health': 50,
            'strength': 8, 'magic': 2, 'xp_reward': 25, 'gold_reward': 10
        }
    elif enemy_type == "orc":
        return {
            'name': 'Orc', 'health': 80, 'max_health': 80,
            'strength': 12, 'magic': 5, 'xp_reward': 50, 'gold_reward': 25
        }
    elif enemy_type == "dragon":
        return {
            'name': 'Dragon', 'health': 200, 'max_health': 200,
            'strength': 25, 'magic': 15, 'xp_reward': 200, 'gold_reward': 100
        }
    else:
        # This is for your Creativity Bonus if you add more
        # As long as the required 3 exist, this is fine.
        raise InvalidTargetError(f"Enemy type '{enemy_type}' not recognized.")

def get_random_enemy_for_level(character_level):
    """
    Get an appropriate enemy for character's level
    
    """
    if character_level <= 2:
        return create_enemy("goblin")
    elif character_level <= 5:
        return create_enemy("orc")
    else:
        return create_enemy("dragon")

# ============================================================================
# COMBAT SYSTEM
# ============================================================================

class SimpleBattle:
    """
    Simple turn-based combat system
    Manages combat between character and enemy
    """
    
    def __init__(self, character, enemy):
        """Initialize battle with character and enemy"""
        self.character = character
        self.enemy = enemy
        self.combat_active = False
        self.turn = 1
        # Cooldown: 0 means ready, >0 is turns remaining
        self.ability_cooldown = 0
    
    def start_battle(self):
        """
        Start the combat loop
        
        Raises: CharacterDeadError if character is already dead
        """
        if self.character['health'] <= 0:
            raise CharacterDeadError("Cannot start battle, character is dead.")
            
        self.combat_active = True
        self.turn = 1
        display_battle_log(f"A wild {self.enemy['name']} appears!")
        
        winner = None
        
        while self.combat_active:
            display_battle_log(f"--- Turn {self.turn} ---")
            
            # --- Player Turn ---
            self.player_turn()
            
            # Check for win or escape
            if not self.combat_active:
                winner = 'escaped'
                break
                
            winner = self.check_battle_end()
            if winner:
                break
                
            # --- Enemy Turn ---
            self.enemy_turn()
            
            winner = self.check_battle_end()
            if winner:
                break
                
            self.turn += 1
            # Cooldown ticks down each turn
            if self.ability_cooldown > 0:
                self.ability_cooldown -= 1

        # --- Battle Over ---
        if winner == 'player':
            display_battle_log(f"You defeated the {self.enemy['name']}!")
            rewards = get_victory_rewards(self.enemy)
            
            # Use character_manager to safely grant rewards
            character_manager.gain_experience(self.character, rewards['xp'])
            character_manager.add_gold(self.character, rewards['gold'])
            
            return {
                'winner': 'player', 
                'xp_gained': rewards['xp'], 
                'gold_gained': rewards['gold']
            }
        elif winner == 'enemy':
            display_battle_log("You have been defeated... Game Over.")
            return {'winner': 'enemy', 'xp_gained': 0, 'gold_gained': 0}
        else: # Player escaped
            display_battle_log("You fled from the battle.")
            return {'winner': 'none', 'xp_gained': 0, 'gold_gained': 0}

    
    def player_turn(self):
        """
        Handle player's turn
        
        Raises: CombatNotActiveError if called outside of battle
        """
        if not self.combat_active:
            raise CombatNotActiveError("player_turn called when combat is not active.")
            
        display_combat_stats(self.character, self.enemy)
        
        print("\n--- Your Turn ---")
        print("1. Basic Attack")
        print(f"2. Special Ability ({self.character['class']})")
        print("3. Try to Run")
        
        choice = input("Choose your action (1-3): ")
        
        if choice == '1':
            # Basic Attack
            display_battle_log("You attack!")
            damage = self.calculate_damage(self.character, self.enemy)
            self.apply_damage(self.enemy, damage)
            display_battle_log(f"The {self.enemy['name']} takes {damage} damage.")
            
        elif choice == '2':
            # Special Ability
            if self.ability_cooldown > 0:
                display_battle_log(
                    f"Ability on cooldown! {self.ability_cooldown} turns left."
                )
                # Player wastes their turn
                return

            try:
                # We pass 'self' (the battle object) so helpers can use it
                message = use_special_ability(self.character, self.enemy, self)
                display_battle_log(message)
                # Set cooldown (e.g., 3 turns)
                self.ability_cooldown = 3 
            except Exception as e:
                display_battle_log(f"Ability failed: {e}")
                
        elif choice == '3':
            # Try to Run
            self.attempt_escape()
            
        else:
            display_battle_log("Invalid choice. You hesitate and lose your turn.")
    
    def enemy_turn(self):
        """
        Handle enemy's turn - simple AI
        
        Raises: CombatNotActiveError if called outside of battle
        """
        if not self.combat_active:
            raise CombatNotActiveError("enemy_turn called when combat is not active.")

        display_battle_log(f"The {self.enemy['name']} attacks!")
        damage = self.calculate_damage(self.enemy, self.character)
        self.apply_damage(self.character, damage)
        display_battle_log(f"You take {damage} damage.")
    
    def calculate_damage(self, attacker, defender):
        """
        Calculate damage from attack
        
        Returns: Integer damage amount
        """
        # We'll use a slightly different calc for player vs. enemy
        if 'class' in attacker: # Attacker is player
            base_damage = attacker['strength']
        else: # Attacker is enemy
            base_damage = attacker['strength']
            
        # Simple defense calculation (not in starter, but makes sense)
        # Let's use the one from the docstring
        damage = base_damage - (defender['strength'] // 4)
        
        # Minimum damage is 1
        return max(1, damage)
    
    def apply_damage(self, target, damage):
        """
        Apply damage to a character or enemy
        
        """
        target['health'] -= damage
        # Prevent health from going below 0
        target['health'] = max(0, target['health'])
    
    def check_battle_end(self):
        """
        Check if battle is over
        
        """
        if self.character['health'] <= 0:
            self.combat_active = False
            return 'enemy'
        elif self.enemy['health'] <= 0:
            self.combat_active = False
            return 'player'
        
        return None
    
    def attempt_escape(self):
        """
        Try to escape from battle
        
        """
        # 50% success chance
        if random.random() < 0.5:
            display_battle_log("You successfully escaped!")
            self.combat_active = False # This will end the battle loop
            return True
        else:
            display_battle_log("You failed to escape!")
            return False

# ============================================================================
# SPECIAL ABILITIES
# ============================================================================

def use_special_ability(character, enemy, battle):
    """
    Use character's class-specific special ability
    
    We pass the 'battle' object so helpers can use its methods
    """
    char_class = character['class']
    
    if char_class == 'Warrior':
        return warrior_power_strike(character, enemy, battle)
    elif char_class == 'Mage':
        return mage_fireball(character, enemy, battle)
    elif char_class == 'Rogue':
        return rogue_critical_strike(character, enemy, battle)
    elif char_class == 'Cleric':
        return cleric_heal(character, battle)
    else:
        return "You have no special ability."

def warrior_power_strike(character, enemy, battle):
    """Warrior: Power Strike (2x strength damage)"""
    # Use a modified damage calc
    damage = (character['strength'] * 2) - (enemy['strength'] // 4)
    damage = max(1, damage)
    battle.apply_damage(enemy, damage)
    return f"You use Power Strike for {damage} damage!"

def mage_fireball(character, enemy, battle):
    """Mage: Fireball (2x magic damage)"""
    # Uses magic stat instead of strength
    damage = (character['magic'] * 2) - (enemy['magic'] // 4) # Simple magic defense
    damage = max(1, damage)
    battle.apply_damage(enemy, damage)
    return f"You cast Fireball for {damage} damage!"

def rogue_critical_strike(character, enemy, battle):
    """Rogue: Critical Strike (3x strength damage, 50% chance)"""
    if random.random() < 0.5: # 50% chance
        damage = (character['strength'] * 3) - (enemy['strength'] // 4)
        damage = max(1, damage)
        battle.apply_damage(enemy, damage)
        return f"CRITICAL STRIKE! You deal {damage} damage!"
    else:
        return "Your critical strike missed..."

def cleric_heal(character, battle):
    """Cleric: Heal (restore 30 health)"""
    # We MUST use character_manager's heal function
    # to correctly handle the max_health cap
    healed_amount = character_manager.heal_character(character, 30)
    return f"You use Heal, restoring {healed_amount} HP."

# ============================================================================
# COMBAT UTILITIES
# ============================================================================

def can_character_fight(character):
    """
    Check if character is in condition to fight
    
    """
    # We just check if they are alive
    return character['health'] > 0

def get_victory_rewards(enemy):
    """
    Calculate rewards for defeating enemy
    
    """
    return {'xp': enemy['xp_reward'], 'gold': enemy['gold_reward']}

def display_combat_stats(character, enemy):
    """
    Display current combat status
    
    """
    print(f"\n{character['name']}: HP={character['health']}/{character['max_health']}")
    print(f"{enemy['name']}: HP={enemy['health']}/{enemy['max_health']}")

def display_battle_log(message):
    """
    Display a formatted battle message
    """
    print(f">>> {message}")

# ============================================================================
# TESTING
# ============================================================================

if __name__ == "__main__":
    print("=== COMBAT SYSTEM TEST ===")
    
    # Test enemy creation
    # try:
    #     goblin = create_enemy("goblin")
    #     print(f"Created {goblin['name']}")
    # except InvalidTargetError as e:
    #     print(f"Invalid enemy: {e}")
    
    # Test battle
    # test_char = {
    #     'name': 'Hero',
    #     'class': 'Warrior',
    #     'health': 120,
    #     'max_health': 120,
    #     'strength': 15,
    #     'magic': 5
    # }
    #
    # battle = SimpleBattle(test_char, goblin)
    # try:
    #     result = battle.start_battle()
    #     print(f"Battle result: {result}")
    # except CharacterDeadError:
    #     print("Character is dead!")
