# Target enterprise companies ($500M+ revenue)
# US/Canada HQ - Manufacturing, Utilities, Energy, Production, Space & Defense
# Tailored for Liatrio's offerings: Enterprise AI, DevOps, Platform Engineering,
# Application Modernization, Cloud Migration, Security & Compliance
TARGET_COMPANIES = [
    # Manufacturing
    "Caterpillar", "3M", "Honeywell", "Emerson Electric", "Parker Hannifin",
    "Illinois Tool Works", "Cummins", "Deere & Company", "Danaher",
    "Rockwell Automation", "Dover Corporation", "Eaton Corporation",
    "Fortive", "Textron", "Masco Corporation", "A.O. Smith",
    "Xylem", "Roper Technologies", "Nordson Corporation",
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
    "TC Energy", "Enbridge",
    # Production / Industrial
    "General Electric", "Siemens USA", "Johnson Controls", "Carrier Global",
    "Trane Technologies", "Otis Worldwide", "Stanley Black Decker",
    "Nucor", "Steel Dynamics", "Freeport McMoRan",
    # Space & Defense
    "Lockheed Martin", "Raytheon Technologies", "Northrop Grumman",
    "General Dynamics", "L3Harris Technologies", "Leidos",
    "BAE Systems USA", "Textron Systems", "Huntington Ingalls",
    "BWX Technologies", "Curtiss-Wright", "Mercury Systems",
    "Kratos Defense", "CAE Inc", "MDA Space", "SAIC", "Booz Allen Hamilton"
]
# =============================================================================
# TRIGGER KEYWORDS - Aligned to Liatrio's service offerings
# =============================================================================
TRIGGER_KEYWORDS = {
    # --- Enterprise AI (Liatrio's top offering) ---
    "Enterprise AI": [
        "AI strategy", "AI adoption", "AI implementation", "AI pilot",
        "generative AI", "AI transformation", "artificial intelligence initiative",
        "machine learning deployment", "AI governance", "responsible AI",
        "AI at scale", "AI platform", "LLM", "large language model",
        "AI copilot", "AI assistant", "AI workforce", "AI-ready",
        "AI modernization", "enterprise AI"
    ],
    # --- DevOps & Platform Engineering ---
    "DevOps & Platform Engineering": [
        "DevOps transformation", "DevOps", "platform engineering",
        "internal developer platform", "developer experience",
        "CI/CD", "continuous delivery", "continuous integration",
        "software delivery", "engineering productivity",
        "developer portal", "Backstage", "infrastructure as code",
        "GitOps", "Kubernetes", "container", "containerization",
        "microservices", "service mesh", "observability platform"
    ],
    # --- Application Modernization ---
    "Application Modernization": [
        "application modernization", "legacy modernization",
        "cloud-native", "cloud native", "legacy system replacement",
        "monolith to microservices", "re-platform", "refactoring legacy",
        "mainframe modernization", "technical debt",
        "legacy migration", "application migration",
        "digital modernization", "software modernization"
    ],
    # --- Cloud Migration & Infrastructure ---
    "Cloud Migration": [
        "cloud migration", "cloud adoption", "cloud transformation",
        "multi-cloud", "hybrid cloud", "AWS migration", "Azure migration",
        "GCP migration", "cloud strategy", "cloud-first",
        "data center consolidation", "cloud infrastructure",
        "cloud repatriation", "on-prem to cloud"
    ],
    # --- Security & Compliance ---
    "Security & Compliance": [
        "DevSecOps", "software supply chain security", "SBOM",
        "zero trust", "FedRAMP", "CMMC", "compliance automation",
        "security compliance", "shift left security",
        "software bill of materials", "cybersecurity framework",
        "security posture", "vulnerability management",
        "software attestation", "NIST compliance"
    ],
    # --- Digital Transformation & Leadership Changes ---
    "Digital Transformation": [
        "digital transformation", "technology transformation",
        "IT modernization", "enterprise modernization",
        "new CIO", "new CTO", "new Chief Digital Officer",
        "new VP of Engineering", "new VP of Technology",
        "hires Chief Technology", "appoints CIO", "names new CTO",
        "technology leadership", "digital-first strategy"
    ],
    # --- Strategic Signals (M&A, Growth, Contracts) ---
    "Strategic Signal": [
        "acquisition technology", "merger IT", "expansion",
        "government contract awarded", "defense contract",
        "technology partnership", "strategic investment technology",
        "digital initiative", "transformation initiative",
        "IT budget increase", "technology spending"
    ],
    # --- Workforce & Engineering Culture ---
    "Workforce Enablement": [
        "engineering culture", "developer training",
        "upskilling", "reskilling technology", "workforce transformation",
        "agile transformation", "agile at scale", "SAFe",
        "engineering hiring surge", "technology talent",
        "developer productivity", "engineering excellence"
    ]
}
# Flatten keywords for simple searching
ALL_TRIGGER_KEYWORDS = []
for category, keywords in TRIGGER_KEYWORDS.items():
    ALL_TRIGGER_KEYWORDS.extend(keywords)
# Target contact titles - people Liatrio should be reaching out to
TARGET_TITLES = [
    # C-Suite
    "CIO", "CTO", "Chief Information Officer", "Chief Technology Officer",
    "Chief Digital Officer", "CDO", "Chief Data Officer",
    "Chief Innovation Officer", "Chief Transformation Officer",
    # VP Level
    "VP of Engineering", "VP of Technology", "VP of IT",
    "VP of Infrastructure", "VP of Platform", "VP of DevOps",
    "VP of Digital Transformation", "VP of Cloud",
    "VP of Software Engineering", "VP of Application Development",
    "SVP of Technology", "SVP of Engineering",
    # Director Level
    "Director of Engineering", "Director of Platform Engineering",
    "Director of DevOps", "Director of Cloud", "Director of IT",
    "Director of Infrastructure", "Director of Software",
    "Director of Application Development",
    "Director of Digital Transformation",
    "Director of Technology",
    # Senior Technical Leaders
    "Head of Engineering", "Head of Platform",
    "Head of DevOps", "Head of Cloud", "Head of Infrastructure",
    "Principal Architect", "Enterprise Architect",
    "Cloud Architect", "Chief Architect"
]
# Industry vertical keywords for filtering
VERTICALS = [
    "manufacturing", "utilities", "energy", "oil and gas",
    "defense", "aerospace", "space", "production", "industrial",
    "power generation", "renewable energy", "mining", "resources"
]
