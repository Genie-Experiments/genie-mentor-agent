import React from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import CitationRenderer from '../CitationRenderer';
import CodeBlock from '../../../../components/ui/CodeBlock';
import { SectionHeader } from './SectionHeader';
import type { ExecutorAgent } from '../../../../lib/api-service';

interface AnswerSectionProps {
  finalAnswer: string;
  executorAgent?: ExecutorAgent;
  onCitationClick: (index: number) => void;
}

type MarkdownProps = {
  children?: React.ReactNode;
  [key: string]: unknown;
};

/**
 * Answer section with markdown rendering and citation support
 */
export const AnswerSection: React.FC<AnswerSectionProps> = ({
  finalAnswer,
  executorAgent,
  onCitationClick,
}) => {
  const markdownComponents = {
    p: ({ children, ...props }: MarkdownProps) => {
      if (typeof children === 'string') {
        return (
          <p {...props}>
            <CitationRenderer
              onCitationClick={onCitationClick}
              metadata={(executorAgent?.metadata_by_source as Record<string, unknown[]>) || {}}
              dataSources={Object.keys(executorAgent?.metadata_by_source || {})}
            >
              {children}
            </CitationRenderer>
          </p>
        );
      }
      return <p {...props}>{children}</p>;
    },

    strong: ({ children, ...props }: MarkdownProps) => (
      <strong className="font-bold" {...props}>
        {children}
      </strong>
    ),

    em: ({ children, ...props }: MarkdownProps) => (
      <em className="italic" {...props}>
        {children}
      </em>
    ),

    pre: ({ children, ...props }: MarkdownProps) => {
      const codeElement = React.Children.toArray(children).find(
        (child) => React.isValidElement(child) && child.type === 'code'
      );

      if (React.isValidElement(codeElement)) {
        const element = codeElement as React.ReactElement<{
          className?: string;
          children?: React.ReactNode;
        }>;

        const className = element.props.className || '';
        const match = className.match(/language-(\w+)/);
        const language = match ? match[1] : 'plaintext';

        let code = '';
        if (element.props.children) {
          if (typeof element.props.children === 'string') {
            code = element.props.children;
          } else if (Array.isArray(element.props.children)) {
            code = element.props.children.join('');
          }
        }

        return <CodeBlock code={code} language={language} />;
      }

      return <pre {...props}>{children}</pre>;
    },

    ul: ({ children, ...props }: MarkdownProps) => (
      <ul className="mb-2 list-disc pl-6" {...props}>
        {children}
      </ul>
    ),

    ol: ({ children, ...props }: MarkdownProps) => (
      <ol className="mb-2 list-decimal pl-6" {...props}>
        {children}
      </ol>
    ),

    li: ({ children, ...props }: MarkdownProps) => (
      <li className="mb-1" {...props}>
        <CitationRenderer
          onCitationClick={onCitationClick}
          metadata={(executorAgent?.metadata_by_source as Record<string, unknown[]>) || {}}
          dataSources={Object.keys(executorAgent?.metadata_by_source || {})}
        >
          {children}
        </CitationRenderer>
      </li>
    ),
  };

  return (
    <div>
      <SectionHeader title="Answer" />
      <div
        style={{
          color: '#002835',
          fontFamily: 'Inter',
          fontSize: 16,
          fontWeight: 400,
          lineHeight: '23px',
          marginBottom: '30px',
        }}
        className="markdown-content"
      >
        <ReactMarkdown
          remarkPlugins={[remarkGfm]}
          // eslint-disable-next-line @typescript-eslint/no-explicit-any
          components={markdownComponents as any}
        >
          {finalAnswer}
        </ReactMarkdown>
      </div>
    </div>
  );
};
