#!/usr/bin/env python3
"""
Deep Research Agent for Château de Versailles
Uses Mistral AI for comprehensive research on current events, news, closures, and renovations
"""

import os
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
import re
from dotenv import load_dotenv
import logging
from mistralai import Mistral
import feedparser
from bs4 import BeautifulSoup
import time

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

@dataclass
class ResearchResult:
    """Structure for research results"""
    timestamp: str
    category: str  # 'tip', 'news', 'event', 'closure', 'renovation'
    title: str
    content: str
    source: str
    url: Optional[str]
    date_start: Optional[str]
    date_end: Optional[str]
    location: Optional[str]
    impact_level: Optional[str]  # 'low', 'medium', 'high'
    metadata: Dict[str, Any]

class VersaillesDeepResearchAgent:
    """
    Deep Research Agent for Château de Versailles using Mistral AI
    """
    
    def __init__(self):
        self.mistral_api_key = os.getenv('MISTRAL_API_KEY')
        if not self.mistral_api_key:
            raise ValueError("MISTRAL_API_KEY not found in environment")
        
        self.mistral_client = Mistral(api_key=self.mistral_api_key)
        self.mistral_model = os.getenv('MISTRAL_MODEL', 'mistral-large-latest')
        
        # Research sources
        self.sources = {
            'official_website': 'https://www.chateauversailles.fr',
            'rss_feed': 'https://www.chateauversailles.fr/rss.xml',
            'twitter': '@CVersailles',
            'press': 'https://presse.chateauversailles.fr',
            'tripadvisor': 'https://www.tripadvisor.com/Attraction_Review-g187148-d188681',
        }
        
        # Base research categories - will be enhanced with AI-generated smart clauses
        self.base_research_categories = [
            "upcoming events and exhibitions",
            "temporary closures and renovations", 
            "seasonal changes and special openings",
            "musical fountains and shows schedule",
            "visitor tips and best visiting times",
            "current exhibitions and displays",
            "restoration projects and closed areas",
            "special nocturnal visits and evening events",
            "accessibility updates and services",
            "new digital experiences and mobile apps"
        ]
        
        # Will be populated with AI-generated smart search clauses
        self.research_topics = []
        self.results = []
    
    def generate_smart_search_clauses(self) -> List[str]:
        """
        Use Mistral AI to generate contextual and time-aware search clauses
        """
        try:
            logger.info("🧠 Generating smart search clauses with Mistral AI...")
            
            # Get current date context
            current_date = datetime.now()
            current_month = current_date.strftime("%B")
            current_year = current_date.year
            next_month = (current_date.replace(day=28) + timedelta(days=4)).replace(day=1).strftime("%B")
            season = self._get_current_season()
            
            # Create context-aware prompt
            search_generation_prompt = f"""You are an expert research assistant specializing in Château de Versailles. 

Current Context:
- Date: {current_date.strftime("%B %d, %Y")}
- Current Month: {current_month} {current_year}
- Next Month: {next_month} {current_year}
- Season: {season}
- Day of Week: {current_date.strftime("%A")}

Your task is to generate 15-20 highly specific, contextual search queries for researching current and upcoming information about Château de Versailles. 

Base categories to enhance:
{', '.join(self.base_research_categories)}

Requirements:
1. Include current month/year in time-sensitive queries
2. Consider seasonal relevance (e.g., garden events in spring/summer, indoor events in winter)
3. Include specific French terms and official names
4. Focus on actionable visitor information
5. Consider upcoming holidays and special periods
6. Include both French and English search terms where relevant

Generate search queries that are:
- Specific and actionable
- Time-aware and contextual
- Focused on visitor impact
- Including exact dates when possible
- Covering both immediate (next 2 weeks) and future (next 3 months) timeframes

Format as a simple numbered list, one query per line.
Example format:
1. Château de Versailles fermetures exceptionnelles {current_month} {current_year}
2. Versailles musical fountains schedule {season} {current_year}

Generate 18 specific search queries:"""

            messages = [
                {"role": "system", "content": "You are a specialized research query generator for Château de Versailles, expert in French cultural sites and tourism."},
                {"role": "user", "content": search_generation_prompt}
            ]
            
            response = self.mistral_client.chat.complete(
                model=self.mistral_model,
                messages=messages,
                temperature=0.4,  # Slightly higher for creativity
                max_tokens=1500
            )
            
            content = response.choices[0].message.content
            
            # Parse the numbered list
            search_queries = []
            lines = content.strip().split('\n')
            
            for line in lines:
                line = line.strip()
                # Remove numbering and clean up
                if line and (line[0].isdigit() or line.startswith('-') or line.startswith('•')):
                    # Remove numbering pattern like "1.", "1)", "- ", "• "
                    cleaned = re.sub(r'^[\d\-•\s\.\)]+', '', line).strip()
                    if cleaned and len(cleaned) > 10:  # Ensure meaningful queries
                        search_queries.append(cleaned)
            
            # Fallback to base categories if parsing failed
            if len(search_queries) < 5:
                logger.warning("AI-generated queries insufficient, using enhanced base categories")
                search_queries = self._generate_fallback_queries()
            
            logger.info(f"✅ Generated {len(search_queries)} smart search clauses")
            return search_queries
            
        except Exception as e:
            logger.error(f"Error generating smart search clauses: {e}")
            logger.info("Using fallback search queries")
            return self._generate_fallback_queries()
    
    def _get_current_season(self) -> str:
        """Determine current season"""
        month = datetime.now().month
        if month in [12, 1, 2]:
            return "winter"
        elif month in [3, 4, 5]:
            return "spring"
        elif month in [6, 7, 8]:
            return "summer"
        else:
            return "autumn"
    
    def _generate_fallback_queries(self) -> List[str]:
        """Generate fallback queries if AI generation fails"""
        current_date = datetime.now()
        current_month = current_date.strftime("%B")
        current_year = current_date.year
        season = self._get_current_season()
        
        return [
            f"Château de Versailles événements {current_month} {current_year}",
            f"Versailles fermetures travaux {current_year}",
            f"Grandes Eaux Musicales Versailles {season} {current_year}",
            f"Versailles nocturnes spectacles {current_year}",
            f"Château Versailles expositions temporaires {current_month} {current_year}",
            f"Versailles jardins {season} horaires {current_year}",
            f"Marie-Antoinette domaine fermeture rénovation {current_year}",
            f"Versailles accessibility disabled visitors {current_year}",
            f"Château Versailles mobile app nouvelles fonctionnalités",
            f"Versailles best time visit avoid crowds {current_month}",
            f"Trianon palace closure renovation {current_year}",
            f"Versailles photography rules restrictions {current_year}",
            f"Château Versailles group visits booking {current_year}",
            f"Versailles Christmas events December {current_year}",
            f"Galerie des Glaces restoration work {current_year}"
        ]
    
    def deep_research_with_mistral(self, query: str) -> List[Dict[str, Any]]:
        """
        Perform deep research using Mistral AI's advanced capabilities
        """
        try:
            logger.info(f"🔍 Deep researching: {query}")
            
            # Create a comprehensive research prompt
            research_prompt = f"""You are a specialized research assistant for Château de Versailles.
            
Your task is to provide comprehensive, current information about: {query}

Please research and provide:
1. **Current Status**: What's happening now (as of late 2024/early 2025)
2. **Upcoming Changes**: Scheduled events, closures, or renovations
3. **Practical Tips**: Visitor advice and insider information
4. **Dates and Times**: Specific scheduling information
5. **Impact on Visitors**: How this affects the visitor experience

Format your response as a structured analysis with clear sections.
Include any relevant dates, locations within the palace/gardens, and practical implications.
Be specific about which rooms, gardens, or areas are affected.

IMPORTANT: Focus on factual, current information that would be valuable for visitors planning their trip."""

            messages = [
                {"role": "system", "content": "You are a Versailles expert providing detailed, accurate, and current information about the palace, its events, and visitor experience."},
                {"role": "user", "content": research_prompt}
            ]
            
            response = self.mistral_client.chat.complete(
                model=self.mistral_model,
                messages=messages,
                temperature=0.3,
                max_tokens=2000
            )
            
            content = response.choices[0].message.content
            
            # Parse the response and extract structured information
            extracted_info = self._parse_research_response(content, query)
            
            return extracted_info
            
        except Exception as e:
            logger.error(f"Error in Mistral research: {e}")
            return []
    
    def _parse_research_response(self, content: str, original_query: str) -> List[Dict[str, Any]]:
        """
        Parse Mistral's response and extract structured information
        """
        results = []
        
        # Determine category based on query
        category = self._determine_category(original_query)
        
        # Extract dates from content
        date_pattern = r'\b(\d{1,2}[-/]\d{1,2}[-/]\d{2,4}|\w+\s+\d{1,2},?\s+\d{4}|(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4})\b'
        dates = re.findall(date_pattern, content, re.IGNORECASE)
        
        # Extract specific sections
        sections = self._split_into_sections(content)
        
        for section_title, section_content in sections.items():
            if section_content.strip():
                result = ResearchResult(
                    timestamp=datetime.now().isoformat(),
                    category=category,
                    title=f"{original_query} - {section_title}",
                    content=section_content,
                    source="Mistral AI Deep Research",
                    url=self.sources['official_website'],
                    date_start=dates[0] if dates else None,
                    date_end=dates[1] if len(dates) > 1 else None,
                    location=self._extract_location(section_content),
                    impact_level=self._assess_impact(section_content),
                    metadata={
                        'query': original_query,
                        'section': section_title,
                        'extracted_dates': dates,
                        'research_timestamp': datetime.now().isoformat()
                    }
                )
                results.append(asdict(result))
        
        return results
    
    def _determine_category(self, query: str) -> str:
        """Determine the category based on the query content"""
        query_lower = query.lower()
        
        if any(word in query_lower for word in ['event', 'concert', 'exhibition', 'show']):
            return 'event'
        elif any(word in query_lower for word in ['closure', 'closed', 'fermeture']):
            return 'closure'
        elif any(word in query_lower for word in ['renovation', 'restoration', 'travaux']):
            return 'renovation'
        elif any(word in query_lower for word in ['tip', 'advice', 'best time', 'conseil']):
            return 'tip'
        else:
            return 'news'
    
    def _split_into_sections(self, content: str) -> Dict[str, str]:
        """Split content into logical sections"""
        sections = {}
        
        # Common section headers
        section_patterns = [
            r'(?:^|\n)(?:\*\*)?([A-Z][^:\n]*?)(?:\*\*)?:',
            r'(?:^|\n)(?:\d+\.\s+)?(?:\*\*)?([A-Z][^:\n]*?)(?:\*\*)?:',
        ]
        
        current_section = "General Information"
        current_content = []
        
        lines = content.split('\n')
        for line in lines:
            found_section = False
            for pattern in section_patterns:
                match = re.match(pattern, line)
                if match:
                    # Save previous section
                    if current_content:
                        sections[current_section] = '\n'.join(current_content).strip()
                    # Start new section
                    current_section = match.group(1).strip()
                    current_content = [line[match.end():].strip()]
                    found_section = True
                    break
            
            if not found_section and line.strip():
                current_content.append(line)
        
        # Save last section
        if current_content:
            sections[current_section] = '\n'.join(current_content).strip()
        
        return sections if sections else {"Full Content": content}
    
    def _extract_location(self, content: str) -> Optional[str]:
        """Extract location information from content"""
        location_keywords = [
            'Hall of Mirrors', 'Galerie des Glaces',
            'Gardens', 'Jardins',
            'Grand Apartments', 'Grands Appartements',
            'Chapel', 'Chapelle',
            'Opera', 'Opéra',
            'Trianon', 'Marie-Antoinette',
            'Orangerie', 'Colonnade',
            'Grand Canal', 'Bassin'
        ]
        
        found_locations = []
        content_lower = content.lower()
        
        for keyword in location_keywords:
            if keyword.lower() in content_lower:
                found_locations.append(keyword)
        
        return ', '.join(found_locations) if found_locations else None
    
    def _assess_impact(self, content: str) -> str:
        """Assess the impact level on visitors"""
        content_lower = content.lower()
        
        high_impact_words = ['closed', 'fermeture', 'cancelled', 'annulé', 'inaccessible', 'major renovation']
        medium_impact_words = ['partial', 'limited', 'some areas', 'certain rooms', 'modified']
        
        if any(word in content_lower for word in high_impact_words):
            return 'high'
        elif any(word in content_lower for word in medium_impact_words):
            return 'medium'
        else:
            return 'low'
    
    def search_web_sources(self, query: str) -> List[Dict[str, Any]]:
        """
        Search web sources for additional information
        """
        results = []
        
        try:
            # Search using a web search API or scrape official sources
            search_url = f"https://www.chateauversailles.fr/search?keys={query.replace(' ', '+')}"
            
            logger.info(f"🌐 Searching web: {query}")
            
            # Simulate web search results (in production, use actual web scraping or API)
            web_result = ResearchResult(
                timestamp=datetime.now().isoformat(),
                category='news',
                title=f"Web search: {query}",
                content=f"Searching official Versailles website for: {query}",
                source="Versailles Official Website",
                url=search_url,
                date_start=None,
                date_end=None,
                location=None,
                impact_level='low',
                metadata={
                    'search_query': query,
                    'search_timestamp': datetime.now().isoformat()
                }
            )
            results.append(asdict(web_result))
                
        except Exception as e:
            logger.error(f"Error in web search: {e}")
        
        return results
    
    def analyze_rss_feeds(self) -> List[Dict[str, Any]]:
        """
        Analyze RSS feeds for latest news and updates
        """
        results = []
        
        try:
            logger.info("📰 Analyzing RSS feeds...")
            
            # Parse RSS feed
            feed_url = "https://www.chateauversailles.fr/actualites/feed"
            feed = feedparser.parse(feed_url)
            
            for entry in feed.entries[:10]:  # Get latest 10 entries
                # Determine category from entry
                category = 'news'
                if 'fermeture' in entry.title.lower() or 'closed' in entry.title.lower():
                    category = 'closure'
                elif 'événement' in entry.title.lower() or 'event' in entry.title.lower():
                    category = 'event'
                
                result = ResearchResult(
                    timestamp=datetime.now().isoformat(),
                    category=category,
                    title=entry.title,
                    content=entry.get('summary', ''),
                    source="Versailles RSS Feed",
                    url=entry.link,
                    date_start=entry.get('published', None),
                    date_end=None,
                    location=self._extract_location(entry.get('summary', '')),
                    impact_level=self._assess_impact(entry.get('summary', '')),
                    metadata={
                        'feed_source': 'official_rss',
                        'published_date': entry.get('published', ''),
                        'entry_id': entry.get('id', '')
                    }
                )
                results.append(asdict(result))
                
        except Exception as e:
            logger.error(f"Error parsing RSS feed: {e}")
        
        return results
    
    def generate_visitor_tips(self) -> List[Dict[str, Any]]:
        """
        Generate visitor tips using AI
        """
        tips_queries = [
            "Best time to visit Versailles to avoid crowds in 2024-2025",
            "Secret spots and hidden gems in Versailles palace and gardens",
            "Money-saving tips for visiting Versailles",
            "Photography tips and best photo spots in Versailles",
            "Accessibility tips for elderly or disabled visitors at Versailles"
        ]
        
        results = []
        
        for query in tips_queries:
            try:
                response = self.mistral_client.chat.complete(
                    model=self.mistral_model,
                    messages=[
                        {"role": "system", "content": "You are a Versailles expert tour guide providing practical visitor tips."},
                        {"role": "user", "content": f"Provide specific, actionable advice about: {query}"}
                    ],
                    temperature=0.3,
                    max_tokens=500
                )
                
                tip_content = response.choices[0].message.content
                
                result = ResearchResult(
                    timestamp=datetime.now().isoformat(),
                    category='tip',
                    title=query,
                    content=tip_content,
                    source="AI-Generated Visitor Tips",
                    url=None,
                    date_start=None,
                    date_end=None,
                    location="Château de Versailles",
                    impact_level='low',
                    metadata={
                        'tip_type': 'visitor_advice',
                        'generation_model': self.mistral_model
                    }
                )
                results.append(asdict(result))
                
            except Exception as e:
                logger.error(f"Error generating tip for '{query}': {e}")
        
        return results
    
    def run_comprehensive_research(self):
        """
        Run comprehensive research on all topics
        """
        logger.info("🚀 Starting comprehensive Versailles research...")
        
        all_results = []
        
        # 0. Generate smart search clauses first
        logger.info("🧠 Step 1: Generating AI-powered search clauses...")
        self.research_topics = self.generate_smart_search_clauses()
        
        logger.info(f"📋 Generated {len(self.research_topics)} smart search topics:")
        for i, topic in enumerate(self.research_topics[:5], 1):
            logger.info(f"  {i}. {topic}")
        if len(self.research_topics) > 5:
            logger.info(f"  ... and {len(self.research_topics) - 5} more")
        
        # 1. Deep research on AI-generated topics
        logger.info("\n🔍 Step 2: Deep research on generated topics...")
        for i, topic in enumerate(self.research_topics, 1):
            logger.info(f"Researching {i}/{len(self.research_topics)}: {topic[:60]}...")
            results = self.deep_research_with_mistral(topic)
            all_results.extend(results)
            time.sleep(2)  # Rate limiting for API calls
        
        # 2. Analyze RSS feeds
        rss_results = self.analyze_rss_feeds()
        all_results.extend(rss_results)
        
        # 3. Generate visitor tips
        tips = self.generate_visitor_tips()
        all_results.extend(tips)
        
        # 4. Search for current events
        current_month = datetime.now().strftime("%B %Y")
        events_query = f"Versailles events {current_month}"
        events = self.search_web_sources(events_query)
        all_results.extend(events)
        
        self.results = all_results
        logger.info(f"✅ Research complete! Found {len(all_results)} items")
        
        return all_results
    
    def save_to_jsonl(self, filename: str = None):
        """
        Save research results to JSONL file
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"versailles_research_{timestamp}.jsonl"
        
        filepath = os.path.join(
            '/Users/abedattal/Documents/projects/LumiereVersailles',
            filename
        )
        
        with open(filepath, 'w', encoding='utf-8') as f:
            for result in self.results:
                f.write(json.dumps(result, ensure_ascii=False) + '\n')
        
        logger.info(f"💾 Saved {len(self.results)} research items to {filepath}")
        return filepath
    
    def get_summary(self) -> Dict[str, Any]:
        """
        Get a summary of research results
        """
        if not self.results:
            return {"status": "No results yet"}
        
        summary = {
            "total_items": len(self.results),
            "categories": {},
            "sources": {},
            "high_impact_items": [],
            "upcoming_events": [],
            "recent_updates": []
        }
        
        for result in self.results:
            # Count by category
            cat = result.get('category', 'unknown')
            summary['categories'][cat] = summary['categories'].get(cat, 0) + 1
            
            # Count by source
            source = result.get('source', 'unknown')
            summary['sources'][source] = summary['sources'].get(source, 0) + 1
            
            # Collect high impact items
            if result.get('impact_level') == 'high':
                summary['high_impact_items'].append({
                    'title': result.get('title'),
                    'category': result.get('category'),
                    'content': result.get('content', '')[:200] + '...'
                })
            
            # Collect events
            if result.get('category') == 'event' and result.get('date_start'):
                summary['upcoming_events'].append({
                    'title': result.get('title'),
                    'date': result.get('date_start'),
                    'location': result.get('location')
                })
        
        # Sort events by date if possible
        summary['upcoming_events'] = sorted(
            summary['upcoming_events'],
            key=lambda x: x.get('date', ''),
            reverse=False
        )[:10]  # Keep top 10
        
        return summary


def main():
    """
    Main execution function
    """
    print("=" * 70)
    print("🏰 VERSAILLES DEEP RESEARCH AGENT")
    print("=" * 70)
    print("Powered by Mistral AI - Smart Search Generation")
    
    # Get current context
    current_date = datetime.now()
    print(f"📅 Current Date: {current_date.strftime('%B %d, %Y (%A)')}")
    print(f"🌍 Season: {VersaillesDeepResearchAgent()._get_current_season().title()}")
    print("-" * 70)
    
    agent = VersaillesDeepResearchAgent()
    
    print("\n🧠 AI will generate contextual search topics based on:")
    print("   • Current date and season")
    print("   • Upcoming events and holidays")
    print("   • Seasonal relevance")
    print("   • Visitor impact priorities")
    
    print("\n🚀 Starting intelligent research... This may take several minutes.")
    print("-" * 70)
    
    # Run research
    results = agent.run_comprehensive_research()
    
    # Save to JSONL
    filepath = agent.save_to_jsonl()
    
    # Print summary
    summary = agent.get_summary()
    
    print("\n📊 RESEARCH SUMMARY")
    print("=" * 60)
    print(f"Total items found: {summary['total_items']}")
    
    print("\n📂 By Category:")
    for cat, count in summary['categories'].items():
        print(f"  • {cat}: {count} items")
    
    print("\n📰 By Source:")
    for source, count in summary['sources'].items():
        print(f"  • {source}: {count} items")
    
    if summary['high_impact_items']:
        print("\n⚠️ High Impact Items:")
        for item in summary['high_impact_items'][:5]:
            print(f"  • [{item['category'].upper()}] {item['title']}")
    
    if summary['upcoming_events']:
        print("\n📅 Upcoming Events:")
        for event in summary['upcoming_events'][:5]:
            print(f"  • {event['title']}")
            if event['date']:
                print(f"    Date: {event['date']}")
            if event['location']:
                print(f"    Location: {event['location']}")
    
    print("\n" + "=" * 60)
    print(f"✅ Research complete! Results saved to:")
    print(f"   {filepath}")
    print("=" * 60)


if __name__ == "__main__":
    main()
