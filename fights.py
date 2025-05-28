from utils import DiceRoller, wait_for_enter
from combat import Combat, LOCAL_DEPUTY, SECTOR_BADGE, FEDERATION_RANGER, GALACTIC_ENFORCER, BountyHunter, Enemy
import random
class PoliceEncounter():
    """Federation police patrol encounter. Difficulty affected by heat."""
    def __init__(self, game):
        self.game = game

    def run(self):
        # Atmospheric opening based on heat level
        
        if self.game.player.heat > 80:
            atmosphere_lines = [
                "Your ship's radar scream is going haywire. Something is coming...",
                "The comm crackles with encrypted chatter - they've been hunting you...",
                "Warning lights bathe the cockpit in red as heavily armed ships converge..."
            ]
        elif self.game.player.heat > 40:
            atmosphere_lines = [
                "Your scanner picks up an authoritative transponder signal.",
                "The comm channel bursts with official Federation frequencies.",
                "Professional voices come over the comm channel."
            ]
        else:
            atmosphere_lines = [
                "A routine patrol sweep brings unwanted attention - lights start flashing behind you.",
                "Your ship registers on someone's scanner at the wrong moment. Lights start flashing behind you.",
                "The comm channel is buzzing with an official message. You've been flagged for inspection."
            ]
        wait_for_enter()
        print(random.choice(atmosphere_lines))
        wait_for_enter()

        # Add a chance for some NOVA lines based on cargo and legality before boarding
        player = self.game.player
        nova_lines = []

        # Check for contract cargo
        has_contract_cargo = bool(getattr(player, "current_contract", None) and getattr(player.current_contract, "crates", []))
        # Check for illegal contract cargo
        has_illegal_contract_cargo = False
        if has_contract_cargo:
            for crate in player.current_contract.crates:
                if getattr(crate, "is_contraband", False) or getattr(crate, "is_illegal", False) or getattr(crate, "is_stolen", False):
                    has_illegal_contract_cargo = True
                    break

        # Check for illegal items in inventory
        has_illegal_inventory = False
        for item in getattr(player, "inventory", []):
            if getattr(item, "is_contraband", False) or getattr(item, "is_illegal", False) or getattr(item, "is_stolen", False):
                has_illegal_inventory = True
                break

        # Chance to trigger a NOVA line (about 40%)
        if random.random() < 0.5:
            if has_illegal_contract_cargo or has_illegal_inventory:
                illegal_lines = [
                    "[NOVA] 'Uh, we've got some things on board that would be... hard to explain.'",
                    "[NOVA] 'If they find the contraband, we're toast.'",
                    "[NOVA] 'Maybe now's a good time to hide the illegal stuff. Oh wait, too late.'",
                    "[NOVA] 'Just act natural. And hope they don't bring out the scanners.'",
                    "[NOVA] 'I told you that stuff looked suspicious. Now look where we are.'"
                ]
                print(random.choice(illegal_lines))
            elif has_contract_cargo:
                cargo_lines = [
                    "[NOVA] 'Let's hope they don't get curious about our cargo manifest.'",
                    "[NOVA] 'Smile and wave. Maybe they won't ask about the crates.'",
                    "[NOVA] 'If they open those crates, we might have some explaining to do.'"
                ]
                print(random.choice(cargo_lines))
            else:
                nervous_lines = [
                    "[NOVA] 'Try not to look guilty. Routine inspection, right?'",
                    "[NOVA] 'Maybe they'll just check our papers and move on.'",
                    "[NOVA] 'Deep breaths. We can get through this.'"
                ]
                print(random.choice(nervous_lines))
            wait_for_enter()

        # Determine patrol type based on heat
        if self.game.player.heat > 85:  # Heat level 5 (81-100): Bounty Hunters
            enemy_type, patrol_desc = self._select_enemy_by_heat(5)
        elif self.game.player.heat > 65:  # Heat level 4 (61-80): Primarily Galactic Enforcers
            enemy_type, patrol_desc = self._select_enemy_by_heat(4)
        elif self.game.player.heat > 40:  # Heat level 3 (41-60): Primarily Federation Rangers
            enemy_type, patrol_desc = self._select_enemy_by_heat(3)
        elif self.game.player.heat > 20:  # Heat level 2 (21-40): Primarily Sector Badges
            enemy_type, patrol_desc = self._select_enemy_by_heat(2)
        else:  # Heat level 1 (0-20): Primarily Local Deputies
            enemy_type, patrol_desc = self._select_enemy_by_heat(1)
            
        print(f"\n{patrol_desc}")
        wait_for_enter()
        
        # NOVA quips based on encounter type
        if random.random() < 0.5:
            enemy = enemy_type()
            if any(hunter_name in enemy.name for hunter_name in ["Agent Andrews", "Killer Klakring", "T-Mont the Tyrant", "Garth Vader", "D-Mac the Destroyer"]):
                nova_bounty_quips = [
                    "[NOVA] 'Well, that's not good. Bounty hunters don't usually give warnings.'",
                    "[NOVA] 'I've seen this hunter's work before. It's not pretty.'",
                    "[NOVA] 'They're here for the bounty on your head. No negotiating with them.'",
                    "[NOVA] 'Professional killer, incoming. Hope your life insurance is up to date.'"
                ]
                print(random.choice(nova_bounty_quips))
            elif "Galactic Enforcer" in enemy.name:
                nova_enforcer_quips = [
                    "[NOVA] 'Galactic Enforcers. The Federation's finest. This is bad.'",
                    "[NOVA] 'These guys don't mess around. They shoot first and file paperwork later.'",
                    "[NOVA] 'Elite forces. I'd suggest compliance, but you never listen to me anyway.'"
                ]
                print(random.choice(nova_enforcer_quips))
            elif "Federation Ranger" in enemy.name:
                nova_ranger_quips = [
                    "[NOVA] 'Rangers. Professional, disciplined, and very well-armed.'",
                    "[NOVA] 'These aren't corrupt locals. They actually believe in justice.'",
                    "[NOVA] 'Federation Rangers don't take bribes. Just so you know.'"
                ]
                print(random.choice(nova_ranger_quips))
            elif "Sector Badge" in enemy.name:
                nova_badge_quips = [
                    "[NOVA] 'Sector badges. Greedy, but predictable.'",
                    "[NOVA] 'These guys are in it for the credits. Might be negotiable.'",
                    "[NOVA] 'Corrupt enforcement. They'll shake you down if you let them.'"
                ]
                print(random.choice(nova_badge_quips))
            else:  # Local Deputy
                nova_deputy_quips = [
                    "[NOVA] 'Local deputy. Probably bored and looking for excitement.'",
                    "[NOVA] 'Small-time law enforcement. This should be manageable.'",
                    "[NOVA] 'Local authorities. A few credits usually solves this problem.'"
                ]
                print(random.choice(nova_deputy_quips))
            wait_for_enter()
        
        print("They're closing in fast...")
        wait_for_enter()
        
        print("\nWhat do you do?")
        print("1. Run for it")
        print("2. Stop and comply")
        
        while True:
            print("\n> ", end="")
            choice = input().strip()
            if choice == "1":  # Run
                return self._handle_run(enemy_type)
            elif choice == "2":  # Stop
                return self._handle_stop(enemy_type)
            else:
                print("Invalid choice. Please enter 1 or 2")
    
    def _select_enemy_by_heat(self, primary_level):
        """Select an enemy based on heat level with weighted probabilities"""
        # Define the weighted distributions for each heat level
        # Format: [(enemy_type_function, weight, description), ...]
        
        # Level 1 distribution - almost always LOCAL_DEPUTY
        level_1_distribution = [
            (LOCAL_DEPUTY, 90, "It's a local deputy's patrol skiff."),
            (SECTOR_BADGE, 10, "A sector badge vessel appears, looking for easy credits."),
        ]
        
        # Level 2 distribution - primarily SECTOR_BADGE with some LOCAL_DEPUTY
        level_2_distribution = [
            (LOCAL_DEPUTY, 20, "It's a bored local deputy."),
            (SECTOR_BADGE, 70, "A sector badge cruiser cuts you off, its extortion crew ready to board."),
            (FEDERATION_RANGER, 10, "A Federation Ranger patrol appears from out of the fog."),
        ]
        
        # Level 3 distribution - primarily FEDERATION_RANGER
        level_3_distribution = [
            (SECTOR_BADGE, 20, "A sector badge vessel with veteran markings moves to intercept."),
            (FEDERATION_RANGER, 70, "A Federation Ranger vessel calls you closer."),
            (GALACTIC_ENFORCER, 10, "A sleek Galactic Enforcement vessel appears from stealth mode."),
        ]
        
        # Level 4 distribution - primarily GALACTIC_ENFORCER
        level_4_distribution = [
            (FEDERATION_RANGER, 25, "A heavily-armed Federation Ranger patrol locks weapons on your ship."),
            (GALACTIC_ENFORCER, 65, "A sleek Galactic Enforcement strike team vessel appears from stealth mode."),
            (lambda: BountyHunter.get_random_hunter(), 10, "A specialized bounty hunter ship appears, targeting you specifically."),
        ]
        
        # Level 5 distribution - high chance of BOUNTY_HUNTER
        level_5_distribution = [
            (FEDERATION_RANGER, 5, "A Federation Ranger patrol stumbles upon your location."),
            (GALACTIC_ENFORCER, 35, "An elite Galactic Enforcement team locks onto your signature."),
            (lambda: BountyHunter.get_random_hunter(), 60, "A notorious bounty hunter's ship emerges from hyperspace right beside you."),
        ]
        
        # Select the appropriate distribution based on primary_level
        distributions = [
            None,  # No level 0
            level_1_distribution,
            level_2_distribution,
            level_3_distribution,
            level_4_distribution,
            level_5_distribution,
        ]
        
        # Get the distribution for the given level
        distribution = distributions[primary_level]
        
        # Extract enemy types and their weights
        enemy_types, weights, descriptions = zip(*distribution)
        
        # Select enemy type based on weights
        index = DiceRoller.weighted_choice(weights)
        enemy_type = enemy_types[index]
        patrol_desc = descriptions[index]
        
        return enemy_type, patrol_desc
    
    def _handle_run(self, enemy_type):
        """Handle attempt to run from authorities"""
        print("\nYou gun the engines, trying to shake the patrol!")
        wait_for_enter()
        
        # They shoot at you - damage based on enemy type
        enemy = enemy_type()
        
        # Dramatic combat descriptions
        if random.random() < 0.35:
            combat_descriptions = [
                "Energy bolts streak past your viewport!",
                "Your ship shudders under weapons fire!",
                "Warning alarms blare as they open fire!",
                "Laser bursts light up the space around you!",
                "The hull groans under the impact of their shots!"
            ]
            print(random.choice(combat_descriptions))
            wait_for_enter()
        
        # More powerful enemies do more damage when you run
        if any(hunter_name in enemy.name for hunter_name in ["Agent Andrews", "Killer Klakring", "T-Mont the Tyrant", "Garth Vader", "D-Mac the Destroyer"]):
            # Bounty hunters do serious damage when you run
            base_damage = 30
            damage_variance = DiceRoller.d20()
        elif "Galactic Enforcer" in enemy.name:
            base_damage = 25
            damage_variance = DiceRoller.d12() if hasattr(DiceRoller, 'd12') else DiceRoller.d6() + DiceRoller.d6()
        elif "Federation Ranger" in enemy.name:
            base_damage = 20
            damage_variance = DiceRoller.d10() if hasattr(DiceRoller, 'd10') else DiceRoller.d6() + (DiceRoller.d6() // 2)
        elif "Sector Badge" in enemy.name:
            base_damage = 15
            damage_variance = DiceRoller.d8() if hasattr(DiceRoller, 'd8') else DiceRoller.d6()
        else:  # Local Deputy
            base_damage = 10
            damage_variance = DiceRoller.d6()
            
        damage = base_damage + damage_variance
        self.game.player.hp -= damage
        print(f"\nThey open fire! You take {damage} damage!")
        
        # NOVA damage commentary
        if random.random() < 0.3:
            if damage > 25:
                print("[NOVA] 'That hurt! Hull integrity is compromised!'")
            elif damage > 15:
                print("[NOVA] 'We're taking heavy fire! This was a bad idea!'")
            else:
                print("[NOVA] 'Minor damage. Could be worse.'")
        wait_for_enter()
        
        # Check if player is dead
        if self.game.player.hp <= 0:
            print("Systems failing... emergency ejection activated...")
            if random.random() < 0.5:
                print("[NOVA] 'Well, this is embarrassing. See you in the next life.'")
            wait_for_enter()
            #print("\nGAME OVER")
            self.game.game_over = True
            return "game_over"
        
        # Chance to escape based on ship speed and inversely on enemy strength
        is_bounty_hunter = any(hunter_name in enemy.name for hunter_name in ["Agent Andrews", "Killer Klakring", "T-Mont the Tyrant", "Garth Vader", "D-Mac the Destroyer"])
        
        if is_bounty_hunter:
            enemy_factor = 0.4  # Very hard to escape
        elif "Galactic Enforcer" in enemy.name:
            enemy_factor = 0.35
        elif "Federation Ranger" in enemy.name:
            enemy_factor = 0.3
        elif "Sector Badge" in enemy.name:
            enemy_factor = 0.2
        else:  # Local Deputy
            enemy_factor = 0.1  # Easy to escape
            
        # Significantly increase impact of ship speed on escape chance
        speed_bonus = (self.game.ship.speed - 1) * 0.10  # Each speed level adds 15% escape chance
        escape_chance = max(0.1, 0.3 + speed_bonus - enemy_factor)
        
        # Display escape chance information to player
        #print(f"\nYour ship's speed rating: {self.game.ship.speed}")
        #escape_percent = int(escape_chance * 100)
        #print(f"Estimated escape chance: {escape_percent}%")
        
        if DiceRoller.chance(escape_chance):
            print("\nYou manage to lose them in an asteroid field!")
            if random.random() < 0.4:
                escape_descriptions = [
                    "Your ship weaves between floating debris, sensors confused.",
                    "The asteroid field's mineral composition scrambles their tracking.",
                    "You cut engines and drift silently among the rocks.",
                    "A lucky jump through a debris field shakes your pursuers."
                ]
                print(random.choice(escape_descriptions))
                wait_for_enter()
            if random.random() < 0.3:
                nova_escape_quips = [
                    "[NOVA] 'Not bad. I didn't think we'd make it out of that one.'",
                    "[NOVA] 'Running from the law. Again. I should update my resume.'",
                    "[NOVA] 'Lucky asteroid field. I'm marking this location for future reference.'",
                    "[NOVA] 'Well, that was terrifying. Let's not do it again.'",
                    "[NOVA] 'Impressive flying. I take back half the things I said about your piloting.'"
                ]
                print(random.choice(nova_escape_quips))
                wait_for_enter()
            self.game.player.heat += 10  # Heat goes up for running
            wait_for_enter()
            return None
        else:
            print("\nThey catch up to you...")
            if random.random() < 0.3:
                capture_descriptions = [
                    "Their ship's tractor beam locks onto your hull.",
                    "Superior engines bring them alongside your ship.",
                    "A boarding tube extends from their vessel.",
                    "Magnetic grapples secure your ship to theirs."
                ]
                print(random.choice(capture_descriptions))
            wait_for_enter()
            return self._handle_stop(enemy_type)
    
    def _handle_stop(self, enemy_type):
        """Handle stopping for authorities"""
        enemy = enemy_type()
        
        print(f"\nYou power down your engines as the {enemy.name} approaches...")
        
        # Atmospheric descriptions of the stop
        if random.random() < 0.35:
            stop_descriptions = [
                "Your ship drifts to a halt, engine signatures fading to idle.",
                "Compliance protocols activate as you surrender control.",
                "The patrol vessel moves in with practiced precision.",
                "Scanning beams sweep across your hull methodically.",
                "Communication arrays synchronize for official contact."
            ]
            print(random.choice(stop_descriptions))
        wait_for_enter()
        
        # Authority dialogue based on enemy type
        if random.random() < 0.4:
            is_bounty_hunter = any(hunter_name in enemy.name for hunter_name in ["Agent Andrews", "Killer Klakring", "T-Mont the Tyrant", "Garth Vader", "D-Mac the Destroyer"])
            if is_bounty_hunter:
                authority_dialogue = [
                    f"'{enemy.name}' opens a comm channel: \"End of the line. You're worth more alive, but dead works too.\"",
                    f"'{enemy.name}' transmits: \"I've been tracking you for days. Time to collect.\"",
                    f"'{enemy.name}' says coldly: \"The bounty didn't specify what condition you had to be in.\""
                ]
            elif "Galactic Enforcer" in enemy.name:
                authority_dialogue = [
                    "\"This is Galactic Enforcement. Prepare for immediate inspection.\"",
                    "\"By Federation authority, you will submit to search and seizure.\"",
                    "\"Galactic Enforcement priority intercept. Compliance is mandatory.\""
                ]
            elif "Federation Ranger" in enemy.name:
                authority_dialogue = [
                    "\"Federation Ranger patrol. You are subject to lawful inspection.\"",
                    "\"This is Ranger Command. We're conducting routine enforcement operations.\"",
                    "\"Federal jurisdiction applies. Prepare for boarding and inspection.\""
                ]
            elif "Sector Badge" in enemy.name:
                authority_dialogue = [
                    "\"Sector enforcement here. Time for a little... tax collection.\"",
                    "\"This sector requires additional fees. Let's discuss your options.\"",
                    "\"Sector badge inspection. Hope you've been paying your 'insurance.'\""
                ]
            else:  # Local Deputy
                authority_dialogue = [
                    "\"Local deputy here. Just a routine check, nothing fancy.\"",
                    "\"This is deputy patrol. Standard inspection protocols apply.\"",
                    "\"Local enforcement. Let's keep this simple and everybody goes home happy.\""
                ]
            print(random.choice(authority_dialogue))
            wait_for_enter()
        
        # Try to bribe first - all types are bribable but with different conditions
        is_bribable = True
        
        # Galactic Enforcers are harder to bribe but still possible
        if "Galactic Enforcer" in enemy.name:
            print("\nThe Galactic Enforcers are here on official business. Only an enormous bribe might work.")
            wait_for_enter()
        # For bounty hunters, mention the bounty directly
        elif any(hunter_name in enemy.name for hunter_name in ["Agent Andrews", "Killer Klakring", "T-Mont the Tyrant", "Garth Vader", "D-Mac the Destroyer"]):
            print("\nThe bounty hunter eyes you coldly. \"I could take the bounty... or something better.\"")
            if random.random() < 0.3:
                print("[NOVA] 'Bounty hunters are mercenaries. Everything has a price.'")
            wait_for_enter()
            
        if is_bribable and self._attempt_bribe(enemy):
            return None
            
        # If bribe fails or player can't afford it, they search the ship
        return self._handle_search(enemy)
    
    def _attempt_bribe(self, enemy):
        """Try to bribe the authorities"""
        # Bribe amount scales with heat and enemy type
        base_bribe = 100
        
        # Different enemies have different bribe preferences
        is_bounty_hunter = any(hunter_name in enemy.name for hunter_name in ["Agent Andrews", "Killer Klakring", "T-Mont the Tyrant", "Garth Vader", "D-Mac the Destroyer"])
        
        if is_bounty_hunter:
            # Bounty hunters require massive bribes based on heat
            bribe_multiplier = 1000
            base_bribe = 10000
            base_bribe_chance = 0.6  # Motivated by money
        elif "Galactic Enforcer" in enemy.name:
            bribe_multiplier = 20
            base_bribe = 5000
            base_bribe_chance = 0.3  # Elite forces, very difficult to bribe
        elif "Federation Ranger" in enemy.name:
            bribe_multiplier = 15
            base_bribe = 1000
            base_bribe_chance = 0.5  # More legitimate, harder to bribe
        elif "Sector Badge" in enemy.name:
            bribe_multiplier = 10
            base_bribe = 500
            base_bribe_chance = 0.7  # They're corrupt, but greedy
        else:  # Local Deputy
            bribe_multiplier = 5
            base_bribe = 100
            base_bribe_chance = 0.8  # Very easy to bribe
        
        bribe_amount = base_bribe + (self.game.player.heat * bribe_multiplier)
        
        if is_bounty_hunter:
            print(f"\n{enemy.name} glances around furtively...")
        else:
            print(f"\nThe {enemy.name} glances around furtively...")
        
        # Bribe setup dialogue
        if random.random() < 0.35:
            if is_bounty_hunter:
                bribe_setup = [
                    "\"The bounty's worth a lot... but I'm always open to negotiation.\"",
                    "\"Credits talk louder than justice sometimes.\"",
                    "\"I could forget I saw you... for the right price.\""
                ]
            elif "Galactic Enforcer" in enemy.name:
                bribe_setup = [
                    "\"This never happened. Understood?\"",
                    "\"I have expenses that Federation pay doesn't cover.\"",
                    "\"Sometimes regulations... need interpretation.\""
                ]
            elif "Sector Badge" in enemy.name:
                bribe_setup = [
                    "\"Sector fees are always negotiable.\"",
                    "\"I'm sure we can work out a mutually beneficial arrangement.\"",
                    "\"The official rate is high, but there's always a discount available.\""
                ]
            else:
                bribe_setup = [
                    "\"Maybe we can handle this quietly.\"",
                    "\"Paperwork is such a hassle, don't you think?\"",
                    "\"Sometimes a small administrative fee makes problems disappear.\""
                ]
            print(random.choice(bribe_setup))
            wait_for_enter()
        
        print(f"You could try to bribe them...")
        wait_for_enter()
        if bribe_amount > self.game.player.credits:
            if is_bounty_hunter:
                print(f"\nYou don't have enough to match the bounty ({bribe_amount} credits).")
                wait_for_enter()
            else:
                print(f"\nYou don't have enough to bribe them ({bribe_amount} credits).")
            if random.random() < 0.3:
                print("[NOVA] 'Being broke has its disadvantages. Who knew?'")
            wait_for_enter()
            return False
    
        print(f"1. Offer {bribe_amount:,} credits bribe")
        print("2. Let them search")
        
        while True:
            print("\n> ", end="")
            choice = input().strip()
            if choice == "1":
                # Chance of accepting bribe decreases with heat
                bribe_chance = base_bribe_chance - (self.game.player.heat / 200)
                
                if is_bounty_hunter:
                    # Bounty hunters are more likely to accept big bribes
                    bribe_chance = min(0.95, bribe_chance + 0.2)
                    
                if DiceRoller.chance(bribe_chance):
                    if is_bounty_hunter:
                        success_dialogue = [
                            f"{enemy.name} counts your credits with a grin. \"Pleasure doing business.\"",
                            f"{enemy.name} pockets the credits. \"I never saw you. We understand each other?\"",
                            f"{enemy.name} smiles coldly. \"The bounty can wait. This is better.\""
                        ]
                        print(f"\n{random.choice(success_dialogue)}")
                    else:
                        success_dialogue = [
                            "They accept your credits with a knowing smile...",
                            "\"Administrative fee processed. Have a safe flight.\"",
                            "The credits disappear quickly. \"What inspection? I don't see any problems here.\""
                        ]
                        print(random.choice(success_dialogue))
                    if random.random() < 0.3:
                        print("[NOVA] 'Money talks. And apparently, it speaks their language fluently.'")
                    wait_for_enter()
                    self.game.player.credits -= bribe_amount
                    
                    # Heat reduction based on enemy type
                    if is_bounty_hunter:
                        heat_reduction = 3  # Bounty hunters can reduce heat more
                    else:
                        heat_reduction = 1  # Normal heat reduction
                        
                    self.game.player.heat -= heat_reduction
                    return True
                else:
                    if is_bounty_hunter:
                        failure_dialogue = [
                            f"{enemy.name} pockets your credits and draws a weapon anyway!",
                            # INSERT_YOUR_CODE
                            f"{enemy.name} takes your credits, then levels their weapon at you. \"Nothing personal, {self.game.player.name}. Business is business.\"",
                            f"{enemy.name} grins, pocketing your bribe. \"Business is business, {self.game.player.name}. Now I'll get paid twice.\"",
                            f"{enemy.name} takes your money, then immediately goes for their blaster. \"You didn't really think that would work, did you?\"",
                        ]
                        print(f"\n{random.choice(failure_dialogue)}")
                    else:
                        failure_dialogue = [
                            "They pocket your credits... and search anyway!",
                            "\"Thanks for the donation. Now prepare to be searched.\"",
                            "\"Credits accepted. But I still have quotas to meet.\""
                        ]
                        print(random.choice(failure_dialogue))
                    if random.random() < 0.3:
                        print("[NOVA] 'Well, that backfired spectacularly.'")
                    wait_for_enter()
                    self.game.player.credits -= bribe_amount
                    self.game.player.heat += 5  # Failed bribe increases heat
                    return False
            elif choice == "2":
                return False
            else:
                print("Invalid choice. Please enter 1 or 2")
        

    def _handle_search(self, enemy):
        """Handle ship search and potential combat"""
        # INSERT_YOUR_CODE
        is_bounty_hunter = any(hunter_name in enemy.name for hunter_name in ["Agent Andrews", "Killer Klakring", "T-Mont the Tyrant", "Garth Vader", "D-Mac the Destroyer"])

        if is_bounty_hunter:
            print(f"\n{enemy.name} sneers: \"I'm not here for your cargo. I'm here for you. Dead or alive.\"")
            wait_for_enter()
            combat = Combat(self.game, enemy)
            result = combat.run()
            if result == "defeat":
                return "game_over"
            elif result == "escaped":
                self.game.player.heat += 10  # Big heat increase for fighting and running
            else:  # victory
                if is_bounty_hunter:
                    print(f"\nYou've eliminated {enemy.name}. One less hunter on your trail.")
                    BountyHunter.mark_eliminated(enemy.name)
                    heat_increase = 30
                    if random.random() < 0.3:
                        print("[NOVA] 'One bounty hunter down. Unfortunately, there are always more where they came from.'")
                elif "Local Deputy" in enemy.name:
                    heat_increase = 12
                    print("\nKilling a local deputy will be noticed in this system...")
                    if random.random() < 0.3:
                        print("[NOVA] 'Local law enforcement won't forget this. We should probably avoid this system for a while.'")
                elif "Sector Badge" in enemy.name:
                    heat_increase = 18
                    print("\nThe sector badges will be looking for revenge...")
                    if random.random() < 0.3:
                        print("[NOVA] 'Sector badges hold grudges. Expect company next time we're in their territory.'")
                elif "Federation Ranger" in enemy.name:
                    heat_increase = 20
                    print("\nThe Federation will not take kindly to losing a Ranger...")
                    if random.random() < 0.3:
                        print("[NOVA] 'Rangers are elite forces. The Federation will escalate their response after this.'")
                else:
                    heat_increase = 25
                    print("\nEliminating a Galactic Enforcer... The Federation will hunt you to the ends of space!")
                    if random.random() < 0.3:
                        print("[NOVA] 'Galactic Enforcers don't just disappear. We're going to have the entire Federation after us now.'")
                self.game.player.heat += heat_increase
                wait_for_enter()
            return None
        
        print(f"\nThe {enemy.name} begins searching your ship...")
        
        # Search atmosphere
        if random.random() < 0.35:
            search_descriptions = [
                "Heavy boots clank through your ship's corridors.",
                "Scanners beep methodically as they probe every compartment.",
                "Gloved hands rifle through your belongings.",
                "Detection equipment sweeps the cargo bay systematically.",
                "They work with professional efficiency, missing nothing."
            ]
            print(random.choice(search_descriptions))
        
        if random.random() < 0.3:
            nova_search_quips = [
                "[NOVA] 'They're being very thorough. I hope you hid everything properly.'",
                "[NOVA] 'Professional search pattern. These guys know what they're doing.'",
                "[NOVA] 'If they find something, just remember this was your idea.'",
                "[NOVA] 'Scanning... scanning... this is making me nervous.'"
            ]
            print(random.choice(nova_search_quips))
        wait_for_enter()

        def is_illegal_item(item):
            return (
                getattr(item, 'is_contraband', False) or
                getattr(item, 'is_illegal', False) or
                getattr(item, 'is_stolen', False) or
                (isinstance(item, dict) and (
                    item.get('is_contraband') or item.get('is_illegal') or item.get('is_stolen')
                ))
            )

        manifest = []  # List of (source, item) tuples
        found_crate = False

        # 1. Search contract crates
        if self.game.player.current_contract:
            for i, crate in enumerate(self.game.player.current_contract.crates):
                base_search_chance = 0.3
                if "Local Deputy" in enemy.name:
                    search_mod = 0
                elif "Sector Badge" in enemy.name:
                    search_mod = 0.05
                elif "Federation Ranger" in enemy.name:
                    search_mod = 0.1
                elif "Galactic Enforcer" in enemy.name:
                    search_mod = 0.15
                else:
                    search_mod = 0.2
                search_chance = base_search_chance + (self.game.player.heat / 100) + search_mod
                if DiceRoller.chance(search_chance):
                    print(f"\nThey find a {crate.tier} crate...")
                    wait_for_enter()
                    if crate.tier == "legit":
                        print("They mark it as cleared.")
                        wait_for_enter()
                    elif crate.tier == "illicit":
                        print("Contraband detected!")
                        if random.random() < 0.4:
                            contraband_reactions = [
                                "\"Well, well, what do we have here?\"",
                                "\"This is definitely not legal in Federation space.\"",
                                "\"Illegal goods. You're in serious trouble.\"",
                                "\"Contraband smuggling. That's a felony.\""
                            ]
                            print(random.choice(contraband_reactions))
                        wait_for_enter()
                        manifest.append(('crate', crate))
                        found_crate = True
                    else:  # sealed
                        if DiceRoller.chance(0.5):
                            print("They crack it open... Contraband!")
                            if random.random() < 0.3:
                                print("\"Sealed cargo always makes me suspicious. Let's see... yep, highly illegal It's over, buddy.\"")
                            wait_for_enter()
                            manifest.append(('crate', crate))
                            found_crate = True
                        else:
                            print("They crack it open... It's legal cargo.")
                            if random.random() < 0.25:
                                print("\"Hmm. Sealed, but legitimate. I guess you got lucky.\"")
                            wait_for_enter()
                else:
                    print(f"They didn't find crate #{i + 1}...")
                    if random.random() < 0.2:
                        print("[NOVA] 'Lucky. That one would have been problematic.'")
                    wait_for_enter()

        # 2. Search player inventory
        for idx, item in enumerate(getattr(self.game.player, 'inventory', [])):
            if is_illegal_item(item):
                manifest.append(('inventory', item))

        # 3. Search equipped weapon
        weapon = getattr(self.game.player, 'weapon', None)
        if weapon and is_illegal_item(weapon):
            manifest.append(('weapon', weapon))

        # 4. Search equipped armor
        armor = getattr(self.game.player, 'armor_item', None)
        if armor and is_illegal_item(armor):
            manifest.append(('armor', armor))

        # 5. Search combat items (if any)
        for idx, item in enumerate(getattr(self.game.player, 'items', [])):
            if is_illegal_item(item):
                manifest.append(('combat_item', item))

        if manifest:
            # Present manifest and single choice
            print(f"\nThe {enemy.name} confronts you with a manifest of illegal items they intend to confiscate:")
            
            # Confrontation dialogue
            if random.random() < 0.4:
                confrontation_lines = [
                    "\"Well, this is interesting. Care to explain?\"",
                    "\"Looks like we've got ourselves a smuggler.\"",
                    "\"These items are all highly illegal. You're under arrest.\"",
                    "\"Contraband smuggling is a serious federal offense.\""
                ]
                print(random.choice(confrontation_lines))
                wait_for_enter()
            
            for source, item in manifest:
                if source == 'crate':
                    print(f"- Contract Crate: {getattr(item, 'tier', str(item))}")
                elif source == 'inventory':
                    print(f"- Inventory: {item['name'] if isinstance(item, dict) else getattr(item, 'name', str(item))}")
                elif source == 'weapon':
                    print(f"- Weapon: {item.name}")
                elif source == 'armor':
                    print(f"- Armor: {item.name}")
                elif source == 'combat_item':
                    print(f"- Combat Item: {item.name}")
            wait_for_enter()
            print("\nWhat do you do?")
            print("1. Comply and hand over all items")
            print("2. Refuse")
            while True:
                print("\n> ", end="")
                choice = input().strip()
                if choice == "1":
                    # Compliance dialogue
                    if random.random() < 0.3:
                        compliance_reactions = [
                            "\"Smart choice. Cooperation is always appreciated.\"",
                            "\"Thank you for your compliance. This will be noted.\"",
                            "\"Wise decision. Violence never solves anything.\""
                        ]
                        print(random.choice(compliance_reactions))
                        wait_for_enter()
                    
                    # Confiscate all items
                    # INSERT_YOUR_CODE
                    for source, item in manifest:
                        if source == 'inventory':
                            try:
                                self.game.player.inventory.remove(item)
                            except Exception:
                                pass
                        elif source == 'weapon':
                            self.game.player.weapon = None
                        elif source == 'armor':
                            self.game.player.armor_item = None
                        elif source == 'combat_item':
                            try:
                                self.game.player.items.remove(item)
                            except Exception:
                                pass
                    # If any crate is found, fail the contract and remove all crates
                    if found_crate and self.game.player.current_contract:
                        self.game.player.current_contract.crates.clear()
                        self.game.player.current_contract = None
                        print("\nAll your contract cargo is confiscated. Your contract has failed!")
                        if random.random() < 0.3:
                            print("[NOVA] 'Well, there goes our paycheck. Hope it was worth it, because the cartel's going to be pissed.'")
                        wait_for_enter()
                        print("\nYou hand over the item(s) and the authorities let you go, but the cartel will not be pleased...")
                        wait_for_enter()
                        self.game.player.cartel_threat_level += 1
                        if random.random() < 0.25:
                            print("[NOVA] 'Could have been worse. At least we're still breathing.'")
                            wait_for_enter()

                        for source, item in manifest:
                            if source == 'inventory':
                                try:
                                    self.game.player.inventory.remove(item)
                                except Exception:
                                    pass
                            elif source == 'weapon':
                                self.game.player.weapon = None
                            elif source == 'armor':
                                self.game.player.armor_item = None
                            elif source == 'combat_item':
                                try:
                                    self.game.player.items.remove(item)
                                except Exception:
                                    pass
                        

                        # Chance of immediate cartel retaliation
                        if DiceRoller.chance(0.5):  # 50% chance of cartel encounter
                            print("\nAs you leave the checkpoint, a ship with Syndicate markings appears on your radar...")
                            if random.random() < 0.3:
                                print("[NOVA] 'Oh great. From bad to worse. Get ready!'")
                            wait_for_enter()
                            cartel = CartelEncounter(self.game)
                            result = cartel.run()
                            if result == "game_over":
                                return "game_over"
                    
                    return None
                elif choice == "2":
                    print(f"\nYou refuse to comply!")
                    if random.random() < 0.4:
                        refusal_reactions = [
                            "\"So you want to do this the hard way? Fine by me.\"",
                            "\"Resisting arrest? Bad choice, friend.\"",
                            "\"I was hoping you'd say that. I need the target practice.\"",
                            "\"Alright, if that's how you want it!\""
                        ]
                        print(random.choice(refusal_reactions))
                    if random.random() < 0.3:
                        print("[NOVA] 'Here we go again. Try not to get us killed this time.'")
                    wait_for_enter()
                    # Start combat
                    combat = Combat(self.game, enemy)
                    result = combat.run()
                    if result == "defeat":
                        return "game_over"
                    elif result == "escaped":
                        self.game.player.heat += 10  # Big heat increase for fighting and running
                    else:  # victory
                        is_bounty_hunter = any(hunter_name in enemy.name for hunter_name in ["Agent Andrews", "Killer Klakring", "T-Mont the Tyrant", "Garth Vader", "D-Mac the Destroyer"])
                        if is_bounty_hunter:
                            print(f"\nYou've eliminated {enemy.name}. One less hunter on your trail.")
                            BountyHunter.mark_eliminated(enemy.name)
                            heat_increase = 30
                            if random.random() < 0.3:
                                print("[NOVA] 'One bounty hunter down. Unfortunately, there are always more where they came from.'")
                        elif "Local Deputy" in enemy.name:
                            heat_increase = 12
                            print("\nKilling a local deputy will be noticed in this system...")
                            if random.random() < 0.3:
                                print("[NOVA] 'Local law enforcement won't forget this. We should probably avoid this system for a while.'")
                        elif "Sector Badge" in enemy.name:
                            heat_increase = 18
                            print("\nThe sector badges will be looking for revenge...")
                            if random.random() < 0.3:
                                print("[NOVA] 'Sector badges hold grudges. Expect company next time we're in their territory.'")
                        elif "Federation Ranger" in enemy.name:
                            heat_increase = 20
                            print("\nThe Federation will not take kindly to losing a Ranger...")
                            if random.random() < 0.3:
                                print("[NOVA] 'Rangers are elite forces. The Federation will escalate their response after this.'")
                        else:
                            heat_increase = 25
                            print("\nEliminating a Galactic Enforcer... The Federation will hunt you to the ends of space!")
                            if random.random() < 0.3:
                                print("[NOVA] 'Galactic Enforcers don't just disappear. We're going to have the entire Federation after us now.'")
                        self.game.player.heat += heat_increase
                        wait_for_enter()
                    return None
                else:
                    print("Invalid choice. Please enter 1 or 2")
        else:
            print(f"\nThe {enemy.name} finds nothing suspicious.")
            if random.random() < 0.35:
                clean_search_reactions = [
                    "\"Everything checks out. You're free to go.\"",
                    "\"Clean ship. Safe travels, citizen.\"",
                    "\"No violations found. Carry on.\"",
                    "\"Ship passes inspection. Have a good flight.\""
                ]
                print(random.choice(clean_search_reactions))
            if random.random() < 0.25:
                player = getattr(self, "game", None)
                if player:
                    player = getattr(self.game, "player", None)
                if player:
                    # Check for illegal contract cargo
                    has_illegal_contract_cargo = False
                    contract = getattr(player, "current_contract", None)
                    if contract and getattr(contract, "crates", []):
                        for crate in contract.crates:
                            if getattr(crate, "is_contraband", False) or getattr(crate, "is_illegal", False) or getattr(crate, "is_stolen", False):
                                has_illegal_contract_cargo = True
                                break
                    # Check for illegal items in inventory
                    has_illegal_inventory = False
                    for item in getattr(player, "inventory", []):
                        if getattr(item, "is_contraband", False) or getattr(item, "is_illegal", False) or getattr(item, "is_stolen", False):
                            has_illegal_inventory = True
                            break
                    if has_illegal_contract_cargo or has_illegal_inventory:
                        nova_lucky_lines = [
                            "[NOVA] 'I can't believe they missed the contraband. That was way too close.'",
                            "[NOVA] 'We got lucky. If they'd looked a little harder, we'd be in a cell right now.'",
                            "[NOVA] 'That was a miracle. Next time we might not be so lucky.'"
                        ]
                        print(random.choice(nova_lucky_lines))
            wait_for_enter()
            self.game.player.heat = max(0, self.game.player.heat - 1)  # Small heat reduction for clean search
            return None

class CartelEncounter():
    """Cartel encounter - triggered when you steal cargo or fail a contract.
    Difficulty scales with cartel_threat_level."""
    
    # Cartel dialogue options for variety
    INTRO_DIALOGUES = [
        "\"You thought you could cross the Syndicate? Prepare to face the consequences.\"",
        "\"We've been tracking you for some time. Time to collect what's ours.\"",
        "\"No one steals from the cartel and lives. This ends now.\"",
        "\"The boss sends his regards... and a death warrant.\"",
        "\"You've got something that belongs to us. Hand it over, or we take it from your corpse.\""
    ]
    
    # Bluff dialogue options
    BLUFF_OPTIONS = [
        "\"Wait! I can explain! There was a navigation error...\"",
        "\"I was actually trying to protect your cargo from Federation agents!\"",
        "\"I can pay you double what it's worth!\"",
        "\"I have information about a Federation sting operation you'll want to hear...\"",
        "\"The cargo was contaminated - I was doing you a favor!\""
    ]
    
    def __init__(self, game):
        self.game = game
        self.player = game.player
        self.threat_level = self.player.cartel_threat_level
    
    def run(self):
        print("\nA ship with Syndicate markings intercepts you...")
        wait_for_enter()
        
        # Pick a random intro dialogue
        dialogue_index = min(self.threat_level, len(self.INTRO_DIALOGUES)-1)
        print(f"\nCartel Enforcer: {self.INTRO_DIALOGUES[dialogue_index]}")
        wait_for_enter()
        
        # Present options
        print("\nWhat do you do?")
        print("1. Fight your way out")
        print("2. Try to run for it")
        print("3. Attempt to bluff your way out")
        print("4. Surrender and beg for mercy")
        
        while True:
            print("\n> ", end="")
            choice = input().strip()
            if choice == "1":  # Fight
                return self._handle_fight()
            elif choice == "2":  # Run
                return self._handle_run()
            elif choice == "3":  # Bluff
                return self._handle_bluff()
            elif choice == "4":  # Surrender
                return self._handle_surrender()
            else:
                print("Invalid choice. Please enter 1-4")
    
    def _handle_fight(self):
        """Handle direct combat with the cartel"""
        print("\nYou draw your weapon...")
        wait_for_enter()
        
        # Create cartel enemies based on threat level
        enemies = self._generate_cartel_enemies()
        
        for enemy in enemies:
            print(f"A {enemy.name} steps forward...")
            wait_for_enter()
            
            # Start combat
            combat = Combat(self.game, enemy)
            result = combat.run()
            
            if result == "defeat":
                print("\nThe cartel has eliminated you...")
                wait_for_enter()
                return "game_over"
            elif result == "escaped":
                self.player.heat += 15
                self.player.cartel_threat_level += 1
                print("\nYou've escaped the cartel... for now. But they won't forget this.")
                wait_for_enter()
                return None
            
            # If we're here, the player defeated this enemy, continue to the next one
        
        # If player defeats all enemies
        print("\nYou've eliminated the cartel enforcers, but word of this will spread quickly.")
        wait_for_enter()
        
        # Major heat and threat level increase for defeating cartel
        self.player.heat += 20
        self.player.cartel_threat_level += 1
        
        return None
    
    def _handle_run(self):
        """Handle escape attempt"""
        print("\nYou gun the engines, trying to outrun the cartel ship!")
        wait_for_enter()
        
        # Increasing difficulty with threat level
        escape_penalty = min(0.35, 0.05 * self.threat_level)
        
        # Speed bonus from ship, but with diminishing returns at higher threat levels
        base_escape_chance = 0.3
        speed_bonus = (self.game.ship.speed - 1) * 0.10  # Slightly lower than normal
        escape_chance = max(0.1, base_escape_chance + speed_bonus - escape_penalty)  # Minimum 5% chance
        
        # Convert to percentage for display
        #escape_percent = int(escape_chance * 100)
        #print(f"Your ship's speed rating: {self.game.ship.speed}")
        #print(f"Estimated escape chance: {escape_percent}%")
        #wait_for_enter()
        
        if DiceRoller.chance(escape_chance):
            print("\nYou manage to slip away into an asteroid field!")
            wait_for_enter()
            
            # Running increases heat and threat level
            self.player.heat += 15
            self.player.cartel_threat_level += 1
            
            return None
        else:
            print("\nTheir ship is faster - they cut you off!")
            wait_for_enter()
            
            # Failed escape leads to combat
            return self._handle_fight()
    
    def _handle_bluff(self):
        """Handle bluff attempt"""
        # Random bluff dialogue
        bluff_index = random.randint(0, len(self.BLUFF_OPTIONS)-1)
        print(f"\nYou try to talk your way out: {self.BLUFF_OPTIONS[bluff_index]}")
        wait_for_enter()
        
        # Bluff becomes much harder with higher threat level
        base_bluff_chance = 0.5  # 50% base chance
        threat_penalty = min(0.45, 0.08 * self.threat_level)  # 8% penalty per level, max 45%
        final_chance = max(0.05, base_bluff_chance - threat_penalty)  # Minimum 5% chance
        
        # Roll for success
        if DiceRoller.chance(final_chance):
            print("\nThe cartel enforcer narrows their eyes...")
            wait_for_enter()
            print("\"Fine. But the boss will hear about this. Don't cross us again.\"")
            wait_for_enter()
            
            # Successful bluff still increases heat a bit
            self.player.heat += 5
            return None
        else:
            print("\nThe cartel enforcer laughs. \"Nice try. Get them!\"")
            wait_for_enter()
            
            # Failed bluff leads to combat with penalty
            self.player.cartel_threat_level += 1
            return self._handle_fight()
    
    def _handle_surrender(self):
        """Handle surrender attempt"""
        print("\nYou raise your hands. \"I surrender! Take what you want!\"")
        wait_for_enter()
        
        # Chance they accept surrender decreases with threat level
        acceptance_chance = max(0.1, 0.7 - (0.1 * self.threat_level))  # 10% decrease per level, minimum 10%
        
        if DiceRoller.chance(acceptance_chance):
            print("\nThe cartel enforcer gestures to his men to take your cargo...")
            wait_for_enter()
            
            # They take your cargo
            if self.game.player.current_contract:
                self.game.player.current_contract = None
                print("They confiscate all contract cargo and mark the contract as failed.")
            
            # Take some credits too as penalty
            penalty = min(self.player.credits, 2000 * (1 + self.threat_level))
            self.player.credits -= penalty
            print(f"They also take {penalty} credits as \"compensation\".")
            wait_for_enter()
            
            # Even surrender increases heat
            self.player.heat += 15
            print("\n\"Don't cross us again. Next time we won't be so merciful.\"")
            wait_for_enter()
            return None
        else:
            print("\nThe cartel enforcer smirks. \"Too late for that. Make an example of them.\"")
            wait_for_enter()
            
            # They attack anyway
            self.player.cartel_threat_level += 1
            return self._handle_fight()
    
    def _generate_cartel_enemies(self):
        """Generate cartel enemies based on threat level"""
        enemies = []
        
        # Base enemy stats
        base_hp = 60
        base_min_damage = 10
        base_max_damage = 20
        base_credits = 150
        
        # Threat level 0-1: Single weak enemy
        if self.threat_level <= 1:
            enemies.append(Enemy(name="Cartel Thug", 
                               hp=base_hp + (5 * self.threat_level), 
                               min_damage=base_min_damage + self.threat_level, 
                               max_damage=base_max_damage + (2 * self.threat_level),
                               credits_reward=base_credits + (50 * self.threat_level)))
        
        # Threat level 2-3: One medium enemy
        elif self.threat_level <= 3:
            enemies.append(Enemy(name="Cartel Enforcer", 
                               hp=base_hp + 15 + (5 * self.threat_level), 
                               min_damage=base_min_damage + 3 + self.threat_level, 
                               max_damage=base_max_damage + 5 + (2 * self.threat_level),
                               credits_reward=base_credits + 100 + (50 * self.threat_level)))
        
        # Threat level 4-5: Two medium enemies
        elif self.threat_level <= 5:
            for i in range(2):
                enemies.append(Enemy(name=f"Cartel Enforcer {i+1}", 
                                   hp=base_hp + 20 + (5 * self.threat_level), 
                                   min_damage=base_min_damage + 5 + self.threat_level, 
                                   max_damage=base_max_damage + 8 + (2 * self.threat_level),
                                   credits_reward=base_credits + 150 + (50 * self.threat_level)))
        
        # Threat level 6+: One strong enemy and one medium enemy
        else:
            # Strong enemy
            enemies.append(Enemy(name="Cartel Lieutenant", 
                               hp=base_hp * 2 + (8 * self.threat_level), 
                               min_damage=base_min_damage + 8 + (2 * self.threat_level), 
                               max_damage=base_max_damage + 15 + (3 * self.threat_level),
                               credits_reward=base_credits * 2 + (75 * self.threat_level)))
            
            # Medium backup
            enemies.append(Enemy(name="Cartel Enforcer", 
                               hp=base_hp + 25 + (5 * self.threat_level), 
                               min_damage=base_min_damage + 5 + self.threat_level, 
                               max_damage=base_max_damage + 10 + (2 * self.threat_level),
                               credits_reward=base_credits + 150 + (50 * self.threat_level)))
        
        return enemies
