import React, { useState } from 'react';
import type {
  ExecutorAgent,
  WebsearchMetadata,
  GitHubMetadata,
  NotionMetadata,
} from '../../../lib/api-service';
import ContextModal from './ContextModal';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import './markdown-styles.css';

interface AnswerTabProps {
  finalAnswer: string;
  executorAgent?: ExecutorAgent;
}

interface ContextCardProps {
  title: string;
  content: string;
  index: number;
  onClick: (index: number) => void;
}

const ContextCard: React.FC<ContextCardProps> = ({ title, content, index, onClick }) => (
  <div
    onClick={() => onClick(index)}
    className="flex cursor-pointer flex-col items-start justify-center gap-[10px] rounded-[8px] border border-[#9CBFBC] bg-white transition-shadow hover:shadow-[0px_12px_21px_0px_#CDE6E5]"
    style={{ width: 243, padding: '15px 18px' }}
  >
    <div className="flex items-center gap-2">
      <span style={{ width: 16, height: 16, display: 'inline-flex', alignItems: 'center' }}>
        <svg
          xmlns="http://www.w3.org/2000/svg"
          width="12"
          height="11"
          viewBox="0 0 12 11"
          fill="none"
        >
          <path
            d="M5.04894 0.927049C5.3483 0.00573826 6.6517 0.00573993 6.95106 0.927051L7.5716 2.83688C7.70547 3.2489 8.08943 3.52786 8.52265 3.52786H10.5308C11.4995 3.52786 11.9023 4.76748 11.1186 5.33688L9.49395 6.51722C9.14347 6.77187 8.99681 7.22323 9.13068 7.63525L9.75122 9.54508C10.0506 10.4664 8.9961 11.2325 8.21238 10.6631L6.58778 9.48278C6.2373 9.22813 5.7627 9.22814 5.41221 9.48278L3.78761 10.6631C3.0039 11.2325 1.94942 10.4664 2.24878 9.54508L2.86932 7.63526C3.00319 7.22323 2.85653 6.77186 2.50604 6.51722L0.881445 5.33688C0.0977311 4.76748 0.500508 3.52786 1.46923 3.52786H3.47735C3.91057 3.52786 4.29453 3.2489 4.4284 2.83688L5.04894 0.927049Z"
            fill="#00A599"
          />
        </svg>
      </span>
      <span
        style={{
          color: '#002835',
          fontFamily: 'Inter',
          fontSize: 13,
          fontWeight: 400,
          opacity: 0.6,
          overflow: 'hidden',
          textOverflow: 'ellipsis',
          whiteSpace: 'nowrap',
          maxWidth: 180,
        }}
      >
        {title || `Context ${index + 1}`}
      </span>
    </div>
    <div
      style={{
        color: '#002835',
        fontFamily: 'Inter',
        fontSize: 14,
        fontWeight: 400,
        overflow: 'hidden',
        textOverflow: 'ellipsis',
        display: '-webkit-box',
        WebkitLineClamp: 2,
        WebkitBoxOrient: 'vertical',
        maxWidth: 200,
        height: '42px',
      }}
    >
      {content}
    </div>
  </div>
);

const AnswerTab: React.FC<AnswerTabProps> = ({ finalAnswer, executorAgent }) => {
  const [modalVisible, setModalVisible] = useState(false);
  const [activeContext, setActiveContext] = useState<{ title: string; content: string }>({
    title: '',
    content: '',
  });

  const openContextModal = (index: number) => {
    if (!executorAgent?.documents_by_source?.knowledgebase) return;

    const content = executorAgent.documents_by_source.knowledgebase[index] || '';
    const title =
      executorAgent.metadata_by_source?.knowledgebase?.[index]?.title || `Context ${index + 1}`;

    setActiveContext({ title, content });
    setModalVisible(true);
  };

  const closeContextModal = () => {
    setModalVisible(false);
  };

  // Function to get top sources from different metadata types
  const getTopSources = (): Array<{ title: string; url: string; description: string }> => {
    const sources: Array<{ title: string; url: string; description: string }> = [];

    if (executorAgent?.metadata_by_source) {
      // Add websearch sources
      if (executorAgent.metadata_by_source.websearch) {
        executorAgent.metadata_by_source.websearch.forEach((source: WebsearchMetadata) => {
          sources.push({
            title: source.title || 'Untitled',
            url: source.url || '#',
            description: source.description || 'No description available',
          });
        });
      }

      // Add GitHub sources
      if (executorAgent.metadata_by_source.github) {
        executorAgent.metadata_by_source.github.forEach((source: GitHubMetadata) => {
          sources.push({
            title: source.repo || 'Untitled',
            url: source.url || '#',
            description: `File: ${source.file_path}`,
          });
        });
      }

      // Add Notion sources
      if (executorAgent.metadata_by_source.notion) {
        executorAgent.metadata_by_source.notion.forEach((source: NotionMetadata) => {
          sources.push({
            title: source.title || 'Untitled',
            url: source.url || '#',
            description: `Page ID: ${source.page_id}`,
          });
        });
      }
    }

    // Return top 3 sources or fewer if there aren't enough
    return sources.slice(0, 3);
  };

  // Get context data from knowledgebase
  const getContexts = (): Array<{ title: string; content: string }> => {
    const contexts: Array<{ title: string; content: string }> = [];

    if (
      executorAgent?.documents_by_source?.knowledgebase &&
      executorAgent.documents_by_source.knowledgebase.length > 0
    ) {
      executorAgent.documents_by_source.knowledgebase.forEach((content: string, index: number) => {
        // Get title from metadata if available, otherwise use a default
        const title =
          executorAgent.metadata_by_source?.knowledgebase?.[index]?.title ||
          executorAgent.metadata_by_source?.knowledgebase?.[index]?.document_title ||
          `Context ${index + 1}`;
        contexts.push({
          title,
          content: content || 'No content available',
        });
      });
    }

    return contexts.slice(0, 3); // Show top 3 contexts
  };

  // Check if there are any contexts available
  const hasContexts = (): boolean => {
    return (
      !!executorAgent?.documents_by_source?.knowledgebase &&
      executorAgent.documents_by_source.knowledgebase.length > 0
    );
  };

  // Get the sources and contexts to display
  const topSources = getTopSources();
  const contexts = getContexts();
  const contextsAvailable = hasContexts();

  // Function to truncate URL
  const truncateUrl = (url: string, maxLength: number = 30): string => {
    if (url.length <= maxLength) return url;

    // Try to keep the domain and truncate the path
    const urlObj = new URL(url);
    const domain = urlObj.hostname;
    const path = url.substring(url.indexOf(domain) + domain.length);

    if (domain.length >= maxLength - 3) {
      return domain.substring(0, maxLength - 3) + '...';
    }

    const availableChars = maxLength - domain.length - 3;
    return domain + path.substring(0, availableChars) + '...';
  };

  return (
    <div className="flex w-full flex-col gap-8">
      {/* Top Sources Section - Only shown if sources are available */}
      {topSources.length > 0 && (
        <div>
          <div
            className="mb-4"
            style={{
              color: '#002835',
              fontFamily: 'Inter',
              fontSize: 16,
              fontWeight: 500,
              textTransform: 'uppercase',
              opacity: 0.4,
            }}
          >
            Top sources
          </div>
          <div className="flex w-full gap-4" style={{ rowGap: 13 }}>
            {topSources.map((source, i) => (
              <a
                key={i}
                href={source.url}
                target="_blank"
                rel="noopener noreferrer"
                className="flex flex-col items-start justify-center gap-[10px] rounded-[8px] border border-[#9CBFBC] bg-white transition-shadow hover:shadow-[0px_12px_21px_0px_#CDE6E5]"
                style={{ width: 243, padding: '15px 18px', textDecoration: 'none' }}
              >
                <div className="flex items-center gap-2">
                  {/* Star Icon */}
                  <span
                    style={{ width: 16, height: 16, display: 'inline-flex', alignItems: 'center' }}
                  >
                    <svg
                      xmlns="http://www.w3.org/2000/svg"
                      width="12"
                      height="11"
                      viewBox="0 0 12 11"
                      fill="none"
                    >
                      <path
                        d="M5.04894 0.927049C5.3483 0.00573826 6.6517 0.00573993 6.95106 0.927051L7.5716 2.83688C7.70547 3.2489 8.08943 3.52786 8.52265 3.52786H10.5308C11.4995 3.52786 11.9023 4.76748 11.1186 5.33688L9.49395 6.51722C9.14347 6.77187 8.99681 7.22323 9.13068 7.63525L9.75122 9.54508C10.0506 10.4664 8.9961 11.2325 8.21238 10.6631L6.58778 9.48278C6.2373 9.22813 5.7627 9.22814 5.41221 9.48278L3.78761 10.6631C3.0039 11.2325 1.94942 10.4664 2.24878 9.54508L2.86932 7.63526C3.00319 7.22323 2.85653 6.77186 2.50604 6.51722L0.881445 5.33688C0.0977311 4.76748 0.500508 3.52786 1.46923 3.52786H3.47735C3.91057 3.52786 4.29453 3.2489 4.4284 2.83688L5.04894 0.927049Z"
                        fill="#00A599"
                      />
                    </svg>
                  </span>
                  <span
                    style={{
                      color: '#002835',
                      fontFamily: 'Inter',
                      fontSize: 13,
                      fontWeight: 400,
                      opacity: 0.6,
                    }}
                  >
                    {truncateUrl(source.url)}
                  </span>
                </div>
                <div
                  style={{
                    color: '#002835',
                    fontFamily: 'Inter',
                    fontSize: 14,
                    fontWeight: 400,
                    overflow: 'hidden',
                    textOverflow: 'ellipsis',
                    display: '-webkit-box',
                    WebkitLineClamp: 2,
                    WebkitBoxOrient: 'vertical',
                    maxWidth: 200,
                    height: '42px',
                  }}
                >
                  {source.title}
                </div>
              </a>
            ))}
          </div>
        </div>
      )}

      {/* Context Section - Only shown if contexts are available */}
      {contextsAvailable && (
        <div>
          <div
            className="mb-4"
            style={{
              color: '#002835',
              fontFamily: 'Inter',
              fontSize: 16,
              fontWeight: 500,
              textTransform: 'uppercase',
              opacity: 0.4,
            }}
          >
            Context
          </div>
          <div className="flex w-full gap-4" style={{ rowGap: 13 }}>
            {contexts.map((context, index) => (
              <ContextCard
                key={index}
                title={context.title}
                content={context.content}
                index={index}
                onClick={openContextModal}
              />
            ))}
          </div>
        </div>
      )}

      {/* Context Modal */}
      <ContextModal
        isVisible={modalVisible}
        title={activeContext.title}
        content={activeContext.content}
        onClose={closeContextModal}
      />

      {/* Answer Section */}
      <div>
        <div
          className="mb-2"
          style={{
            color: '#002835',
            fontFamily: 'Inter',
            fontSize: 16,
            fontWeight: 500,
            textTransform: 'uppercase',
            opacity: 0.4,
          }}
        >
          Answer
        </div>{' '}
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
          <ReactMarkdown remarkPlugins={[remarkGfm]}>{finalAnswer}</ReactMarkdown>
        </div>
      </div>
    </div>
  );
};

export default AnswerTab;
