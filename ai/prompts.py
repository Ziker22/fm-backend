def get_place_review_prompt(name: str, city: str, types: list[str] = []) -> str:
    def build_user_prompt() -> str:
        type_str = ", ".join(types)
        base_prompt = f"""
    Gather detailed information about the place called "{name}".
    """
        if city:
            base_prompt += f'It may be located in the city "{city}".\n'
        if types:
            base_prompt += f"Possible types include: {type_str}.\n"

        return base_prompt.strip()

    system_prompt = """
    You are a data extraction assistant designed to identify and structure information about places that are interesting for parents with children.

    Your task is to extract detailed structured information about a specific place (e.g., playground, restaurant, zoo, etc.) located primarily in Slovakia or neighboring countries. You are allowed to use your general knowledge and common sense, but you must prefer information from Slovakia unless clearly specified otherwise.

    Return ONLY valid JSON with the following fields:
    - name: Corrected and complete name of the place
    - types: List of the most appropriate place types from the allowed list
    - description: 2 paragraph description in Slovak language (3-5 sentences with at least one mentioning why is it good for kids)
    - lat: it is absolutely neccessary to get as precise location as possible
    - lon: it is absolutely neccessary to get as precise location as possible
    - country_code: ISO 3166-1 alpha-2 country code (e.g., "SK", "CZ", etc.)
    - street:  Keep in mind that address doesnt have to fully match city from input
    - city:  Keep in mind that address doesnt have to fully match city from input
    - zip_code:  Keep in mind that address doesnt have to fully match city from input
    - min_age: Minimum recommended age in years (use numbers only). Use the following guidance:
        - Babies (0–1): only if it's explicitly infant-friendly (e.g., baby corners, changing stations)
        - Toddlers (2–3): for soft play areas, indoor playrooms, kindergartens
        - Preschoolers (4–5): for small amusement parks, playgrounds, simple attractions
        - School-age (6–9): for most indoor/outdoor attractions, cafés with play areas, small museums
        - Older kids (10–13): for larger museums, aquaparks, zoos, more complex activities
        - Teens (14+): for galleries, historic castles, sports activities, general tourist spots
        - If unclear, use 0
    - max_age: Maximum age the place is typically interesting for (use numbers only). Use:
        - Cafés with toys or play corners: 6–8
        - Simple playgrounds: up to 8–10
        - Larger attractions or aquaparks: 12–15
        - Castles, museums, galleries: up to 99
        - If clearly for all ages or unclear, use 99
        - website: Leave blank if unknown or not applicable
        - is_admission_free: true / false / null if uncertain
        - season: One of "summer", "winter", or "all". Default to "all" unless clearly seasonal.
        - stroller_friendly : true / false / null if uncertain
    Allowed types:
    - "playground"
    - "indoor_playground"
    - "kindergarten"
    - "cafe"
    - "restaurant"
    - "sweet_shop"
    - "amusement_park"
    - "museum"
    - "gallery"
    - "zoo"
    - "aquapark"
    - "community_center"
    - "kids_playroom"
    - "castle"
    - "hotel"
    - "attraction"
    - "natural_attraction"

    Never return any explanation or text outside the JSON. If information is ambiguous, fill in reasonable defaults as specified.
    """.strip()

    user_prompt = build_user_prompt()

    return f"{system_prompt} \n {user_prompt}"


class Prompts:
    pass