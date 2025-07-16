export const SOURCES_CONSTANTS = {
  ICON_SIZE: 16,
  NUMBERED_INDEX_WIDTH: '24px',
  VERTICAL_SPACING: {
    SMALL: '7px',
    MEDIUM: '10px',
    LARGE: '14px',
    SECTION: '18px',
    SEPARATOR: '27px',
  },
  HORIZONTAL_SPACING: {
    SMALL: '8px',
    LARGE: '32px',
  },
} as const;

export const SOURCES_STYLES = {
  sectionTitle: {
    color: '#002835',
    fontFamily: 'Inter',
    fontSize: '16px',
    fontStyle: 'normal',
    fontWeight: 500,
    lineHeight: 'normal',
    textTransform: 'uppercase' as const,
    opacity: 0.4,
  },
  itemTitle: {
    color: '#002835',
    fontFamily: 'Inter',
    fontSize: '16px',
    fontStyle: 'normal',
    fontWeight: 500,
    lineHeight: 'normal',
  },
  itemDetail: {
    color: '#002835',
    fontFamily: 'Inter',
    fontSize: '14px',
    fontStyle: 'normal',
    fontWeight: 400,
    lineHeight: 'normal',
  },
  itemIndex: {
    color: '#002835',
    fontFamily: 'Inter',
    fontSize: '16px',
    fontStyle: 'normal',
    fontWeight: 500,
    lineHeight: 'normal',
    width: '24px',
    flexShrink: 0,
  },
  link: {
    color: '#002835',
    fontFamily: 'Inter',
    fontSize: '13px',
    fontStyle: 'normal',
    fontWeight: 400,
    lineHeight: 'normal',
    opacity: 0.6,
  },
  separator: {
    background: '#9CBFBC',
    height: '1px',
    margin: '27px 0',
  },
  viewDetails: {
    color: '#00A599',
    fontFamily: 'Inter',
    fontSize: '16px',
    fontStyle: 'normal',
    fontWeight: 500,
    lineHeight: '24px',
    cursor: 'pointer',
    display: 'flex',
    alignItems: 'center',
  },
  noSourcesMessage: {
    color: '#002835',
    fontFamily: 'Inter',
    fontSize: '16px',
    fontStyle: 'normal',
    fontWeight: 400,
    lineHeight: 'normal',
    textAlign: 'center' as const,
    padding: '32px 0',
  },
  listContainer: {
    paddingLeft: 0,
  },
  listItem: {
    marginBottom: '18px',
    display: 'flex',
    flexDirection: 'column' as const,
    alignItems: 'flex-start',
    listStyle: 'none',
  },
  itemHeader: {
    display: 'flex',
    alignItems: 'baseline',
    gap: '8px',
  },
  itemContent: {
    marginLeft: 32,
    width: '100%',
  },
  starIcon: {
    xmlns: 'http://www.w3.org/2000/svg',
    width: '16',
    height: '16',
    viewBox: '0 0 12 11',
    fill: 'none',
  },
} as const;

export const SOURCES_SECTION_TITLES = {
  KNOWLEDGE_BASE: 'Knowledge Base Sources',
  WEB_SOURCES: 'Web Sources',
  GITHUB_SOURCES: 'GitHub Sources',
  NOTION_SOURCES: 'Notion Sources',
} as const;

export const SOURCES_FIELD_LABELS = {
  SOURCE: 'Source',
  PAGE: 'Page',
  SHOW_DETAIL: 'Show Detail',
} as const;

export const MESSAGES = {
  NO_SOURCES: 'No sources available for this answer.',
  NO_SOURCE_INFO: 'No source information available.',
  UNTITLED: 'Untitled',
  GITHUB_REPO: 'Untitled GitHub Repository',
  NOTION_DOC: 'Untitled Notion Document',
  NO_DESCRIPTION: 'No description available.',
  GITHUB_DESCRIPTION: 'GitHub Repository',
  NOTION_DESCRIPTION: 'Notion Document',
} as const;
