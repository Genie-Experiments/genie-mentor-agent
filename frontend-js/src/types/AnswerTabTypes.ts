import type { ExecutorAgent } from "@/lib/api-service";

export interface AnswerTabProps {
  finalAnswer: string;
  executorAgent?: ExecutorAgent;
}

export interface SourceCard {
  title: string;
  url: string;
  description: string;
}

export interface ContextCard {
  title: string;
  content: string;
}

export interface ContextModalState {
  isVisible: boolean;
  title: string;
  content: string;
}

export interface SectionProps {
  className?: string;
  children: React.ReactNode;
}

export interface SectionHeaderProps {
  title: string;
  className?: string;
}
