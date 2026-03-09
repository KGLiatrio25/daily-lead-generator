import feedparser
import datetime
import csv
import os
import json
from target_companies import TARGET_COMPANIES, TRIGGER_KEYWORDS, VERTICALS
def search_google_news(query, num_results=10):
    """Search Google News RSS feed for a query."""
    encoded_query = query.replace(" ", "+")
    url = f"https://news.google.com/rss/search?q={encoded_query}&hl=en-US&gl=US&ceid=US:en"
    feed = feedparser.parse(url)
    results = []
    for entry in feed.entries[:num_results]:
        results.append({
            "title": entry.get("title", ""),
            "link": entry.get("link", ""),
            "published": entry.get("published", ""),
            "source": entry.get("source", {}).get("title", "Unknown")
        })
    return results
def score_article(title, company):
    """Score an article based on how many trigger keywords it matches."""
    title_lower = title.lower()
    score = 0
    matched_triggers = []
    for keyword in TRIGGER_KEYWORDS:
        if keyword.lower() in title_lower:
            score += 1
            matched_triggers.append(keyword)
    # Bonus if vertical keyword is also present
    for vertical in VERTICALS:
        if vertical.lower() in title_lower:
            score += 0.5
            break
    return score, matched_triggers
def categorize_trigger(triggers):
    """Categorize the trigger type based on matched keywords."""
    if not triggers:
        return "General News"
    leadership = ["new CIO", "new CEO", "new Chief Digital Officer", "new VP", 
                   "hires Chief", "appoints", "names new", "leadership change"]
    digital = ["digital transformation", "cloud migration", "modernization",
               "legacy system replacement", "ERP implementation", "cloud adoption",
               "SaaS", "AI adoption", "artificial intelligence", "process automation"]
    strategic = ["earnings call", "quarterly results", "competitive advantage",
                 "customer experience"]
    expansion = ["acquisition", "merger", "expansion", "new facility",
                 "government contract", "defense contract", "partnership"]
    tech = ["cybersecurity", "data center", "IoT", "smart manufacturing",
            "Industry 4.0", "digital twin", "predictive maintenance"]
    trigger_lower = " ".join(triggers).lower()
    if any(k.lower() in trigger_lower for k in leadership):
        return "Leadership Change"
    elif any(k.lower() in trigger_lower for k in digital):
        return "Digital Transformation"
    elif any(k.lower() in trigger_lower for k in expansion):
        return "Expansion / M&A / Contract"
    elif any(k.lower() in trigger_lower for k in tech):
        return "Technology Adoption"
    elif any(k.lower() in trigger_lower for k in strategic):
        return "Strategic / Competitive"
    else:
        return "Other Signal"
def run_lead_generator():
    """Main function to generate leads."""
    print(f"Running lead generator at {datetime.datetime.now()}")
    all_leads = []
    seen_titles = set()
    for company in TARGET_COMPANIES:
        print(f"Searching for: {company}")
        # Search for company + key trigger terms
        search_queries = [
            f'"{company}" digital transformation',
            f'"{company}" new CIO OR new CEO OR appoints',
            f'"{company}" cloud migration OR modernization OR AI',
            f'"{company}" acquisition OR expansion OR contract awarded',
            f'"{company}" ERP OR automation OR IoT OR Industry 4.0',
        ]
        for query in search_queries:
            articles = search_google_news(query, num_results=5)
            for article in articles:
                # Skip duplicates
                if article["title"] in seen_titles:
                    continue
                seen_titles.add(article["title"])
                score, triggers = score_article(article["title"], company)
                if score > 0:
                    trigger_type = categorize_trigger(triggers)
                    all_leads.append({
                        "company": company,
                        "trigger_type": trigger_type,
                        "headline": article["title"],
                        "source": article["source"],
                        "url": article["link"],
                        "published": article["published"],
                        "score": score,
                        "matched_keywords": ", ".join(triggers)
                    })
    # Sort by score (highest first)
    all_leads.sort(key=lambda x: x["score"], reverse=True)
    # Save to CSV
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)
    date_str = datetime.datetime.now().strftime("%Y-%m-%d")
    filename = f"{output_dir}/leads_{date_str}.csv"
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "company", "trigger_type", "headline", "source", 
            "url", "published", "score", "matched_keywords"
        ])
        writer.writeheader()
        writer.writerows(all_leads)
    print(f"\\nFound {len(all_leads)} leads. Saved to {filename}")
    # Also save as JSON for potential API use
    json_filename = f"{output_dir}/leads_{date_str}.json"
    with open(json_filename, "w", encoding="utf-8") as f:
        json.dump(all_leads, f, indent=2, ensure_ascii=False)
    # Print summary
    print("\\n--- TOP 20 LEADS ---")
    for i, lead in enumerate(all_leads[:20], 1):
        print(f"{i}. [{lead['trigger_type']}] {lead['company']}: {lead['headline']}")
        print(f"   Score: {lead['score']} | Keywords: {lead['matched_keywords']}")
        print()
    return all_leads
if __name__ == "__main__":
    run_lead_generator()
