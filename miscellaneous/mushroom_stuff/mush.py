species = {
	"Agaricus Campestris": {
		"Cap Color": ["white", "cream", "off-white"],
		"Spore Print": ["dark-brown", "purple-brown", "brown-purple"],
		"Gill Color": ["pink", "light pink", "dark brown", "purple-brown", "brown-purple", "black-brown", "brown-black"],
		"Bruising": "none",
		"Smell": "none",
		"Chemical Test KOH": ["none", "pale yellow"],
		"Edible": True,
		"Habitat": ["grassland", "field", "lawn", "pasture"],
		"Lookalikes": ["Agaricus Xanthodermus (difference: Has a bright yellow KOH test result. Gastrointestinal issues)", "Amanita Virosa (difference: Has a volva, gives off a bright yellow color in the KOH test, has pure white gills. Deadly)", "Amanita Hygroscopica (difference: Has a volva, gives off a bright yellow color in the KOH test, has pink gills. Deadly)", "Agaricus Andrewii (identical except microscopically. Fully edible)", "Agaricus Solidipes (identical except microscopically. Fully edible)"]
	},
	"Agaricus Xanthodermus": {
		"Cap Color": ["white", "cream"],
		"Spore Print": ["dark brown", "purple-brown", "brown-purple"],
		"Gill Color": ["pink", "light pink", "dark brown", "purple-brown", "brown-purple", "black-brown", "brown-black"],
		"Bruising": "turns yellow at base",
		"Smell": "phenol, ink, chemical",
		"Chemical Test KOH": ["bright yellow"],
		"Edible": False,
		"Habitat": ["grassland", "field", "lawn", "pasture"],
		"Lookalikes": ["Agarius Campestris (difference: Does not give a color in a KOH test, or gives a pale yellow)"]
	},
	"Cantharellus Cibarius": {
		"Cap Color": ["yellow", "golden", "orange-yellow"],
		"Spore Print": ["pale yellow", "cream"],
		"Gill Color": ["pale yellow", "yellow", "decurrent"],
		"Bruising": "none or pale brown",
		"Smell": "apricot, fruity",
		"Chemical Test KOH": "none",
		"Edible": True,
		"Habitat": ["mixed forest", "moss", "birch", "pine"],
		"Lookalikes": ["Hygrophoropsis Aurantiaca (false chanterelle, has orange gills, no apricot smell)"]
	},
	"Boletus Edulis": {
		"Cap Color": ["brown", "chestnut", "dark brown", "red-brown"],
		"Spore Print": ["olive-brown", "brown"],
		"Gill Color": ["white", "pale yellow", "olive"],
		"Bruising": ["none", "faint brown"],
		"Smell": "nutty, earthy",
		"Chemical Test KOH": ["dark brown", "black"],
		"Edible": True,
		"Habitat": ["mixed forest", "deciduous", "coniferous"],
		"Lookalikes": ["Tylopilus Felleus (bitter bolete, has pink pores, extremely bitter taste)"]
	}
}

max_score = 14

def identify_fuzzy(cap_color: str, spore_print: str = None, bruising: str = None, smell: str = None, koh_result: str = None, gill_color: str = None, habitat: str = None):
	results = []
	for name, traits in species.items():
		score = 0
		if cap_color in traits.get("Cap Color", []):
			score += 2
		if spore_print in traits.get("Spore Print", []):
			score += 2
		if gill_color in traits.get("Gill Color", []):
			score += 2
		if habitat in traits.get("Habitat"):
			score += 2
		if bruising and bruising == traits.get("Bruising"):
			score += 2
		if smell and smell == traits.get("Smell"):
			score += 2
		if koh_result in traits.get("Chemical Test KOH"):
			score += 2
		confidence = (score / max_score) * 10
		results.append((name, confidence, traits))
	results.sort(key=lambda x: x[1], reverse=True)
	for name, conf, traits in (results[0],):
		print(f"{name}")
		print("")
		print(f"Confidence: {conf:.2f}/10")
		for trait, value in traits.items():
			print(f"{trait}: {value}")
	print("\nThe other top 3:")
	for i in range(min(3, len(results) - 1)):
		print(f"{i + 1}. {results[i + 1][0]} - Confidence {results[i + 1][1]:.2f}")
	return

identify_fuzzy("white", "brown-purple", "none", "none", "none", "brown-black", "field")

# trees > logs > firewood > money