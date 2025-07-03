export const SOURCE_TYPES = {
  KNOWLEDGE_BASE: 'knowledgebase',
  WEB_SEARCH: 'websearch',
  GITHUB: 'github',
  NOTION: 'notion',
};

export const SOURCE_DISPLAY_NAMES = {
  [SOURCE_TYPES.KNOWLEDGE_BASE]: 'Knowledge Base',
  [SOURCE_TYPES.WEB_SEARCH]: 'Web Source',
  [SOURCE_TYPES.GITHUB]: 'GitHub Source',
  [SOURCE_TYPES.NOTION]: 'Notion Doc',
};

export const EXTERNAL_SOURCES = [
  SOURCE_TYPES.WEB_SEARCH,
  SOURCE_TYPES.GITHUB,
  SOURCE_TYPES.NOTION,
];
