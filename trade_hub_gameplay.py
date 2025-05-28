from flavor import get_random_trade_quote, get_random_cargo_quote, generate_trade_hub_name
from shop import TradeHubShop
import random
from utils import DiceRoller
from fights import PoliceEncounter

def wait_for_enter():
    input("\n...\n")

def handle_trade_hub(game):
    """Handles all trade hub interactions. Takes the game instance to access player, ship, and hub."""
    hub_name, hub_type = generate_trade_hub_name()
    wait_for_enter()


    #print("\nYou enter at the trade hub...")
    #wait_for_enter()

    # Police encounter before entering the trade hub, based on heat
    if game.player.heat > 0:
        print("\nAs you prepare to enter the trade hub, flashing lights appear outside your viewport.")
        #wait_for_enter()
        heat_before = game.player.heat
        police_result = PoliceEncounter(game).run()
        if police_result == "game_over":
            return  # Player defeated or arrested
        elif police_result is not None:  # Player ran/escaped
            print("\nYou blast off, evading the authorities.")
            wait_for_enter()
            return  # Do not enter the trade hub
        heat_after = game.player.heat
        if heat_after - heat_before > 10:
            print("\nAfter a violent incident with the authorities, you land your ship amidst tense stares and hushed whispers...")
        else:
            print("\nThe authorities clear you to land. You exit your ship and enter the bustling trade hub...")
        wait_for_enter()

    
    # Generate contracts based on ship's cargo capacity
    game.current_hub.generate_contracts(game.ship.max_cargo)

    #encounter

    # Check for police encounter based on heat level

   
    # Generate weighted random fuel price

    weights = [15, 12, 10, 8, 5]  # default

    if hub_type == "slum":
        weights = [20, 15, 8, 5, 2]  # More likely to be cheap, but rare gouging
    elif hub_type == "corp":
        weights = [5, 10, 15, 10, 8]  # More likely mid-high, but not always
    elif hub_type == "cartel":
        weights = [8, 10, 12, 10, 10]  # Fairly even, but slightly more mid-high
    elif hub_type == "ghost":
        weights = [12, 10, 10, 8, 5]  # Slightly favoring low/mid, but can be odd
    elif hub_type == "blacksite":
        weights = [2, 5, 8, 12, 18]  # Most likely expensive
    else:
        weights = [15, 12, 10, 8, 5]  # Default

    price_ranges = [(30,45), (46,60), (61,75), (76,85), (86,100)]
    
    selected_range = price_ranges[DiceRoller.weighted_choice(weights)]
    game.current_hub.fuel_price = random.randint(selected_range[0], selected_range[1])
    
    # STARTING FUEL SAFETY CHECK: Prevent impossible starts
    # If player has very low fuel (0-2) and limited credits, cap fuel price to ensure viability
    if game.ship.fuel <= 2 and game.player.credits <= 600:
        max_affordable_fuel = game.player.credits // game.current_hub.fuel_price
        if max_affordable_fuel < 8:  # Need at least 8 fuel units for viable gameplay
            # Cap fuel price to ensure player can afford at least 8 units
            print(f"[NOVA] 'Looks like the fuel prices just dropped. Lucky break, {game.player.name}.'")
            max_safe_price = game.player.credits // 8
            if game.current_hub.fuel_price > max_safe_price and max_safe_price >= 30:
                game.current_hub.fuel_price = max(max_safe_price, 30)  # Don't go below 30 credits
            elif max_safe_price < 30:
                # If even 30 credits per unit would be too expensive, set to 30 anyway
                # This ensures fuel never goes below 30 credits but prioritizes game balance
                game.current_hub.fuel_price = 30

    # Create shop instance
    shop = TradeHubShop()
    
    # Fuel flavor lines by hub type
    FUEL_FLAVOR = {
        "slum": "A grimy attendant wipes their hands. 'Fuel's cheap, but don't ask what we cut it with.'",
        "corp": "A digital sign flashes: 'Premium fuel for premium customers.'",
        "cartel": "A vendor glances around. 'No questions, no receipts.'",
        "ghost": "The pumps whir in the empty silence. You feel watched, but see no one.",
        "blacksite": "A silent drone monitors you as you refuel from the military-grade pumps.",
    }
    while True:
        print("\n=== Trade Hub ===")
        print(f"Your Credits: {game.player.credits:,}")
        print(f"Your Fuel: {game.ship.fuel}/{game.ship.max_fuel}")
        print("\nOptions:")
        print("1. View Available Contracts")
        print(f"2. Buy Fuel")
        print("3. Visit Equipment Shop | Sell Goods")
        print("4. Ship Upgrades")
        print("\n0. Leave Trade Hub")
        
        try:
            choice = int(input("\nEnter your choice (1-4) or 0 to leave: "))
            if choice == 1:
                if game.player.current_contract:
                    print("You already have an active contract! The hub's fixers don't like double-dealing.")
                    wait_for_enter()
                else:
                    # INSERT_YOUR_CODE
                    # Add some flavor when viewing contracts, random and affected by hub type
                    CONTRACT_FLAVOR = {
                        "slum": [
                            "A fixer in a patched jacket waves you over. 'Got work, if you ain't picky.'",
                            "A battered terminal flickers: 'Jobs posted. No questions asked.'",
                            "A tired voice mutters: 'Take it or leave it. Someone else will.'"
                        ],
                        "corp": [
                            "A sleek kiosk displays: 'Opportunities for ambitious contractors.'",
                            "A corporate agent smiles: 'All contracts are fully insured and monitored.'",
                            "A digital assistant chirps: 'Your performance will be evaluated.'"
                        ],
                        "cartel": [
                            "A shadowy figure leans in: 'Only the bold get paid around here.'",
                            "A gruff voice: 'Don't screw this up. The boss is watching.'",
                            "A coded message blinks: 'No cops. No witnesses.'"
                        ],
                        "ghost": [
                            "A cold terminal hums: 'Jobs available. Payment... uncertain.'",
                            "You hear static as the contract list loads. No one else is around.",
                            "A chill runs down your spine as you scan the contracts."
                        ],
                        "blacksite": [
                            "A uniformed officer hands you a sealed dossier. 'You never saw me.'",
                            "A secure console: 'Clearance required. All actions are logged.'",
                            "A terse message: 'Failure is not tolerated.'"
                        ]
                    }
                    if hub_type in CONTRACT_FLAVOR:
                        print(f"\n{random.choice(CONTRACT_FLAVOR[hub_type])}")
                    else:
                        print("\nA bored clerk slides a contract list across the counter.")
                    wait_for_enter()
                    game.current_hub.display_contracts()
                    try:
                        contract_choice = int(input("\nSelect contract (1-3) or 0 to cancel: "))
                        if 1 <= contract_choice <= 3:
                            contract = game.current_hub.available_contracts[contract_choice - 1]
                            if contract.accept(game):
                                print(f"\nContract accepted. {get_random_cargo_quote()}")
                                wait_for_enter()
                    except ValueError:
                        print("Invalid choice")
            elif choice == 2:
                max_possible = min(
                    game.ship.max_fuel - game.ship.fuel,  # Space left in tank
                    game.player.credits // game.current_hub.fuel_price  # What you can afford
                )
                if hub_type in FUEL_FLAVOR:
                    print(f"\n{FUEL_FLAVOR[hub_type]}")
                    #wait_for_enter()
                if max_possible <= 0:
                    if game.ship.fuel >= game.ship.max_fuel:
                        print("Your fuel tank is already full. The attendant shrugs and moves on.")
                    else:
                        print("You can't afford any fuel. Maybe try your luck in the alleys.")
                    wait_for_enter()
                    continue
                
                print(f"\nYou can buy up to {max_possible} units of fuel.")
                print(f"Current price per unit: {game.current_hub.fuel_price} credits")
                print(f"Your credits: {game.player.credits:,}")
                
                try:
                    amount = int(input(f"\nHow many units would you like to buy (0-{max_possible})? "))
                    if 0 <= amount <= max_possible:
                        cost = amount * game.current_hub.fuel_price
                        if game.current_hub.refuel_ship(game.player, game.ship, amount):
                            print(f"\nThe fuel pumps whir to life...")
                            print(f"Added {amount} units of fuel for {cost} credits")
                            print(f"Credits remaining: {game.player.credits:,}")
                            wait_for_enter()
                    else:
                        print("Invalid amount!")
                        wait_for_enter()
                except ValueError:
                    print("Invalid input!")
                    wait_for_enter()
            elif choice == 3:
                # Visit equipment shop
                print("\nYou enter the Trade Hub's licensed equipment shop...")
                #wait_for_enter()
                shop.shop_menu(game, hub_type)
            elif choice == 4:
                # Ship upgrades
                handle_ship_upgrades(game)
            elif choice == 0:
                print("\nYou leave the Trade Hub...")
                # INSERT_YOUR_CODE
                print("\nYou head back to your ship, engines roaring as you leave the trade hub and its secrets behind.")
                wait_for_enter()
                if game.ship.fuel < 2:
                    print("\nWarning: Low fuel! The void doesn't forgive mistakes.")
                    wait_for_enter()
                return
        except ValueError:
            print("Invalid choice")
            wait_for_enter()

def handle_ship_upgrades(game):
    """Handle ship upgrade menu and purchases"""
    ship = game.ship
    player = game.player
    
    while True:
        # Calculate upgrade costs with steeper exponential increase
        # Base costs are higher and multiplier is 3x instead of 2x
        speed_cost = 3000 * (3 ** (ship.speed - 1))  # Base 3000, triples each level
        cargo_cost = 5000 * (3 ** (ship.max_cargo - 3))  # Base 5000, triples each level
        fuel_cost = 3000 * (3 ** (ship.max_fuel // 5 - 1))  # Base 4000, triples each level
        
        print("\n=== SHIP UPGRADES ===")
        print(f"Your Credits: {player.credits:,}")
        print("\nCurrent Ship Stats:")
        print(f"Speed: {ship.speed}")
        print(f"Cargo Hold: {ship.max_cargo} slots")
        print(f"Fuel Tank: {ship.max_fuel} units")
        print("\nAvailable Upgrades:")
        
        # Show available upgrades based on current levels
        if ship.speed < 5:
            print(f"1. Increase Speed ({ship.speed} → {ship.speed + 1}) - {speed_cost:,} credits")
        else:
            print("1. Speed (MAX)")
            
        if ship.max_cargo < 5:
            print(f"2. Expand Cargo Hold ({ship.max_cargo} → {ship.max_cargo + 1} slots) - {cargo_cost:,} credits")
        else:
            print("2. Cargo Hold (MAX)")
            
        if ship.max_fuel < 20:
            print(f"3. Upgrade Fuel Tank ({ship.max_fuel} → {ship.max_fuel + 5} units) - {fuel_cost:,} credits")
        else:
            print("3. Fuel Tank (MAX)")
            
        print("\n0. Back")
        
        try:
            choice = int(input("\nSelect upgrade (0-3): "))
            
            if choice == 0:

                print("\nYou go back the Trade Hub...")
                wait_for_enter()
                return
                
            if choice == 1 and ship.speed < 5:
                if player.credits >= speed_cost:
                    player.credits -= speed_cost
                    ship.speed += 1
                    print(f"\nSpeed upgraded to {ship.speed}!")
                    wait_for_enter()
                else:
                    print("\nNot enough credits!")
                    wait_for_enter()
                    
            elif choice == 2 and ship.max_cargo < 5:
                if player.credits >= cargo_cost:
                    player.credits -= cargo_cost
                    ship.max_cargo += 1
                    print(f"\nCargo hold expanded to {ship.max_cargo} slots!")
                    print("\nYou'll need to visit another trade hub to get contracts for your expanded cargo capacity.")
                    wait_for_enter()
                else:
                    print("\nNot enough credits!")
                    wait_for_enter()
                    
            elif choice == 3 and ship.max_fuel < 20:
                if player.credits >= fuel_cost:
                    player.credits -= fuel_cost
                    ship.max_fuel += 5
                    ship.fuel = min(ship.fuel, ship.max_fuel)  # Adjust current fuel if needed
                    print(f"\nFuel tank upgraded to {ship.max_fuel} units!")
                    wait_for_enter()
                else:
                    print("\nNot enough credits!")
                    wait_for_enter()
                    
        except ValueError:
            print("\nInvalid choice.")
            wait_for_enter() 