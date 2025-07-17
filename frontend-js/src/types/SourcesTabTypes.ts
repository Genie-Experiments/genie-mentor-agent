import type {
  ExecutorAgent,
  KnowledgebaseMetadata,
  WebsearchMetadata,
} from '@/lib/api-service';

export interface SourcesTabProps {
  executorAgent: ExecutorAgent;
}

export interface SourceItemProps {
  item: KnowledgebaseMetadata | WebsearchMetadata;
  index: number;
  onShowDetail?: (title: string, index: number) => void;
  showDetailButton?: boolean;
}

export interface KnowledgeBaseSourceItemProps {
  item: KnowledgebaseMetadata;
  index: number;
  onShowDetail: (title: string, index: number) => void;
}

export interface WebSourceItemProps {
  item: WebsearchMetadata;
  index: number;
}

export interface SourceSectionProps {
  title: string;
  children: React.ReactNode;
  showSeparator?: boolean;
}

export interface StarIconProps {
  className?: string;
}

export interface ViewDetailsButtonProps {
  onClick: () => void;
  text?: string;
}

export interface SourcesModalState {
  isVisible: boolean;
  title: string;
  content: string;
}

export interface UseSourcesModalReturn {
  modalState: SourcesModalState;
  openModal: (title: string, content: string) => void;
  closeModal: () => void;
}

export interface NoSourcesMessageProps {
  message: string;
}
