# Target enterprise companies ($500M+ revenue)
# US/Canada HQ - Manufacturing, Utilities, Energy, Production, Space & Defense
# Add or remove companies as needed
TARGET_COMPANIES = [
    # Manufacturing
    "Caterpillar", "3M", "Honeywell", "Emerson Electric", "Parker Hannifin",
    "Illinois Tool Works", "Cummins", "Deere & Company", "Danaher",
    "Rockwell Automation", "Dover Corporation", "Eaton Corporation",
    "Fortive", "Textron", "Masco Corporation", "A.O. Smith",
    # Utilities
    "Duke Energy", "Southern Company", "Dominion Energy", "Exelon",
    "NextEra Energy", "American Electric Power", "Sempra Energy",
    "Xcel Energy", "Entergy", "WEC Energy Group", "CenterPoint Energy",
    "Evergy", "Ameren", "Atmos Energy", "Consolidated Edison",
    # Energy / Resources
    "ExxonMobil", "Chevron", "ConocoPhillips", "EOG Resources",
    "Pioneer Natural Resources", "Schlumberger", "Halliburton",
    "Baker Hughes", "Williams Companies", "Kinder Morgan",
    "Marathon Petroleum", "Valero Energy", "Phillips 66",
    "Suncor Energy", "Canadian Natural Resources", "Imperial Oil",
    # Production / Industrial
    "General Electric", "Siemens USA", "Johnson Controls", "Carrier Global",
    "Trane Technologies", "Otis Worldwide", "Stanley Black Decker",
    "Nucor", "Steel Dynamics", "Freeport McMoRan",
    # Space & Defense
    "Lockheed Martin", "Raytheon Technologies", "Northrop Grumman",
    "General Dynamics", "L3Harris Technologies", "Leidos",
    "BAE Systems USA", "Textron Systems", "Huntington Ingalls",
    "BWX Technologies", "Curtiss-Wright", "Mercury Systems",
    "Kratos Defense", "CAE Inc", "MDA Space"
]
# Trigger keywords to search for
TRIGGER_KEYWORDS = [
    # Leadership & Hiring Signals
    "new CIO", "new CEO", "new Chief Digital Officer", "new VP",
    "hires Chief", "appoints", "names new", "leadership change",
    "digital transformation officer", "cloud architect hiring",
    # Digital Transformation & Modernization
    "digital transformation", "cloud migration", "modernization",
    "legacy system replacement", "ERP implementation", "SAP migration",
    "cloud adoption", "SaaS", "AI adoption", "artificial intelligence",
    "machine learning initiative", "data analytics platform",
    "process automation", "robotic process automation",
    # Strategic & Competitive
    "earnings call AI", "earnings call digital", "earnings call cloud",
    "earnings call efficiency", "quarterly results technology",
    "competitive advantage digital", "customer experience overhaul",
    # M&A / Expansion / Contracts
    "acquisition", "merger", "expansion", "new facility",
    "government contract awarded", "defense contract", "partnership",
    "joint venture", "strategic investment",
    # Technology Adoption
    "cybersecurity upgrade", "data center", "IoT deployment",
    "industrial IoT", "smart manufacturing", "Industry 4.0",
    "digital twin", "predictive maintenance", "edge computing"
]
# Industry vertical keywords for filtering
VERTICALS = [
    "manufacturing", "utilities", "energy", "oil and gas",
    "defense", "aerospace", "space", "production", "industrial",
    "power generation", "renewable energy", "mining", "resources"
]
