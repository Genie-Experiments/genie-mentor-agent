import type {
  ExecutorAgent,
  GitHubMetadata,
  NotionMetadata,
  WebsearchMetadata,
} from '@/lib/api-service';
import { MESSAGES } from '@/constant/sourcesTab';

/**
 * Check if executor agent has any sources available
 */
export const hasNoSources = (executorAgent?: ExecutorAgent): boolean => {
  if (!executorAgent) return true;

  const { metadata_by_source } = executorAgent;

  // If metadata_by_source is undefined or null, there are no sources
  if (!metadata_by_source) return true;

  // Check if all source arrays are either undefined, null, or empty
  const hasKnowledgebase =
    metadata_by_source.knowledgebase && metadata_by_source.knowledgebase.length > 0;
  const hasWebsearch = metadata_by_source.websearch && metadata_by_source.websearch.length > 0;
  const hasGithub = metadata_by_source.github && metadata_by_source.github.length > 0;
  const hasNotion = metadata_by_source.notion && metadata_by_source.notion.length > 0;

  // Return true if all source arrays are empty or missing
  return !hasKnowledgebase && !hasWebsearch && !hasGithub && !hasNotion;
};

/**
 * Count how many source types are available
 */
export const countSourceTypes = (executorAgent?: ExecutorAgent): number => {
  const { metadata_by_source } = executorAgent || {};
  let count = 0;
  if (metadata_by_source?.knowledgebase && metadata_by_source.knowledgebase.length > 0) count++;
  if (metadata_by_source?.websearch && metadata_by_source.websearch.length > 0) count++;
  if (metadata_by_source?.github && metadata_by_source.github.length > 0) count++;
  if (metadata_by_source?.notion && metadata_by_source.notion.length > 0) count++;
  return count;
};

/**
 * Map GitHub metadata to WebsearchMetadata format for consistent rendering
 */
export const mapGitHubToWebsearchMetadata = (metadata: GitHubMetadata[]): WebsearchMetadata[] => {
  const result: WebsearchMetadata[] = [];

  metadata.forEach((item) => {
    if (item.repo_links && item.repo_names) {
      for (let i = 0; i < item.repo_links.length; i++) {
        result.push({
          title: item.repo_names[i] || MESSAGES.GITHUB_REPO,
          description: MESSAGES.GITHUB_DESCRIPTION,
          url: item.repo_links[i] || '#',
        });
      }
    }
  });

  return result;
};

/**
 * Map Notion metadata to WebsearchMetadata format for consistent rendering
 */
export const mapNotionToWebsearchMetadata = (metadata: NotionMetadata[]): WebsearchMetadata[] => {
  const result: WebsearchMetadata[] = [];

  metadata.forEach((item) => {
    if (item.doc_links && item.doc_names) {
      for (let i = 0; i < item.doc_links.length; i++) {
        result.push({
          title: item.doc_names[i] || MESSAGES.NOTION_DOC,
          description: MESSAGES.NOTION_DESCRIPTION,
          url: item.doc_links[i] || '#',
        });
      }
    }
  });

  return result;
};

/**
 * Get the source documents for knowledge base modal
 */
export const getKnowledgeBaseDocument = (
  executorAgent?: ExecutorAgent,
  index?: number
): string => {
  if (!executorAgent?.documents_by_source?.knowledgebase || index === undefined) {
    return '';
  }
  return executorAgent.documents_by_source.knowledgebase[index] || '';
};

/**
 * Safely get title with fallback
 */
export const getSourceTitle = (title?: string, fallback: string = MESSAGES.UNTITLED): string => {
  return title || fallback;
};

/**
 * Safely get description with fallback
 */
export const getSourceDescription = (description?: string): string => {
  return description || MESSAGES.NO_DESCRIPTION;
};
