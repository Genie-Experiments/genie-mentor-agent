import React, { useState } from 'react';
import type {
  ExecutorAgent,
  KnowledgebaseMetadata,
  GitHubMetadata,
  NotionMetadata,
  WebsearchMetadata,
} from '../../../lib/api-service';
import ContextModal from './ContextModal';

interface SourcesTabProps {
  executorAgent: ExecutorAgent;
}

const SourcesTab: React.FC<SourcesTabProps> = ({ executorAgent }) => {
  const [modalVisible, setModalVisible] = useState(false);
  const [activeContext, setActiveContext] = useState<{ title: string; content: string }>({
    title: '',
    content: '',
  });

  const openContextModal = (title: string, index: number) => {
    if (!executorAgent.documents_by_source?.knowledgebase) return;

    const content = executorAgent.documents_by_source.knowledgebase[index] || '';

    setActiveContext({ title, content });
    setModalVisible(true);
  };

  const closeContextModal = () => {
    setModalVisible(false);
  };
  const sectionTitleStyle: React.CSSProperties = {
    color: '#002835',
    fontFamily: 'Inter',
    fontSize: '16px',
    fontStyle: 'normal',
    fontWeight: 500,
    lineHeight: 'normal',
    textTransform: 'uppercase',
    opacity: 0.4,
  };

  const itemTitleStyle: React.CSSProperties = {
    color: '#002835',
    fontFamily: 'Inter',
    fontSize: '16px',
    fontStyle: 'normal',
    fontWeight: 500,
    lineHeight: 'normal',
  };

  const itemDetailStyle: React.CSSProperties = {
    color: '#002835',
    fontFamily: 'Inter',
    fontSize: '14px',
    fontStyle: 'normal',
    fontWeight: 400,
    lineHeight: 'normal',
  };

  const linkStyle: React.CSSProperties = {
    color: '#002835',
    fontFamily: 'Inter',
    fontSize: '13px',
    fontStyle: 'normal',
    fontWeight: 400,
    lineHeight: 'normal',
    opacity: 0.6,
  };
  const separatorStyle: React.CSSProperties = {
    background: '#9CBFBC',
    height: '1px',
    margin: '27px 0',
  };

  const viewDetailsStyle: React.CSSProperties = {
    color: '#00A599',
    fontFamily: 'Inter',
    fontSize: '16px',
    fontStyle: 'normal',
    fontWeight: 500,
    lineHeight: '24px',
    cursor: 'pointer',
    display: 'flex',
    alignItems: 'center',
  };

  const renderKnowledgeBaseSources = (metadata: KnowledgebaseMetadata[]) => (
    <ol style={{ paddingLeft: 0 }}>
      {metadata.map((item, index) => (
        <li
          key={index}
          style={{
            marginBottom: '18px',
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'flex-start',
            listStyle: 'none',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'baseline', gap: '8px' }}>
            <span
              style={{
                ...itemDetailStyle,
                fontWeight: 500,
                fontSize: '16px',
                width: '24px',
                flexShrink: 0,
              }}
            >
              {index + 1}.
            </span>
            <span style={itemTitleStyle}>{item.title || 'Untitled'}</span>
          </div>
          <div style={{ marginLeft: 32, width: '100%' }}>
            <div style={{ height: '14px' }} />
            <div style={{ display: 'flex', flexDirection: 'column', gap: 0 }}>
              <div style={itemDetailStyle}>Source: {item.source}</div>
              <div style={itemDetailStyle}>Page: {item.page}</div>
            </div>
            <div style={{ height: '14px' }} />
            <div
              style={viewDetailsStyle}
              onClick={() => openContextModal(item.title || 'Untitled', index)}
            >
              Show Detail
              <svg
                xmlns="http://www.w3.org/2000/svg"
                width="21"
                height="22"
                viewBox="0 0 21 22"
                fill="none"
                style={{ marginLeft: '8px' }}
              >
                <path
                  d="M7.875 16.25L13.125 11L7.875 5.75"
                  stroke="#00A599"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                />
              </svg>
            </div>
          </div>
        </li>
      ))}
    </ol>
  );
  const renderWebSources = (metadata: WebsearchMetadata[]) => (
    <ol style={{ paddingLeft: 0 }}>
      {metadata.map((item, index) => (
        <li
          key={index}
          style={{
            marginBottom: '18px',
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'flex-start',
            listStyle: 'none',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'baseline', gap: '8px' }}>
            <span
              style={{
                ...itemDetailStyle,
                fontWeight: 500,
                fontSize: '16px',
                width: '24px',
                flexShrink: 0,
              }}
            >
              {index + 1}.
            </span>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <svg
                xmlns="http://www.w3.org/2000/svg"
                width="16"
                height="16"
                viewBox="0 0 12 11"
                fill="none"
              >
                <path
                  d="M5.04894 0.927049C5.3483 0.00573826 6.6517 0.00573993 6.95106 0.927051L7.5716 2.83688C7.70547 3.2489 8.08943 3.52786 8.52265 3.52786H10.5308C11.4995 3.52786 11.9023 4.76748 11.1186 5.33688L9.49395 6.51722C9.14347 6.77187 8.99681 7.22323 9.13068 7.63525L9.75122 9.54508C10.0506 10.4664 8.9961 11.2325 8.21238 10.6631L6.58778 9.48278C6.2373 9.22813 5.7627 9.22814 5.41221 9.48278L3.78761 10.6631C3.0039 11.2325 1.94942 10.4664 2.24878 9.54508L2.86932 7.63526C3.00319 7.22323 2.85653 6.77186 2.50604 6.51722L0.881445 5.33688C0.0977311 4.76748 0.500508 3.52786 1.46923 3.52786H3.47735C3.91057 3.52786 4.29453 3.2489 4.4284 2.83688L5.04894 0.927049Z"
                  fill="#00A599"
                />
              </svg>
              <a href={item.url} target="_blank" rel="noopener noreferrer" style={linkStyle}>
                {item.url}
              </a>
            </div>
          </div>{' '}
          <div style={{ marginLeft: 32, width: '100%' }}>
            <div style={{ height: '10px' }} />
            <div style={itemTitleStyle}>{item.title || 'Untitled'}</div>
            <div style={{ height: '7px' }} />
            <div style={itemDetailStyle}>{item.description || 'No description available.'}</div>
          </div>
        </li>
      ))}
    </ol>
  );
  const mapGitHubToWebsearchMetadata = (metadata: GitHubMetadata[]): WebsearchMetadata[] => {
    const result: WebsearchMetadata[] = [];

    metadata.forEach((item) => {
      if (item.repo_links && item.repo_names) {
        for (let i = 0; i < item.repo_links.length; i++) {
          result.push({
            title: item.repo_names[i] || 'Untitled GitHub Repository',
            description: 'GitHub Repository',
            url: item.repo_links[i] || '#',
          });
        }
      }
    });

    return result;
  };

  const mapNotionToWebsearchMetadata = (metadata: NotionMetadata[]): WebsearchMetadata[] => {
    const result: WebsearchMetadata[] = [];

    metadata.forEach((item) => {
      if (item.doc_links && item.doc_names) {
        for (let i = 0; i < item.doc_links.length; i++) {
          result.push({
            title: item.doc_names[i] || 'Untitled Notion Document',
            description: 'Notion Document',
            url: item.doc_links[i] || '#',
          });
        }
      }
    });

    return result;
  };

  const renderGitHubSources = (metadata: GitHubMetadata[]) =>
    renderWebSources(mapGitHubToWebsearchMetadata(metadata));

  const renderNotionSources = (metadata: NotionMetadata[]) =>
    renderWebSources(mapNotionToWebsearchMetadata(metadata));
  // Helper function to check if all sources are empty or missing
  const hasNoSources = () => {
    const { metadata_by_source } = executorAgent;

    // If metadata_by_source is undefined or null, there are no sources
    if (!metadata_by_source) return true;

    // Check if all source arrays are either undefined, null, or empty
    const hasKnowledgebase =
      metadata_by_source.knowledgebase && metadata_by_source.knowledgebase.length > 0;
    const hasWebsearch = metadata_by_source.websearch && metadata_by_source.websearch.length > 0;
    const hasGithub = metadata_by_source.github && metadata_by_source.github.length > 0;
    const hasNotion = metadata_by_source.notion && metadata_by_source.notion.length > 0;

    // Return true if all source arrays are empty or missing
    return !hasKnowledgebase && !hasWebsearch && !hasGithub && !hasNotion;
  };

  const noSourcesMessageStyle: React.CSSProperties = {
    color: '#002835',
    fontFamily: 'Inter',
    fontSize: '16px',
    fontStyle: 'normal',
    fontWeight: 400,
    lineHeight: 'normal',
    textAlign: 'center',
    padding: '32px 0',
  };
  // Helper function to count how many source types are available
  const countSourceTypes = () => {
    const { metadata_by_source } = executorAgent;
    let count = 0;
    if (metadata_by_source?.knowledgebase && metadata_by_source.knowledgebase.length > 0) count++;
    if (metadata_by_source?.websearch && metadata_by_source.websearch.length > 0) count++;
    if (metadata_by_source?.github && metadata_by_source.github.length > 0) count++;
    if (metadata_by_source?.notion && metadata_by_source.notion.length > 0) count++;
    return count;
  };

  // Get the total number of source types
  const sourceTypeCount = countSourceTypes();

  // Track which source type we're currently rendering
  let renderedSourcesCount = 0;

  return (
    <div className="flex w-full flex-col gap-4 font-['Inter'] text-[#002835]">
      {hasNoSources() ? (
        <div style={noSourcesMessageStyle}>No sources available for this answer.</div>
      ) : (
        <>
          {executorAgent.metadata_by_source?.knowledgebase &&
            executorAgent.metadata_by_source.knowledgebase.length > 0 && (
              <>
                <div style={sectionTitleStyle}>Knowledge Base Sources</div>
                {renderKnowledgeBaseSources(executorAgent.metadata_by_source.knowledgebase)}
                {++renderedSourcesCount < sourceTypeCount && <div style={separatorStyle} />}
              </>
            )}
          {executorAgent.metadata_by_source?.websearch &&
            executorAgent.metadata_by_source.websearch.length > 0 && (
              <>
                <div style={sectionTitleStyle}>Web Sources</div>
                {renderWebSources(executorAgent.metadata_by_source.websearch)}
                {++renderedSourcesCount < sourceTypeCount && <div style={separatorStyle} />}
              </>
            )}
          {executorAgent.metadata_by_source?.github &&
            executorAgent.metadata_by_source.github.length > 0 && (
              <>
                <div style={sectionTitleStyle}>GitHub Sources</div>
                {renderGitHubSources(executorAgent.metadata_by_source.github)}
                {++renderedSourcesCount < sourceTypeCount && <div style={separatorStyle} />}
              </>
            )}
          {executorAgent.metadata_by_source?.notion &&
            executorAgent.metadata_by_source.notion.length > 0 && (
              <>
                <div style={sectionTitleStyle}>Notion Sources</div>
                {renderNotionSources(executorAgent.metadata_by_source.notion)}
              </>
            )}
        </>
      )}
      <ContextModal
        isVisible={modalVisible}
        onClose={closeContextModal}
        title={activeContext.title}
        content={activeContext.content}
      />
    </div>
  );
};

export default SourcesTab;
