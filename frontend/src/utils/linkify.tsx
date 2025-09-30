import React from 'react';

/**
 * Converts URLs in text to clickable links
 * Supports markdown-style links [text](url), plain URLs, and www. URLs
 */
export const linkifyText = (text: string): React.ReactNode[] => {
  const parts: React.ReactNode[] = [];
  let lastIndex = 0;

  // First, handle markdown-style links [text](url)
  const markdownLinkRegex = /\[([^\]]+)\]\((https?:\/\/[^)]+)\)/g;
  let match;

  while ((match = markdownLinkRegex.exec(text)) !== null) {
    const linkText = match[1];
    let url = match[2];
    const index = match.index;

    // Add text before the markdown link
    if (index > lastIndex) {
      const beforeText = text.substring(lastIndex, index);
      parts.push(...linkifyPlainUrls(beforeText, lastIndex));
    }

    // Clean URL - remove any whitespace/newlines that might have been captured
    url = url.replace(/\s+/g, '');

    // Add the markdown link as a clickable link
    parts.push(
      <a
        key={`link-${index}`}
        href={url}
        target="_blank"
        rel="noopener noreferrer"
        className="message-link"
      >
        {linkText}
      </a>
    );

    lastIndex = index + match[0].length;
  }

  // Handle remaining text after last markdown link
  if (lastIndex < text.length) {
    const remainingText = text.substring(lastIndex);
    parts.push(...linkifyPlainUrls(remainingText, lastIndex));
  }

  return parts.length > 0 ? parts : [text];
};

/**
 * Helper function to linkify plain URLs (not markdown)
 */
const linkifyPlainUrls = (text: string, baseIndex: number): React.ReactNode[] => {
  const parts: React.ReactNode[] = [];
  const urlRegex = /(https?:\/\/[^\s),.;!?]+)|(www\.[^\s),.;!?]+)/g;
  let lastIndex = 0;
  let match;

  while ((match = urlRegex.exec(text)) !== null) {
    let url = match[0];
    const index = match.index;

    // Remove trailing punctuation that might have been captured
    url = url.replace(/[),.;!?]+$/, '');

    // Add text before the URL
    if (index > lastIndex) {
      parts.push(text.substring(lastIndex, index));
    }

    // Add the URL as a clickable link
    const href = url.startsWith('www.') ? `https://${url}` : url;
    parts.push(
      <a
        key={`plain-link-${baseIndex + index}`}
        href={href}
        target="_blank"
        rel="noopener noreferrer"
        className="message-link"
      >
        {url}
      </a>
    );

    lastIndex = index + url.length;
  }

  // Add remaining text
  if (lastIndex < text.length) {
    parts.push(text.substring(lastIndex));
  }

  return parts.length > 0 ? parts : [text];
};

/**
 * Processes message content line by line and linkifies URLs
 */
export const renderMessageContent = (content: string): React.ReactNode => {
  return content.split('\n').map((line, index) => (
    <React.Fragment key={index}>
      {linkifyText(line)}
      {index < content.split('\n').length - 1 && <br />}
    </React.Fragment>
  ));
};