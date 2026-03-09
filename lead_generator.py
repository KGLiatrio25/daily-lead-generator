import feedparser
import datetime
import csv
import os
import json
import urllib.parse
import time
from target_companies import (
    TARGET_COMPANIES, TRIGGER_KEYWORDS,
    VERTICALS
)
def search_google_news(query, num_results=10):
    """Search Google News RSS feed for a query."""
    encoded_query = urllib.parse.quote(query)
    url = f"https://news.google.com/rss/search?q={encoded_query}&hl=en-US&gl=US&ceid=US:en"
    try:
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
    except Exception as e:
        print(f"  Error fetching news: {e}")
        return []
def score_and_categorize(title):
    """Score an article and categorize by Liatrio service area."""
    title_lower = title.lower()
    category_scores = {}
    all_matched = []
    for category, keywords in TRIGGER_KEYWORDS.items():
        matched = []
        for keyword in keywords:
            if keyword.lower() in title_lower:
                matched.append(keyword)
        if matched:
            category_scores[category] = len(matched)
            all_matched.extend(matched)
    if not all_matched:
        return 0, "No Match", []
    score = sum(category_scores.values())
    for vertical in VERTICALS:
        if vertical.lower() in title_lower:
            score += 0.5
            break
    primary_category = max(category_scores, key=category_scores.get)
    return score, primary_category, all_matched
def get_outreach_angle(category):
    """Return a suggested Liatrio outreach angle based on trigger category."""
    angles = {
        "Enterprise AI": "Liatrio helps enterprises move from AI pilots to production-scale AI. Offer an AI Strategy Session.",
        "DevOps & Platform Engineering": "Liatrio builds internal developer platforms that accelerate delivery. Offer a DevOps maturity assessment.",
        "Application Modernization": "Liatrio turns legacy apps into cloud-native, AI-ready software. Offer a modernization roadmap.",
        "Cloud Migration": "Liatrio designs AI-ready cloud platforms. Offer a cloud migration assessment.",
        "Security & Compliance": "Liatrio integrates security into the software delivery pipeline. Offer a DevSecOps assessment.",
        "Digital Transformation": "Liatrio drives holistic transformation across people, process, and technology. Reference the leadership change and offer a strategy session.",
        "Strategic Signal": "Company is investing in technology. Position Liatrio as their transformation partner.",
        "Workforce Enablement": "Liatrio coaches engineering teams to become high-performing. Offer a team enablement workshop.",
    }
    return angles.get(category, "Position Liatrio as enterprise transformation partner.")
def run_lead_generator():
    """Main function — finds trigger events and outputs the TOP 10 companies."""
    print(f"{'='*60}")
    print(f"LIATRIO DAILY LEAD GENERATOR")
    print(f"Running at {datetime.datetime.now()}")
    print(f"{'='*60}\\n")
    all_leads = []
    seen_titles = set()
    for i, company in enumerate(TARGET_COMPANIES, 1):
        print(f"[{i}/{len(TARGET_COMPANIES)}] Searching: {company}")
        search_queries = [
            f'"{company}" AI adoption OR AI strategy OR generative AI OR "AI transformation"',
            f'"{company}" DevOps OR "platform engineering" OR Kubernetes OR "developer experience"',
            f'"{company}" "cloud migration" OR "application modernization" OR "legacy modernization" OR "cloud-native"',
            f'"{company}" DevSecOps OR "software supply chain" OR "zero trust" OR FedRAMP OR CMMC',
            f'"{company}" "new CIO" OR "new CTO" OR "digital transformation" OR "technology transformation"',
            f'"{company}" "technology contract" OR "IT modernization" OR "engineering hiring" OR "developer productivity"',
        ]
        company_leads = []
        for query in search_queries:
            articles = search_google_news(query, num_results=5)
            for article in articles:
                if article["title"] in seen_titles:
                    continue
                seen_titles.add(article["title"])
                score, category, keywords = score_and_categorize(article["title"])
                if score > 0:
                    company_leads.append({
                        "company": company,
                        "liatrio_service_area": category,
                        "headline": article["title"],
                        "source": article["source"],
                        "url": article["link"],
                        "published": article["published"],
                        "relevance_score": score,
                        "matched_keywords": ", ".join(keywords),
                        "outreach_angle": get_outreach_angle(category)
                    })
            time.sleep(0.3)
        # Add all leads for this company
        all_leads.extend(company_leads)
    # =============================================
    # AGGREGATE: Score each COMPANY by total signals
    # =============================================
    company_scores = {}
    company_leads_map = {}
    for lead in all_leads:
        company = lead["company"]
        if company not in company_scores:
            company_scores[company] = 0
            company_leads_map[company] = []
        company_scores[company] += lead["relevance_score"]
        company_leads_map[company].append(lead)
    # Rank companies and take TOP 10
    ranked_companies = sorted(company_scores.items(), key=lambda x: x[1], reverse=True)
    top_10_companies = ranked_companies[:10]
    # Build final output — only top 10 companies
    top_10_leads = []
    for company, total_score in top_10_companies:
        leads = company_leads_map[company]
        # Sort this company's leads by score
        leads.sort(key=lambda x: x["relevance_score"], reverse=True)
        # Add company rank and total score
        for lead in leads:
            lead["company_rank"] = top_10_companies.index((company, total_score)) + 1
            lead["company_total_score"] = total_score
        top_10_leads.extend(leads)
    # =============================================
    # SAVE OUTPUTS
    # =============================================
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)
    date_str = datetime.datetime.now().strftime("%Y-%m-%d")
    # 1. Top 10 Companies CSV (the main output)
    top10_file = f"{output_dir}/top10_companies_{date_str}.csv"
    with open(top10_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "company_rank", "company", "company_total_score",
            "liatrio_service_area", "headline", "source", "url",
            "published", "relevance_score", "matched_keywords",
            "outreach_angle"
        ])
        writer.writeheader()
        writer.writerows(top_10_leads)
    # 2. Claude prompt file — ready to paste into Claude for contact research
    prompt_file = f"{output_dir}/claude_research_prompt_{date_str}.md"
    with open(prompt_file, "w", encoding="utf-8") as f:
        f.write(f"# Liatrio Daily Lead Research — {date_str}\\n\\n")
        f.write("Paste everything below into Claude and ask it to research contacts.\\n\\n")
        f.write("---\\n\\n")
        f.write("I work at Liatrio, an enterprise AI and DevOps transformation consultancy. ")
        f.write("We help large enterprises with: Enterprise AI enablement, DevOps transformation, ")
        f.write("platform engineering, application modernization (cloud-native), cloud migration, ")
        f.write("security & compliance (DevSecOps), and workforce enablement/coaching.\\n\\n")
        f.write("Below are today's top 10 target companies based on trigger events that signal ")
        f.write("they may need Liatrio's services. For EACH company, please:\\n\\n")
        f.write("1. Search LinkedIn and Google for 5-10 contacts at the company who would be the right ")
        f.write("decision-makers or influencers for Liatrio's offerings (CIO, CTO, VP of Engineering, ")
        f.write("Director of Platform Engineering, Director of DevOps, Head of Cloud, Enterprise Architect, etc.)\\n")
        f.write("2. For each contact, provide: Name, Title, LinkedIn URL\\n")
        f.write("3. Write a short personalized outreach message referencing the trigger event\\n\\n")
        f.write("---\\n\\n")
        for company, total_score in top_10_companies:
            leads = company_leads_map[company]
            rank = top_10_companies.index((company, total_score)) + 1
            f.write(f"## #{rank}: {company} (Signal Score: {total_score})\\n\\n")
            f.write(f"**Liatrio Service Fit:** {leads[0]['liatrio_service_area']}\\n")
            f.write(f"**Suggested Angle:** {leads[0]['outreach_angle']}\\n\\n")
            f.write("**Trigger Events:**\\n")
            for lead in leads[:5]:  # Top 5 triggers per company
                f.write(f"- [{lead['liatrio_service_area']}] {lead['headline']}\\n")
                f.write(f"  Source: {lead['source']} | {lead['url']}\\n")
            f.write("\\n---\\n\\n")
    # 3. Full JSON
    json_file = f"{output_dir}/full_report_{date_str}.json"
    report = {
        "generated_at": str(datetime.datetime.now()),
        "top_10_companies": [
            {
                "rank": i+1,
                "company": company,
                "total_score": score,
                "leads": company_leads_map[company]
            }
            for i, (company, score) in enumerate(top_10_companies)
        ]
    }
    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    # =============================================
    # PRINT SUMMARY
    # =============================================
    print(f"\\n{'='*60}")
    print(f"TODAY'S TOP 10 COMPANIES TO TARGET")
    print(f"{'='*60}\\n")
    for rank, (company, total_score) in enumerate(top_10_companies, 1):
        leads = company_leads_map[company]
        print(f"#{rank} — {company} (Score: {total_score})")
        print(f"   Service Fit: {leads[0]['liatrio_service_area']}")
        print(f"   Angle: {leads[0]['outreach_angle']}")
        print(f"   Top trigger: {leads[0]['headline']}")
        print()
    print(f"Files saved:")
    print(f"  {top10_file}")
    print(f"  {prompt_file}")
    print(f"  {json_file}")
    return top_10_leads
if __name__ == "__main__":
    run_lead_generator()
