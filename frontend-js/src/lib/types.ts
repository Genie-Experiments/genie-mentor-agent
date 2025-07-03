export interface Message {
  id: string;
  content: string;
  sender: 'user' | 'assistant';
  timestamp: Date;
}

export interface Conversation {
  id: string;
  title: string;
  messages: Message[];
  createdAt: Date;
}

export interface CitationRendererProps {
  children: React.ReactNode;
  onCitationClick: (citationIndex: number, sourceIndex?: number) => void;
  isMultiSource?: boolean;
  dataSources?: string[];
  sourceUrls?: Record<string, string>;
  onOpenUrl?: (url: string) => void;
  metadata?: Record<string, unknown[]>;
}

export type TextPart = {
  type: 'text';
  content: string;
};

export type CitationPart = {
  type: 'citation';
  content: string;
  sourceIndex?: number;
  docIndex: number;
  originalText?: string;
};

export type TextPartType = TextPart | CitationPart;
