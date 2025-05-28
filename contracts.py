from utils import DiceRoller, wait_for_enter
import random
from trade_hub_gameplay import handle_trade_hub
from fights import CartelEncounter

class Crate:
    def __init__(self, tier):
        self.tier = tier  # "legit", "illicit", or "sealed"
        self.contents = None  # Will be revealed when opened
        self.is_opened = False
        self.is_stone = False
        self.stone_type = None
        self.value = self._set_value()  # Set initial value based on tier
    
    def _set_value(self):
        """Calculate the value of the crate"""
        if self.tier == "legit":
            return DiceRoller.d6() * 100
        elif self.tier == "illicit":
            return DiceRoller.d6() * 500
        else:  # sealed
            return DiceRoller.d6() * 1000

    def open(self, contract=None, game=None):
        """Open the crate and determine its contents"""
        if self.is_opened:
            return self.contents, self.value
            
        self.is_opened = True
        
        # Add some tension when opening crates
        if self.tier == "sealed":
            tension_lines = [
                "The seals hiss as they release...",
                "You hear a faint humming from inside the crate...",
                "The lid creaks open with an ominous groan...",
                "Strange symbols glow briefly on the crate's surface...",
                "A cold mist escapes as the crate unseals..."
            ]
            print(random.choice(tension_lines))
            wait_for_enter()
        
        # Determine if it's a stone based on tier
        stone_chance = {
            "legit": 0.05,  # 5% chance
            "illicit": 0.1,  # 10% chance
            "sealed": 0.85  # 85% chance
        }
        
        if DiceRoller.chance(stone_chance[self.tier]):
            self.is_stone = True
            # List of available stones
            stones = ["Space", "Mind", "Reality", "Power", "Soul", "Time"]
            
            # Remove stones already discovered by the player
            if game and hasattr(game.player, 'stones_discovered'):
                available_stones = [stone for stone in stones if stone not in game.player.stones_discovered]
            else:
                available_stones = stones[:]
            
            # Remove stones already found in this contract
            if contract:
                stones_in_contract = [crate.stone_type for crate in contract.crates if crate.is_stone and crate.stone_type]
                available_stones = [stone for stone in available_stones if stone not in stones_in_contract]
            
            # If no stones are available, this crate becomes normal cargo
            if not available_stones:
                self.is_stone = False
            else:
                self.stone_type = random.choice(available_stones)
                self.contents = f"{self.stone_type} Stone"
                self.value = random.randint(5, 10) * 10000 # Update value for stone
                
                # Dramatic stone discovery
                if random.random() < 0.5:
                    nova_stone_lines = [
                        "[NOVA] 'Well, that's not in any shipping manifest I've ever seen.'",
                        "[NOVA] 'I'm reading energy signatures that shouldn't exist. Congratulations, you found trouble.'",
                        "[NOVA] 'My sensors are going crazy. Whatever that is, it's not from around here.'",
                        "[NOVA] 'If that thing starts glowing, I'm ejecting you into space.'"
                    ]
                    print(random.choice(nova_stone_lines))
                    wait_for_enter()
        
        if not self.is_stone:
            # Generate normal contents based on tier
            if self.tier == "legit":
                contents_list = [
                    "Medical Supplies",
                    "Food Rations",
                    "Spare Parts",
                    "Construction Materials",
                    "Scientific Equipment"
                ]
            elif self.tier == "illicit":
                contents_list = [
                    "Smuggled Weapons",
                    "Illegal Cybernetics",
                    "Restricted Biotech",
                    "Black Market AI",
                    "Forbidden Artifacts"
                ]
            else:  # sealed
                contents_list = [
                    "Experimental Quantum Core",
                    "Ancient Alien Relic",
                    "Prototype Warp Drive",
                    "Crystalline Power Matrix",
                    "Temporal Stabilizer",
                    "Strange Device"
                ]
            self.contents = random.choice(contents_list)
            
            # Occasional NOVA comment on contents
            if random.random() < 0.2:
                if self.tier == "illicit":
                    nova_comments = [
                        "[NOVA] 'That's definitely not legal in most systems.'",
                        "[NOVA] 'I didn't see anything. Just so we're clear.'",
                        "[NOVA] 'If you get arrested, I'm pleading ignorance.'"
                    ]
                elif self.tier == "sealed":
                    nova_comments = [
                        "[NOVA] 'I can't even scan what that is. That's... concerning.'",
                        "[NOVA] 'Whatever that is, someone really didn't want it opened.'",
                        "[NOVA] 'My databases have no record of this technology.'"
                    ]
                else:
                    nova_comments = [
                        "[NOVA] 'Finally, something normal. I was starting to worry.'",
                        "[NOVA] 'Standard cargo. How refreshingly boring.'"
                    ]
                print(random.choice(nova_comments))
                wait_for_enter()
        
        return self.contents, self.value

class Contract:
    def __init__(self, max_crates):
        self.crates = []
        # First determine distance (sectors to travel)
        self.distance = DiceRoller.d6() + 2  # 3-8 sectors
        # Deadline must be >= distance to be possible
        self.deadline = max(self.distance, DiceRoller.d6() + 4)  # Ensures deadline >= distance
        self.sectors_traveled = 0
        self.base_reward = 0
        self.reward = 0
        self._generate_crates(max_crates)
        self._calculate_reward()
    
    def is_illegal(self):
        """Check if the contract contains any illicit or sealed crates"""
        return any(crate.tier in ['illicit', 'sealed'] for crate in self.crates)
    
    def _generate_crates(self, max_crates):
        # Generate 1 to max_crates number of crates
        num_crates = random.randint(1, max_crates)
        
        for _ in range(num_crates):
            # Weight the random choice towards legit crates
            # Weight heavily towards legit crates
            roll = DiceRoller.d100()
            # More balanced distribution:
            # 60% legit, 25% illicit, 15% sealed
            if roll <= 50:  # 60% chance
                tier = "legit"
            elif roll <= 75:  # 25% chance
                tier = "illicit"
            else:  # 15% chance
                tier = "sealed"
            
            crate = Crate(tier)
            self.crates.append(crate)
            self.base_reward += crate.value
    
    def _calculate_reward(self):
        """Calculate final reward based on deadline pressure and distance"""
        # First calculate base value from crates
        self.base_reward = sum(crate.value for crate in self.crates)
        
        
        # Time pressure multiplier:
        # If deadline == distance (minimum possible): 2.0x
        # For each extra day, reduce by 0.25x
        # Minimum multiplier is 1.0x
        time_pressure = self.deadline - self.distance  # Extra days available
        deadline_multiplier = max(1, 1.5 - (time_pressure * 0.25))
        
        # Apply both multipliers
        self.reward = int(self.base_reward * deadline_multiplier)

    def _recalculate_reward_after_opening(self):
        """Recalculate reward based on actual opened crate values"""
        # Calculate new base reward from opened crate values
        actual_base_reward = sum(crate.value for crate in self.crates)
        
        # Apply the same deadline multiplier that was used initially
        time_pressure = self.deadline - self.distance if self.deadline > 0 else 0
        deadline_multiplier = max(1, 1.5 - (time_pressure * 0.25))
        
        # Update reward based on actual values
        self.reward = int(actual_base_reward * deadline_multiplier)

    def calculate_heat_risk(self):
        """Calculate how much heat this contract will add when accepted"""
        heat = 0
        for crate in self.crates:
            if crate.tier == "illicit":
                heat += 5  # Illicit crates are obviously suspicious
            elif crate.tier == "sealed":
                heat += 10  # Sealed crates are even more suspicious
        return heat

    def accept(self, game):
        """Accept the contract and apply consequences"""
        heat_increase = self.calculate_heat_risk()

        game.player.heat += heat_increase
        game.player.current_contract = self
        
        # Occasional contract acceptance flavor
        if random.random() < 0.4:
            if self.is_illegal():
                contract_warnings = [
                    "The handler's eyes dart around nervously as they hand over the manifest.",
                    "'Don't open the crates until you reach the destination,' they whisper.",
                    "You notice the contract has no official stamps or signatures.",
                    "'If anyone asks, you never saw me,' the contact mutters before disappearing.",
                    "The payment is in untraceable credits. You don't ask why.",
                    "The client is a little too eager to get rid of these crates.",
                    "The broker laughs nervously as you sign the contract."
                ]
            else:
                contract_acceptance = [
                    "The clerk stamps the contract with practiced efficiency.",
                    "'Standard shipping insurance is included,' they note cheerfully.",
                    "You shake hands with the client. A legitimate business transaction.",
                    "The paperwork is filed in triplicate. Everything by the book.",
                    "'Safe travels,' the handler says with a smile."
                ]
            print(random.choice(contract_warnings if self.is_illegal() else contract_acceptance))
            wait_for_enter()
        
        # NOVA quips about contract acceptance
        if random.random() < 0.3:
            if self.is_illegal():
                nova_illegal_quips = [
                    "[NOVA] 'You sure about this? My insurance doesn't cover acts of stupidity.'",
                    "[NOVA] 'If this goes bad, I'm updating my resume.'",
                    "[NOVA] 'I'm logging this under 'questionable life choices.''",
                    "[NOVA] 'Next time, maybe read the fine print before signing.'"
                ]
            else:
                nova_legal_quips = [
                    "[NOVA] 'A legal job. How... ordinary.'",
                    "[NOVA] 'Finally, something that won't get us shot at.'",
                    "[NOVA] 'I like these boring contracts. They're good for my stress levels.'"
                ]
            print(random.choice(nova_illegal_quips if self.is_illegal() else nova_legal_quips))
            wait_for_enter()
        
        return True


    def get_progress_map(self):
        """Returns ASCII progress map"""
        total_sectors = self.distance
        current_pos = self.sectors_traveled
        
        # Create the map
        map_str = "[HUB]"
        for i in range(total_sectors + 1):
            map_str += "---"
            if i == current_pos:
                map_str += "[YOU]"  # Current position
            elif i < current_pos:
                map_str += "[?]"  # Visited sector
            elif i == total_sectors :
                map_str += "[DEST]"  # Destination
            else:
                map_str += "[?]"  # Unknown sector
        
        return map_str

    def is_at_destination(self):
        """Check if we've arrived"""
        return self.sectors_traveled >= self.distance

    def check_deadline(self, game):
        """Handle contract deadline and consequences"""
        if self.deadline <= 0:  # Already at 0, now expires
            print("\nContract expired! The cartel is not happy...")
            if random.random() < 0.4:
                print("[NOVA] 'I tried to warn you about time management.'")
            wait_for_enter()
            print("They're coming to collect their cargo...")
            wait_for_enter()
            
            # Trigger cartel encounter instead of TODO
            cartel = CartelEncounter(game)
            result = cartel.run()
            
            if result == "game_over":
                return "game_over"
                
            game.player.current_contract = None
        else:
            self.deadline -= 1  # Decrement at end of check

    def handle_arrival(self, game):
        """Handle arrival at destination"""
        print("\nYou've arrived at your destination!")
        
        # Arrival atmosphere
        if random.random() < 0.4:
            arrival_descriptions = [
                "The docking clamps engage with a satisfying thunk.",
                "You can see other cargo haulers loading and unloading nearby.",
                "The destination hub buzzes with commercial activity.",
                "Security scanners sweep your ship as you land.",
                "A ground crew waves you toward a loading bay."
            ]
            print(random.choice(arrival_descriptions))
            wait_for_enter()

        
        if random.random() < 0.25:
            nova_arrival_quips = [
                "[NOVA] 'Docking complete. Try not to do anything suspicious.'",
                "[NOVA] 'We made it in one piece. I'm as surprised as you are.'",
                "[NOVA] 'Time to see if your cargo is what they ordered.'"
            ]
            print(random.choice(nova_arrival_quips))
            wait_for_enter()


        print("Opening crates to verify contents...")
        wait_for_enter()
        
        # Open all crates and reveal contents
        stones_found = []
        print("\nCrate Contents:")
        for i, crate in enumerate(self.crates, 1):
            print(f"\nCrate {i}:")
            print("Opening seal...")
            wait_for_enter()
            
            contents, value = crate.open(self, game)

            if crate.is_stone:
                print("An otherworldly energy pulses through the ground as you open the crate...")
                wait_for_enter()
                print(f"Contains the {crate.stone_type} Stone! Value: {value:,} credits")
                wait_for_enter()
                stones_found.append(crate)
                game.player.stones_discovered.append(crate.stone_type)

                # Each stone adds heat to the player
                game.player.heat += 5
            else:   
                print(f"Contains: {contents} | Value: {value:,} credits")
        
        # Recalculate reward based on actual opened crate values
        self._recalculate_reward_after_opening()
        
        # Check if we arrived early and give bonus for each day (now based on correct reward)
        if self.deadline > 0:
            bonus_per_day = self.reward * 0.05  # 5% bonus per day early
            total_bonus = int(bonus_per_day * self.deadline)
            print(f"\nThe seller is impressed that you are {self.deadline} days early and offers a bonus of {total_bonus:,} credits!")
            wait_for_enter()

            if random.random() < 0.3:
                nova_time_quips = [
                "[NOVA] 'Wow, you made it early. I never thought I'd see the day.'",
                "[NOVA] 'Good work, I guess.Let's try to keep this up.'",
                "[NOVA] 'Punctuality pays. Who would have thought?'"
                ]
                print(random.choice(nova_time_quips))
                wait_for_enter()
            self.reward += total_bonus
        
        # Display payment breakdown
        print("\n" + "="*50)
        print("PAYMENT BREAKDOWN")
        print("="*50)
        
        # Calculate components for display
        base_crate_value = sum(crate.value for crate in self.crates)
        time_pressure = self.deadline - self.distance if self.deadline > 0 else 0
        deadline_multiplier = max(1, 1.5 - (time_pressure * 0.25))
        base_reward = int(base_crate_value * deadline_multiplier)
        early_bonus = self.reward - base_reward if self.deadline > 0 else 0
        
        print(f"Crate Values:        {base_crate_value:,} credits")
        print(f"Time Pressure: x{deadline_multiplier:.2f}")
        print(f"Base Payment:        {base_reward:,} credits")
        if early_bonus > 0:
            print(f"Early Bonus:         +{early_bonus:,} credits")
        print("-" * 50)
        print(f"TOTAL PAYMENT:       {self.reward:,} credits")
        print("="*50)
        wait_for_enter()
        
        print("\nWhat would you like to do?")
        print("1. Complete delivery")
        print("2. Steal the cargo")
        
        while True:
            try:
                choice = int(input("\nEnter your choice (1-2): "))
                if choice == 1:
                    # Complete delivery
                    print("\nThe client accepts the delivery...")
                    
                    # Client dialogue based on what was delivered
                    if random.random() < 0.3:
                        if stones_found:
                            client_stone_dialogue = [
                                "'Excellent work. This will change everything.'",
                                "'You have no idea what you've just delivered. He will be very pleased.'",
                                "'The universe is about to shift, thanks to you.'"
                            ]
                            print(f"\n{random.choice(client_stone_dialogue)}")
                        elif self.is_illegal():
                            client_illegal_dialogue = [
                                "'Good. No questions asked, as agreed.'",
                                "'The less you know about this, the better.'",
                                "'Look, pretend this transaction never happened.'"
                            ]
                            print(f"\n{random.choice(client_illegal_dialogue)}")
                        else:
                            client_legal_dialogue = [
                                "'Perfect condition. Exactly what we ordered.'",
                                "'Excellent work. We'll use your services again.'",
                                "'A professional job. Thank you.'"
                            ]
                            print(f"\n{random.choice(client_legal_dialogue)}")
                    wait_for_enter()
                    
                    # If we delivered any stones, track them
                    if stones_found:
                        print("\nAs you hand over the stones, you feel the weight of your decision...")
                        wait_for_enter()
                        print("The universe may never be the same...")
                        if random.random() < 0.3:
                            # INSERT_YOUR_CODE
                            nova_lines = [
                                "[NOVA] 'I hope you know what you just did.'",
                                "[NOVA] 'Well, at least we don't have to deal with those on us.'"
                            ]
                            print(random.choice(nova_lines))
                        wait_for_enter()
                        
                    game.player.credits += self.reward
                    print(f"You earned {self.reward:,} credits!")
                    
                    wait_for_enter()
                    
                    # Clear contract
                    game.player.current_contract = None
                    break
                    
                elif choice == 2:
                    # Steal cargo
                    print("\nYou decide to keep the cargo for yourself - the cartel won't be happy about this...")
                    
                    wait_for_enter()
                    
                    # Major heat increase for stealing
                    game.player.heat += 30
                    game.player.illegal_activity_today = True
                    
                    # Add all items to inventory
                    for crate in self.crates:
                        if crate.is_stone:
                            game.player.stones.append(crate.stone_type)
                            print(f"\nThe {crate.stone_type} Stone pulses with energy as you pocket it...")
                            if random.random() < 0.3:
                                print("[NOVA] 'That thing is giving off readings I can't even classify.'")
                            wait_for_enter()
                        else:
                            game.player.inventory.append({
                                'name': crate.contents,
                                'value': crate.value,
                                'is_contraband': crate.tier in ['illicit', 'sealed']
                            })
                            print(f"\nAdded to inventory: {crate.contents}")
                            wait_for_enter()
                    
                    # Trigger cartel encounter instead of TODO
                    # 50% chance of cartel encounter
                    game.player.cartel_threat_level += 1  # Increase threat either way
                    if DiceRoller.chance(0.5):
                        cartel = CartelEncounter(game)
                        result = cartel.run()
                        if result == "game_over":
                            return "game_over"
                    
                    # Clear contract
                    game.player.current_contract = None
                    break
                    
            except ValueError:
                print("Invalid choice")
        
        game.check_for_endings()
        # Contract delivery is complete - let the game loop handle the next day
        # The player will visit a trade hub on their next turn

class TradeHub:
    def __init__(self):
        self.fuel_price = 50  # Credits per unit
        self.available_contracts = []
    
    def generate_contracts(self, max_crates):
        """Generate new contracts respecting ship's cargo capacity"""
        self.available_contracts = [Contract(max_crates) for _ in range(3)]
    
    def display_contracts(self):
        print("\nAvailable Contracts:")
        for i, contract in enumerate(self.available_contracts, 1):
            print(f"\nContract {i}:")
            print(f"Distance: {contract.distance} sectors")
            print(f"Deadline: {contract.deadline} days")
            show_reward = True
            for crate in contract.crates:
                if crate.tier.title() == "Sealed":
                    show_reward = False
            if show_reward:
                print(f"Reward: {contract.reward:,} credits")
            else:
                print("Reward: ???")
            
            print("Cargo:")
            for crate in contract.crates:
                print(f"- {crate.tier.title()} Crate")
            
            heat_risk = contract.calculate_heat_risk()
            print(f"Heat Increase: +{heat_risk}")
            
            print("-" * 20)
    
    def refuel_ship(self, player, ship, amount):
        cost = amount * self.fuel_price
        if player.credits >= cost:
            player.credits -= cost
            ship.fuel = min(ship.max_fuel, ship.fuel + amount)  # Cap at ship's max fuel capacity
            return True
        return False
    
    def police_search(self, player):
        """Basic police search based on heat level"""
        if DiceRoller.chance(player.heat / 100):  # Heat is percentage chance of search
            print("\nPOLICE SEARCH!")
            return True
        return False 