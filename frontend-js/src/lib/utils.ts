import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';
import { SOURCE_DISPLAY_NAMES, EXTERNAL_SOURCES } from '../constant';
import type { TextPartType } from './types';

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export const getSourceDisplayName = (sourceName: string): string => {
  const lowerName = sourceName.toLowerCase();
  if (lowerName in SOURCE_DISPLAY_NAMES) {
    return SOURCE_DISPLAY_NAMES[lowerName];
  }
  return sourceName.charAt(0).toUpperCase() + sourceName.slice(1);
};

export const isExternalSource = (sourceName: string): boolean => {
  const sourceLower = sourceName.toLowerCase();
  return EXTERNAL_SOURCES.includes(sourceLower);
};

export const getCitationUrl = (sourceName: string, docIndex: number, sourceUrls: Record<string, string>): string | undefined => {
  const sourceLower = sourceName.toLowerCase();
  const key = `${sourceLower}_${docIndex}`;

  // Direct match for the specific source and index
  if (sourceUrls[key]) {
    return sourceUrls[key];
  }

  // Handle external sources (notion, websearch, github)
  if (isExternalSource(sourceLower)) {
    // First try to find an exact match for this index
    const sourceKeys = Object.keys(sourceUrls).filter((k) => k.startsWith(`${sourceLower}_`));
    
    if (sourceKeys.length > 0) {
      if (docIndex < sourceKeys.length) {
        // Sort keys by their index to ensure correct ordering
        const sortedKeys = sourceKeys.sort((a, b) => {
          const aIndex = parseInt(a.split('_')[1], 10);
          const bIndex = parseInt(b.split('_')[1], 10);
          return aIndex - bIndex;
        });
        return sourceUrls[sortedKeys[docIndex]];
      } else {
        // If the requested index is out of range, use the first available URL for this source
        return sourceUrls[sourceKeys[0]];
      }
    }
    
    // Try with alternative formats that might be present in the sourceUrls
    for (const urlKey in sourceUrls) {
      if (urlKey.includes(sourceLower)) {
        return sourceUrls[urlKey];
      }
    }
  }
  
  return undefined;
};

export const getExternalSourceUrl = (
  sourceName: string,
  docIndex: number,
  metadata: Record<string, unknown[]> = {}
): string | undefined => {
  const sourceLower = sourceName.toLowerCase();
  
  if (!isExternalSource(sourceLower) || !metadata[sourceLower] || !metadata[sourceLower][docIndex]) {
    return undefined;
  }

  const sourceMetadata = metadata[sourceLower][docIndex];

  switch (sourceLower) {
    case 'websearch':
      // For websearch, we expect a URL property
      return typeof sourceMetadata === 'object' && sourceMetadata !== null && 'url' in sourceMetadata
        ? String(sourceMetadata.url)
        : undefined;
    
    case 'github':
      // For GitHub, we expect a repo_links array
      if (
        typeof sourceMetadata === 'object' && 
        sourceMetadata !== null && 
        'repo_links' in sourceMetadata && 
        Array.isArray(sourceMetadata.repo_links) && 
        sourceMetadata.repo_links.length > 0
      ) {
        return String(sourceMetadata.repo_links[0]);
      }
      break;
    
    case 'notion':
      // For Notion, we expect a doc_links array
      if (
        typeof sourceMetadata === 'object' && 
        sourceMetadata !== null && 
        'doc_links' in sourceMetadata && 
        Array.isArray(sourceMetadata.doc_links) && 
        sourceMetadata.doc_links.length > 0
      ) {
        return String(sourceMetadata.doc_links[0]);
      }
      break;
    
    default:
      return undefined;
  }

  return undefined;
};

export const processCitationText = (childrenAsString: string, isMultiSource: boolean): TextPartType[] => {
  if (!childrenAsString) return [];

  const singleSourceRegex = /\[(\d+(?:\.\d+)?)\]/g;
  const multiSourceRegex = /\[([A-Z])\]\[(\d+(?:\.\d+)?)\]/g;

  const regex = isMultiSource ? multiSourceRegex : singleSourceRegex;
  const parts: TextPartType[] = [];
  let lastIndex = 0;
  let match;

  // Clean up the text and preserve list formatting
  const processedText = childrenAsString
    .replace(/\\n\\n/g, ' ')
    .replace(/\\n/g, ' ')
    // Handle numbered list items, ensuring we preserve the original numbering
    .replace(/^\s*(\d+)\.\s+/gm, '§LIST§$1§DOT§ ')
    // Handle bullet list items
    .replace(/^\s*([*•-])\s+/gm, '§BULLET§ ');

  while ((match = regex.exec(processedText)) !== null) {
    if (match.index > lastIndex) {
      const beforeText = processedText.substring(lastIndex, match.index)
        .replace(/§LIST§(\d+)§DOT§/g, '$1.')
        .replace(/§BULLET§/g, '•');
      
      parts.push({ type: 'text', content: beforeText });
    }

    if (isMultiSource) {
      const sourceIndex = match[1].charCodeAt(0) - 65; 
      const citationNumber = parseInt(match[2].split('.')[0], 10);

      parts.push({
        type: 'citation',
        content: match[0],
        sourceIndex: sourceIndex,
        docIndex: citationNumber - 1,
        originalText: match[2], 
      });
    } else {
      const citationNumber = parseInt(match[1].split('.')[0], 10);

      parts.push({
        type: 'citation',
        content: match[0],
        docIndex: citationNumber - 1,
        originalText: match[1],
      });
    }

    lastIndex = match.index + match[0].length;
  }

  if (lastIndex < processedText.length) {
    const remainingText = processedText.substring(lastIndex)
      .replace(/§LIST§(\d+)§DOT§/g, '$1.')
      .replace(/§BULLET§/g, '•');
    
    parts.push({ type: 'text', content: remainingText });
  }

  return parts;
};
