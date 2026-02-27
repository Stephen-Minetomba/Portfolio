INVULNERABLE = "invulnerable"
SHIELDS = "shields"
troop_types = {
    "knight": {
        "power": 35,
        "health": 90, # Soldier HP (40) + Horse HP (50) = 90
        "range": 2,
        "speed": 6,
        "delay": 1.2,
        "cost": 250, # Larger cost than soldiers because of horses (with armor) + soldiers
        "texture": "K",
        "description": "A heavily armored cavalry unit wielding a lance."
    },
    "archer": {
        "power": 20,
        "health": 30,
        "range": 3,
        "speed": 3,
        "delay": 0.7,
        "cost": 90,
        "texture": "A",
        "description": "A ranged unit that fires arrows from a distance."
    },
    "soldier": {
        "power": 15,
        "health": 40,
        "range": 1,
        "speed": 1.5, # 2x Slower than archers because they have 2x more gear/health
        "delay": 0.4, # Faster than archers because they don't need to reload.
        "cost": 100, # Larger cost than archers because of armor + sword.
        "texture": "S",
        "description": "A heavily armored soldier fighting with a sword."
    },
    "tank": {
        "power": 150,
        "health": 300,
        "range": 4,
        "speed": 0.8,
        "delay": 10.0,
        "cost": 500,
        "texture": "T",
        "description": "A colossal tank unit that deals massive damage but moves slowly and attacks once in a while."
    },
    "shield": { # Special troop
        "power": 0,
        "health": INVULNERABLE, # The invulnerable attribute makes this troop (technically an object) not take any damage
        "range": 0,
        "speed": 0,
        "delay": 0.0,
        "cost": 400,
        "texture": "H", # Second letter in "sHield"
        "description": "A powerful static shield able to resist any hit from any troop (except archers, since they basically shoot over the shield) and sniper shot."
    }
}

weapon_types = {
    "air_strike": {
        "power": 800, # (this includes range. The actual damage per troop in the blast range is 200)
        "range": 4, # Compared to the troops, this statistic means the range of the blast (since the range is basically infinite)
        "texture": "R", # From "rockets"
        "cost": 300, # Lower than tanks, but has a high cooldown
        "cooldown": 30.0, # Needs good management (only use this in emergencies or when the enemy is defeating your troops)
        "description": "Launches a powerful air strike to the chosen location.",
        "special_attributes": [] # None
    },
    "snipe": {
        "power": 1000, # One shots anything (except for invulnerable troops)
        "range": 4,
        "texture": "B", # From "bullet"
        "cost": 80, # Pretty low
        "cooldown": 25.0,
        "description": "Snipes an enemy troop with 100% accuracy (not that realistic compared to real life since there are no wind-induced trajectory modifications)",
        "special_attributes": [SHIELDS] # The "SHIELDS" attribute blocks it from shooting at enemies behind shields
    }
}