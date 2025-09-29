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


def extract_text_from_content(content: Union[Dict, List, str]) -> List[str]:
    """
    Recursively extract meaningful text content from nested JSON structures.
    Filters out short text content (7 words or less).

    Args:
        content: JSON content (dict, list, or string)

    Returns:
        List of meaningful text strings found in the content
    """
    texts = []

    if isinstance(content, str):
        # Direct string - add if meaningful
        text = content.strip()
        if text and is_meaningful_text(text):
            texts.append(text)

    elif isinstance(content, dict):
        # Handle different content types
        content_type = content.get('type', '')

        # Extract text from text field
        if 'text' in content and content['text']:
            text = content['text'].strip()
            if is_meaningful_text(text):
                texts.append(text)

        # Extract text from heading
        if content_type == 'heading' and 'text' in content:
            text = content['text'].strip()
            if is_meaningful_text(text):
                texts.append(text)

        # Extract items from lists
        if content_type == 'list' and 'items' in content:
            for item in content['items']:
                texts.extend(extract_text_from_content(item))

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

        # Extract title
        title = data.get('title', '')

        # Extract all text from content
        content = data.get('content', [])
        text_parts = extract_text_from_content(content)

        # Add title at the beginning if it exists
        if title:
            text_parts.insert(0, title)

        # Join all text parts with spaces
        full_text = ' '.join(text_parts)

        # Clean up extra whitespace
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
    input_file = "versailles_semantic_complete_20250813_204248.jsonl"
    output_file = "versailles_concentrated_filtered.jsonl"

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