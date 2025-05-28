from utils import DiceRoller, wait_for_enter
from trade_hub_gameplay import handle_trade_hub
from combat import Combat, LOCAL_DEPUTY, SECTOR_BADGE, FEDERATION_RANGER, GALACTIC_ENFORCER, BountyHunter, Enemy
from shop import BlackMarketShop
import random
from fights import PoliceEncounter
def wait_for_enter():
    input("\n...\n")

class Encounter:
    """Base class for all encounters"""
    def __init__(self, game):
        self.game = game
    
    def run(self):
        """Run the encounter. Must be implemented by subclasses."""
        raise NotImplementedError

class PlanetEncounter(Encounter):
    """Planet encounter - could be trade hub or black market"""
    def run(self):
        print("\nYou encounter a planet in the distance...")
        wait_for_enter()
        
        print("Would you like to land?")
        print("1. Yes")
        print("2. No")
        
        while True:
            print("\n> ", end="")
            choice = input().strip().lower()
            if choice in ['1', 'y', 'yes']:
                # Determine if it's a trade hub or black market
                if random.random() < 0.7:  # 70% chance of trade hub
                    print("\nIt appears to be a legitimate trading port...")
                    wait_for_enter()
                    handle_trade_hub(self.game)
                else:
                    print("\nSomething seems off about this place...")
                    wait_for_enter()
                    
                    print("This must be a black market outpost.")
                    wait_for_enter()
                    
                    # Create and run the black market shop
                    black_market = BlackMarketShop()
                    black_market.shop_menu(self.game)
                    
                    self.game.player.illegal_activity_today = True  # Black market is always illegal
                return "planet_landing"
            elif choice in ['2', 'n', 'no']:
                print("\nYou continue past the planet...")
                wait_for_enter()
                return None
            else:
                print("Invalid choice. Please enter 1 (yes) or 2 (no)")

class HandlePoliceEncounter(Encounter):
    """Handle police encounter"""
    def run(self):
        police_encounter = PoliceEncounter(self.game)
        return police_encounter.run()

class HazardEncounter(Encounter):
    """Space hazards like asteroids. Choice between using fuel to go around or risking damage."""
    def run(self):
        print("\nYou spot an asteroid field ahead!")
        wait_for_enter()
        print("1. Go around")
        print("2. Go through")
        
        while True:
            print("\n> ", end="")
            choice = input().strip()
            if choice == "1":
                # Calculate extra fuel and time needed
                extra_fuel = DiceRoller.d6() // 2 + 1  # 1-3 extra fuel
                extra_days = DiceRoller.d6() // 2  # 0-2 extra days
                
                if self.game.ship.fuel < extra_fuel:
                    print(f"\nYou don't have enough fuel to take the long route! (Needs {extra_fuel} fuel)")
                    wait_for_enter()
                    continue
                
                print("\nYou take the long way around...")
                wait_for_enter()
                
                self.game.ship.fuel -= extra_fuel
                self.game.day += extra_days
                
                if extra_days > 0:
                    print(f"The detour costs you {extra_fuel} fuel and {extra_days} extra days")
                else:
                    print(f"The detour costs you {extra_fuel} fuel but you make good time!")
                wait_for_enter()
                
                return "hazard_avoided"
            elif choice == "2":
                print("\nYou navigate through the field...")
                wait_for_enter()
                
                # High chance to take damage, potentially lethal
                if DiceRoller.chance(0.7):  # 70% chance to get hit
                    raw_damage = DiceRoller.d20() + DiceRoller.d20() + 10  # 12-22 damage
                    
                    # Apply armor reduction (same as combat system)
                    armor_reduction = self.game.player.armor_item.defense if self.game.player.armor_item else 0
                    final_damage = max(0, raw_damage - armor_reduction)
                    
                    if armor_reduction > 0:
                        print(f"\nYour armor absorbs {armor_reduction} damage from the asteroid impacts!")
                    
                    self.game.player.hp -= final_damage
                    print(f"\nYour ship is struck by asteroids! Takes {final_damage} damage!")
                    wait_for_enter()
                    
                    # Check if player is dead
                    if self.game.player.hp <= 0:
                        print("Systems failing... emergency ejection activated...")
                        self.game.game_over = True
                        wait_for_enter()
                        print("\nGAME OVER")
                        return "game_over"
                else:
                    print("\nYou manage to slip through unscathed!")
                    wait_for_enter()
                return None
            else:
                print("Invalid choice. Please enter 1 or 2")

class TractorBeamEncounter(Encounter):
    """Base class for tractor beam encounters - should not be used directly"""
    def __init__(self, game, encounter_type):
        super().__init__(game)
        self.encounter_type = encounter_type  # "cartel", "federation", or "stones"
    
    def run(self):
        # Build suspense with initial detection
        print("\n" * 50)
        wait_for_enter()

        print("\nSomething's wrong...")
        wait_for_enter()

        if random.random() < 0.4:
            nova_quips = [
                f"[NOVA] 'Uh... {self.game.player.name}? Something's wrong. Really wrong.'",
                "[NOVA] 'I—I can't get a lock on it! It's like the whole sensor array is screaming!'",
                "[NOVA] 'This isn't just a blip, this is BAD. We need to move, NOW!'",
                "[NOVA] 'Whatever that is, it's bending space around us! I don't like this, not one bit!'",
                "[NOVA] 'Warning lights are everywhere! I can't even tell what's failing first!'",
                "[NOVA] 'Uhh... sensors are picking up something, but I can't even describe it.'",
            ]
            print(random.choice(nova_quips))
            wait_for_enter()
        print("Your ship's proximity alarms start chirping. Something is coming for you...")
        wait_for_enter()
        
        # The reveal - based on encounter type
        if self.encounter_type == "cartel":
            print("Your comms catch a whisper before jamming: 'Target reacquired.'")
            wait_for_enter()
            print("The cartel's Executor-class dreadnought emerges from hyperspace, spanning the length of a planet.")
        elif self.encounter_type == "stones":
            print("The stones in your cargo hold begin to pulse violently, syncing with a heartbeat that's not your own.")
            wait_for_enter()
            print("Space bends open like fabric tearing and a perfect sphere emerges, its surface is polished like a mirror. Symbols scroll along the edge, none known to galactic linguistics.")
        elif self.encounter_type == "federation":
            print("The Federation Leviathan emerges from hyperspace, twenty sectors long, its twin blade-like hulls flanking a central command tower.")
            wait_for_enter()
            print("Hundreds of armed capital ships escort it, looking like ants alongside the Leviathan they flank.")
        else:
            print("Space ripples as something massive decloaks directly ahead.")
            wait_for_enter()
            print("A featureless black ship - no markings, no identification.")
        
        wait_for_enter()
        
        if random.random() < 0.5:
            if self.encounter_type == "stones":
                print("[NOVA] 'The stones are resonating with something on that ship! What's going on?'")
            elif self.encounter_type == "cartel":
                print("[NOVA] 'Would now be a good time to ask if you paid off your debts? No? Great.'")
            elif self.encounter_type == "federation":
                print("[NOVA] 'I-I've never seen anything like it! That's the kind of ship they send to end rebellions and erase planets from memory!'")
            else:
                print("[NOVA] 'I've never seen technology like this. We're being scanned!'")
            wait_for_enter()
        
        # The trap closes
        print("Invisible forces grip your ship. Your engines strain as you are caught in an irresistible tractor beam pull.")
        wait_for_enter()
        
        print("\nWhat do you do?")
        print("1. Try to escape")
        print("2. Hide in smuggling compartment")
        print("3. Let them pull you in")
        
        while True:
            print("\n> ", end="")
            choice = input().strip()
            if choice == "1":
                return self._handle_escape_attempt()
            elif choice == "2":
                print("You have ample time to hide in the smuggling compartment as you are pulled towards the ship...")
                return self._handle_hide(True)
            elif choice == "3":
                print("You let them pull you in...")
                wait_for_enter()
                # Different descriptions based on encounter type
                if self.encounter_type == "cartel":
                    print("Cartel enforcers in blood-red armor surround your ship, weapons drawn.")
                elif self.encounter_type == "federation":
                    print("Armored operatives emerge from the shadows, moving with military precision.")
                else:
                    print("Figures in unmarked armor emerge, weapons trained on your ship.")
                wait_for_enter()
                
                # After failed escape, different options based on encounter type
                if self.encounter_type == "cartel":
                    print("\nThe cartel doesn't negotiate. What do you do?")
                    print("1. Hide in smuggling compartment")
                    print("2. Come out fighting")
                    
                    while True:
                        print("\n> ", end="")
                        choice = input().strip()
                        if choice == "1":
                            return self._handle_hide()
                        elif choice == "2":
                            return self._handle_fight()
                        else:
                            print("Invalid choice. Please enter 1 or 2")
                else:
                    print("\nWhat do you do now?")
                    print("1. Hide in smuggling compartment")
                    print("2. Come out peacefully")
                    print("3. Come out fighting")
                    
                    while True:
                        print("\n> ", end="")
                        choice = input().strip()
                        if choice == "1":
                            return self._handle_hide()
                        elif choice == "2":
                            return self._handle_peaceful()
                        elif choice == "3":
                            return self._handle_fight()
                        else:
                            print("Invalid choice. Please enter 1, 2, or 3")
            else:
                print("Invalid choice. Please enter 1, 2, or 3")
    
    def _handle_escape_attempt(self):
        """Handle attempt to escape the tractor beam"""
        print("\nYou gun the engines, trying to break free!")
        wait_for_enter()
        
        # Speed significantly impacts escape chance, but varies by encounter type
        base_escape_chance = 0.2  # 20% base chance
        speed_bonus = (self.game.ship.speed - 1) * 0.05  # 15% per speed level
        
        # Cartel dreadnoughts are harder to escape from
        if self.encounter_type == "cartel":
            base_escape_chance = 0.1  # Much harder
        elif self.encounter_type == "federation":
            base_escape_chance = 0.15  # Slightly harder
        
        escape_chance = base_escape_chance + speed_bonus
        
        print("Your ship shudders as you fight against the tractor beam...")
        wait_for_enter()
        
        if DiceRoller.chance(escape_chance):
            print("You break free! Your ship tears away from their grip!")
            wait_for_enter()
            print("You escape into hyperspace before they can react.")
            wait_for_enter()
            
            if random.random() < 0.3:
                if self.encounter_type == "cartel":
                    print("[NOVA] 'We got lucky. The cartel won't forget this.'")
                elif self.encounter_type == "federation":
                    print("[NOVA] 'Black ops doesn't give up easily. They'll be back.'")
                else:
                    print("[NOVA] 'That was too close. What did they want with us?'")
                wait_for_enter()
            
            return None
        else:
            print("Their technology is too advanced. You're pulled helplessly forward.")
            wait_for_enter()
            print("Your ship is drawn into a cavernous hangar bay.")
            wait_for_enter()
            
            # Different descriptions based on encounter type
            if self.encounter_type == "cartel":
                print("Cartel enforcers in blood-red armor surround your ship, weapons drawn.")
            elif self.encounter_type == "federation":
                print("Armored operatives emerge from the shadows, moving with military precision.")
            else:
                print("Figures in unmarked armor emerge, weapons trained on your ship.")
            wait_for_enter()
            
            # After failed escape, different options based on encounter type
            if self.encounter_type == "cartel":
                print("\nThe cartel doesn't negotiate. What do you do?")
                print("1. Hide in smuggling compartment")
                print("2. Come out fighting")
                
                while True:
                    print("\n> ", end="")
                    choice = input().strip()
                    if choice == "1":
                        return self._handle_hide()
                    elif choice == "2":
                        return self._handle_fight()
                    else:
                        print("Invalid choice. Please enter 1 or 2")
            else:
                print("\nWhat do you do now?")
                print("1. Hide in smuggling compartment")
                print("2. Come out peacefully")
                print("3. Come out fighting")
                
                while True:
                    print("\n> ", end="")
                    choice = input().strip()
                    if choice == "1":
                        return self._handle_hide()
                    elif choice == "2":
                        return self._handle_peaceful()
                    elif choice == "3":
                        return self._handle_fight()
                    else:
                        print("Invalid choice. Please enter 1, 2, or 3")

    def _handle_hide(self, early_warning=False):
        """Handle hiding in smuggling compartment"""
        # Check if player has empty cargo space
        cargo_slots_used = 0
        if self.game.player.current_contract:
            cargo_slots_used = len(self.game.player.current_contract.crates)
        
        if cargo_slots_used >= self.game.ship.max_cargo:
            print("\nYou can't hide in the smuggling compartment - your cargo hold is full!")
            wait_for_enter()
            print("You need to choose another option quickly!")
            wait_for_enter()
            
            print("What do you do instead?")
            print("1. Come out peacefully")
            print("2. Come out fighting")
            
            while True:
                print("\n> ", end="")
                choice = input().strip()
                if choice == "1":
                    return self._handle_peaceful()
                elif choice == "2":
                    return self._handle_fight()
                else:
                    print("Invalid choice. Please enter 1 or 2")
        
        catch_chance = 0
        if not early_warning:
            catch_chance = 0.15 + (self.game.player.heat * 0.003)  # 15% base, +0.3% per heat
        
        if random.random() < catch_chance:
            print("\nAs you try to slip into the smuggling compartment, the hatch slams open and a security officer grabs you!")
            wait_for_enter()
            print("You've been caught trying to hide. The situation just got a lot worse...")
            wait_for_enter()
            print("\nWhat do you do?")
            print("1. Surrender peacefully")
            print("2. Fight your way out")
            while True:
                print("\n> ", end="")
                choice = input().strip()
                if choice == "1":
                    return self._handle_peaceful()
                elif choice == "2":
                    return self._handle_fight()
                else:
                    print("Invalid choice. Please enter 1 or 2")
        else:
            print("\nYou quickly slip into the ship's hidden smuggling compartment...")
            wait_for_enter()
            
            # Success chance based on heat level and ship condition
            base_success_chance = 0.6
            heat_penalty = self.game.player.heat * 0.005  # 0.5% penalty per heat point
            success_chance = max(0.1, base_success_chance - heat_penalty)
            
            print("Heavy boots clank through your ship...")
            wait_for_enter()
            
            if DiceRoller.chance(success_chance):
                print("They search thoroughly but find nothing.")
                wait_for_enter()
                print("After what feels like hours, you hear them leave.")
                wait_for_enter()
                print("You emerge from hiding...")
                wait_for_enter()
                
                if random.random() < 0.3:
                    print("[NOVA] 'That was close. But now we have an opportunity...'")
                    wait_for_enter()
                
                print("Your ship is still docked in their hangar bay.")
                wait_for_enter()
                print("You could explore their ship while they're distracted, or escape now.")
                wait_for_enter()
                
                print("\nWhat do you do?")
                print("1. Explore their ship")
                print("2. Escape immediately")
                
                while True:
                    print("\n> ", end="")
                    choice = input().strip()
                    if choice == "1":
                        print("\nYou slip out of your ship to explore...")
                        wait_for_enter()
                        return self._handle_dungeon_exploration()
                    elif choice == "2":
                        print("\nYou fire up the engines and escape while they're distracted!")
                        wait_for_enter()
                        if random.random() < 0.3:
                            print("[NOVA] 'Smart choice. Sometimes discretion is the better part of valor.'")
                            wait_for_enter()
                        return None
                    else:
                        print("Invalid choice. Please enter 1 or 2")
            else:
                print("A scanner beam sweeps over your hiding spot...")
                wait_for_enter()
                print("'Found something!' They drag you out in restraints.")
                wait_for_enter()
                
                if random.random() < 0.3:
                    print("[NOVA] 'Well, that didn't work. Good luck!'")
                    wait_for_enter()
                
                return self._handle_capture()
    
    def _handle_peaceful(self):
        """Handle coming out peacefully"""
        print("\nYou power down your weapons and step out with hands visible...")
        wait_for_enter()
        print("The armored figures approach cautiously.")
        wait_for_enter()
        
        # They search you AND your ship (like police encounter)
        return self._handle_search()
    
    def _handle_fight(self):
        """Handle immediate combat"""
        if self.encounter_type == "cartel":
            print("\nYou burst out of your ship, weapon drawn!")
            wait_for_enter()
            print("The cartel enforcers open fire immediately!")
            wait_for_enter()
        else:
            print("\nYou burst out of your ship, weapon drawn!")
            wait_for_enter()
        
        # Create enemy based on encounter type
        enemy = self._generate_shadow_enemy()
        
        print(f"A {enemy.name} steps forward to meet your challenge...")
        wait_for_enter()
        
        combat = Combat(self.game, enemy)
        result = combat.run()
        
        if result == "defeat":
            if self.encounter_type == "cartel":
                print("\nThe cartel shows no mercy...")
                wait_for_enter()
                print("Everything goes dark...")
                wait_for_enter()
                self.game.game_over = True
                return "game_over"
            else:
                print("\nYou're overwhelmed and captured...")
                wait_for_enter()
                return self._handle_capture()
        elif result == "escaped":
            print("\nYou fight your way back to your ship and escape!")
            wait_for_enter()
            if self.encounter_type == "cartel":
                self.game.player.heat += 30
                self.game.player.cartel_threat_level += 1
            else:
                self.game.player.heat += 20
            return None
        else:  # victory
            print("\nYou've defeated their boarding party!")
            wait_for_enter()
            if self.encounter_type == "cartel":
                print("The cartel will remember this...")
                wait_for_enter()
                self.game.player.cartel_threat_level += 1
            print("With their forces scattered, you can explore their ship...")
            wait_for_enter()
            return self._handle_dungeon_exploration()
    
    def _handle_search(self):
        """Handle being searched (similar to police but only personal items)"""
        print("\nThey begin searching you and your ship...")
        wait_for_enter()
        
        # Search atmosphere
        search_descriptions = [
            "Cold, efficient hands pat you down systematically.",
            "Strange scanning devices sweep over your body and ship.",
            "They examine every piece of equipment you carry.",
            "Professional search techniques, unlike any law enforcement you've seen."
        ]
        print(random.choice(search_descriptions))
        wait_for_enter()

        # Random chance for them to comment on the player's name, explaining how they found it
        if random.random() < 0.5:
            player_name = getattr(self.game.player, 'name', None)
            if player_name:
                print(f"One of the guards glances at a scanner.")
                wait_for_enter()
                id_sources = [
                    "your ship's registration logs",
                    "a datachip in your pocket",
                    "your ID badge",
                    "the ship's manifest",
                    "a Federation database entry",
                    "a worn-out cargo license",
                    "a digital passport in your comms"
                ]
                source = random.choice(id_sources)
                name_comments = [
                    f"'Found a match for your name in {source}... {player_name}, huh? That's atupid name.'",
                    f"'So, {player_name}... according to {source}, that's you.'",
                    f"'Your name came up in {source}. {player_name}. We'll be keeping an eye on you. '",
                    f"'Looks like {player_name} is the name on {source}. Noted.'"
                ]
                print(random.choice(name_comments))
                wait_for_enter()
        
        # Build list of items they might find (personal items AND ship cargo)
        found_items = []
        found_crate = False
        
        # Search contract crates (like police encounter)
        if self.game.player.current_contract:
            for i, crate in enumerate(self.game.player.current_contract.crates):
                base_search_chance = 0.4  # Higher than police since these are more thorough
                search_chance = base_search_chance + (self.game.player.heat / 100)
                
                if DiceRoller.chance(search_chance):
                    print(f"\nThey find a {crate.tier} crate...")
                    wait_for_enter()
                    if crate.tier == "legit":
                        print("They mark it as cleared.")
                        wait_for_enter()
                    elif crate.tier == "illicit":
                        print("Contraband detected!")
                        wait_for_enter()
                        found_items.append(('crate', crate))
                        found_crate = True
                    else:  # sealed
                        if DiceRoller.chance(0.6):  # Higher chance than police
                            print("They crack it open... Contraband!")
                            wait_for_enter()
                            found_items.append(('crate', crate))
                            found_crate = True
                        else:
                            print("They crack it open... It's legal cargo.")
                            wait_for_enter()
        
        # Search personal inventory (chance to miss items)
        for item in getattr(self.game.player, 'inventory', []):
            if self._is_illegal_item(item):
                if DiceRoller.chance(0.8):  # Higher chance than police
                    found_items.append(('inventory', item))
        
        # Search equipped weapon (harder to hide)
        weapon = getattr(self.game.player, 'weapon', None)
        if weapon and getattr(weapon, 'is_illegal', False):
            if DiceRoller.chance(0.95):  # Very high chance
                found_items.append(('weapon', weapon))
        
        # Search equipped armor (harder to hide)
        armor = getattr(self.game.player, 'armor_item', None)
        if armor and getattr(armor, 'is_illegal', False):
            if DiceRoller.chance(0.95):  # Very high chance
                found_items.append(('armor', armor))
        
        # Search combat items (easier to hide)
        for item in getattr(self.game.player, 'items', []):
            if getattr(item, 'is_illegal', False):
                if DiceRoller.chance(0.6):  # Moderate chance
                    found_items.append(('combat_item', item))
        
        # Special check for stones (they always detect these)
        if self.game.player.stones:
            print("\nTheir scanners go wild as they detect the stones...")
            wait_for_enter()
            print("'Confirmed. Stone exposure detected. Bring them in for processing.'")
            wait_for_enter()
            return self._handle_capture()
        
        if found_items:
            print("\nThey confront you with illegal items:")
            for source, item in found_items:
                if source == 'crate':
                    print(f"- Contract Crate: {getattr(item, 'tier', str(item))}")
                elif source == 'inventory':
                    print(f"- {item['name'] if isinstance(item, dict) else item.name}")
                elif source == 'weapon':
                    print(f"- Weapon: {item.name}")
                elif source == 'armor':
                    print(f"- Armor: {item.name}")
                elif source == 'combat_item':
                    print(f"- {item.name}")
            wait_for_enter()
            
            print("'Contraband detected. You're coming with us.'")
            wait_for_enter()
            
            # Confiscate found items
            for source, item in found_items:
                if source == 'crate':
                    # Handle crate confiscation like police
                    pass  # Crates handled below
                elif source == 'inventory':
                    try:
                        self.game.player.inventory.remove(item)
                    except:
                        pass
                elif source == 'weapon':
                    self.game.player.weapon = None
                elif source == 'armor':
                    self.game.player.armor_item = None
                elif source == 'combat_item':
                    try:
                        self.game.player.items.remove(item)
                    except:
                        pass
            
            # Handle contract confiscation
            if found_crate and self.game.player.current_contract:
                self.game.player.current_contract = None
                print("\nAll your contract cargo is confiscated!")
                wait_for_enter()
            
            return self._handle_capture()
        else:
            print("\nThey find nothing suspicious on your person or ship.")
            wait_for_enter()
            
            # But they might still be interested based on other factors
            if self.game.player.heat > 50:
                print("'Heat signature indicates criminal activity. Detain for questioning.'")
                wait_for_enter()
                return self._handle_capture()
            elif len(self.game.player.stones_discovered) > 0:
                print("'Residual stone energy detected. This one has been exposed.'")
                wait_for_enter()
                return self._handle_capture()
            else:
                print("'Clean. But we're watching you.'")
                wait_for_enter()
                print("They escort you back to your ship.")
                wait_for_enter()
                
                print("\nWhat do you do?")
                print("1. Leave immediately")
                print("2. Try to fight them now")
                print("3. Ask about their ship")
                
                while True:
                    print("\n> ", end="")
                    choice = input().strip()
                    if choice == "1":
                        print("\nYou fire up your engines and leave quickly.")
                        wait_for_enter()
                        return None
                    elif choice == "2":
                        print("\nYou suddenly attack the guards!")
                        wait_for_enter()
                        return self._handle_fight()
                    elif choice == "3":
                        print("\n'Who are you people? What do you want?'")
                        wait_for_enter()
                        print("They ignore your questions and gesture toward the exit.")
                        wait_for_enter()
                        print("'Leave. Now.'")
                        wait_for_enter()
                        print("\nYou have no choice but to go.")
                        wait_for_enter()
                        return None
                    else:
                        print("Invalid choice. Please enter 1, 2, or 3")
    
    def _is_illegal_item(self, item):
        """Check if an item is illegal"""
        return (
            getattr(item, 'is_contraband', False) or
            getattr(item, 'is_illegal', False) or
            (isinstance(item, dict) and (
                item.get('is_contraband') or item.get('is_illegal')
            ))
        )
    
    def _handle_capture(self):
        """Handle being captured and thrown in prison"""
        
        print("You're dragged through sterile corridors...")
        wait_for_enter()
        print("The walls are lined with strange technology you don't recognize.")
        wait_for_enter()
        
        print("You are taken to prison.")
        wait_for_enter()
        print("You're thrown into a detention cell.")
        wait_for_enter()
        
        # Your ship is impounded but cargo remains
        print("Through the cell's window, you can see your ship in their impound bay.")
        wait_for_enter()
        
        if random.random() < 0.5:
            print("[NOVA] 'I'm still in the ship's systems. I'll try to help when you get back.'")
            wait_for_enter()
        
        return self._handle_prison_escape()
    
    def _handle_prison_escape(self):
        """Handle the prison escape dungeon"""
        print("\nYou examine your cell...")
        wait_for_enter()
        print("The lock is electronic, but the ventilation grate looks loose.")
        wait_for_enter()
        
        # Meet other prisoners
        print("A voice whispers from the next cell:")
        wait_for_enter()
        
        prisoner_dialogues = [
            "'They've been collecting people who've touched the stones...'",
            "'I was a cartel courier. They grabbed me after a stone delivery.'",
            "'Federation agent here. This isn't any government operation.'",
            "'They're preparing for something big. Something cosmic.'"
        ]
        print(f"'{random.choice(prisoner_dialogues)}'")
        wait_for_enter()
        
        print("\nWhat do you do?")
        print("1. Try to escape through the ventilation")
        print("2. Wait for a guard and try to overpower them")
        print("3. Look for another way out")
        
        while True:
            print("\n> ", end="")
            choice = input().strip()
            if choice == "1":
                return self._escape_through_vents()
            elif choice == "2":
                return self._overpower_guard()
            elif choice == "3":
                return self._find_alternate_escape()
            else:
                print("Invalid choice. Please enter 1, 2, or 3")
    
    def _escape_through_vents(self):
        """Stealth escape route"""
        print("\nYou quietly work the grate loose...")
        wait_for_enter()
        
        if DiceRoller.chance(0.5):
            print("Success! You crawl through the ventilation system.")
            wait_for_enter()
            return self._handle_dungeon_exploration()
        else:
            print("The grate clatters to the floor loudly!")
            wait_for_enter()
            print("Guards rush in!")
            wait_for_enter()
            return self._fight_guards()
    
    def _overpower_guard(self):
        """Combat escape route"""
        print("\nYou wait by the door...")
        wait_for_enter()
        print("A guard enters to check on you.")
        wait_for_enter()
        
        return self._fight_guards()
    
    def _find_alternate_escape(self):
        """Alternative escape with prisoner help"""
        print("\nYou examine the cell more carefully...")
        wait_for_enter()
        
        print("The prisoner in the next cell whispers:")
        wait_for_enter()
        print("'There's a maintenance tunnel behind the wall panel. I can create a distraction.'")
        wait_for_enter()
        
        print("Suddenly, alarms start blaring from another section!")
        wait_for_enter()
        print("Guards rush past your cell toward the commotion.")
        wait_for_enter()
        print("You slip out through the maintenance tunnel.")
        wait_for_enter()
        
        return self._handle_dungeon_exploration()
    
    def _fight_guards(self):
        """Fight prison guards"""
        enemy = Enemy(name="Shadow Guard", hp=40, min_damage=8, max_damage=15, credits_reward=100)
        
        print(f"A {enemy.name} confronts you!")
        wait_for_enter()
        
        combat = Combat(self.game, enemy)
        result = combat.run()
        
        if result == "defeat":
            print("\nYou're overpowered and dragged back to your cell...")
            wait_for_enter()
            print("This time, they post extra guards.")
            wait_for_enter()
            print("After hours of waiting, you manage to slip away during a shift change.")
            wait_for_enter()
            return self._handle_dungeon_exploration()
        else:
            print("\nYou've defeated the guard!")
            wait_for_enter()
            return self._handle_dungeon_exploration()
    
    def _handle_dungeon_exploration(self):
        """Simple dungeon exploration like IQ1"""
        print("\nYou're free to move through the ship...")
        wait_for_enter()
        
        # Random number of rooms (3-8)
        max_rooms = DiceRoller.d6() + 2  # 3-8 rooms
        rooms_explored = 0
        
        print("The corridors stretch ahead into darkness.")
        wait_for_enter()
        print("You can leave at any time, but valuable intel and loot await...")
        wait_for_enter()
        
        while rooms_explored < max_rooms:
            print(f"\nYou approach another section of the ship...")
            print("1. Investigate this area")
            print("2. Head to the impound bay and escape")
            
            while True:
                print("\n> ", end="")
                choice = input().strip()
                if choice == "1":
                    print("\nYou move carefully through the shadows...")
                    wait_for_enter()
                    
                    result = self._explore_room()
                    if result == "combat_defeat":
                        return "game_over"
                    elif result == "forced_escape":
                        return self._escape_to_ship()
                    rooms_explored += 1
                    
                    # Add tension after each room
                    if rooms_explored < max_rooms:
                        if random.random() < 0.3:
                            tension_lines = [
                                "Footsteps echo in the distance...",
                                "You hear voices approaching...",
                                "Security lights sweep the corridor ahead...",
                                "The ship's systems hum ominously around you..."
                            ]
                            print(f"\n{random.choice(tension_lines)}")
                            wait_for_enter()
                    break
                elif choice == "2":
                    return self._escape_to_ship()
                else:
                    print("Invalid choice. Please enter 1 or 2")
        
        print("\nYou've explored as much as you dare.")
        wait_for_enter()
        print("Time to get out before they notice you're missing.")
        wait_for_enter()
        return self._escape_to_ship()
    
    def _explore_room(self):
        """Explore a single room"""
        room_types = [
            "detention_block",
            "cargo_bay", 
            "command_room",
            "laboratory",
            "reactor_room",
            "armory"  # New room type
        ]
        
        room_type = random.choice(room_types)
        
        if room_type == "detention_block":
            print("\nYou slip into the detention block...")
            wait_for_enter()
            print("Rows of empty cells stretch into the darkness.")
            wait_for_enter()
            
            if DiceRoller.chance(0.6):
                print("A prisoner whispers: 'They're collecting stone-touched individuals for experiments.'")
                wait_for_enter()
                print("'The boss is preparing for His return.'")
                wait_for_enter()
            
            # Small chance to find a stone here too (from a previous prisoner)
            if DiceRoller.chance(0.15):  # 15% chance - lower than lab
                # List of available stones
                stones = ["Space", "Mind", "Reality", "Power", "Soul", "Time"]
                
                # Remove stones already discovered by the player
                available_stones = [stone for stone in stones if stone not in self.game.player.stones_discovered]
                
                # Remove stones already in player's possession
                available_stones = [stone for stone in available_stones if stone not in self.game.player.stones]
                
                if available_stones:
                    found_stone = random.choice(available_stones)
                    print(f"\nIn an abandoned cell, you find the {found_stone} Stone hidden under a loose floor panel!")
                    wait_for_enter()
                    print("A previous prisoner must have hidden it here...")
                    wait_for_enter()
                    
                    print("What do you do?")
                    print("1. Take the stone")
                    print("2. Leave it hidden")
                    
                    while True:
                        print("\n> ", end="")
                        choice = input().strip()
                        if choice == "1":
                            self.game.player.stones.append(found_stone)
                            self.game.player.stones_discovered.append(found_stone)
                            self.game.player.heat += 5  # Stones always add heat
                            print(f"\nYou pocket the {found_stone} Stone.")
                            wait_for_enter()
                            print("You can feel its power resonating with your very being...")
                            wait_for_enter()
                            if random.random() < 0.3:
                                print("[NOVA] 'Another one? At this rate, we'll have a target painted on our hull.'")
                                wait_for_enter()
                            break
                        elif choice == "2":
                            print("\nYou leave it where it is. Someone else can deal with that responsibility.")
                            wait_for_enter()
                            break
                        else:
                            print("Invalid choice. Please enter 1 or 2")
            
            # Chance to find personal items left by prisoners
            if DiceRoller.chance(0.4):
                print("\nYou search through abandoned personal effects...")
                wait_for_enter()
                
                loot_options = [
                    ("credits", DiceRoller.d6() * 200),
                    ("combat_item", "medkit"),
                    ("combat_item", "shield"),
                ]
                
                loot_type, loot_value = random.choice(loot_options)
                
                if loot_type == "credits":
                    self.game.player.credits += loot_value
                    print(f"You find {loot_value} credits hidden in a mattress!")
                elif loot_type == "combat_item":
                    if loot_value == "medkit":
                        from combat import MEDKIT
                        self.game.player.add_item(MEDKIT())
                        print("You find a medkit hidden under a bunk!")
                    elif loot_value == "shield":
                        from combat import SHIELD
                        self.game.player.add_item(SHIELD())
                        print("You find a personal shield generator!")
                wait_for_enter()
            
            # Increased detection chance - you're making noise
            if DiceRoller.chance(0.4):
                print("\nYou hear footsteps approaching!")
                wait_for_enter()
                return self._encounter_enemy()
                
        elif room_type == "cargo_bay":
            print("\nYou enter a massive cargo bay...")
            wait_for_enter()
            print("Confiscated goods from dozens of ships fill the space.")
            wait_for_enter()
            
            # Multiple loot opportunities in cargo bay
            loot_found = 0
            
            # Credits are common
            if DiceRoller.chance(0.8):
                credits_found = (DiceRoller.d6() + DiceRoller.d6()) * 500  # 1000-6000 credits
                self.game.player.credits += credits_found
                print(f"You find {credits_found} credits in a secure lockbox!")
                wait_for_enter()
                print("Someone's life savings, now yours.")
                wait_for_enter()
                loot_found += 1
            
            # Chance for confiscated weapons/armor
            if DiceRoller.chance(0.5):
                from equipment import get_random_weapon, get_random_armor, UNCOMMON, RARE
                
                if random.random() < 0.6:  # 60% weapon, 40% armor
                    weapon = get_random_weapon(include_illegal=True, min_rarity=UNCOMMON)
                    print(f"\nAmong the confiscated goods, you discover a {weapon.name}!")
                    print(f"{weapon}")
                    
                    # Compare with current weapon
                    if self.game.player.weapon:
                        print(f"\nYour current weapon: {self.game.player.weapon}")
                        if weapon.damage > self.game.player.weapon.damage:
                            print("This weapon does more damage than your current one.")
                        else:
                            print("This weapon does less damage than your current one.")
                    
                    wait_for_enter()
                    print("What do you do?")
                    print("1. Take the weapon")
                    print("2. Leave it")
                    
                    while True:
                        print("\n> ", end="")
                        choice = input().strip()
                        if choice == "1":
                            self.game.player.equip_weapon(weapon)
                            print(f"\nYou equip the {weapon.name}.")
                            wait_for_enter()
                            break
                        elif choice == "2":
                            print("\nYou leave it where it is.")
                            wait_for_enter()
                            break
                        else:
                            print("Invalid choice. Please enter 1 or 2")
                else:
                    armor = get_random_armor(include_illegal=True, min_rarity=UNCOMMON)
                    print(f"\nAmong the confiscated goods, you discover {armor.name}!")
                    print(f"{armor}")
                    
                    # Compare with current armor
                    if self.game.player.armor_item:
                        print(f"\nYour current armor: {self.game.player.armor_item}")
                        if armor.defense > self.game.player.armor_item.defense:
                            print("This armor provides more protection than your current one.")
                        else:
                            print("This armor provides less protection than your current one.")
                    
                    wait_for_enter()
                    print("What do you do?")
                    print("1. Take the armor")
                    print("2. Leave it")
                    
                    while True:
                        print("\n> ", end="")
                        choice = input().strip()
                        if choice == "1":
                            self.game.player.equip_armor(armor)
                            print(f"\nYou equip the {armor.name}.")
                            wait_for_enter()
                            break
                        elif choice == "2":
                            print("\nYou leave it where it is.")
                            wait_for_enter()
                            break
                        else:
                            print("Invalid choice. Please enter 1 or 2")
                loot_found += 1
            
            # Chance for combat items
            if DiceRoller.chance(0.6):
                from combat import MEDKIT, SHIELD, STUN_GRENADE
                
                item_options = [MEDKIT, SHIELD, STUN_GRENADE]
                item_func = random.choice(item_options)
                item = item_func()
                
                self.game.player.add_item(item)
                print(f"\nYou find a {item.name} among the confiscated supplies!")
                wait_for_enter()
                loot_found += 1
            
            # Rare chance for contraband inventory items
            if DiceRoller.chance(0.3):
                contraband_items = [
                    {"name": "Rare Minerals", "value": 5000, "is_contraband": True},
                    {"name": "Alien Artifacts", "value": 8000, "is_contraband": True},
                    {"name": "Classified Data Chips", "value": 3000, "is_contraband": True},
                    {"name": "Experimental Tech", "value": 12000, "is_contraband": True},
                ]
                
                item = random.choice(contraband_items)
                self.game.player.inventory.append(item)
                print(f"\nYou discover {item['name']} worth {item['value']:,} credits!")
                wait_for_enter()
                print("This is definitely contraband, but very valuable...")
                wait_for_enter()
                loot_found += 1
                
            if loot_found == 0:
                print("\nMost of the cargo has already been processed. You find nothing of value.")
                wait_for_enter()
                
            if DiceRoller.chance(0.3):
                print("\nA security drone activates!")
                wait_for_enter()
                return self._encounter_enemy()
                
        elif room_type == "armory":
            print("\nYou discover the ship's armory...")
            wait_for_enter()
            print("Racks of weapons and armor line the walls, secured behind energy barriers.")
            wait_for_enter()
            
            print("You could try to bypass the security...")
            print("1. Attempt to hack the security system")
            print("2. Try to force the locks")
            print("3. Leave the armory alone")
            
            while True:
                print("\n> ", end="")
                choice = input().strip()
                if choice == "1":
                    # Hacking has better success rate but higher detection chance
                    if DiceRoller.chance(0.7):
                        print("\nSecurity bypassed! The energy barriers flicker and die.")
                        wait_for_enter()
                        
                        # Guaranteed high-quality loot
                        from equipment import get_random_weapon, get_random_armor, RARE, EPIC, LEGENDARY
                        
                        # Player gets to choose between weapon and armor
                        weapon = get_random_weapon(include_illegal=True, min_rarity=RARE)
                        armor = get_random_armor(include_illegal=True, min_rarity=RARE)
                        
                        print(f"You can take one item:")
                        
                        # Show weapon with comparison
                        weapon_text = f"1. {weapon.name} - {weapon.damage} damage ({weapon.rarity})"
                        if self.game.player.weapon:
                            damage_diff = weapon.damage - self.game.player.weapon.damage
                            if damage_diff > 0:
                                weapon_text += f" [+{damage_diff} damage upgrade]"
                            elif damage_diff < 0:
                                weapon_text += f" [{damage_diff} damage downgrade]"
                        print(weapon_text)
                        
                        # Show armor with comparison
                        armor_text = f"2. {armor.name} - {armor.defense} defense ({armor.rarity})"
                        if self.game.player.armor_item:
                            defense_diff = armor.defense - self.game.player.armor_item.defense
                            if defense_diff > 0:
                                armor_text += f" [+{defense_diff} defense upgrade]"
                            elif defense_diff < 0:
                                armor_text += f" [{defense_diff} defense downgrade]"
                        print(armor_text)
                        
                        print("3. Take nothing")
                        
                        while True:
                            print("\n> ", end="")
                            loot_choice = input().strip()
                            if loot_choice == "1":
                                self.game.player.equip_weapon(weapon)
                                print(f"\nYou equip the {weapon.name}!")
                                wait_for_enter()
                                break
                            elif loot_choice == "2":
                                self.game.player.equip_armor(armor)
                                print(f"\nYou equip the {armor.name}!")
                                wait_for_enter()
                                break
                            elif loot_choice == "3":
                                print("\nYou decide not to risk carrying stolen military equipment.")
                                wait_for_enter()
                                break
                            else:
                                print("Invalid choice. Please enter 1, 2, or 3")
                        
                        # High detection chance after hacking
                        if DiceRoller.chance(0.8):
                            print("\nAlarms blare! The security breach has been detected!")
                            wait_for_enter()
                            return self._encounter_enemy()
                    else:
                        print("\nHacking failed! Alarms start blaring!")
                        wait_for_enter()
                        return self._encounter_enemy()
                    break
                    
                elif choice == "2":
                    # Forcing has lower success rate but lower detection chance
                    if DiceRoller.chance(0.4):
                        print("\nYou manage to pry open one of the weapon lockers!")
                        wait_for_enter()
                        
                        # Lower quality loot than hacking
                        from equipment import get_random_weapon, get_random_armor, UNCOMMON, RARE
                        
                        if random.random() < 0.7:  # 70% weapon, 30% armor
                            weapon = get_random_weapon(include_illegal=True, min_rarity=UNCOMMON)
                            print(f"You find a {weapon.name}!")
                            print(f"{weapon}")
                            
                            # Compare with current weapon
                            if self.game.player.weapon:
                                print(f"\nYour current weapon: {self.game.player.weapon}")
                                if weapon.damage > self.game.player.weapon.damage:
                                    print("This weapon does more damage than your current one.")
                                else:
                                    print("This weapon does less damage than your current one.")
                            
                            wait_for_enter()
                            print("What do you do?")
                            print("1. Take the weapon")
                            print("2. Leave it")
                            
                            while True:
                                print("\n> ", end="")
                                loot_choice = input().strip()
                                if loot_choice == "1":
                                    self.game.player.equip_weapon(weapon)
                                    print(f"\nYou equip the {weapon.name}.")
                                    wait_for_enter()
                                    break
                                elif loot_choice == "2":
                                    print("\nYou leave it in the locker.")
                                    wait_for_enter()
                                    break
                                else:
                                    print("Invalid choice. Please enter 1 or 2")
                        else:
                            armor = get_random_armor(include_illegal=True, min_rarity=UNCOMMON)
                            print(f"You find {armor.name}!")
                            print(f"{armor}")
                            
                            # Compare with current armor
                            if self.game.player.armor_item:
                                print(f"\nYour current armor: {self.game.player.armor_item}")
                                if armor.defense > self.game.player.armor_item.defense:
                                    print("This armor provides more protection than your current one.")
                                else:
                                    print("This armor provides less protection than your current one.")
                            
                            wait_for_enter()
                            print("What do you do?")
                            print("1. Take the armor")
                            print("2. Leave it")
                            
                            while True:
                                print("\n> ", end="")
                                loot_choice = input().strip()
                                if loot_choice == "1":
                                    self.game.player.equip_armor(armor)
                                    print(f"\nYou equip the {armor.name}.")
                                    wait_for_enter()
                                    break
                                elif loot_choice == "2":
                                    print("\nYou leave it in the locker.")
                                    wait_for_enter()
                                    break
                                else:
                                    print("Invalid choice. Please enter 1 or 2")
                        
                        # Lower detection chance
                        if DiceRoller.chance(0.4):
                            print("\nSecurity sensors detect the breach!")
                            wait_for_enter()
                            return self._encounter_enemy()
                    else:
                        print("\nThe locks are too strong! You can't force them open.")
                        wait_for_enter()
                        
                        # Small chance of detection even on failure
                        if DiceRoller.chance(0.2):
                            print("\nYour attempts trigger a silent alarm!")
                            wait_for_enter()
                            return self._encounter_enemy()
                    break
                    
                elif choice == "3":
                    print("\nYou decide the armory is too risky and leave it alone.")
                    wait_for_enter()
                    break
                else:
                    print("Invalid choice. Please enter 1, 2, or 3")
                
        elif room_type == "command_room":
            print("\nYou access a command terminal...")
            wait_for_enter()
            print("Classified data streams across multiple screens.")
            wait_for_enter()
            
            # Calculate how many stones are still unaccounted for
            all_stones = {"Space", "Mind", "Reality", "Power", "Soul", "Time"}
            player_stones = set(self.game.player.stones)
            discovered_stones = set(self.game.player.stones_discovered)
            accounted_for = player_stones.union(discovered_stones)
            unaccounted_stones = all_stones - accounted_for
            
            intel_options = [
                f"Stone tracking data shows {len(unaccounted_stones)} stones still unaccounted for.",
                "Communication logs mention 'Project Convergence' and 'His awakening.'",
                "Shipping manifests show regular deliveries to coordinates in deep space.",
                "Personnel files list agents embedded in major cartels and Federation outposts."
            ]
            print(f"Intel discovered: {random.choice(intel_options)}")
            wait_for_enter()
            
            # Bonus credits for intel
            if DiceRoller.chance(0.5):
                intel_credits = DiceRoller.d6() * 300
                self.game.player.credits += intel_credits
                print(f"You download valuable data worth {intel_credits} credits!")
                wait_for_enter()
            
            # Chance to find access codes or valuable data
            if DiceRoller.chance(0.4):
                data_items = [
                    {"name": "Security Codes", "value": 4000, "is_contraband": False},
                    {"name": "Navigation Charts", "value": 2500, "is_contraband": False},
                    {"name": "Classified Intel", "value": 8000, "is_contraband": True},
                ]
                
                item = random.choice(data_items)
                self.game.player.inventory.append(item)
                print(f"\nYou copy {item['name']} to a data chip!")
                wait_for_enter()
            
            if DiceRoller.chance(0.6):
                print("\nAlarms suddenly blare - you've been detected!")
                wait_for_enter()
                return self._encounter_enemy()
                
        elif room_type == "laboratory":
            print("\nYou enter a sterile laboratory...")
            wait_for_enter()
            print("Disturbing research data on stone exposure effects fills the screens.")
            wait_for_enter()
            print("Test subjects show cellular mutation and enhanced abilities.")
            wait_for_enter()
            
            # Chance to find a stone in the lab
            if DiceRoller.chance(0.3):  # 30% chance to find a stone
                # List of available stones
                stones = ["Space", "Mind", "Reality", "Power", "Soul", "Time"]
                
                # Remove stones already discovered by the player
                available_stones = [stone for stone in stones if stone not in self.game.player.stones_discovered]
                
                # Remove stones already in player's possession
                available_stones = [stone for stone in available_stones if stone not in self.game.player.stones]
                
                if available_stones:
                    found_stone = random.choice(available_stones)
                    print(f"\nIn a containment unit, you discover the {found_stone} Stone!")
                    wait_for_enter()
                    print("The stone pulses with otherworldly energy...")
                    wait_for_enter()
                    
                    print("What do you do?")
                    print("1. Take the stone")
                    print("2. Leave it alone")
                    
                    while True:
                        print("\n> ", end="")
                        choice = input().strip()
                        if choice == "1":
                            self.game.player.stones.append(found_stone)
                            self.game.player.stones_discovered.append(found_stone)
                            self.game.player.heat += 5  # Stones always add heat
                            print(f"\nYou carefully extract the {found_stone} Stone.")
                            wait_for_enter()
                            print("Its power courses through you...")
                            wait_for_enter()
                            if random.random() < 0.3:
                                print("[NOVA] 'That thing is giving off readings I can't classify. We're in deep now.'")
                                wait_for_enter()
                            break
                        elif choice == "2":
                            print("\nYou decide it's too dangerous to take.")
                            wait_for_enter()
                            break
                        else:
                            print("Invalid choice. Please enter 1 or 2")
            
            # Chance to find experimental equipment or samples
            if DiceRoller.chance(0.5):
                lab_loot = [
                    ("combat_item", "medkit"),
                    ("combat_item", "stun_grenade"),
                    ("inventory", {"name": "Experimental Samples", "value": 6000, "is_contraband": True}),
                    ("inventory", {"name": "Research Data", "value": 4000, "is_contraband": False}),
                ]
                
                loot_type, loot_value = random.choice(lab_loot)
                
                if loot_type == "combat_item":
                    if loot_value == "medkit":
                        from combat import MEDKIT
                        self.game.player.add_item(MEDKIT())
                        print("\nYou find an advanced medical kit!")
                    elif loot_value == "stun_grenade":
                        from combat import STUN_GRENADE
                        self.game.player.add_item(STUN_GRENADE())
                        print("\nYou find an experimental stun device!")
                elif loot_type == "inventory":
                    self.game.player.inventory.append(loot_value)
                    print(f"\nYou secure {loot_value['name']}!")
                wait_for_enter()
            
            # High detection chance - labs are monitored
            if DiceRoller.chance(0.7):
                print("\nBioscanners detect your presence!")
                wait_for_enter()
                return self._encounter_enemy()
                
        elif room_type == "reactor_room":
            print("\nYou reach the ship's reactor core...")
            wait_for_enter()
            print("Massive energy conduits pulse with alien power.")
            wait_for_enter()
            
            print("You could sabotage their systems...")
            print("1. Sabotage the reactor")
            print("2. Leave it alone")
            
            while True:
                print("\n> ", end="")
                choice = input().strip()
                if choice == "1":
                    print("\nYou overload several key systems...")
                    wait_for_enter()
                    print("This should make your escape easier!")
                    wait_for_enter()
                    # Sabotage makes escape guaranteed AND gives credits
                    self.sabotaged = True
                    sabotage_bonus = DiceRoller.d6() * 400
                    self.game.player.credits += sabotage_bonus
                    print(f"You also steal {sabotage_bonus:,} credits worth of rare components!")
                    wait_for_enter()
                    
                    # Chance to find rare tech components
                    if DiceRoller.chance(0.6):
                        tech_items = [
                            {"name": "Quantum Processors", "value": 8000, "is_contraband": False},
                            {"name": "Exotic Matter", "value": 12000, "is_contraband": True},
                            {"name": "Energy Crystals", "value": 5000, "is_contraband": False},
                        ]
                        
                        item = random.choice(tech_items)
                        self.game.player.inventory.append(item)
                        print(f"You also grab {item['name']} from the reactor systems!")
                        wait_for_enter()
                    break
                elif choice == "2":
                    print("\nYou decide not to risk it.")
                    wait_for_enter()
                    break
                else:
                    print("Invalid choice. Please enter 1 or 2")
            
            if DiceRoller.chance(0.5):
                print("\nEngineering staff arrive for routine maintenance!")
                wait_for_enter()
                return self._encounter_enemy()
        
        return None
    
    def _encounter_enemy(self):
        """Random enemy encounter during exploration"""
        print("\nA patrol guard spots you!")
        wait_for_enter()
        
        enemy = self._generate_shadow_enemy()
        
        combat = Combat(self.game, enemy)
        result = combat.run()
        
        if result == "defeat":
            return "combat_defeat"
        elif result == "escaped":
            print("\nYou escape but alarms are now blaring!")
            wait_for_enter()
            return "forced_escape"
        else:
            print("\nYou defeat the guard and continue exploring.")
            wait_for_enter()
            return None
    
    def _escape_to_ship(self):
        """Final escape sequence"""
        print("\nYou make your way to the impound bay...")
        wait_for_enter()
        
        if hasattr(self, 'sabotaged') and self.sabotaged:
            print("The sabotaged systems are causing chaos throughout the ship!")
            wait_for_enter()
            print("You easily slip past the distracted guards.")
            wait_for_enter()
        else:
            print("Guards patrol the area...")
            wait_for_enter()
            
            if DiceRoller.chance(0.6):
                print("You sneak past them successfully.")
                wait_for_enter()
            else:
                print("You're spotted! Fighting your way to the ship!")
                wait_for_enter()
                
                enemy = self._generate_shadow_enemy()
                combat = Combat(self.game, enemy)
                result = combat.run()
                
                if result == "defeat":
                    print("\nYou're recaptured...")
                    wait_for_enter()
                    print("But in the confusion, you manage to break free again!")
                    wait_for_enter()
        
        print("You reach your ship!")
        wait_for_enter()
        
        print("[NOVA] 'About time! I was getting worried. Let's get out of here!'")
        wait_for_enter()            
        
        print("You fire up the engines and blast out of their hangar!")
        wait_for_enter()
        
        # Heat increase for the encounter
        self.game.player.heat += 15
        
        return "tractor_beam_dungeon"
    
    def _generate_shadow_enemy(self):
        """Generate enemy based on encounter type"""
        base_hp = 35
        base_min_damage = 8
        base_max_damage = 16
        base_credits = 200
        
        # Scale with heat level
        heat_factor = self.game.player.heat // 20
        
        hp = base_hp + (heat_factor * 10)
        min_damage = base_min_damage + heat_factor
        max_damage = base_max_damage + (heat_factor * 2)
        credits = base_credits + (heat_factor * 50)
        
        # Different enemy types based on encounter type
        if self.encounter_type == "cartel":
            enemy_names = [
                "Cartel Enforcer",
                "Syndicate Assassin", 
                "Blood Guard",
                "Cartel Lieutenant",
                "Dreadnought Marine"
            ]
            # Cartel enemies are tougher
            hp += 15
            min_damage += 3
            max_damage += 5
            credits += 100
        elif self.encounter_type == "federation":
            enemy_names = [
                "Black Ops Agent",
                "Federation Specter", 
                "Shadow Operative",
                "Classified Enforcer",
                "Dark Protocol Guard"
            ]
            # Federation enemies are more skilled
            hp += 10
            min_damage += 2
            max_damage += 4
            credits += 75
        else:  # stones encounter
            enemy_names = [
                "Void Cultist",
                "Stone Seeker", 
                "Cosmic Enforcer",
                "Reality Warden",
                "Dimensional Agent"
            ]
            # Stone-related enemies have mysterious abilities
            hp += 5
            min_damage += 1
            max_damage += 3
            credits += 50
        
        return Enemy(
            name=random.choice(enemy_names),
            hp=hp,
            min_damage=min_damage,
            max_damage=max_damage,
            credits_reward=credits
        )

class Nothing(Encounter):
    """No encounter"""
    def run(self):
        print("\nYou continue on your way...")
        wait_for_enter()
        return None

def handle_random_encounter(game):
    """Roll for random encounter"""
    # Check for special tractor beam encounters first
    tractor_beam_encounter = check_for_tractor_beam_encounter(game)
    if tractor_beam_encounter:
        return tractor_beam_encounter.run()
    
    # Build weighted encounter list based on heat level
    encounters = []
    weights = []
    
    # Police encounter weight scales with heat
    # Base weight of 10, scales more aggressively with heat level
    police_weight = 10 + (10 * (game.player.heat // 10))
    encounters.append(PoliceEncounter(game))
    weights.append(police_weight)
    
    # Other encounters have fixed weights
    encounters.append(HazardEncounter(game))
    weights.append(30)  # Common
    
    encounters.append(PlanetEncounter(game)) 
    weights.append(25)  # Very common
    
    # Select encounter based on weights
    encounter = random.choices(encounters, weights=weights, k=1)[0]
    
    return encounter.run()

def check_for_tractor_beam_encounter(game):
    """Check if conditions are met for a targeted tractor beam encounter"""
    player = game.player
    
    # Priority 1: Cartel threat level (they actively hunt you)
    if player.cartel_threat_level >= 4:
        # Higher threat = higher chance
        cartel_chance = 0.01 + (player.cartel_threat_level - 4) * 0.02  # 1% base, +2% per level above 4
        if DiceRoller.chance(cartel_chance):
            return TractorBeamEncounter(game, "cartel")
    
    # Priority 2: Carrying stones (mysterious forces are drawn to them)
    if player.stones:
        # More stones = higher chance
        stone_chance = 0.01 + (len(player.stones) * 0.02)  # 1% base, +2% per stone
        if DiceRoller.chance(stone_chance):
            return TractorBeamEncounter(game, "stones")
    
    # Priority 3: High heat level (Federation black ops)
    if player.heat >= 80:
        # Higher heat = higher chance
        fed_chance = 0.05 + ((player.heat - 80) * 0.002)  # 5% base, +0.2% per heat point above 80
        if DiceRoller.chance(fed_chance):
            return TractorBeamEncounter(game, "federation")
    
    return None
    