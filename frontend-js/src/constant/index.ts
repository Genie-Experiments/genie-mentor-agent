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

export const PREDEFINED_QUESTIONS = [
  'What is Genie Mentor Agent?',
  'How can I use this application?',
  'Which of our advanced RAG experiments were only evaluated using the Hit Rate metric and not Answer Similarity?',
  'From all the reports on Advanced RAG experiments, find the technique which provided the maximum score for *UpTrain* Evaluation for “Context Precision” for the github code files data?',
];

export const LARGE_SCREEN_BREAKPOINT = 1525;

export const LAYOUT_CONSTANTS = {
  INPUT_CONTAINER_WIDTH: '752px',
  INPUT_FIELD_WIDTH: '735px',
  GRADIENT_HEIGHT: '200px',
  Z_INDEX: {
    OVERLAY: 10,
    INPUT: 20,
  },
}

export const GRADIENT_STYLE = {
  background: 'linear-gradient(180deg, rgba(240, 255, 254, 0.00) 0%, #F0FFFE 41.99%)',
};

export * from './answerTab';
export * from './chatTheme';
export * from './researchTab';
export * from './sourcesTab';