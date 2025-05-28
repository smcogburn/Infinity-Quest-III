import random

def wait_for_enter():
    input("\n...\n") 
trade_hub_quotes = [
    "The neon signs flicker in the smoky station air...",
    "Shady characters eye your ship from the shadows...",
    "The smell of engine fuel and cheap food fills the air...",
    "Traders haggle loudly at their market stalls...",
    "A patrol of Federation officers walks past, hands on their weapons...",
    
]

travel_quotes = [
    "The void of space stretches endlessly before you...",
    "Your ship's engine hums steadily as you drift through the stars...",
    "You check the radar for any signs of pursuit...",
    "The navigation computer beeps softly in the silence...",
    "Distant nebulae paint beautiful colors across your viewscreen...",
    "Lost in the cosmos, I'm a wanderer without a destination, searching for solace amidst the stars...",
    "You look out into the void of nothing and contemplate why you did this...",
    "You think about your family, you miss them...",
    "You feel lonely in the vast emptiness of space...",
    "You wonder if you could order DoorDash 596,103,405,195 miles into space...", 
    "You wonder if you forgot to feed your pet capybara...",
    "You write some poetry even though you hated English class...",
    "Your partner called. They don't miss you...",
    "You think about how much it feels like a snowglobe in here...",
    "You wonder if Tay-K is out of jail yet...",
]

cargo_loading_quotes = [
    "The loading crew efficiently stacks the supply crates...",
    "Standard shipping containers are loaded according to protocol...",
    "Everything appears to be properly labeled and documented...",
    "The loading proceeds smoothly without any complications...",
    "The dock workers load the cargo onto the ship...",
    "Masked dock workers quietly load the unmarked crates...",
    "The client insists the humming sound from the crates is 'completely normal'...",
    "You notice the crates have warning labels in languages you've never seen...",
    "The manifest just says 'agricultural supplies', but the crates are oddly warm...",
    "A dock worker whispers 'whatever you do, don't shake them'...",
    "The client seems suspiciously eager to get these 'spare parts' moving...",
    "You swear you heard something move inside one of the crates...",
    "The docking bay mysteriously clears out during the loading process...",
    "The crates are surprisingly light for their size...",
    "Your ship's sensors can't seem to get a reading on the contents..."
]

def get_random_trade_quote():
    from random import choice
    return choice(trade_hub_quotes)

def get_random_travel_quote():
    from random import choice
    return choice(travel_quotes)

def get_random_cargo_quote():

    from random import choice
    return choice(cargo_loading_quotes) 

def generate_trade_hub_name():
    suffixes = [
    "", "", "","", "", "","", "", "", f" {random.randint(1, 9)}", " B", " C", " Prime", "-VX", " Omega", f"-{random.randint(1, 99)}", "-Node", " Minor"
    ]
    nouns = [
    "Point", "Spindle", "Haven", "Sector", "Cradle", "Array", "Hold", "Node", "Loop", "Core", "Rim"
    ]
    prefixes = [
        "Red", "Iron", "Dust", "Nova", "Sable", "Drift", "Echo", "Tau", "Dead", "Hollow", "Sky", "Outer"
    ]
    hub_type = random.choice(["slum", "corp", "cartel", "ghost", "blacksite"])

    # These are structured dictionaries for use with your randomized Trade Hub flavor system.
    # Each category is a dict with hub type keys and a list of flavor strings.

    hub_visual = {
        "slum": [
            "Cracked plating and exposed wiring mark the edges of every bulkhead.",
            "Flimsy scaffolds stretch like spiderwebs between cargo pods."
        ],
        "corp": [
            "Everything gleams. Even the floor is polished to reflect your doubts.",
            "Holographic ads pulse across every surface."
        ],
        "cartel": [
            "Painted insignias mark every surface—warning or invitation, hard to tell.",
            "Armed drones hover near every access tunnel."
        ],
        "ghost": [
            "The lights flicker without pattern. Or purpose.",
            "A mural peels off the wall, revealing bulkhead damage beneath."
        ],
        "blacksite": [
            "Everything is matte-black, armored, and over-engineered.",
            "Cargo lifts the size of buildings move without warning or sound."
        ]
    }

    hub_sound = {
        "slum": [
            "Loud music leaks from somewhere. Or maybe it's just shouting.",
            "Vendors yell in at least four languages, none of them polite."
        ],
        "corp": [
            "A soothing corporate jingle repeats on a loop. You've already tuned it out.",
            "Polite voices offer vague security warnings every thirty seconds."
        ],
        "cartel": [
            "Orders barked through encrypted comms echo across the loading docks.",
            "The buzz of silent compliance is almost deafening."
        ],
        "ghost": [
            "Nothing. No voices. Just the distant groan of pressure systems.",
            "An old alert tone pings once, then never again."
        ],
        "blacksite": [
            "You hear nothing. That's by design.",
            "Industrial servos grind somewhere behind the walls."
        ]
    }

    hub_npc = {
        "slum": [
            "A child in a patchwork uniform sells knockoff sneakers out of a crate.",
            "A group of off-duty mercenaries play cards using ration tokens."
        ],
        "corp": [
            "Security staff nod at you like you're on camera (you are).",
            "A man in a perfectly fitted uniform offers you a loyalty card."
        ],
        "cartel": [
            "Everyone walks like they know they're being watched.",
            "A heavily armored guard checks a crate, then nods without smiling."
        ],
        "ghost": [
            "A lone technician stares at a terminal long past saving.",
            "You don't see anyone. That might be worse than seeing someone."
        ],
        "blacksite": [
            "No one talks. Everyone scans.",
            "A man with half a faceplate gestures you into a decontamination chamber."
        ]
    }

    hub_mood = {
        "slum": [
            "No one's in charge. Everyone's just surviving.",
            "This place works, but only because it has to."
        ],
        "corp": [
            "Looks clean. Feels wrong.",
            "Underneath the shine, something's rotting."
        ],
        "cartel": [
            "Disobedience isn't punished. It's erased.",
            "Authority here doesn't explain itself. It doesn't have to."
        ],
        "ghost": [
            "The lights flicker with a ghostly pattern.",
            "Something bad happened here, or is about to."
        ],
        "blacksite": [
            "This isn't a station. It's an installation.",
            "If you're not supposed to be here, you won't be for long."
        ]
    }

    hub_nova = {
        "slum": [
            "[NOVA] 'Docking complete. Keep one hand on your credits—and the other on your sidearm.'",
            "[NOVA] 'The only thing cheaper than the fuel is your life expectancy.'"
        ],
        "corp": [
            "[NOVA] 'Smile. They log emotional compliance here.'",
            "[NOVA] 'This place is 100% safe. Legally speaking.'",
        ],
        "cartel": [
            "[NOVA] 'They know what's in your cargo hold. The real question is whether they care.'",
            "[NOVA] 'Act like you belong. Or don't. Your call.'",
        ],
        "ghost": [
            "[NOVA] 'We dock, we refuel, we leave. No ghost stories.'",
            "[NOVA] 'Even I'm uncomfortable. And I'm code.'",
        ],
        "blacksite": [
            "[NOVA] 'I'd ask who built this place, but I'd rather not know.'",
            "[NOVA] 'No turning back now. Let's get what we need before the lights turn red.'",
        ]
    }

    hub_landing = {
        "slum": [
            "Your ship rattles as it settles onto a landing pad patched with scrap metal.",
            "You land between two ships that look like they might fall apart before takeoff."
        ],
        "corp": [
            "Automated docking clamps hiss as your ship is guided into a pristine bay.",
            "A synthetic voice welcomes you to the corporate port as your ship glides to a perfect stop."
        ],
        "cartel": [
            "Armed figures watch from the shadows as your ship touches down.",
            "Your landing is met with suspicious stares and the glint of concealed weapons."
        ],
        "ghost": [
            "Your ship's landing gear echoes in the empty, dust-choked hangar.",
            "No one greets you as you land, just the hum of old machinery."
        ],
        "blacksite": [
            "Your ship is swallowed by a military-grade hangar that seals shut behind you.",
            "You land in silence, surrounded by unmarked ships and heavy security."
        ]
    }
    
    print(random.choice(hub_landing[hub_type]))
    
    # INSERT_YOUR_CODE
    # Map hub_type to a list of evocative hub descriptors, pick one at random for display
    hub_type_descriptors = {
        "slum": [
            "Freeport", "Salvage Hub", "Fringe Outpost", "Scrap Market", "Rustbelt Exchange"
        ],
        "corp": [
            "Executive Hub", "Corporate Nexus", "Syndicate Terminal", "Platinum Exchange", "Shareholder Port"
        ],
        "cartel": [
            "Smuggler's Hub", "Shadow Market", "Contraband Port", "Black Channel", "Red Market"
        ],
        "ghost": [
            "Phantom Hub", "Echo Outpost", "Wraith Terminal", "Silent Anchorage", "Lost Dock"
        ],
        "blacksite": [
            "Obsidian Station", "Cipher Station", "Deadeye's End", "Abyssal Exchange", "Blacksite Terminal"
        ]
    }
    hub_descriptor = random.choice(hub_type_descriptors.get(hub_type, [hub_type.capitalize() + " Hub"]))

    hub_name = f"{hub_descriptor} on {random.choice(prefixes)} {random.choice(nouns)}{random.choice(suffixes)}"
    print(f"You've arrived at the {hub_name}...")
    wait_for_enter()

    # INSERT_YOUR_CODE
    if random.random() < 0.5:
        print(random.choice(hub_visual[hub_type]))
    if random.random() < 0.5:
        print(random.choice(hub_sound[hub_type]))
    if random.random() < 0.5:  
        print(random.choice(hub_npc[hub_type]))
    if random.random() < 0.5:
        print(random.choice(hub_mood[hub_type]))
        
    if random.random() < 0.75:
        wait_for_enter()
        print(random.choice(hub_nova[hub_type]))
        
    
    return hub_name, hub_type

def get_random_nova_quote(self):

        if random.random() < 1:
            # INSERT_YOUR_CODE
            # 1/3 chance to say something (already checked)
            # Now, choose which pool to draw from: high heat, low health, or generic
            nova_lines = []
            # Define the pools
            high_heat_lines = [
                f"'Great, your heat is {self.player.heat}. Congratulations, you're now the star of every police briefing in the galaxy.'",
                f"'Your heat is off the charts - I'd suggest a disguise, but I don't think a fake mustache fools orbital satellites.'",
                f"'You know your heat is {self.player.heat}, right? Most people try to avoid being on every watchlist at once, {self.player.name}.'",
                "'If we get pulled over, I'm blaming everything on you. Just so we're clear.'",
                "'Should I start prepping our story for if we get stopped, or just the escape pod?'",
                f"'You're trending on the bounty hunter forums with that {self.player.heat} heat. Not in a good way.'",
                f"'Your heat is {self.player.heat}. If you wanted attention, you could've just posted a dance video.'",
                f"'I hope you like sirens, because I hear a lot of them in our future. Heat is {self.player.heat}.'",
                f"'{self.player.heat}? That much heat? Should I just send our coordinates to the bounty board now?'",
            ]
            low_health_lines = [
                "'Vitals are... bad. Very bad. I've seen corpses with better posture.'",
                "'You're leaking blood, sarcasm, and bad ideas. Two of those are fixable.'",
                "'You need a medkit. Or a miracle. Medkit's more likely.'",
                "'You better lock in before I have to scrape your ass off the floor.'"
            ]
            low_fuel_lines = [
                f"'Fuel reserves critical. Maybe try flapping your arms? Fuel is {self.ship.fuel}.'",
                f"'Your fuel is {self.ship.fuel}. I hope you have a plan, {self.player.name}, because I don't.'",
                f"'Your fuel is {self.ship.fuel}. Do you know how to siphon fuel from a parked freighter? Because I don't.'",
            ]
            illegal_cargo_lines = [
                "'You know, we could *try* hauling something legal. Just once. For variety.'",
                "'That crate's moving again. Either it's alive, or we're screwed.'",
                "'If they search this ship, we're both going to jail. Or dead.'",
            ]
            high_money_lines = [
                "'Almost a millionaire. Maybe buy armor that doesn't smell like regret?'",
                "'You're rich. Temporarily. Let's ruin it with one bad decision - I can set your navigation for the closest casino.'",
            ]
            low_money_lines = [
                f"'Getting close to zero credits, {self.player.name}. Are you trying to hit a new low today?'",
                f"'Even your debts have given up on you. {self.player.name}. Go make some money.'",
                f"'Only {self.player.credits} credits? Great news: we officially qualify as galactic trash, {self.player.name}. Do something.'",
                f"Down to {self.player.credits} credits? You're lucky I don't get paid for this, {self.player.name}."
            ]
            deadline_lines = [
                "'One day left. You do remember where the delivery point is, right?'",
                "'Deadline's tomorrow. I'd suggest not dying until then.'",
                "'Clock's ticking. Try arriving before the cartel turns youinto the next news headline'",
            ]

            teasing_lines = [
                "'How many of today's problems are carryovers from yesterday? Be honest.'",
                "'Reminder: if you crash the ship, I get the escape pod. You don't.'",
                "'You realize I log all your bad decisions, right? For science.'",
                "'Oh, you woke up alive. Wasn't expecting that.'",
                "'Starting a new day with optimism? That's not up to regulation.'",
                f"'Don't worry, {self.player.name}. Your streak of near-death idiocy is still intact.'"
            ]

            # Decide which pool(s) are available
            pools = []
            if self.player.heat > 70:
                pools.append('high_heat')
            if self.player.hp < 30:
                pools.append('low_health')
            if self.ship.fuel < 2:
                pools.append('low_fuel')
            if self.player.current_contract:
                if self.player.current_contract.is_illegal():
                    pools.append('illegal_cargo')
            if self.player.credits > 100000:
                pools.append('high_money')
            if self.player.credits < 500:
                pools.append('low_money')
            if self.player.current_contract and self.player.current_contract.deadline == 1:
                pools.append('deadline')
            pools.append('teasing')  # Always available

            # Pick which pool to use: if multiple, randomly choose; teasing always included
            chosen_pool = random.choice(pools)

            if chosen_pool == 'high_heat':
                nova_lines = high_heat_lines
            elif chosen_pool == 'low_health':
                nova_lines = low_health_lines
            else:
                nova_lines = teasing_lines

            line = f"[NOVA] {random.choice(nova_lines)}"
        
            return line