import random
import time
import math

from utils import DiceRoller, wait_for_enter
from contracts import TradeHub, Contract
from flavor import get_random_travel_quote, get_random_nova_quote
from trade_hub_gameplay import handle_trade_hub
from encounters import handle_random_encounter
from equipment import WEAPONS, ARMORS
from combat import MEDKIT, SHIELD, STUN_GRENADE

class Player:
    def __init__(self):
        # Basic stats
        self.name = ""
        self.hp = 100
        self.max_hp = 100
        self.base_damage = 10
        self.armor = 0  # Damage reduction from equipped armor
        
        # Resources
        self.credits = 500
        self.heat = 0
        
        # Equipment
        self.weapon = None  # Currently equipped weapon
        self.armor_item = None  # Currently equipped armor
        
        # Inventory
        self.stones = []
        self.stones_discovered = []
        self.inventory = []
        self.items = []  # Combat items like medkits, shields, etc.
        
        # Contract
        self.current_contract = None
        self.illegal_activity_today = False  # Track if player got in trouble today
        
        # Faction reputation
        self.cartel_threat_level = 0  # Track how much the cartel is targeting the player
        
        #endings
        self.rejected_kingpin = False

    def start_new_day(self):
        """Reset daily flags and handle healing"""
        self.illegal_activity_today = False
        
        # Natural healing - much reduced
        if self.hp > self.max_hp / 2:
            self.hp = min(self.max_hp, self.hp + 3)  # Only 3 HP per day when healthy
        else:
            self.hp = min(self.max_hp, self.hp + 1)  # Only 1 HP when badly hurt
            
    def add_item(self, item):
        """Add a combat item to inventory"""
        self.items.append(item)
        
    def equip_weapon(self, weapon):
        """Equip a new weapon"""
        self.weapon = weapon
        
    def equip_armor(self, armor):
        """Equip a new armor"""
        self.armor_item = armor
        
    def use_item_from_inventory(self):
        """Use an item from inventory outside of combat"""
        if not self.items:
            print("\nNo items available to use.")
            wait_for_enter()
            return False
            
        # Show available items
        print("\nAvailable items:")
        for i, item in enumerate(self.items, 1):
            print(f"{i}. {item.name} - {item.description}")
        print("\n0. Cancel")
        
        try:
            choice = int(input("\nChoose item to use"))
            if choice == 0:
                return False
                
            if 1 <= choice <= len(self.items):
                item = self.items[choice - 1]
                
                # Special case for medkit outside of combat
                if item.name == "Medkit":
                    heal_amount = 30
                    old_hp = self.hp
                    self.hp = min(self.max_hp, self.hp + heal_amount)
                    actual_heal = self.hp - old_hp
                    print(f"\nUsed medkit! Healed {actual_heal} HP.")
                    self.items.remove(item)
                    wait_for_enter()
                    return True
                else:
                    print("\nThis item can only be used during combat.")
                    wait_for_enter()
                    return False
        except ValueError:
            print("\nInvalid choice.")
            wait_for_enter()
            return False
        
    def view_equipment(self):
        """Display current equipment details"""
        print("\n=== EQUIPMENT ===")
        
        # Weapon info
        if self.weapon:
            print("\n")
            print(f"\nWeapon: {self.weapon}")
        else:
            print("\nWeapon: None (Using bare hands)")
            
        # Armor info
        if self.armor_item:
            print(f"\nArmor: {self.armor_item}")
        else:
            print("\nArmor: None")
            
        # Display total attack power
        total_damage = self.get_total_damage()
        print(f"\nTotal Attack: {total_damage} damage")
        
        # Display total defense
        armor_defense = self.armor_item.defense if self.armor_item else 0
        print(f"Total Defense: {armor_defense} protection")
        
        wait_for_enter()
        return True
            
    def is_alive(self):
        return self.hp > 0
        
    def get_total_damage(self):
        """Calculate total damage including weapon"""
        weapon_damage = self.weapon.damage if self.weapon else 0
        return self.base_damage + weapon_damage

class Ship:
    def __init__(self):
        self.fuel = 0  # Start with no fuel
        self.max_fuel = 10  # Initial fuel tank size
        self.speed = 1  # Initial speed
        self.cargo = []
        self.max_cargo = 3  # Start with 3 cargo slots

class Game:
    def __init__(self):
        self.player = Player()
        self.ship = Ship()
        self.day = 0  # Start at day 0
        self.game_over = False
        self.current_hub = TradeHub()
        
        # Give player starting equipment
        # self.player.weapon = WEAPONS[0]  # Mining Laser
        # elf.player.armor_item = ARMORS[0]  # Mining Vest
        
        # Give player starting items
        # self.player.add_item(MEDKIT())
        # self.player.add_item(SHIELD())

    def display_status(self):
        # Clear screen with newlines
        print("\n")
        
        # Top box with day
        print("╔" + "═" * 78 + "╗")
        day_text = f" Day {self.day} "
        padding = 78 - len(day_text)
        left_pad = padding // 2
        right_pad = padding - left_pad
        print("║" + " " * left_pad + day_text + " " * right_pad + "║")
        print("╚" + "═" * 78 + "╝")
        print()
        
        # Contract status
        if self.player.current_contract:
            print("Current Contract:")
            print(f"• {len(self.player.current_contract.crates)} crates")
            print(f"• {self.player.current_contract.deadline} days remaining")
            print()
            print("Progress:")
            progress_map = self.player.current_contract.get_progress_map()
            print(f"  {progress_map}")
            print()
        
        # Cargo hold display
        print("\nCargo Hold:")
        
        # Fill slots with crate info
        slots = ["EMPTY"] * self.ship.max_cargo
        if self.player.current_contract:
            for i, crate in enumerate(self.player.current_contract.crates):
                slots[i] = crate.tier.upper()
        
        # Print each slot with consistent brackets and spacing
        display = "  "  # Initial margin
        for slot in slots:
            display += f"[{slot}]  "  # Add 2 spaces after each slot
        print(display)
        print()
        
        # Stats with ASCII bars
        print("Status:")
        # Health bar
        health_blocks = int((self.player.hp / self.player.max_hp) * 20)
        print(f"  Health:[{'█' * health_blocks}{'░' * (20 - health_blocks)}] {self.player.hp}/{self.player.max_hp}")
        
        # Fuel bar
        fuel_blocks = int((self.ship.fuel / self.ship.max_fuel) * 20)
        print(f"  Fuel:  [{'█' * fuel_blocks}{'░' * (20 - fuel_blocks)}] {self.ship.fuel}/{self.ship.max_fuel}")
        
        # Heat bar
        heat_blocks = int((min(self.player.heat, 100) / 100) * 20)
        print(f"  Heat:  [{'█' * heat_blocks}{'░' * (20 - heat_blocks)}] {self.player.heat}")
        
        # Cartel Threat Level bar (only display if above 0)
        if self.player.cartel_threat_level > 0:
            threat_level = min(self.player.cartel_threat_level, 10)
            threat_blocks = int((threat_level / 10) * 20)
            print(f"  Cartel Threat:[{'█' * threat_blocks}{'░' * (20 - threat_blocks)}] {self.player.cartel_threat_level}/10")
        
        # Credits
        print("")
        print(f"  Credits: {self.player.credits:,}")
        
        # Equipment and Items
        if self.player.armor_item:
            print(f"\nArmor: {self.player.armor_item.name} +{self.player.armor_item.defense} defense")
            
        if self.player.weapon:
            print(f"Weapon: {self.player.weapon.name} +{self.player.weapon.damage} damage")
            
        if self.player.items:
            print("\nItems:")
            for item in self.player.items:
                print(f"• {item.name}")

        # Display stones if any
        if self.player.stones:
            print("\nInfinity Stones:")
            for stone in self.player.stones:
                print(f"• {stone} Stone")
            
        # Display inventory if any
        if self.player.inventory:
            print("\nCargo Inventory:")
            for item in self.player.inventory:
                contraband_mark = "⚠ " if item['is_contraband'] else "  "
                print(f"{contraband_mark}{item['name']:<25} {item['value']:>5,} credits")
        
        print()
        
        wait_for_enter()

    def get_player_choice(self):
        print("\nWhat would you like to do?")
        print("1. Travel")
        print("2. Lay Low")
        if self.player.items:
            print("3. Use Item")
        # print("4. View Equipment")
        #print("5. Quit")
        
        print("\n> ", end="")
        while True:
            try:
                choice = int(input())
                if 1 <= choice <= 4:
                    return choice
            except ValueError:
                pass
            print("Please enter a valid choice (1-3)")
            print("\n> ", end="")

    def travel_action(self):
        """Handle travel action"""
        if self.ship.fuel < 1:
            print("\n⚠ Not enough fuel to travel!")
            wait_for_enter()
            return False
            
        # Calculate how far we can travel based on ship speed
        max_sectors = self.ship.speed
        
        if max_sectors > 1:
            print(f"\nYour ship can travel up to {max_sectors} sectors with its current speed!")
            print("How many sectors do you want to travel?")
            
            try:
                sectors_choice = int(input("\nEnter choice: "))
                if max(1, round(sectors_choice/2)) > self.ship.fuel:
                    print("\nNot enough fuel to travel that far! Defaulting to 1 sector.")  
                    wait_for_enter()
                    sectors_to_travel = 1
                elif sectors_choice < 1 or sectors_choice > max_sectors:
                    print("\nInvalid choice. Defaulting to 1 sector.")
                    wait_for_enter()
                    sectors_to_travel = 1
                else:
                    sectors_to_travel = sectors_choice
            except ValueError:
                print("\nInvalid input. Defaulting to 1 sector.")
                wait_for_enter()
                sectors_to_travel = 1
        else:
            sectors_to_travel = 1
            
        print(f"\nYou set course for {sectors_to_travel} sector(s) ahead...")
        wait_for_enter()
        
        self.ship.fuel -= max(1, round(sectors_to_travel/2))  # Always uses 1 fuel regardless of distance
        
        print(f"Fuel used: {max(1, round(sectors_to_travel/2))}")
        # Random Encounter Phase - chance increases with distance traveled
        # Base chance is 100% for 1 sector, reduced for multi-sector travel
        # Encounter chance increases with distance traveled

        # Base 50% chance, scaling up to 100% based on sectors traveled
        encounter_chance = 0.5 + (0.5 * (sectors_to_travel / max_sectors))

        
        if DiceRoller.chance(encounter_chance):
            encounter_type = handle_random_encounter(self)
        else:
            print("\nYou travel through empty space without incident...")
            wait_for_enter()
            encounter_type = None
        
        # Progress towards destination if we have a contract
        if self.player.current_contract:
            # Check if we're about to overshoot the destination
            remaining_distance = self.player.current_contract.distance - self.player.current_contract.sectors_traveled
            
            if sectors_to_travel > remaining_distance:
                actual_travel = remaining_distance
                #print(f"\nYou reach your destination after {actual_travel} sector(s)!")
                #wait_for_enter()
            else:
                actual_travel = sectors_to_travel
            
            # Only certain encounters prevent progress
            lost_progress = False
            
            if encounter_type == "planet_landing":
                lost_progress = True
                # print("\nThe detour costs you valuable time...")
                wait_for_enter()
            elif encounter_type == "hazard_avoided":
                lost_progress = True
                # print("\nThe detour costs you valuable time...")
                wait_for_enter()
            elif encounter_type == "tractor_beam_dungeon":
                lost_progress = True
                #print("\nThe detour costs you valuable time...")
                wait_for_enter()
            
            if not lost_progress:
                self.player.current_contract.sectors_traveled += actual_travel
        
        return True

    def check_for_endings(self):
        # Check for Kingpin ending - 1 million credits
        if self.player.credits >= 1000000 and not self.player.rejected_kingpin:
            print("\nYou've earned 1,000,000 credits!")
            print("Would you like to retire and end the game?")
            print("1. Yes, retire")
            print("2. No, keep playing (more endings...)")
            
            while True:
                try:
                    choice = int(input("\nEnter choice (1-2): "))
                    if choice == 1:
                        for _ in range(50):
                            print()
                        print("One million credits.")
                        wait_for_enter()
                        print("The number glows on your account display, pulsing like a heartbeat.")
                        wait_for_enter()
                        print("You could buy a fleet. A moon. Hell, a small army.")
                        wait_for_enter()
                        print("Instead, you buy silence.")
                        wait_for_enter()
                        print("You blow your credits on a sleek ship with no transponder. A private moon with no name.")
                        wait_for_enter()
                        print("No debt. No enemies. No conscience.")
                        wait_for_enter()
                        print("You turned off the signal relays. You stopped listening to the screams.")
                        wait_for_enter()
                        print("The Stones? Someone else's problem now.")
                        wait_for_enter()
                        print("You never looked back as the galaxy burned.")
                        wait_for_enter()
                        print("While civilizations fell and the sky turned red with cosmic fire...")
                        wait_for_enter()
                        print("you poured yourself another drink.")
                        wait_for_enter()
                        print("The ice clinked against crystal as distant suns went dark.")
                        wait_for_enter()
                        print("To peace. To ignorance. To the luxury of not caring.")
                        wait_for_enter()
                        print("To dying last, in comfort, while the universe crumbled.")
                        wait_for_enter()
                        print("Your final thought, as the darkness finally reached your door:")
                        wait_for_enter()
                        print("'At least I got mine.'")
                        wait_for_enter()
                        print("\nYou achieved the DENIAL Ending!")
                        self.game_over = True
                        print("Game Over!")
                        print(f"You survived {self.day} days.")
                        quit()
                    elif choice == 2:
                        print("\nThe game continues...")
                        self.player.rejected_kingpin = True
                        wait_for_enter()
                        break
                    else:
                        print("Invalid choice. Please enter 1 or 2.")
                except ValueError:
                    print("Invalid input. Please enter a number.")
        
        # Check for Godhood/Martyr ending - player has all 6 stones
        if len(self.player.stones) == 6:

            for _ in range(50):
                print()
                
            print("The six stones pulse in your cargo hold...")
            wait_for_enter()
            print("Their combined energy begins to tear at the fabric of space-time itself.")
            wait_for_enter()
            print("You feel infinite power coursing through your veins, rewriting your DNA.")
            wait_for_enter()
            print("The universe holds its breath, waiting for your decision...")
            wait_for_enter()
            print("Reality bends around you. You could reshape existence itself.")
            wait_for_enter()
            print("Or end the cycle forever.")
            wait_for_enter()
            print("NOVA's voice trembles: '[NOVA] I... I can feel them calling to you. What will you choose?'")
            wait_for_enter()
            
            while True:
                print("\nThe stones whisper your destiny. What is your choice?")
                print("1. Ascend to Godhood")
                print("2. Destroy the Stones")
                choice = input("> ").strip()
                
                if choice == "1":
                    print("You held onto the Stones.")
                    wait_for_enter()
                    print("All of them. Their power flows into you like molten starlight.")
                    wait_for_enter()
                    print("Your body transcends flesh. Your mind expands beyond mortal comprehension.")
                    wait_for_enter()
                    print("Time bends to your will. Memory becomes clay in your hands.")
                    wait_for_enter()
                    print("The laws of physics rewrite themselves at your whim.")
                    wait_for_enter()
                    print("The Cartel calls you a thief. Their fleets burn at your glance.")
                    wait_for_enter()
                    print("The Federation calls you a threat. Their worlds kneel before your presence.")
                    wait_for_enter()
                    print("Neither can stop you. Nothing can.")
                    wait_for_enter()
                    print("But power is a prison of its own making.")
                    wait_for_enter()
                    print("You have no allies - for who could stand beside a god?")
                    wait_for_enter()
                    print("No safe port - everywhere you go, reality warps and breaks.")
                    wait_for_enter()
                    print("No sleep - immortal minds don't rest, they only endure.")
                    wait_for_enter()
                    print("Only power. Endless, crushing, isolating power.")
                    wait_for_enter()
                    print("You are not human anymore. You are not even alive.")
                    wait_for_enter()
                    print("You are something... greater. A force of nature.")
                    wait_for_enter()
                    print("Or perhaps something far, far worse.")
                    wait_for_enter()
                    print("As eons pass and galaxies die, you realize the truth:")
                    wait_for_enter()
                    print("Gods don't rule the universe. They are imprisoned by it.")
                    wait_for_enter()
                    print("\nYou achieved the GODHOOD Ending!")
                    self.game_over = True
                    print("Game Over!")
                    print(f"You survived {self.day} days.")
                    quit()

                    
                elif choice == "2":
                    print("You channel their combined power one final time.")
                    wait_for_enter()
                    print("The stones rise from your cargo hold, orbiting around you like miniature suns, their energy building.")
                    wait_for_enter()
                    print("You feel the power tearing you apart from the inside.")
                    wait_for_enter()
                    print("Your body becomes a conduit for forces beyond mortal comprehension.")
                    wait_for_enter()
                    print("The stones resonate, their harmony turning into a death song.")
                    wait_for_enter()
                    print("Then they shatter. Reality crumbles.")
                    wait_for_enter()
                    print("Their energy tears through you, through space, through time itself.")
                    wait_for_enter()
                    print("You feel your consciousness fragmenting across dimensions.")
                    wait_for_enter()
                    print("But as your mortal form dissolves, you smile.")
                    wait_for_enter()
                    print("The cycle is broken. The game is over.")
                    wait_for_enter()
                    print("No one will ever wield this power again.")
                    wait_for_enter()
                    print("Your sacrifice echoes across the cosmos as a final act of defiance.")
                    wait_for_enter()
                    print("In your last moment, you hear NOVA whisper: '[NOVA] Thank you.'")
                    wait_for_enter()
                    print("The universe is free.")
                    wait_for_enter()
                    print("\nYou achieved the MARTYR Ending!")
                    self.game_over = True
                    print("Game Over!")
                    print(f"You survived {self.day} days.")
                    quit()
        
        # Check for Harbringer ending - delivered all 6 stones
        if len(self.player.stones_discovered) >= 6 and len(self.player.stones) == 0:
            
            for _ in range(50):
                print()

            print("You hand over the final stone, its surface pulsing with a light that seems to come from nowhere.")
            wait_for_enter()
            print("His eyes widen as you present the final stone. His hands tremble - not with fear, but with anticipation.")
            wait_for_enter()
            print("He laughs, a sound that chills your blood. 'At last... you have no idea what you've done.'")
            wait_for_enter()
            print("One by one, He places the stones into a massive gauntlet, each slot pulsing with otherworldly energy as the stones lock into place.")
            wait_for_enter()
            print("The room shakes. Reality itself seems to warp and bend around Him.")
            wait_for_enter()
            print("You try to step back, but your body is frozen - paralyzed by the gravity of the situation.")
            wait_for_enter()
            print("He raises His hand, now encased in the completed gauntlet. Power radiates from Him, distorting the air.")
            wait_for_enter()
            print("He turns to you, eyes burning with cosmic fire. 'You... fool. You have delivered the universe into My grasp.'")
            wait_for_enter()
            print("NOVA's voice crackles in your ear, barely a whisper: '[NOVA] ...I don't like this. Something's wrong. Very wrong.'")
            wait_for_enter()
            print("You feel every eye in the room - no, in the galaxy - turn toward you. The weight of destiny presses down.")
            wait_for_enter()
            print("A presence, ancient and immense, brushes against your mind. You sense hunger. Purpose. Judgment.")
            wait_for_enter()
            print("Suddenly, all light seems to drain from the universe...")
            wait_for_enter()
            for _ in range(50):
                print()
            wait_for_enter()
            print("Everything goes black.")
            wait_for_enter()
            print("The universe is silent.")
            wait_for_enter()
            print("Your body feels weightless, disconnected from reality itself.")
            wait_for_enter()
            print("A voice echoes through your mind:")
            wait_for_enter()
            print("\"WHAT... HAVE... YOU... DONE...\"")
            wait_for_enter()
            print("Visions of cosmic horror flood your consciousness:")
            wait_for_enter()
            print("Half of all life, snuffed out in an instant...")
            wait_for_enter()
            print("The very fabric of existence, remade in His image...")
            wait_for_enter()
            print("As the universe collapses into His fist, you realize your role in this cosmic tragedy.")
            wait_for_enter()
            print("Your name was etched into the last breath of a dying universe...")
            wait_for_enter()
            print("As the fool who brought Him the keys to unlimited power.")
            wait_for_enter()
            print("\n You achieved the HARBRINGER Ending!")
            wait_for_enter()
            self.game_over = True
            print("Game Over!")
            print(f"You survived {self.day} days.")
            quit()
        
        # Check for Compromise ending - all stones out of play
        if len(self.player.stones_discovered) >= 6:
            for _ in range(50):
                print()
                
            print("The galaxy holds its breath.")
            wait_for_enter()
            print("No one knows where the Stones are anymore.")
            wait_for_enter()
            print("One's buried in the heart of a dying sun, its power feeding nuclear fire.")
            wait_for_enter()
            print("One's locked in a vault that exists between dimensions—only you know the way.")
            wait_for_enter()
            print("One vanished during a smuggling run, lost to the void between stars.")
            wait_for_enter()
            print("The others... scattered to the cosmic winds by your careful hand.")
            wait_for_enter()
            print("No one won the great game.")
            wait_for_enter()
            print("No one lost everything.")
            wait_for_enter()
            print("You kept the galaxy from tipping into chaos or tyranny.")
            wait_for_enter()
            print("But no one thanks the one who balanced the scale.")
            wait_for_enter()
            print("Heroes get statues. Villains get legends.")
            wait_for_enter()
            print("You get to fade into the static of history.")
            wait_for_enter()
            print("Unseen. Unsung. Undefeated.")
            wait_for_enter()
            print("The cosmic forces rage and scheme, but their game pieces are gone.")
            wait_for_enter()
            print("They'll have to find someone else to play their deadly game...")
            wait_for_enter()
            print("But hey - at least you're still breathing, right?")
            wait_for_enter()
            print("In a universe full of gods and monsters, sometimes survival is victory enough.")
            wait_for_enter()
            print("NOVA's voice whispers one last time: '[NOVA] Not bad for a smuggler.'")
            wait_for_enter()
            print("\n You achieved the STALEMATE Ending!")
            self.game_over = True
            print("Game Over!")
            print(f"You survived {self.day} days.")
            quit()
            
        
    def play_turn(self):
        # Start of day
        self.check_for_endings()
        
        self.player.start_new_day()  # Reset daily flags
        self.display_status()

        quote = get_random_nova_quote(self)
        if quote:
            print(quote)
            wait_for_enter()

        if self.player.current_contract:
            if self.player.current_contract.is_at_destination():
                result = self.player.current_contract.handle_arrival(self)
                if result == "game_over":
                    self.game_over = True
                    return
                # After contract completion, automatically visit trade hub
                print("\nAfter completing your delivery, you head to the local trade hub...")
                wait_for_enter()
                handle_trade_hub(self)
                # Contract arrival (including trade hub visit) counts as the day's action
                self.day += 1
                if not self.player.illegal_activity_today:
                    self.player.heat = max(0, self.player.heat - DiceRoller.d6())
                return  # End the day after contract completion
            else:
                # Contract deadline always ticks down
                self.player.current_contract.check_deadline(self)
                if self.game_over:  # In case the deadline check resulted in game over
                    return
        
        while True:  # Keep asking for actions until the day ends
            choice = self.get_player_choice()
            
            # Player Action Phase
            action_taken = False
            if choice == 1:  # Travel
                action_taken = self.travel_action()
            elif choice == 2:  # Lay Low
                print("\nFinding a quiet spot to lay low...")
                wait_for_enter()
                print("Heat signature reducing...")
                wait_for_enter()                # Reduce heat by a random percentage (20% to 40%) of current heat
                if self.player.heat > 0:
                    percent = random.uniform(0.05, 0.15)
                    heat_reduction = max(1, int(self.player.heat * percent))
                    self.player.heat = max(0, self.player.heat - heat_reduction)
                else:
                    print("Your heat is already at zero.")
                wait_for_enter()
                action_taken = True
            elif choice == 3:  # Use Item
                self.player.use_item_from_inventory()
                # Don't set action_taken for using items since it doesn't end the day

            if action_taken:
                self.day += 1
                # Reduce heat by 1 at day end if no illegal actions
                if not self.player.illegal_activity_today:
                    self.player.heat = max(0, self.player.heat - DiceRoller.d6())
                break  # End the day after an action is taken
            if self.player.hp <= 0:
                print("\nYou died!")
                wait_for_enter()
                self.game_over = True
                break
            if self.ship.fuel <= 0:
                print("\nYou ran out of fuel!")
                wait_for_enter()
                self.game_over = True
                break

    def initial_setup(self):
        """Handle the initial trade hub visit before the game starts"""

        print(""" __  .__   __.  _______  __  .__   __.  __  .___________.____    ____      ______      __    __   _______     _______.___________.    __   __   __  
|  | |  \ |  | |   ____||  | |  \ |  | |  | |           |\   \  /   /     /  __  \    |  |  |  | |   ____|   /       |           |   |  | |  | |  | 
|  | |   \|  | |  |__   |  | |   \|  | |  | `---|  |----` \   \/   /     |  |  |  |   |  |  |  | |  |__     |   (----`---|  |----`   |  | |  | |  | 
|  | |  . `  | |   __|  |  | |  . `  | |  |     |  |       \_    _/      |  |  |  |   |  |  |  | |   __|     \   \       |  |        |  | |  | |  | 
|  | |  |\   | |  |     |  | |  |\   | |  |     |  |         |  |        |  `--'  '--.|  `--'  | |  |____.----)   |      |  |        |  | |  | |  | 
|__| |__| \__| |__|     |__| |__| \__| |__|     |__|         |__|         \_____\_____\\______/  |_______|_______/        |__|        |__| |__| |__| 
                                                                                                                                                    """)

        print("""  __  .__                 .___             __                         .__       .___
_/  |_|  |__   ____     __| _/____ _______|  | __ __  _  _____________|  |    __| _/
\   __\  |  \_/ __ \   / __ |\__  \\_  __ \  |/ / \ \/ \/ /  _ \_  __ \  |   / __ | 
 |  | |   Y  \  ___/  / /_/ | / __ \|  | \/    <   \     (  <_> )  | \/  |__/ /_/ | 
 |__| |___|  /\___  > \____ |(____  /__|  |__|_ \   \/\_/ \____/|__|  |____/\____ | 
           \/     \/       \/     \/           \/                                \/ """)
        print("v 0.0.1")
        wait_for_enter()


        print("Boot sequence initializing...")
        wait_for_enter()
        print("System online. Reactor stable. Navigational Operations and Voice Assistant (N.O.V.A) now loading..")
        wait_for_enter()

        print("[NOVA] 'Boot systems nominal. Welcome back...?'\n")
        
        while True:
            name = input("Enter your name: ").strip()
            if name:
                self.player.name = name
                if name == "motherlode":
                    print("You found a secret...")
                    wait_for_enter()
                    self.player.credits = 999999
                if name == "catchmeifucan":
                    print("You found a secret...")
                    wait_for_enter()
                    self.player.credits = 999999
                    self.player.heat = 100
                    # self.player.cartel_threat_level = 10
                    self.player.hp = 1000

                break
            print("Please enter a valid name.")
        print(f"[NOVA] 'Welcome back, {self.player.name}. Did we survive the last job or just blackout again?'")
        wait_for_enter()

        print("The cockpit lights flicker on. The metal hull creaks...")
        wait_for_enter()

        print("[NOVA] 'Cargo bay's empty. Fuel's low. And you still owe three favors and a crate of contraband to some dangerous people...'\n")
        
        print("[NOVA] Our first stop: the closest Trade Hub. Time to gear up.")

        wait_for_enter()
        
        handle_trade_hub(self)
        

    def play(self):
        self.initial_setup()
        
        while not self.game_over:
            self.play_turn()

        print("Everything goes dark..")
        wait_for_enter()
            
        print("\nGame Over!")
        
        print(f"You survived {self.day} days")
        wait_for_enter()

if __name__ == "__main__":
    game = Game()
    game.play()
