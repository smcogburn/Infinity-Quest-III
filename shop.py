from utils import DiceRoller, wait_for_enter
from equipment import (
    WEAPONS, ARMORS, get_random_weapon, get_random_armor,
    COMMON, UNCOMMON, RARE, EPIC, LEGENDARY
)
from combat import MEDKIT, SHIELD, STUN_GRENADE
from fights import CartelEncounter, PoliceEncounter

import random

def generate_black_market_atmosphere():
    """Generate black market atmosphere similar to trade hub system"""
    market_types = ["underground", "smuggler_den", "pirate_outpost", "shadow_bazaar"]
    market_type = random.choice(market_types)
    
    market_visual = {
        "underground": [
            "Dim red lighting casts long shadows across the cramped space.",
            "Exposed pipes drip condensation onto stacked weapon crates.",
            "The ceiling is so low you have to duck under hanging cables."
        ],
        "smuggler_den": [
            "A maze of shipping containers converted into makeshift stalls.",
            "Holographic signs flicker in multiple alien languages.",
            "The floor is stained with engine oil and things you don't want to identify."
        ],
        "pirate_outpost": [
            "Skull insignias and battle scars mark every surface.",
            "Trophy weapons hang from the walls like a museum of violence.",
            "The air smells of gunpowder and stale victory."
        ],
        "shadow_bazaar": [
            "Merchants huddle in dark alcoves, their faces hidden by hoods.",
            "Price tags are written in code that only the initiated understand.",
            "Everything here has a story, and none of them are legal."
        ]
    }
    
    market_sound = {
        "underground": [
            "Ventilation fans whir loudly, drowning out whispered negotiations.",
            "Somewhere in the distance, metal grinds against metal.",
            "The sound of your footsteps echoes off the concrete walls."
        ],
        "smuggler_den": [
            "Engine diagnostics beep constantly from hidden workshops.",
            "Muffled arguments in a dozen different languages leak through thin walls.",
            "The hiss of hydraulics accompanies every transaction."
        ],
        "pirate_outpost": [
            "Raucous laughter and the clink of stolen credits fill the air.",
            "Someone's telling war stories loudly at a nearby table.",
            "The sound of weapons being tested echoes from the back rooms."
        ],
        "shadow_bazaar": [
            "Whispered conversations stop when you pass by.",
            "The only sounds are the soft shuffle of feet and rustling credits.",
            "An eerie silence hangs over everything, broken only by occasional murmurs."
        ]
    }
    
    market_mood = {
        "underground": [
            "Everyone here is running from something.",
            "This place exists in the cracks between law and chaos.",
            "Trust is a currency more valuable than credits."
        ],
        "smuggler_den": [
            "Business is business, but loyalty has a price.",
            "Every deal comes with risk, but the rewards are worth it.",
            "The only law here is don't ask where it came from."
        ],
        "pirate_outpost": [
            "Strength is respected. Weakness gets you robbed.",
            "Every scar tells a story of survival.",
            "Honor among thieves is just good business practice."
        ],
        "shadow_bazaar": [
            "Information is as valuable as ammunition here.",
            "Nothing is as it seems, and everything has a hidden cost.",
            "The darkness hides more than just illegal goods."
        ]
    }
    
    dealer_personalities = {
        "underground": [
            "A nervous tech specialist taps anxiously on a datapad.",
            "A grizzled veteran with cybernetic implants studies you carefully.",
            "A young face that's seen too much peers at you from behind reinforced glass."
        ],
        "smuggler_den": [
            "A smooth-talking merchant with gold teeth flashes a dangerous smile.",
            "A no-nonsense dealer barely looks up from their inventory manifest.",
            "A former pilot with burn scars gestures toward their collection."
        ],
        "pirate_outpost": [
            "A battle-scarred warrior leans against a rack of assault weapons.",
            "A fierce-looking captain with multiple holsters sizes you up.",
            "A grinning raider with fresh bandages offers you a drink."
        ],
        "shadow_bazaar": [
            "A figure in dark robes speaks only in whispers.",
            "A pale merchant with too many eyes watches your every move.",
            "Someone wearing a featureless mask gestures silently at their wares."
        ]
    }
    
    nova_commentary = {
        "underground": [
            "[NOVA] 'Well, this place has 'terrible life choices' written all over it.'",
            "[NOVA] 'The structural integrity here is... questionable. Like your decision-making.'",
            "[NOVA] 'I'm detecting seventeen different safety violations. And that's just the lighting.'"
        ],
        "smuggler_den": [
            "[NOVA] 'Ah, the entrepreneurial spirit. If by spirit you mean felonies.'",
            "[NOVA] 'I recognize some of these ship parts. They're definitely stolen.'",
            "[NOVA] 'This place smells like bad decisions and engine coolant.'"
        ],
        "pirate_outpost": [
            "[NOVA] 'Charming. It's like a museum of everything the galaxy considers illegal.'",
            "[NOVA] 'Half these weapons are banned by twelve different treaties.'",
            "[NOVA] 'I'd suggest keeping your hands visible. And your head down.'"
        ],
        "shadow_bazaar": [
            "[NOVA] 'This place gives me the digital equivalent of chills.'",
            "[NOVA] 'Even my sensors can't tell what half this stuff is supposed to be.'",
            "[NOVA] 'I'm logging this visit as 'questionable research' in my files.'"
        ]
    }
    
    return market_type, market_visual, market_sound, market_mood, dealer_personalities, nova_commentary

class Shop:
    """Base class for all shop types"""
    def __init__(self, name):
        self.name = name
        self.inventory = {
            'weapons': [],
            'armor': [],
            'items': []
        }
        
    def display_inventory(self, category, player):
        """Display items of a specific category with enhanced atmospheric formatting"""
        if not self.inventory[category]:
            print(f"\nNo {category} available in stock.")
            wait_for_enter()
            return
            
        # Simple header without box
        print(f"\n=== {self.name.upper()} - {category.upper()} ===")
        print(f"Your Credits: {player.credits:,}")
        print("\nAvailable inventory:")
        
        for i, item in enumerate(self.inventory[category], 1):
            print("\n" + "─" * 60)
            
            if hasattr(item, 'damage'):  # Weapon
                self._display_weapon(i, item, player)
            elif hasattr(item, 'defense'):  # Armor  
                self._display_armor(i, item, player)
            else:  # Combat item
                self._display_combat_item(i, item, player)
        
        print("\n" + "─" * 60)
        print("\n[0] Back")
    
    def handle_purchase(self, category, player, choice):
        """Handle purchasing an item from the shop"""
        try:
            idx = int(choice) - 1
            if idx < 0 or idx >= len(self.inventory[category]):
                return False
                
            item = self.inventory[category][idx]
            price = self._get_item_price(item)
            
            if player.credits < price:
                print("\nYou don't have enough credits!")
                wait_for_enter()
                return False
                
            # Handle purchase based on item type
            if category == 'weapons':
                self._handle_weapon_purchase(player, item, price)
            elif category == 'armor':
                self._handle_armor_purchase(player, item, price)
            else:  # items
                self._handle_item_purchase(player, item, price)
                
            return True
                
        except (ValueError, IndexError):
            return False
    
    def _handle_weapon_purchase(self, player, weapon, price):
        """Process weapon purchase"""
        # Show comparison if player has a weapon
        if player.weapon:
            print(f"\nYour current weapon: {player.weapon}")
            if weapon.damage > player.weapon.damage:
                print(f"This weapon does {weapon.damage - player.weapon.damage} more damage than your current one.")
            else:
                print(f"This weapon does {player.weapon.damage - weapon.damage} less damage than your current one.")
        
        # Confirm purchase
        print(f"\nPurchase {weapon.name} for {price:,} credits?")
        print("1. Yes")
        print("2. No")
        
        while True:
            try:
                choice = int(input("\nEnter choice (1-2): "))
                if choice == 1:
                    player.credits -= price
                    player.weapon = weapon
                    print(f"\nYou purchased and equipped {weapon.name}!")
                    wait_for_enter()
                    return True
                elif choice == 2:
                    return False
            except ValueError:
                pass
            print("Invalid choice. Please enter 1 (yes) or 2 (no)")
    
    def _handle_armor_purchase(self, player, armor, price):
        """Process armor purchase"""
        # Show comparison if player has armor
        if player.armor_item:
            print(f"\nYour current armor: {player.armor_item}")
            if armor.defense > player.armor_item.defense:
                print(f"This armor provides {armor.defense - player.armor_item.defense} more protection than your current one.")
            else:
                print(f"This armor provides {player.armor_item.defense - armor.defense} less protection than your current one.")
        
        # Confirm purchase
        print(f"\nPurchase {armor.name} for {price:,} credits?")
        print("1. Yes")
        print("2. No")
        
        while True:
            try:
                choice = int(input("\nEnter choice (1-2): "))
                if choice == 1:
                    player.credits -= price
                    player.armor_item = armor
                    print(f"\nYou purchased and equipped {armor.name}!")
                    if hasattr(armor, 'is_illegal') and armor.is_illegal:
                        player.illegal_activity_today = True
                    wait_for_enter()
                    return True
                elif choice == 2:
                    return False
            except ValueError:
                pass
            print("Invalid choice. Please enter 1 (yes) or 2 (no)")
    
    def _handle_item_purchase(self, player, item, price):
        """Process combat item purchase"""
        # Create an instance of the item first
        item_instance = item()
        
        # Confirm purchase
        print(f"\nPurchase {item_instance.name} for {price:,} credits?")
        print("1. Yes")
        print("2. No")
        
        while True:
            try:
                choice = int(input("\nEnter choice (1-2): "))
                if choice == 1:
                    player.credits -= price
                    player.add_item(item())  # Create a new instance of the item
                    print(f"\nYou purchased {item_instance.name}!")
                    wait_for_enter()
                    return True
                elif choice == 2:
                    return False
            except ValueError:
                pass
            print("Invalid choice. Please enter 1 (yes) or 2 (no)")
    
    def _get_item_price(self, item):
        """Get the price of an item"""
        if hasattr(item, 'price'):
            return item.price
        
        # Combat items have fixed prices
        if hasattr(item, 'name'):
            if item().name == "Medkit":
                return 200
            elif item().name == "Shield":
                return 350
            elif item().name == "Stun Grenade":
                return 500
        
        # Default price
        return 100

    def _get_rarity_symbol(self, rarity):
        """Get visual symbol for item rarity"""
        rarity_symbols = {
            'common': '●',
            'uncommon': '◆', 
            'rare': '★',
            'epic': '◈',
            'legendary': '☆'
        }
        return rarity_symbols.get(rarity.lower(), '●')
    
    def _get_rarity_color_desc(self, rarity):
        """Get atmospheric description for rarity"""
        rarity_descriptions = {
            'common': 'Standard',
            'uncommon': 'Quality',
            'rare': 'Superior', 
            'epic': 'Exceptional',
            'legendary': 'Mythic'
        }
        return rarity_descriptions.get(rarity.lower(), 'Standard')
    
    def _display_weapon(self, index, weapon, player):
        """Display weapon with clean formatting"""
        price = self._get_item_price(weapon)
        
        # Build title with rarity and legal status
        title = f"{weapon.name} [{weapon.rarity.capitalize()}]"
        if hasattr(weapon, 'is_illegal') and weapon.is_illegal:
            title += " [ILLEGAL]"
        
        print(f"[{index}] {title}")
        print(f"    Damage: {weapon.damage}  |  Price: {price:,} credits")
        
        # Show comparison with current weapon
        if player.weapon:
            damage_diff = weapon.damage - player.weapon.damage
            if damage_diff > 0:
                print(f"    +{damage_diff} damage upgrade")
            elif damage_diff < 0:
                print(f"    {damage_diff} damage downgrade")
    
    def _display_armor(self, index, armor, player):
        """Display armor with clean formatting"""
        price = self._get_item_price(armor)
        
        # Build title with rarity and legal status
        title = f"{armor.name} [{armor.rarity.capitalize()}]"
        if hasattr(armor, 'is_illegal') and armor.is_illegal:
            title += " [ILLEGAL]"
            
        print(f"[{index}] {title}")
        print(f"    Defense: {armor.defense}  |  Price: {price:,} credits")
        
        # Show comparison with current armor
        if player.armor_item:
            defense_diff = armor.defense - player.armor_item.defense
            if defense_diff > 0:
                print(f"    +{defense_diff} defense upgrade")
            elif defense_diff < 0:
                print(f"    {defense_diff} defense downgrade")
    
    def _display_combat_item(self, index, item_func, player):
        """Display combat item with clean formatting"""
        item_instance = item_func()
        price = self._get_item_price(item_func)
        
        print(f"[{index}] {item_instance.name}")
        print(f"    {item_instance.description}")
        print(f"    Price: {price:,} credits")
        
        # Show current stock if player has any
        current_count = sum(1 for item in player.items if item.name == item_instance.name)
        if current_count > 0:
            print(f"    You have: {current_count}x")

class TradeHubShop(Shop):
    """Legal shop available at trade hubs"""
    def __init__(self):
        super().__init__("Trade Hub Shop")
        self.restock()
    
    def restock(self):
        """Restock the shop with legal items"""
        # Clear inventory
        self.inventory = {
            'weapons': [],
            'armor': [],
            'items': [MEDKIT, SHIELD]  # Always have medkits and shields
        }
        
        # Add 2-4 legal weapons based on rarity
        num_weapons = DiceRoller.d6() // 2 + 1  # 1-3 weapons
        for _ in range(num_weapons):
            weapon = get_random_weapon(include_illegal=False)
            if weapon:
                self.inventory['weapons'].append(weapon)
                
        # Add 1-2 legal armor pieces
        num_armor = DiceRoller.d6() // 3 + 1  # 1-2 armor pieces
        for _ in range(num_armor):
            armor = get_random_armor(include_illegal=False)
            if armor:
                self.inventory['armor'].append(armor)
    
    def shop_menu(self, game, hub_type=None):
        """Main shop menu for Trade Hub, with hub_type flavor."""
        player = game.player

        # Expanded intro flavor by hub type
        SHOP_INTROS = {
            "slum": [
                "A vendor behind a battered counter grunts: 'If you break it, you buy it.'",
                "A tired merchant eyes you warily. 'No credit, no trouble.'",
                "The shop smells of ozone and desperation. 'Looking for something cheap or just lost?'"
            ],
            "corp": [
                "A holographic clerk beams: 'Welcome, valued customer. All transactions are monitored.'",
                "A synthetic voice chimes: 'Your satisfaction is our highest priority. Please spend generously.'",
                "A pristine counter gleams. 'May I interest you in our premium loyalty program?'"
            ],
            "cartel": [
                "A sharp-eyed merchant mutters: 'Ask for what you want. Don't waste my time.'",
                "A tattooed vendor leans in. 'If you can't pay, you can leave.'",
                "A heavyset dealer grins. 'We got what you need—if you got the credits.'"
            ],
            "ghost": [
                "A flickering terminal displays: 'State your request. No refunds.'",
                "The shop is empty, save for a humming console. 'Inventory... limited.'",
                "A chill hangs in the air. 'Welcome. Or what's left of it.'"
            ],
            "blacksite": [
                "A masked military officer says flatly: 'State your request. Efficiency is expected.'",
                "A cold voice echoes: 'Transactions are logged. Do not linger.'",
                "A security drone hovers nearby. 'Authorized personnel only.'"
            ],
        }
        SHOP_BANTER = {
            "slum": [
                "You want a receipt? I can write one on scrap paper.",
                "Hey, no refunds if it breaks.",
                "If it sparks, that's normal. Probably."
            ],
            "corp": [
                "Your purchase has been logged for loyalty points. Please come back soon!",
                "All sales are final, unless you're a shareholder!",
                "Thank you for supporting our quarterly projections! We're all in this together!"
            ],
            "cartel": [
                "Don't ask where it came from. You don't want to know.",
                "If you see the boss, you didn't see me.",
                "Don't ask too many questions around here.",
                "No refunds. No witnesses."
            ],
            "ghost": [
                "The terminal flickers: 'Thank you for your... presence.'",
                "You hear static. Or is it whispering?",
                "A cold draft follows you as you browse."
            ],
            "blacksite": [
                "Authorization confirmed. You have five minutes to exit.",
                "Unmarked crates only. No questions.",
                "Transaction complete. Move along."
            ],
        }
        if hub_type in SHOP_INTROS:
            print(f"\n{random.choice(SHOP_INTROS[hub_type])}")
        else:
            print("\nThe shopkeeper eyes you as you enter.")

        while True:
            print(f"\n=== {self.name} ===")
            print(f"Your Credits: {player.credits:,}")
            print("\nWhat would you like to do?")
            print("1. Browse Weapons")
            print("2. Browse Armor")
            print("3. Browse Items")
            print("4. Sell Goods")
            print("\n0. Go back")
            try:
                choice = int(input("\nEnter your choice (1-4): "))
                if choice == 1:  # Weapons
                    self.display_inventory('weapons', player)
                    weapon_choice = input("\nSelect weapon to buy: ")
                    self.handle_purchase('weapons', player, weapon_choice)
                    # Occasional banter
                    if hub_type in SHOP_BANTER and random.random() < 0.33:
                        print(random.choice(SHOP_BANTER[hub_type]))
                elif choice == 2:  # Armor
                    self.display_inventory('armor', player)
                    armor_choice = input("\nSelect armor to buy: ")
                    self.handle_purchase('armor', player, armor_choice)
                    if hub_type in SHOP_BANTER and random.random() < 0.33:
                        print(random.choice(SHOP_BANTER[hub_type]))
                elif choice == 3:  # Items
                    self.display_inventory('items', player)
                    item_choice = input("\nSelect item to buy: ")
                    self.handle_purchase('items', player, item_choice)
                    if hub_type in SHOP_BANTER and random.random() < 0.33:
                        print(random.choice(SHOP_BANTER[hub_type]))
                elif choice == 4:  # Sell Items
                    self._sell_items(player, game)
                elif choice == 0:  # Leave
                    print("\nYou go back to the Trade Hub...")
                    wait_for_enter()
                    return
            except ValueError:
                print("Invalid choice. Please enter 1-4.")
                wait_for_enter()

    def _sell_items(self, player, game):
        """Sell contraband items from player's inventory"""
        if not player.inventory:
            print("\nYou don't have any items to sell.")
            wait_for_enter()
            return
            
        print("\n=== SELL GOODS ===")
        # Warn about selling stolen goods at legal shops
        # INSERT_YOUR_CODE
        # Add some flavor text and make the warning come from NOVA
        print("\nYou approach the counter, goods in hand. The clerk eyes you with a practiced indifference.")
        wait_for_enter()
        if random.random() < 0.5:
            print("A nearby security drone swivels its camera in your direction, its lens glinting coldly.")
            wait_for_enter()
        print("[NOVA] 'Just a heads up: selling stolen or illegal goods at a legal trade hub is a great way to end up in a holding cell.'")
        wait_for_enter()


        print("Available items:")
        
        # Loop through all items in inventory
        for item in player.inventory[:]:  # Create a copy of list to allow removal during iteration
            base_value = item['value']
            
            # Generate random offer between 60% and 120% of value
            offer_multiplier = random.uniform(0.6, 1.2)
            offer = int(base_value * offer_multiplier)
            
            print(f"\n{item['name']}")
            print(f"Base value: {base_value:,} credits")
            print(f"The seller offers you: {offer:,} credits")
            
            print("\nAccept their offer?")
            print("1. Yes")
            print("2. No")
            print("\n0. Stop selling")
            
            try:
                choice = input("\nEnter choice (1-3): ")
                
                if choice == "0":
                    print("\nStopping sales...")
                    wait_for_enter()
                    return
                    
                if choice == "1":
                    if DiceRoller.chance(0.5):
                        print("\nThe seller confiscated the item and called in the cops!")
                        player.inventory.remove(item)
                        player.illegal_activity_today = True
                        police_result = PoliceEncounter(game).run()
                        if police_result == "game_over":
                            print("Game Over!")
                            print(f"You survived {game.days_survived} days.")
                            quit()
                        else:
                            print("\nYou escaped the police and returned to the trade hub.")
                            wait_for_enter()
                            break
                    else:
                        print(f"\nSold {item['name']} for {offer:,} credits!")
                        wait_for_enter()
                        player.inventory.remove(item)
                        player.credits += offer
                    wait_for_enter()
                elif choice == "2":
                    print("\nOffer declined.")
                    wait_for_enter()
            except ValueError:
                print("\nInvalid choice.")
                wait_for_enter()
                continue

class BlackMarketShop(Shop):
    """Illegal shop with better items but higher prices and heat risk"""
    def __init__(self):
        super().__init__("Black Market")
        self.restock()
    
    def restock(self):
        """Restock the black market with both legal and illegal items"""
        # Clear inventory
        self.inventory = {
            'weapons': [],
            'armor': [],
            'items': [MEDKIT, SHIELD, STUN_GRENADE]  # More items available at black market
        }
        
        # Add 3-5 weapons with preference for illegal ones
        num_weapons = DiceRoller.d6() // 2 + 2  # 2-4 weapons
        for _ in range(num_weapons):
            # 80% chance of illegal weapons
            if DiceRoller.chance(0.8):
                weapon = get_random_weapon(include_illegal=True, min_rarity=UNCOMMON)
            else:
                weapon = get_random_weapon(include_illegal=False, min_rarity=RARE)
                
            if weapon and weapon not in self.inventory['weapons']:
                self.inventory['weapons'].append(weapon)
                
        # Add 2-3 armor pieces with preference for illegal ones
        num_armor = DiceRoller.d6() // 2 + 1  # 1-3 armor pieces
        for _ in range(num_armor):
            # 80% chance of illegal armor
            if DiceRoller.chance(0.8):
                armor = get_random_armor(include_illegal=True, min_rarity=UNCOMMON)
            else:
                armor = get_random_armor(include_illegal=False, min_rarity=RARE)
                
            if armor and armor not in self.inventory['armor']:
                self.inventory['armor'].append(armor)
    
    def _get_item_price(self, item):
        """Get the price of an item, with black market markup"""
        base_price = super()._get_item_price(item)
        
        # Apply black market discount based on legality
        if hasattr(item, 'is_illegal'):
            if not item.is_illegal:
                return int(base_price * 0.9)  # Discount on legal weapons
            else:
                return int(base_price * 1) 
        else:
            return int(base_price * 1) 
    
    def shop_menu(self, game):
        """Main shop menu for Black Market"""
        player = game.player
        
        # Increase heat for visiting black market
        player.illegal_activity_today = True
        
        # Generate atmospheric details
        market_type, market_visual, market_sound, market_mood, dealer_personalities, nova_commentary = generate_black_market_atmosphere()
        
        # Entry atmosphere
        print(f"\nYou descend into the {market_type.replace('_', ' ')}...")
        wait_for_enter()
        
        # Random atmospheric details
        if random.random() < 0.7:
            print(random.choice(market_visual[market_type]))
        if random.random() < 0.5:
            print(random.choice(market_sound[market_type]))
        if random.random() < 0.5:
            print(random.choice(market_mood[market_type]))
                
        # Dealer introduction
        print(random.choice(dealer_personalities[market_type]))
        wait_for_enter()
        
        # NOVA commentary
        if random.random() < 0.6:
            print(random.choice(nova_commentary[market_type]))
            wait_for_enter()
        
        # Shop banter by market type
        shop_banter = {
            "underground": [
                "\"Cash only. No questions.\"",
                "\"If it breaks, you never saw me.\"",
                "\"Keep your voice down. The walls have ears.\""
            ],
            "smuggler_den": [
                "\"Everything's hot, but it all works.\"",
                "\"No receipts, no returns, no problems.\"",
                "\"You want warranty? Try the corporate districts.\""
            ],
            "pirate_outpost": [
                "\"Fresh from a Federation convoy. Still warm.\"",
                "\"You break it, you bought it. Literally.\"",
                "\"No cops have found this place yet. Let's keep it that way.\""
            ],
            "shadow_bazaar": [
                "\"Some things are better left unasked.\"",
                "\"The price includes discretion.\"",
                "\"Payment first. Questions never.\""
            ]
        }

        while True:
            print(f"\n=== {self.name} ===")
            print(f"Your Credits: {player.credits:,}")
            print("\nWhat would you to do?")
            print("1. Browse Weapons")
            print("2. Browse Armor")
            print("3. Browse Items")
            print("4. Sell Goods")
            print("5. Open Sealed Crates")
            print("\n0. Leave Black Market")
            
            try:
                choice = int(input("\nEnter your choice (1-5): "))
                
                if choice == 1:  # Weapons
                    self.display_inventory('weapons', player)
                    weapon_choice = input("\nSelect weapon to buy: ")
                    if self.handle_purchase('weapons', player, weapon_choice):
                        # Occasional dealer banter
                        if random.random() < 0.4:
                            print(f"\n{random.choice(shop_banter[market_type])}")
                            wait_for_enter()
                    
                elif choice == 2:  # Armor
                    self.display_inventory('armor', player)
                    armor_choice = input("\nSelect armor to buy: ")
                    if self.handle_purchase('armor', player, armor_choice):
                        if random.random() < 0.4:
                            print(f"\n{random.choice(shop_banter[market_type])}")
                            wait_for_enter()
                    
                elif choice == 3:  # Items
                    self.display_inventory('items', player)
                    item_choice = input("\nSelect item to buy: ")
                    if self.handle_purchase('items', player, item_choice):
                        if random.random() < 0.4:
                            print(f"\n{random.choice(shop_banter[market_type])}")
                            wait_for_enter()
                    
                elif choice == 4:  # Sell Items
                    self._sell_items(player, market_type)
                    
                elif choice == 5:  # Crack Sealed Crates
                    self._crack_sealed_crates(player, game, market_type)
                    
                elif choice == 0:  # Leave
                    # Themed exit messages
                    exit_messages = {
                        "underground": "You climb back up to street level, leaving the shadows behind...",
                        "smuggler_den": "You navigate back through the maze of containers...",
                        "pirate_outpost": "You walk past the trophy wall, feeling eyes on your back...",
                        "shadow_bazaar": "The darkness seems to follow you as you leave..."
                    }
                    print(f"\n{exit_messages[market_type]}")
                    wait_for_enter()
                    return
                    
            except ValueError:
                print("Invalid choice. Please enter 1-5.")
                wait_for_enter()
    
    def _crack_sealed_crates(self, player, game, market_type):
        """Open sealed crates if player has a contract with them"""
        if not player.current_contract:
            print("\nYou don't have any crates to open.")
            wait_for_enter()
            return
            
        # Check for sealed crates
        sealed_crates = [
            (i, crate) for i, crate in enumerate(player.current_contract.crates)
            if crate.tier == "sealed" and not crate.is_opened
        ]
        
        if not sealed_crates:
            print("\nYou don't have any sealed crates to open.")
            wait_for_enter()
            return
        
        # Themed approach based on market type
        crate_opening_intro = {
            "underground": "A twitchy tech specialist with modified tools approaches your crates...",
            "smuggler_den": "A skilled cargo handler cracks their knuckles and examines the locks...",
            "pirate_outpost": "A scarred veteran grins and pulls out a plasma cutter...",
            "shadow_bazaar": "A silent figure in dark robes produces mysterious scanning equipment..."
        }
        
        print(f"\n{crate_opening_intro[market_type]}")
        wait_for_enter()
        print("\"I can crack these open for you:\"")
        
        cost = DiceRoller.d6() * 500
        for idx, (crate_idx, crate) in enumerate(sealed_crates, 1):
            print(f"{idx}. Sealed Crate #{crate_idx + 1} - {cost:,} credits")
        print("\n0. Cancel")
        
        try:
            choice = int(input("\nWhich crate do you want to open? "))
            if 1 <= choice <= len(sealed_crates):
                crate_idx, crate = sealed_crates[choice - 1]
                
                # Check if player can afford it
                if player.credits < cost:
                    print("\nYou don't have enough credits.")
                    wait_for_enter()
                    return
                    
                player.credits -= cost
                player.illegal_activity_today = True
                player.heat += 1
                
                # Themed opening process
                opening_process = {
                    "underground": "Sparks fly as modified tools bypass the security locks...",
                    "smuggler_den": "Hydraulic tools hiss as the crate's seals are carefully broken...",
                    "pirate_outpost": "The plasma cutter makes quick work of the reinforced hinges...",
                    "shadow_bazaar": "Strange energy patterns dance across the crate before it opens silently..."
                }
                
                print(f"\n{opening_process[market_type]}")
                wait_for_enter()
                
                # Open the crate
                contents, value = crate.open(player.current_contract, game)
                
                if crate.is_stone:
                    print(f"\n⚠ IT'S AN INFINITY STONE! ⚠")
                    player.stones_discovered.append(crate.stone_type)
                    wait_for_enter()

                print(f"\nThe crate contains: {contents}")

                print("\nWhat do you want to do?")
                print("1. Continue with contract delivery")
                print("2. Steal the items")
                
                try:
                    sell_choice = int(input("\nEnter choice (1-2): "))
                    if sell_choice == 1:
                        print("\nYou decide to stick with the contract.")
                    elif sell_choice == 2:
                        # Store contract reference before clearing it
                        contract = player.current_contract
                        
                        # Add to player inventory and remove from contract
                        for crate in contract.crates:
                            if crate.is_stone:
                                player.stones.append(crate.stone_type)
                                print(f"\nThe {crate.stone_type} Stone pulses with energy as you pocket it...")
                                wait_for_enter()
                            else:
                                player.inventory.append({
                                    'name': crate.contents,
                                    'value': crate.value,
                                    'is_contraband': crate.tier in ['illicit', 'sealed']
                                })
                                print(f"\nAdded to inventory: {crate.contents}")
                                wait_for_enter()
                        
                        # Now clear the contract
                        player.current_contract = None
                        
                        print("\nThe cartel won't be happy about this...")
                        # 50% chance of immediate cartel encounter
                        player.cartel_threat_level += 1  # Increase threat either way
                        if DiceRoller.chance(0.5):
                            cartel = CartelEncounter(game)
                            result = cartel.run()
                            
                            if result == "game_over":
                                return "game_over"
                        
                except ValueError:
                    print("\nInvalid choice.")
                wait_for_enter()
        except ValueError:
            pass
    
    def _sell_items(self, player, market_type):
        """Sell contraband items from player's inventory"""
        
        if not player.inventory:
            print("\nYou don't have any items to sell.")
            wait_for_enter()
            return
        
        # Themed selling introduction
        selling_intro = {
            "underground": "A buyer in the shadows examines your goods with a dim flashlight...",
            "smuggler_den": "A merchant with multiple identity cards evaluates your cargo...",
            "pirate_outpost": "A fence with gold teeth grins at your collection...",
            "shadow_bazaar": "A robed figure appraises your items with unseen eyes..."
        }
        
        print(f"\n{selling_intro[market_type]}")
        wait_for_enter()
        
        print("\n=== SELL ITEMS ===")
        print("Available items:")
        
        # Loop through all items in inventory
        for item in player.inventory[:]:  # Create a copy of list to allow removal during iteration
            base_value = item['value']
            
            # Generate random offer between 60% and 120% of value
            # Increase multiplier for contraband items
            if 'contraband' in item.get('tags', []):
                offer_multiplier = random.uniform(1.2, 1.8)  # 120-180% for contraband
            else:
                offer_multiplier = random.uniform(0.6, 1.2)  # 60-120% for normal items 
            offer = int(base_value * offer_multiplier)
            
            print(f"\n{item['name']}")
            print(f"Base value: {base_value:,} credits")
            print(f"Seller offers: {offer:,} credits")
            
            print("\nAccept offer?")
            print("1. Yes")
            print("2. No")
            print("\n0. Stop selling")
            
            try:
                choice = input("\nEnter choice (1-2, 0 to stop): ")
                
                if choice == "0":
                    # Themed stop selling message
                    stop_messages = {
                        "underground": "You decide to keep your remaining goods hidden...",
                        "smuggler_den": "You zip up your cargo bag and step back...",
                        "pirate_outpost": "You gather your remaining items and nod to the fence...",
                        "shadow_bazaar": "You withdraw your goods into the shadows..."
                    }
                    print(f"\n{stop_messages[market_type]}")
                    wait_for_enter()
                    return
                    
                if choice == "1":
                    # Themed transaction completion
                    transaction_messages = {
                        "underground": "Credits change hands in the darkness...",
                        "smuggler_den": "The deal is sealed with a firm handshake...",
                        "pirate_outpost": "Gold teeth flash as the transaction completes...",
                        "shadow_bazaar": "Payment appears as if from nowhere..."
                    }
                    
                    player.inventory.remove(item)
                    player.credits += offer
                    print(f"\n{transaction_messages[market_type]}")
                    print(f"Sold {item['name']} for {offer:,} credits!")
                    wait_for_enter()
                elif choice == "2":
                    print("\nOffer declined.")
                    wait_for_enter()
            except ValueError:
                print("\nInvalid choice.")
                wait_for_enter()
                continue