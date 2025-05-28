from utils import DiceRoller, wait_for_enter
import random
from equipment import get_enemy_weapon_drop

def use_medkit(combat):
    """Heal 30 HP"""
    heal_amount = 30
    combat.player.hp = min(combat.player.max_hp, combat.player.hp + heal_amount)
    print(f"\nUsed medkit! Healed {heal_amount} HP")
    wait_for_enter()

def use_shield(combat):
    """Activate shield to block next attack"""
    combat.shield_active = True
    print("\nShield activated! Next attack will be blocked")
    wait_for_enter()

def use_stun_grenade(combat):
    """Deal explosive damage to enemy"""
    # Calculate grenade damage (15-25 damage)
    damage = random.randint(15, 35)
    combat.enemy.take_damage(damage)
    print(f"\nExplosive grenade detonates! Deals {damage} damage!")
    wait_for_enter()

# Define some basic items
MEDKIT = lambda: CombatItem(name="Medkit", description="Heals 30 HP", effect=use_medkit)
SHIELD = lambda: CombatItem(name="Shield", description="Blocks next attack", effect=use_shield)
STUN_GRENADE = lambda: CombatItem(name="Explosive Grenade", description="Deals 15-25 damage", effect=use_stun_grenade)

# Define law enforcement enemies (from lowest to highest threat)
LOCAL_DEPUTY = lambda: Enemy(name="Local Deputy", hp=60, min_damage=5, max_damage=15, credits_reward=75)  # Level 1 - Local enforcer
SECTOR_BADGE = lambda: Enemy(name="Sector Badge", hp=90, min_damage=10, max_damage=20, credits_reward=100)  # Level 2 - Corrupt sector cop
FEDERATION_RANGER = lambda: Enemy(name="Federation Ranger", hp=120, min_damage=15, max_damage=25, credits_reward=1500)  # Level 3 - Legitimate authority
GALACTIC_ENFORCER = lambda: Enemy(name="Galactic Enforcer", hp=165, min_damage=20, max_damage=35, credits_reward=2000)  # Level 4 - Elite federal agent

# Bounty Hunter System - unique enemies that can be eliminated permanently
class BountyHunter:
    """Container for bounty hunter instances"""
    # List of available bounty hunters
    HUNTERS = [
        lambda: Enemy(name="Agent Andrews", hp=300, min_damage=25, max_damage=40, credits_reward=2000),
        lambda: Enemy(name="Killer Klakring", hp=350, min_damage=30, max_damage=50, credits_reward=5000),
        lambda: Enemy(name="T-Mont the Tyrant", hp=400, min_damage=35, max_damage=55, credits_reward=10000),
        lambda: Enemy(name="Garth Vader", hp=430, min_damage=40, max_damage=60, credits_reward=20000),
        lambda: Enemy(name="D-Mac the Destroyer", hp=480, min_damage=45, max_damage=75, credits_reward=50000),
    ]
    
    # Track which hunters have been eliminated
    eliminated = set()
    
    @classmethod
    def get_random_hunter(cls):
        """Get a random non-eliminated bounty hunter"""
        available = [i for i, hunter in enumerate(cls.HUNTERS) if i not in cls.eliminated]
        if not available:  # If all hunters are eliminated
            return GALACTIC_ENFORCER()  # Fallback to a Galactic Enforcer
        
        idx = random.choice(available)
        return cls.HUNTERS[idx]()
    
    @classmethod
    def mark_eliminated(cls, hunter_name):
        """Mark a hunter as eliminated"""
        for i, hunter in enumerate(cls.HUNTERS):
            if hunter().name == hunter_name:
                cls.eliminated.add(i)
                return True
        return False

class Enemy:
    def __init__(self, name, hp, min_damage, max_damage, credits_reward):
        self.name = name
        self.hp = hp
        self.min_damage = min_damage
        self.max_damage = max_damage
        self.credits_reward = credits_reward

    def is_alive(self):
        return self.hp > 0

    def take_damage(self, amount):
        self.hp = max(0, self.hp - amount)
        
    def attack(self):
        return random.randint(self.min_damage, self.max_damage)

class CombatItem:
    def __init__(self, name, description, effect):
        self.name = name
        self.description = description
        self.effect = effect  # Function that will be called when item is used

class Combat:
    def __init__(self, game, enemy):
        self.game = game
        self.player = game.player
        self.enemy = enemy
        self.shield_active = False  # Tracks if a shield item is protecting player
        self.enemy_stunned = False  # Tracks if enemy should skip next turn
        
    def display_status(self):
        print("\n=== Combat Status ===")
        print(f"Your HP: {self.player.hp}/{self.player.max_hp}")
        if self.shield_active:
            print("Shield: ACTIVE")
        if self.player.weapon:
            print(f"Weapon: {self.player.weapon.name}")
        if self.player.armor_item:
            print(f"Armor: {self.player.armor_item.name}")
        print(f"{self.enemy.name} HP: {self.enemy.hp}")
        print("=" * 20)
        
    def player_turn(self):
        print("\nYour turn! What would you like to do?")
        print("1. Attack")
        print("2. Use Item")
        print("3. Try to Escape")
        
        while True:
            try:
                choice = input("\nEnter choice (1-3): ")
                if choice == "saveme":
                    print("cheating...")
                    return False
                choice = int(choice)
                if choice == 1:
                    # Use total damage (base + weapon)
                    damage = self.player.get_total_damage()
                    self.enemy.take_damage(damage)
                    print(f"\nYou attack for {damage} damage!")
                    wait_for_enter()
                    return True
                    
                elif choice == 2:
                    if not self.player.items:
                        print("\nNo items to use!")
                        wait_for_enter()
                        continue
                        
                    print("\nAvailable Items:")
                    for i, item in enumerate(self.player.items, 1):
                        print(f"{i}. {item.name} - {item.description}")
                    print("\n0. Cancel")
                    
                    try:
                        item_choice = int(input("\nChoose item:"))
                        if 1 <= item_choice <= len(self.player.items):
                            item = self.player.items[item_choice - 1]
                            item.effect(self)  # Use the item
                            self.player.items.remove(item)  # Remove after use
                            return True
                        elif item_choice == 0:
                            continue
                    except ValueError:
                        print("Invalid choice")
                        
                elif choice == 3:
                    # Base escape chance is increased by ship speed
                    base_escape_chance = 0.10
                    speed_bonus = (self.game.ship.speed - 1) * 0.05  # Each level adds 12% chance
                    escape_chance = base_escape_chance + speed_bonus
                    
                    #print(f"\nYour ship's speed rating: {self.game.ship.speed}")
                    #escape_percent = int(escape_chance * 100)
                    #print(f"Estimated escape chance: {escape_percent}%")
                    #wait_for_enter()
                    
                    if DiceRoller.chance(escape_chance):
                        print("\nYou manage to escape!")
                        wait_for_enter()
                        return False
                    else:
                        print("\nCouldn't get away!")
                        wait_for_enter()
                        return True
            except ValueError:
                print("Invalid choice. Please enter 1-3.")
    
    def enemy_turn(self):
        # Check if enemy is stunned
        if self.enemy_stunned:
            print(f"\n{self.enemy.name} is stunned and skips their turn!")
            self.enemy_stunned = False  # Reset stunned flag after one turn
            wait_for_enter()
            return
            
        raw_damage = self.enemy.attack()
        
        if self.shield_active:
            print("\nYour shield absorbs the attack!")
            self.shield_active = False
            wait_for_enter()
            return
            
        # Apply armor reduction
        armor_reduction = self.player.armor_item.defense if self.player.armor_item else 0
        final_damage = max(0, raw_damage - armor_reduction)
        
        if armor_reduction > 0:
            print(f"\nYour armor absorbs {armor_reduction} damage!")
            
        self.player.hp -= final_damage
        print(f"\n{self.enemy.name} attacks for {final_damage} damage!")
        wait_for_enter()
    
    def run(self):
        """Main combat loop"""
        print(f"\nEngaging {self.enemy.name}!")
        wait_for_enter()
        
        while self.enemy.is_alive() and self.player.hp > 0:
            self.display_status()
            
            # Player's turn
            if not self.player_turn():  # If player escaped
                return "escaped"
            
            # Check if enemy died
            if not self.enemy.is_alive():
                print(f"\n{self.enemy.name} defeated!")
                
                # Award credits
                self.player.credits += self.enemy.credits_reward
                print(f"You found {self.enemy.credits_reward} credits!")
                wait_for_enter()
                
                # Check for equipment drops
                dropped_item = get_enemy_weapon_drop(self.enemy.name)
                if dropped_item:
                    self._handle_equipment_drop(dropped_item)
                
                return "victory"
            
            # Enemy's turn
            self.enemy_turn()
            
            # Check if player died
            if self.player.hp <= 0:
                print("\nYou've been defeated...")
                self.game.game_over = True
                wait_for_enter()
                print("\nGame Over!")
                print(f"You survived {self.game.day} days")
                quit()        
        return "defeat"  # Shouldn't reach here but just in case
    
    def _handle_equipment_drop(self, item):
        """Handle equipment drops from defeated enemies"""
        from equipment import Weapon, Armor
        
        item_type = "weapon" if isinstance(item, Weapon) else "armor"
        print(f"\nThe {self.enemy.name} dropped {item.name}!")
        print(f"{item}")
        
        # Compare with current equipment
        current_item = self.player.weapon if item_type == "weapon" else self.player.armor_item
        
        if current_item:
            print(f"\nYour current {item_type}: {current_item}")
            
            # For weapons, compare damage
            if item_type == "weapon":
                if item.damage > current_item.damage:
                    print("This weapon does more damage than your current one.")
                else:
                    print("This weapon does less damage than your current one.")
            # For armor, compare defense
            else:
                if item.defense > current_item.defense:
                    print("This armor provides more protection than your current one.")
                else:
                    print("This armor provides less protection than your current one.")
        
        # Ask player if they want to take it
        print("\nTake it?")
        print("1. Yes")
        print("2. No")
        
        while True:
            try:
                choice = int(input("\nEnter choice (1-2): "))
                if choice == 1:
                    if item_type == "weapon":
                        self.player.weapon = item
                        print(f"\nEquipped {item.name}!")
                    else:  # armor
                        self.player.armor_item = item
                        print(f"\nEquipped {item.name}!")
                    wait_for_enter()
                    break
                elif choice == 2:
                    print("\nYou leave it behind.")
                    wait_for_enter()
                    break
            except ValueError:
                print("Please enter a valid choice (1-2)")
                
# Export enemies for use in other files
__all__ = ['LOCAL_DEPUTY', 'SECTOR_BADGE', 'FEDERATION_RANGER', 'GALACTIC_ENFORCER', 'BountyHunter', 'Combat', 'CombatItem', 'Enemy', 'MEDKIT', 'SHIELD', 'STUN_GRENADE'] 