"""
COMP 163 - Project 3: Quest Chronicles
Game Data Module - Starter Code

Name: Daylen Hicks

AI Usage: Used an AI assistant to help explain and break down the
          logic, discuss the overall approach, and fix syntactical errors. Also helped with starter File.

This module handles loading and validating game data from text files.
"""

import os
from custom_exceptions import (
    InvalidDataFormatError,
    MissingDataFileError,
    CorruptedDataError
)

# ============================================================================
# DATA LOADING FUNCTIONS
# ============================================================================

def load_quests(filename="data/quests.txt"):
    """
    Load quest data from file
    
    Expected format per quest (separated by blank lines):
    QUEST_ID: unique_quest_name
    TITLE: Quest Display Title
    DESCRIPTION: Quest description text
    REWARD_XP: 100
    REWARD_GOLD: 50
    REQUIRED_LEVEL: 1
    PREREQUISITE: previous_quest_id (or NONE)
    
    Returns: Dictionary of quests {quest_id: quest_data_dict}
    Raises: MissingDataFileError, InvalidDataFormatError, CorruptedDataError
    """
    # TODO: Implement this function
    # Must handle:
    # - FileNotFoundError → raise MissingDataFileError
    # - Invalid format → raise InvalidDataFormatError
    # - Corrupted/unreadable data → raise CorruptedDataError
    all_quests = {}

    if not os.path.exists(filename):
        raise MissingDataFileError(f"Quest data file '{filename}' not found.")
    try:
        with open(filename, 'r') as file:
            content = file.read()
        quest_blocks = content.split('\n\n')
        
        for block in quest_blocks:
            block = block.strip() # Remove leading/trailing whitespace
            if not block:
                continue # Skip empty blocks

            lines = block.split('\n')
            
            # 2. Parse the block
            quest_data = parse_quest_block(lines)
            
            # 3. Validate the parsed data
            validate_quest_data(quest_data)
            
            # 4. Add to the main dictionary
            quest_id = quest_data['quest_id']
            if quest_id in all_quests:
                # This is a form of corruption/invalid data
                raise InvalidDataFormatError(f"Duplicate QUEST_ID found: {quest_id}")
                
            all_quests[quest_id] = quest_data
            
    except InvalidDataFormatError as e:
        # Re-raise the specific error from our helpers
        raise e
    except IOError as e:
        # File exists but we couldn't read it (permissions, etc.)
        raise CorruptedDataError(f"Could not read quest file: {e}")
    except Exception as e:
        # Catch any other unexpected errors (e.g., duplicate ID)
        raise CorruptedDataError(f"An unexpected error occurred parsing quests: {e}")

    return all_quests

def load_items(filename="data/items.txt"):
    """
    Load item data from file
    
    Expected format per item (separated by blank lines):
    ITEM_ID: unique_item_name
    NAME: Item Display Name
    TYPE: weapon|armor|consumable
    EFFECT: stat_name:value (e.g., strength:5 or health:20)
    COST: 100
    DESCRIPTION: Item description
    
    Returns: Dictionary of items {item_id: item_data_dict}
    Raises: MissingDataFileError, InvalidDataFormatError, CorruptedDataError
    """
    # TODO: Implement this function
    # Must handle same exceptions as load_quests
    all_items = {}
    
    # 1. Check for file existence -> MissingDataFileError
    if not os.path.exists(filename):
        raise MissingDataFileError(f"Item data file not found at: {filename}")

    try:
        with open(filename, 'r') as f:
            content = f.read()
            
        item_blocks = content.split('\n\n')
        
        for block in item_blocks:
            block = block.strip()
            if not block:
                continue

            lines = block.split('\n')
            
            # 2. Parse
            item_data = parse_item_block(lines)
            
            # 3. Validate
            validate_item_data(item_data)
            
            # 4. Add to main dictionary
            item_id = item_data['item_id']
            if item_id in all_items:
                raise InvalidDataFormatError(f"Duplicate ITEM_ID found: {item_id}")
                
            all_items[item_id] = item_data
            
    except InvalidDataFormatError as e:
        raise e
    except IOError as e:
        raise CorruptedDataError(f"Could not read item file: {e}")
    except Exception as e:
        raise CorruptedDataError(f"An unexpected error occurred parsing items: {e}")

    return all_items

def validate_quest_data(quest_dict):
    """
    Validate that quest dictionary has all required fields
    
    Required fields: quest_id, title, description, reward_xp, 
                    reward_gold, required_level, prerequisite
    
    Returns: True if valid
    Raises: InvalidDataFormatError if missing required fields
    """
    # TODO: Implement validation
    # Check that all required keys exist
    # Check that numeric values are actually numbers
    REQUIRED_KEYS = [
        'quest_id', 'title', 'description', 'reward_xp', 
        'reward_gold', 'required_level', 'prerequisite'
    ]
    NUMERIC_KEYS = ['reward_xp', 'reward_gold', 'required_level']
    
    for key in REQUIRED_KEYS:
        if key not in quest_dict:
            raise InvalidDataFormatError(f"Quest data is missing required field: {key}")

    for key in NUMERIC_KEYS:
        if not isinstance(quest_dict[key], int):
            raise InvalidDataFormatError(f"Quest field '{key}' must be a number.")
            
    return True

def validate_item_data(item_dict):
    """
    Validate that item dictionary has all required fields
    
    Required fields: item_id, name, type, effect, cost, description
    Valid types: weapon, armor, consumable
    
    Returns: True if valid
    Raises: InvalidDataFormatError if missing required fields or invalid type
    """
    # TODO: Implement validation
    REQUIRED_KEYS = ['item_id', 'name', 'type', 'effect', 'cost', 'description']
    NUMERIC_KEYS = ['cost']
    VALID_TYPES = ['weapon', 'armor', 'consumable']
    
    for key in REQUIRED_KEYS:
        if key not in item_dict:
            raise InvalidDataFormatError(f"Item data is missing required field: {key}")

    for key in NUMERIC_KEYS:
        if not isinstance(item_dict[key], int):
            raise InvalidDataFormatError(f"Item field '{key}' must be a number.")
            
    if item_dict['type'] not in VALID_TYPES:
        raise InvalidDataFormatError(f"Invalid item TYPE: {item_dict['type']}. Must be one of {VALID_TYPES}")

    return True

def create_default_data_files():
    """
    Create default data files if they don't exist
    This helps with initial setup and testing
    """
    # TODO: Implement this function
    # Create data/ directory if it doesn't exist
    # Create default quests.txt and items.txt files
    # Handle any file permission errors appropriately
    try:
        if not os.path.exists("data"):
            os.makedirs("data")
            
        # Default Quests
        if not os.path.exists("data/quests.txt"):
            with open("data/quests.txt", "w") as f:
                f.write(
"""QUEST_ID: goblin_slayer_1
TITLE: Goblin Menace
DESCRIPTION: Goblins are harassing travelers. Clear them out!
REWARD_XP: 100
REWARD_GOLD: 50
REQUIRED_LEVEL: 1
PREREQUISITE: NONE

QUEST_ID: orc_leader
TITLE: The Orc Warlord
DESCRIPTION: Defeat the Orc Warlord ruling the cursed plains.
REWARD_XP: 500
REWARD_GOLD: 250
REQUIRED_LEVEL: 5
PREREQUISITE: goblin_slayer_1

QUEST_ID: dragon_hunt
TITLE: The Red Dragon
DESCRIPTION: A great red dragon is terrorizing the mountain. Slay it.
REWARD_XP: 2000
REWARD_GOLD: 1000
REQUIRED_LEVEL: 10
PREREQUISITE: orc_leader
""")

        # Default Items
        if not os.path.exists("data/items.txt"):
            with open("data/items.txt", "w") as f:
                f.write(
"""ITEM_ID: potion_health_1
NAME: Small Health Potion
TYPE: consumable
EFFECT: health:25
COST: 50
DESCRIPTION: A simple potion that restores 25 HP.

ITEM_ID: sword_basic
NAME: Rusty Sword
TYPE: weapon
EFFECT: strength:3
COST: 20
DESCRIPTION: An old, rusty sword. Better than nothing.

ITEM_ID: leather_armor
NAME: Leather Tunic
TYPE: armor
EFFECT: max_health:10
COST: 30
DESCRIPTION: A tunic made of boiled leather.
""")
        print("Default data files created successfully.")
        
    except IOError as e:
        print(f"Error creating default data files: {e}")
        # In a real game, you might want to raise this
        # but for setup, printing the error is fine.

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

# We create maps to convert file keys (UPPERCASE) 
# to our dictionary keys (lowercase_snake_case)
QUEST_KEY_MAP = {
    "QUEST_ID": "quest_id",
    "TITLE": "title",
    "DESCRIPTION": "description",
    "REWARD_XP": "reward_xp",
    "REWARD_GOLD": "reward_gold",
    "REQUIRED_LEVEL": "required_level",
    "PREREQUISITE": "prerequisite"
}
QUEST_NUMERIC_KEYS = ["REWARD_XP", "REWARD_GOLD", "REQUIRED_LEVEL"]

ITEM_KEY_MAP = {
    "ITEM_ID": "item_id",
    "NAME": "name",
    "TYPE": "type",
    "EFFECT": "effect",
    "COST": "cost",
    "DESCRIPTION": "description"
}
ITEM_NUMERIC_KEYS = ["COST"]


def parse_quest_block(lines):
    """
    Parse a block of lines into a quest dictionary
    
    Args:
        lines: List of strings representing one quest
    
    Returns: Dictionary with quest data
    Raises: InvalidDataFormatError if parsing fails
    """
    # TODO: Implement parsing logic
    # Split each line on ": " to get key-value pairs
    # Convert numeric strings to integers
    # Handle parsing errors gracefully
    quest_data = {}
    try:
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Split on the *first* colon-space only
            key, value = line.split(": ", 1)
            
            # Find our internal key name (e.g., "TITLE" -> "title")
            dict_key = QUEST_KEY_MAP[key]
            
            # Convert to number if needed
            if key in QUEST_NUMERIC_KEYS:
                quest_data[dict_key] = int(value)
            else:
                quest_data[dict_key] = value
                
    except (ValueError, KeyError, IndexError) as e:
        # ValueError: int() failed
        # KeyError: The key (e.g., "TITL") wasn't in our QUEST_KEY_MAP
        # IndexError: split(": ") failed
        raise InvalidDataFormatError(f"Failed to parse quest block. Bad line: '{line}'. Error: {e}")
        
    return quest_data

def parse_item_block(lines):
    """
    Parse a block of lines into an item dictionary
    
    Args:
        lines: List of strings representing one item
    
    Returns: Dictionary with item data
    Raises: InvalidDataFormatError if parsing fails
    """
    # TODO: Implement parsing logic
    item_data = {}
    try:
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            key, value = line.split(": ", 1)
            
            # Find our internal key name (e.g., "ITEM_ID" -> "item_id")
            dict_key = ITEM_KEY_MAP[key]
            
            # Convert to number if needed
            if key in ITEM_NUMERIC_KEYS:
                item_data[dict_key] = int(value)
            else:
                item_data[dict_key] = value
                
    except (ValueError, KeyError, IndexError) as e:
        raise InvalidDataFormatError(f"Failed to parse item block. Bad line: '{line}'. Error: {e}")
        
    return item_data

# ============================================================================
# TESTING
# ============================================================================

if __name__ == "__main__":
    print("=== GAME DATA MODULE TEST ===")
    
    # Test creating default files
    # create_default_data_files()
    
    # Test loading quests
    # try:
    #     quests = load_quests()
    #     print(f"Loaded {len(quests)} quests")
    # except MissingDataFileError:
    #     print("Quest file not found")
    # except InvalidDataFormatError as e:
    #     print(f"Invalid quest format: {e}")
    
    # Test loading items
    # try:
    #     items = load_items()
    #     print(f"Loaded {len(items)} items")
    # except MissingDataFileError:
    #     print("Item file not found")
    # except InvalidDataFormatError as e:
    #     print(f"Invalid item format: {e}")

