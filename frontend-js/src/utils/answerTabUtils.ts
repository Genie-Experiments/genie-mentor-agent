import { DISPLAY_LIMITS } from "@/constant/answerTab";
import type { ExecutorAgent, GitHubMetadata, NotionMetadata, WebsearchMetadata } from "@/lib/api-service";
import type { ContextCard, SourceCard } from "@/types/AnswerTabTypes";

/**
 * Utility to safely truncate URLs while preserving readability
 */
export const truncateUrl = (url: string, maxLength: number = DISPLAY_LIMITS.URL_MAX_LENGTH): string => {
  if (url.length <= maxLength) return url;

  try {
    const urlObj = new URL(url);
    const domain = urlObj.hostname;
    const path = url.substring(url.indexOf(domain) + domain.length);

    if (domain.length >= maxLength - 3) {
      return domain.substring(0, maxLength - 3) + '...';
    }

    const availableChars = maxLength - domain.length - 3;
    return domain + path.substring(0, availableChars) + '...';
  } catch {
    // Fallback for invalid URLs
    return url.substring(0, maxLength - 3) + '...';
  }
};

/**
 * Extract top sources from different metadata types with proper type safety
 */
export const extractTopSources = (executorAgent?: ExecutorAgent): SourceCard[] => {
  if (!executorAgent?.metadata_by_source) return [];

  const sources: SourceCard[] = [];

  // Add websearch sources
  if (executorAgent.metadata_by_source.websearch) {
    executorAgent.metadata_by_source.websearch.forEach((source: WebsearchMetadata) => {
      sources.push({
        title: source.title || 'Untitled',
        url: source.url || '#',
        description: source.description || 'No description available',
      });
    });
  }

  // Add GitHub sources
  if (executorAgent.metadata_by_source.github) {
    executorAgent.metadata_by_source.github.forEach((source: GitHubMetadata) => {
      if (source.repo_links && source.repo_names) {
        const linkCount = Math.min(source.repo_links.length, source.repo_names.length);
        for (let i = 0; i < linkCount; i++) {
          sources.push({
            title: source.repo_names[i] || 'Untitled GitHub Repository',
            url: source.repo_links[i] || '#',
            description: 'GitHub Repository',
          });
        }
      }
    });
  }

  // Add Notion sources
  if (executorAgent.metadata_by_source.notion) {
    executorAgent.metadata_by_source.notion.forEach((source: NotionMetadata) => {
      if (source.doc_links && source.doc_names) {
        const linkCount = Math.min(source.doc_links.length, source.doc_names.length);
        for (let i = 0; i < linkCount; i++) {
          sources.push({
            title: source.doc_names[i] || 'Untitled Notion Document',
            url: source.doc_links[i] || '#',
            description: 'Notion Document',
          });
        }
      }
    });
  }

  return sources.slice(0, DISPLAY_LIMITS.TOP_SOURCES);
};

/**
 * Extract context data from knowledgebase with proper validation
 */
export const extractContexts = (executorAgent?: ExecutorAgent): ContextCard[] => {
  if (!executorAgent?.documents_by_source?.knowledgebase?.length) return [];

  const contexts: ContextCard[] = [];

  executorAgent.documents_by_source.knowledgebase.forEach((content: string, index: number) => {
    const title = 
      executorAgent.metadata_by_source?.knowledgebase?.[index]?.title ||
      executorAgent.metadata_by_source?.knowledgebase?.[index]?.document_title ||
      `Context ${index + 1}`;
    
    contexts.push({
      title,
      content: content || 'No content available',
    });
  });

  return contexts.slice(0, DISPLAY_LIMITS.CONTEXTS);
};

/**
 * Check if contexts are available
 */
export const hasContextsAvailable = (executorAgent?: ExecutorAgent): boolean => {
  return !!(
    executorAgent?.documents_by_source?.knowledgebase &&
    executorAgent.documents_by_source.knowledgebase.length > 0
  );
};

/**
 * Validate citation index and return appropriate context
 */
export const getContextByIndex = (
  executorAgent: ExecutorAgent | undefined, 
  index: number
): { title: string; content: string } | null => {
  if (!executorAgent?.documents_by_source?.knowledgebase) return null;

  const knowledgebase = executorAgent.documents_by_source.knowledgebase;
  if (index < 0 || index >= knowledgebase.length) {
    console.warn(`Citation index ${index} is out of bounds`);
    return null;
  }

  const content = knowledgebase[index] || '';
  const title = 
    executorAgent.metadata_by_source?.knowledgebase?.[index]?.title || 
    `Context ${index + 1}`;

  return { title, content };
};
