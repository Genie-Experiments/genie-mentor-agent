// Tailwind CSS classes for Knowledge Base components
export const KNOWLEDGE_BASE_STYLES = {
  // Main container styles
  container: 'w-full space-y-4',
  
  // Header styles
  header: {
    main: 'flex items-center gap-3 p-4 bg-gradient-to-r from-emerald-50 to-teal-50 rounded-lg border border-emerald-200',
    icon: 'flex items-center justify-center w-10 h-10 bg-emerald-500 rounded-full',
    iconText: 'w-5 h-5 text-white',
    title: 'font-semibold text-emerald-900',
    subtitle: 'text-sm text-emerald-700'
  },

  // Hop card styles
  hop: {
    container: 'border rounded-lg overflow-hidden transition-all duration-200',
    finalBg: 'bg-purple-50 border-purple-200',
    regularBg: 'bg-blue-50 border-blue-200',
    button: 'w-full p-4 text-left hover:bg-white/50 transition-colors duration-200 flex items-center justify-between',
    iconContainer: 'flex items-center justify-center w-8 h-8 rounded-full text-white',
    finalIcon: 'bg-purple-500',
    regularIcon: 'bg-blue-500',
    title: 'font-semibold text-gray-900',
    subtitle: 'text-sm text-gray-600',
    content: 'border-t border-gray-200 bg-white p-4 space-y-4'
  },

  // Sub-question styles
  subQuestion: {
    container: 'border border-gray-200 rounded-lg overflow-hidden bg-gray-50',
    button: 'w-full p-3 text-left hover:bg-gray-100 transition-colors duration-200 flex items-start gap-3',
    icon: 'flex items-center justify-center w-6 h-6 bg-indigo-500 rounded-full text-white flex-shrink-0 mt-0.5',
    question: 'text-sm font-medium text-gray-900 break-words',
    info: 'text-xs text-gray-600 mt-1',
    content: 'border-t border-gray-200 bg-white p-4 space-y-4'
  },

  // Document card styles
  document: {
    container: 'border border-gray-200 rounded-lg overflow-hidden bg-white',
    button: 'w-full p-3 text-left hover:bg-gray-50 transition-colors duration-200 flex items-start gap-3',
    icon: 'flex items-center justify-center w-6 h-6 bg-emerald-500 rounded text-white flex-shrink-0 mt-0.5',
    badge: 'text-xs font-medium text-emerald-600 bg-emerald-100 px-2 py-0.5 rounded',
    metadata: 'text-xs text-gray-600 flex items-center gap-1',
    source: 'text-xs text-gray-700 font-medium mb-1',
    content: 'text-xs text-gray-600 line-clamp-2',
    fullContent: 'border-t border-gray-200 bg-gray-50 p-3 text-xs text-gray-700 whitespace-pre-wrap leading-relaxed'
  },

  // Reasoner output styles
  reasoner: {
    container: 'border border-amber-200 rounded-lg overflow-hidden bg-amber-50',
    header: 'p-3 bg-amber-100 border-b border-amber-200',
    title: 'font-medium text-amber-900',
    sufficient: 'flex items-center gap-1 text-green-700',
    insufficient: 'flex items-center gap-1 text-red-700',
    badge: 'text-xs font-medium',
    content: 'p-4 space-y-4',
    reasoning: 'text-sm text-amber-800 bg-white p-3 rounded border border-amber-200',
    section: 'font-medium text-amber-900 mb-2 flex items-center gap-2',
    item: 'text-xs p-2 rounded border',
    required: 'bg-white border-amber-200 text-amber-800',
    inContext: 'bg-green-50 border-green-200 text-green-800',
    nextQuestion: 'bg-blue-50 border-blue-200 text-blue-800 flex items-start gap-2'
  },

  // Memory display styles
  memory: {
    container: 'space-y-3',
    title: 'font-medium text-gray-800 flex items-center gap-2',
    card: 'border rounded-lg overflow-hidden',
    globalCard: 'border-purple-200 bg-purple-50',
    localCard: 'border-teal-200 bg-teal-50',
    button: 'w-full p-3 text-left transition-colors duration-200 flex items-center justify-between',
    globalButton: 'hover:bg-purple-100',
    localButton: 'hover:bg-teal-100',
    cardTitle: 'font-medium',
    globalTitle: 'text-purple-900',
    localTitle: 'text-teal-900',
    content: 'bg-white p-3 space-y-2',
    entry: 'p-2 rounded border',
    globalEntry: 'bg-purple-50 border-purple-200',
    localEntry: 'bg-teal-50 border-teal-200',
    entryLabel: 'text-xs font-medium mb-1',
    globalLabel: 'text-purple-600',
    tealLabel: 'text-teal-600',
    entryText: 'text-xs',
    globalText: 'text-purple-800',
    tealText: 'text-teal-800',
    localQuestion: 'bg-white p-2 rounded border border-teal-200'
  },

  // Summary styles
  summary: {
    global: 'p-3 bg-green-50 rounded-lg border border-green-200',
    globalTitle: 'font-medium text-green-900 mb-2 flex items-center gap-2',
    globalText: 'text-sm text-green-800',
    local: 'p-3 bg-blue-50 rounded-lg border border-blue-200',
    localTitle: 'font-medium text-blue-900 mb-2 flex items-center gap-2',
    localText: 'text-sm text-blue-800'
  },

  // Final answer styles
  finalAnswer: {
    container: 'mt-6 p-6 bg-gradient-to-br from-blue-50 to-indigo-50 rounded-xl border border-blue-200',
    header: 'flex items-center gap-2 mb-4',
    icon: 'w-6 h-6 text-blue-600',
    title: 'text-lg font-semibold text-blue-900',
    content: 'prose prose-sm max-w-none text-gray-800'
  },

  // Common icon styles
  icons: {
    sm: 'w-3 h-3',
    md: 'w-4 h-4',
    lg: 'w-5 h-5',
    xl: 'w-6 h-6'
  },

  // Animation classes
  animations: {
    fadeIn: 'animate-fade-in',
    slideIn: 'animate-slide-in-up',
    bounce: 'animate-bounce'
  }
} as const;

// Color themes for different hop types
export const HOP_THEMES = {
  regular: {
    bg: 'bg-blue-50 border-blue-200',
    icon: 'bg-blue-500',
    text: 'text-blue-900'
  },
  final: {
    bg: 'bg-purple-50 border-purple-200',
    icon: 'bg-purple-500',
    text: 'text-purple-900'
  }
} as const;
