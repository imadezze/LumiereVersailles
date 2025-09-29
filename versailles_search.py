"""
Versailles Search Module - for use with versailles-visit-advisor agent
Provides search functionality for the concentrated Versailles JSONL database.
"""

import json
import re
from typing import List, Dict, Optional


class VersaillesSearcher:
    """Search tool for Versailles concentrated data."""

    def __init__(self, jsonl_file: str = None):
        """
        Initialize the searcher with the JSONL database file.

        Args:
            jsonl_file: Path to concentrated JSONL file
        """
        if jsonl_file is None:
            self.jsonl_file = "/Users/work_compredict/Documents/Projects000/LumiereVersailles/data/versailles_concentrated_clean.jsonl"
        else:
            self.jsonl_file = jsonl_file

    def extract_keywords(self, query: str) -> List[str]:
        """Extract meaningful keywords from user query."""
        stop_words = {
            'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from',
            'has', 'he', 'in', 'is', 'it', 'its', 'of', 'on', 'that', 'the',
            'to', 'was', 'will', 'with', 'we', 'you', 'your', 'i', 'me', 'my',
            'how', 'what', 'where', 'when', 'why', 'would', 'should', 'could',
            'le', 'la', 'les', 'de', 'du', 'des', 'et', 'ou', 'un', 'une',
            'ce', 'cette', 'ces', 'pour', 'avec', 'dans', 'sur', 'par'
        }

        words = re.findall(r'\b[a-zA-Zàâäéèêëïîôöùûüÿç]{3,}\b', query.lower())
        keywords = [word for word in words if word not in stop_words and len(word) >= 3]

        # Add domain-specific keywords
        domain_keywords = []
        query_lower = query.lower()

        keyword_patterns = {
            ('ticket', 'billet'): ['ticket', 'billet', 'price', 'prix', 'booking', 'réservation'],
            ('photo', 'instagram'): ['photo', 'instagram', 'view', 'vue', 'spot'],
            ('family', 'enfant', 'child'): ['family', 'famille', 'enfant', 'child', 'kids'],
            ('tour', 'visite', 'guided'): ['tour', 'visite', 'guided', 'guide'],
            ('hotel', 'stay', 'accommodation'): ['hotel', 'accommodation', 'stay', 'hébergement'],
            ('lunch', 'restaurant', 'eat', 'food'): ['restaurant', 'lunch', 'café', 'food', 'manger'],
            ('weekend', 'day', 'itinerary', 'schedule'): ['itinerary', 'day', 'schedule', 'programme', 'weekend'],
            ('garden', 'outdoor', 'park'): ['garden', 'jardins', 'outdoor', 'park', 'parc'],
            ('museum', 'exhibition'): ['museum', 'musée', 'exhibition', 'exposition']
        }

        for triggers, additions in keyword_patterns.items():
            if any(trigger in query_lower for trigger in triggers):
                domain_keywords.extend(additions)

        return list(set(keywords + domain_keywords))

    def search(self, query: str, max_results: int = 10, min_matches: int = 1) -> List[Dict]:
        """
        Search for entries matching the query.

        Args:
            query: User's question about Versailles
            max_results: Maximum number of results to return
            min_matches: Minimum keyword matches required

        Returns:
            List of matching entries with metadata
        """
        keywords = self.extract_keywords(query)

        if not keywords:
            return []

        matching_entries = []

        try:
            with open(self.jsonl_file, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    if not line.strip():
                        continue

                    try:
                        entry = json.loads(line)
                        text_content = entry.get('text', '').lower()
                        url = entry.get('url', '')

                        matches = [kw for kw in keywords if kw in text_content]

                        if len(matches) >= min_matches:
                            matching_entries.append({
                                'url': url,
                                'text': entry.get('text', ''),
                                'matched_keywords': matches,
                                'relevance_score': len(matches),
                                'line_number': line_num
                            })

                    except json.JSONDecodeError:
                        continue

        except FileNotFoundError:
            return []

        # Sort by relevance and limit results
        matching_entries.sort(key=lambda x: x['relevance_score'], reverse=True)
        return matching_entries[:max_results]

    def search_formatted(self, query: str, max_results: int = 5) -> str:
        """
        Search and return formatted results for agent consumption.

        Args:
            query: User's question
            max_results: Maximum results to return

        Returns:
            Formatted string with search results
        """
        entries = self.search(query, max_results)

        if not entries:
            return "No relevant information found in the Versailles database."

        result = f"Found {len(entries)} relevant entries:\n\n"

        for i, entry in enumerate(entries, 1):
            result += f"📍 **Source {i}** ({entry['relevance_score']} matches)\n"
            result += f"🔗 {entry['url']}\n"
            result += f"📝 {entry['text'][:400]}{'...' if len(entry['text']) > 400 else ''}\n\n"

        return result


# Convenience function for direct usage
def search_versailles(query: str, max_results: int = 5) -> str:
    """
    Quick search function for Versailles data.

    Args:
        query: User's question about Versailles
        max_results: Maximum number of results

    Returns:
        Formatted search results
    """
    searcher = VersaillesSearcher()
    return searcher.search_formatted(query, max_results)