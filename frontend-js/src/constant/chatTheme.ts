// Design system constants for the Chat feature
export const CHAT_THEME = {
  colors: {
    primary: '#00A599',
    text: {
      primary: '#002835',
      secondary: '#6B7280',
    },
    error: {
      primary: 'rgba(255, 59, 48, 1)',
      background: 'rgba(255, 59, 48, 0.05)',
      border: 'rgba(255, 59, 48, 1)',
    },
    background: {
      main: '#FFFFFF',
      secondary: '#F9FAFB',
    },
  },
  spacing: {
    xs: '0.25rem',  // 4px
    sm: '0.5rem',   // 8px
    md: '1rem',     // 16px
    lg: '1.5rem',   // 24px
    xl: '2rem',     // 32px
    xxl: '2.5rem',  // 40px
  },
  layout: {
    maxWidth: '760px',
    chatHeight: 'calc(100vh - 150px)',
    borderRadius: '0.375rem', // 6px
  },
  typography: {
    fontFamily: 'Inter',
    fontSize: {
      sm: '14px',
      md: '16px',
      lg: '18px',
    },
    fontWeight: {
      normal: '400',
      medium: '500',
      semibold: '600',
    },
  },
} as const;

export const ERROR_MESSAGES = {
  default: 'An error occurred while processing your request.',
  networkError: 'Failed to fetch response from the backend.',
  processingError: 'Unable to process your request at this time.',
} as const;

export const UI_TEXT = {
  processing: 'Processing...',
  answer: 'Answer',
  noResponse: 'No response available',
} as const;
