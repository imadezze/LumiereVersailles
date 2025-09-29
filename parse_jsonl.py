#!/usr/bin/env python3
"""
Parse complex JSONL file into concentrated format with just URL and text.
Extracts all text content from nested structures for easier searching.
"""

import json
import sys
from typing import Dict, List, Any, Union


def is_meaningful_text(text: str, min_words: int = 7) -> bool:
    """
    Check if text content is meaningful (has more than min_words).

    Args:
        text: Text to check
        min_words: Minimum number of words required

    Returns:
        True if text has more than min_words, False otherwise
    """
    if not text or not text.strip():
        return False

    # Count words (split by whitespace)
    word_count = len(text.strip().split())
    return word_count > min_words


def clean_text(text: str) -> str:
    """
    Clean text by removing URLs and normalizing whitespace.

    Args:
        text: Raw text to clean

    Returns:
        Cleaned text
    """
    import re

    # Remove URLs
    text = re.sub(r'https?://[^\s\)]+', '', text)
    text = re.sub(r'\([^)]*https?://[^)]*\)', '', text)

    # Clean up extra whitespace and normalize
    text = ' '.join(text.split())

    return text.strip()


def extract_text_from_content(content: Union[Dict, List, str]) -> List[str]:
    """
    Recursively extract meaningful text content from nested JSON structures.
    Filters out short text content (7 words or less) and removes duplicates.

    Args:
        content: JSON content (dict, list, or string)

    Returns:
        List of meaningful text strings found in the content
    """
    texts = []

    if isinstance(content, str):
        # Direct string - add if meaningful
        text = clean_text(content.strip())
        if text and is_meaningful_text(text):
            texts.append(text)

    elif isinstance(content, dict):
        # Handle different content types
        content_type = content.get('type', '')

        # Extract text from text field
        if 'text' in content and content['text']:
            text = clean_text(content['text'].strip())
            if is_meaningful_text(text):
                texts.append(text)

        # Extract text from heading (with lower threshold for important headings)
        if content_type == 'heading' and 'text' in content:
            text = clean_text(content['text'].strip())
            # Allow shorter headings if they seem important
            if text and (is_meaningful_text(text) or len(text.split()) >= 3):
                texts.append(text)

        # Extract items from lists - join list items to avoid fragmentation
        if content_type == 'list' and 'items' in content:
            list_items = []
            for item in content['items']:
                if isinstance(item, str):
                    cleaned = clean_text(item.strip())
                    if cleaned:
                        list_items.append(cleaned)
                else:
                    list_items.extend(extract_text_from_content(item))

            # Join list items if they form meaningful content together
            if list_items:
                joined_text = '; '.join(list_items)
                if is_meaningful_text(joined_text):
                    texts.append(joined_text)

        # Recursively process nested content
        if 'content' in content:
            texts.extend(extract_text_from_content(content['content']))

        # Process items in content blocks
        if 'items' in content and content_type == 'content_block':
            for item in content['items']:
                texts.extend(extract_text_from_content(item))

        # Process heading content in sections
        if 'heading' in content:
            texts.extend(extract_text_from_content(content['heading']))

    elif isinstance(content, list):
        # Process each item in the list
        for item in content:
            texts.extend(extract_text_from_content(item))

    return texts


def deduplicate_texts(text_parts: List[str]) -> List[str]:
    """
    Remove duplicate text parts while preserving order.

    Args:
        text_parts: List of text strings

    Returns:
        Deduplicated list of text strings
    """
    seen = set()
    result = []

    for text in text_parts:
        # Create a normalized version for comparison
        normalized = text.lower().strip()
        if normalized and normalized not in seen:
            seen.add(normalized)
            result.append(text)

    return result


def parse_jsonl_line(line: str) -> Dict[str, str]:
    """
    Parse a single JSONL line and extract URL and concatenated text.

    Args:
        line: Single line from JSONL file

    Returns:
        Dictionary with 'url' and 'text' keys
    """
    try:
        data = json.loads(line.strip())

        # Extract URL
        url = data.get('url', '')

        # Extract title and clean it
        title = data.get('title', '')
        if title:
            title = clean_text(title)

        # Extract all text from content
        content = data.get('content', [])
        text_parts = extract_text_from_content(content)

        # Add title at the beginning if it exists and is meaningful
        if title and (is_meaningful_text(title) or len(title.split()) >= 2):
            text_parts.insert(0, title)

        # Deduplicate text parts
        text_parts = deduplicate_texts(text_parts)

        # Join all text parts with periods for better readability
        full_text = '. '.join(text_parts)

        # Final cleanup
        full_text = ' '.join(full_text.split())

        return {
            'url': url,
            'text': full_text
        }

    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}", file=sys.stderr)
        return {'url': '', 'text': ''}
    except Exception as e:
        print(f"Error processing line: {e}", file=sys.stderr)
        return {'url': '', 'text': ''}


def main():
    """Main function to process the JSONL file."""
    input_file = "data/versailles_semantic_complete_20250813_204248.jsonl"
    output_file = "data/versailles_concentrated_clean.jsonl"

    processed_count = 0

    try:
        with open(input_file, 'r', encoding='utf-8') as infile, \
             open(output_file, 'w', encoding='utf-8') as outfile:

            for line_num, line in enumerate(infile, 1):
                if line.strip():  # Skip empty lines
                    result = parse_jsonl_line(line)

                    if result['url']:  # Only write if URL exists
                        json.dump(result, outfile, ensure_ascii=False)
                        outfile.write('\n')
                        processed_count += 1
                    else:
                        print(f"Skipped line {line_num}: No URL found", file=sys.stderr)

    except FileNotFoundError:
        print(f"Error: Input file '{input_file}' not found", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error processing file: {e}", file=sys.stderr)
        return 1

    print(f"Successfully processed {processed_count} entries")
    print(f"Output saved to: {output_file}")
    return 0


if __name__ == "__main__":
    sys.exit(main())