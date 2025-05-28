import random

# Rarity levels affect drop rates and shop availability
COMMON = "Common"
UNCOMMON = "Uncommon"
RARE = "Rare" 
EPIC = "Epic"
LEGENDARY = "Legendary"

# Probability weights for different rarities (used in random drops)
RARITY_WEIGHTS = {
    COMMON: 50,
    UNCOMMON: 30,
    RARE: 15,
    EPIC: 4,
    LEGENDARY: 1
}

class Equipment:
    """Base class for all equipment (weapons and armor)"""
    def __init__(self, name, price, is_illegal, rarity):
        self.name = name
        self.price = price
        self.is_illegal = is_illegal
        self.rarity = rarity

class Weapon(Equipment):
    """Weapon that increases player's damage output"""
    def __init__(self, name, damage, price, is_illegal=False, rarity=COMMON):
        super().__init__(name, price, is_illegal, rarity)
        self.damage = damage
        
    def __str__(self):
        legal_status = "ILLEGAL" if self.is_illegal else "Legal"
        return f"{self.name} ({self.rarity}) - {self.damage} damage - {self.price} credits - {legal_status}"

class Armor(Equipment):
    """Armor that reduces damage taken by player"""
    def __init__(self, name, defense, price, is_illegal=False, rarity=COMMON):
        super().__init__(name, price, is_illegal, rarity)
        self.defense = defense
        
    def __str__(self):
        legal_status = "ILLEGAL" if self.is_illegal else "Legal"
        return f"{self.name} ({self.rarity}) - {self.defense} defense - {self.price} credits - {legal_status}"

# Define standard weapons available in the game
WEAPONS = [
    # Legal weapons (available at trade hubs)
    Weapon("Mining Drill", 5, 250, False, COMMON),
    Weapon("Basic Pistol", 8, 750, False, UNCOMMON),
    Weapon("Light Repeater", 10, 2000, False, UNCOMMON),
    Weapon("Merchant's Rifle", 15, 6000, False, RARE),
    Weapon("Federation Combat Blaster", 20, 12000, False, EPIC),
    
    # Illegal weapons (black market or drops only)
    Weapon("Suppresed Scattergun", 20, 8000, True, RARE),
    Weapon("Railgun", 30, 20000, True, RARE),
    Weapon("Plasma Reaper", 40, 30000, True, RARE),
    Weapon("Wraith Cannon", 60, 60000, True, EPIC),
    Weapon("Void Ripper", 85, 100000, True, LEGENDARY),
]

# Define standard armor available in the game
ARMORS = [
    # Legal armor (available at trade hubs)
    Armor("Mining Vest", 3, 550, False, COMMON),
    Armor("Security Vest", 6, 1200, False, UNCOMMON),
    Armor("Kevlar Jacket", 8, 3000, False, RARE),
    Armor("Federation Armor", 10, 10000, False, EPIC),
    Armor("Tactial Guard", 15, 15000, False, EPIC),
    
    # Illegal armor (black market or drops only)
    Armor("Reinforced Jacket", 5, 2400, True, RARE),
    Armor("Phase Armor", 10, 8000, True, RARE),
    Armor("Phase Armor Mk. II", 15, 26000, True, EPIC),
    Armor("Exoskeleton", 25, 800000, True, EPIC),
    Armor("Void Walker Suit", 50, 1600000, True, LEGENDARY),
]

def get_random_equipment(equipment_list, include_illegal=True, min_rarity=None):
    """Get random equipment from list based on rarity weights"""
    filtered_list = equipment_list
    
    # Filter by legality if needed
    if not include_illegal:
        filtered_list = [eq for eq in filtered_list if not eq.is_illegal]
        
    # Filter by minimum rarity if specified
    if min_rarity:
        rarity_ranks = [COMMON, UNCOMMON, RARE, EPIC, LEGENDARY]
        min_idx = rarity_ranks.index(min_rarity)
        filtered_list = [eq for eq in filtered_list if rarity_ranks.index(eq.rarity) >= min_idx]
        
    if not filtered_list:
        return None
    
    # Calculate weights based on rarity
    weights = [RARITY_WEIGHTS[eq.rarity] for eq in filtered_list]
    
    # Make selection
    total = sum(weights)
    r = random.uniform(0, total)
    running_sum = 0
    
    for i, weight in enumerate(weights):
        running_sum += weight
        if running_sum >= r:
            return filtered_list[i]
    
    # Default to first item if something goes wrong
    return filtered_list[0]

def get_random_weapon(include_illegal=True, min_rarity=None):
    """Get a random weapon"""
    return get_random_equipment(WEAPONS, include_illegal, min_rarity)

def get_random_armor(include_illegal=True, min_rarity=None):
    """Get a random armor"""
    return get_random_equipment(ARMORS, include_illegal, min_rarity)

def get_enemy_weapon_drop(enemy_name):
    """Determine what weapon an enemy might drop based on their type"""
    # Bounty hunters have better drop chances
    is_bounty_hunter = any(hunter_name in enemy_name for hunter_name in ["Agent Andrews", "Killer Klakring", "T-Mont the Tyrant", "Garth Vader", "D-Mac the Destroyer"])
    
    # Chance to drop nothing
    if not is_bounty_hunter:
        if random.random() < 0.5:  # 50% chance of no drop for normal enemies
            return None
    elif random.random() < 0.2:  # 20% chance of no drop for bounty hunters
        return None
    
    # Determine min rarity based on enemy type
    if is_bounty_hunter:
        min_rarity = random.choices([UNCOMMON, RARE, EPIC, LEGENDARY], weights=[30, 45, 20, 5])[0]
    elif "Galactic Enforcer" in enemy_name:
        min_rarity = random.choices([COMMON, UNCOMMON, RARE, EPIC], weights=[20, 40, 35, 5])[0]
    elif "Federation Ranger" in enemy_name:
        min_rarity = random.choices([COMMON, UNCOMMON, RARE], weights=[40, 50, 10])[0]
    elif "Sector Badge" in enemy_name:
        min_rarity = random.choices([COMMON, UNCOMMON], weights=[70, 30])[0]
    else:  # Local Deputy
        min_rarity = COMMON
    
    # Get weapon or armor
    if random.random() < 0.7:  # 70% chance for weapon vs armor
        return get_random_weapon(include_illegal=True, min_rarity=min_rarity)
    else:
        return get_random_armor(include_illegal=True, min_rarity=min_rarity)

# Export all the classes and functions needed by other files
__all__ = [
    # Classes
    'Equipment', 'Weapon', 'Armor',
    
    # Rarity constants
    'COMMON', 'UNCOMMON', 'RARE', 'EPIC', 'LEGENDARY',
    
    # Collections
    'WEAPONS', 'ARMORS',
    
    # Functions
    'get_random_weapon', 'get_random_armor', 'get_enemy_weapon_drop'
] 