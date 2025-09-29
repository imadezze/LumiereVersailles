#!/usr/bin/env python3
"""
Versailles Search Tool - searches concentrated JSONL file for user query keywords
and returns relevant entries for the visit advisor agent.
"""

import json
import re
import sys
from typing import List, Dict, Set
import subprocess


def extract_keywords(query: str) -> List[str]:
    """
    Extract meaningful keywords from user query.

    Args:
        query: User's question about Versailles visit

    Returns:
        List of keywords to search for
    """
    # Common stop words to ignore
    stop_words = {
        'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from',
        'has', 'he', 'in', 'is', 'it', 'its', 'of', 'on', 'that', 'the',
        'to', 'was', 'will', 'with', 'we', 'you', 'your', 'i', 'me', 'my',
        'how', 'what', 'where', 'when', 'why', 'would', 'should', 'could',
        'le', 'la', 'les', 'de', 'du', 'des', 'et', 'ou', 'un', 'une',
        'ce', 'cette', 'ces', 'pour', 'avec', 'dans', 'sur', 'par'
    }

    # Clean and split query into words
    words = re.findall(r'\b[a-zA-Zàâäéèêëïîôöùûüÿç]{3,}\b', query.lower())

    # Filter out stop words and short words
    keywords = [word for word in words if word not in stop_words and len(word) >= 3]

    # Add some domain-specific keywords based on common patterns
    domain_keywords = []
    query_lower = query.lower()

    if 'ticket' in query_lower or 'billet' in query_lower:
        domain_keywords.extend(['ticket', 'billet', 'price', 'prix', 'booking', 'réservation'])
    if 'photo' in query_lower:
        domain_keywords.extend(['photo', 'instagram', 'view', 'vue', 'spot'])
    if 'family' in query_lower or 'enfant' in query_lower or 'child' in query_lower:
        domain_keywords.extend(['family', 'famille', 'enfant', 'child', 'kids'])
    if 'tour' in query_lower or 'visite' in query_lower:
        domain_keywords.extend(['tour', 'visite', 'guided', 'guide'])
    if 'hotel' in query_lower or 'stay' in query_lower:
        domain_keywords.extend(['hotel', 'accommodation', 'stay', 'hébergement'])
    if 'lunch' in query_lower or 'restaurant' in query_lower or 'eat' in query_lower:
        domain_keywords.extend(['restaurant', 'lunch', 'café', 'food', 'manger'])
    if 'weekend' in query_lower or 'day' in query_lower or 'itinerary' in query_lower:
        domain_keywords.extend(['itinerary', 'day', 'schedule', 'programme', 'weekend'])

    # Combine and deduplicate
    all_keywords = list(set(keywords + domain_keywords))

    return all_keywords


def search_jsonl_entries(jsonl_file: str, keywords: List[str], min_matches: int = 1) -> List[Dict]:
    """
    Search JSONL file for entries containing the keywords.

    Args:
        jsonl_file: Path to the concentrated JSONL file
        keywords: List of keywords to search for
        min_matches: Minimum number of keyword matches required

    Returns:
        List of matching entries with their relevance scores
    """
    matching_entries = []

    try:
        with open(jsonl_file, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                if not line.strip():
                    continue

                try:
                    entry = json.loads(line)
                    text_content = entry.get('text', '').lower()
                    url = entry.get('url', '')

                    # Count keyword matches
                    matches = []
                    for keyword in keywords:
                        if keyword in text_content:
                            matches.append(keyword)

                    # If enough matches, add to results
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
        print(f"Error: File {jsonl_file} not found", file=sys.stderr)
        return []

    # Sort by relevance score (most matches first)
    matching_entries.sort(key=lambda x: x['relevance_score'], reverse=True)

    return matching_entries


def format_results(entries: List[Dict], max_results: int = 10) -> str:
    """
    Format search results for the agent.

    Args:
        entries: List of matching entries
        max_results: Maximum number of results to return

    Returns:
        Formatted string with search results
    """
    if not entries:
        return "No relevant entries found in the Versailles database."

    # Limit results
    entries = entries[:max_results]

    result = f"Found {len(entries)} relevant entries from Versailles database:\n\n"

    for i, entry in enumerate(entries, 1):
        result += f"=== Result {i} ===\n"
        result += f"URL: {entry['url']}\n"
        result += f"Matched keywords: {', '.join(entry['matched_keywords'])}\n"
        result += f"Relevance score: {entry['relevance_score']}\n"
        result += f"Content: {entry['text'][:500]}{'...' if len(entry['text']) > 500 else ''}\n\n"

    return result


def search_versailles_data(query: str, jsonl_file: str = None, max_results: int = 10) -> str:
    """
    Main function to search Versailles data based on user query.

    Args:
        query: User's question about Versailles visit
        jsonl_file: Path to JSONL file (default: auto-detect)
        max_results: Maximum number of results to return

    Returns:
        Formatted search results
    """
    if jsonl_file is None:
        jsonl_file = "/Users/work_compredict/Documents/Projects000/LumiereVersailles/data/versailles_concentrated_clean.jsonl"

    # Extract keywords from query
    keywords = extract_keywords(query)

    if not keywords:
        return "No meaningful keywords found in the query."

    print(f"Searching for keywords: {', '.join(keywords)}", file=sys.stderr)

    # Search for entries
    entries = search_jsonl_entries(jsonl_file, keywords, min_matches=1)

    # Format and return results
    return format_results(entries, max_results)


def main():
    """CLI interface for the search tool."""
    if len(sys.argv) < 2:
        print("Usage: python versailles_search_tool.py 'your query here'")
        print("Example: python versailles_search_tool.py 'We need tickets for a family visit with children'")
        return 1

    query = ' '.join(sys.argv[1:])
    results = search_versailles_data(query)
    print(results)
    return 0


if __name__ == "__main__":
    sys.exit(main())