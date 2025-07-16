import React from 'react';
import ContextModal from '../ContextModal';
import { SourceSection } from './SourceSection';
import { NoSourcesMessage } from './NoSourcesMessage';
import { KnowledgeBaseSourcesList } from './KnowledgeBaseSourcesList';
import { WebSourcesList } from './WebSourcesList';
import { useSourcesModal } from '@/hooks/useSourcesModal';
import {
  hasNoSources,
  countSourceTypes,
  mapGitHubToWebsearchMetadata,
  mapNotionToWebsearchMetadata,
  getKnowledgeBaseDocument,
  getSourceTitle,
} from '@/utils/sourcesTabUtils';
import { SOURCES_SECTION_TITLES, MESSAGES } from '@/constant/sourcesTab';
import type { SourcesTabProps } from '@/types/SourcesTabTypes';

const SourcesTab: React.FC<SourcesTabProps> = ({ executorAgent }) => {
  const { modalState, openModal, closeModal } = useSourcesModal();

  const handleKnowledgeBaseDetail = (title: string, index: number) => {
    const content = getKnowledgeBaseDocument(executorAgent, index);
    const modalTitle = getSourceTitle(title);
    openModal(modalTitle, content);
  };

  // Ensure executorAgent and metadata exist to prevent errors
  if (!executorAgent || !executorAgent.metadata_by_source) {
    return (
      <div className="flex w-full flex-col gap-4 font-['Inter'] text-[#002835]">
        <NoSourcesMessage message={MESSAGES.NO_SOURCE_INFO} />
      </div>
    );
  }

  const hasSourcesAvailable = !hasNoSources(executorAgent);

  if (!hasSourcesAvailable) {
    return (
      <div className="flex w-full flex-col gap-4 font-['Inter'] text-[#002835]">
        <NoSourcesMessage message={MESSAGES.NO_SOURCES} />
      </div>
    );
  }

  const sourceTypeCount = countSourceTypes(executorAgent);
  const { metadata_by_source } = executorAgent;

  // Track which source type we're currently rendering
  let renderedSourcesCount = 0;

  return (
    <div className="flex w-full flex-col gap-4 font-['Inter'] text-[#002835]">
      {/* Knowledge Base Sources */}
      {metadata_by_source.knowledgebase && metadata_by_source.knowledgebase.length > 0 && (
        <SourceSection
          title={SOURCES_SECTION_TITLES.KNOWLEDGE_BASE}
          showSeparator={++renderedSourcesCount < sourceTypeCount}
        >
          <KnowledgeBaseSourcesList
            metadata={metadata_by_source.knowledgebase}
            onShowDetail={handleKnowledgeBaseDetail}
          />
        </SourceSection>
      )}

      {/* Web Sources */}
      {metadata_by_source.websearch && metadata_by_source.websearch.length > 0 && (
        <SourceSection
          title={SOURCES_SECTION_TITLES.WEB_SOURCES}
          showSeparator={++renderedSourcesCount < sourceTypeCount}
        >
          <WebSourcesList metadata={metadata_by_source.websearch} />
        </SourceSection>
      )}

      {/* GitHub Sources */}
      {metadata_by_source.github && metadata_by_source.github.length > 0 && (
        <SourceSection
          title={SOURCES_SECTION_TITLES.GITHUB_SOURCES}
          showSeparator={++renderedSourcesCount < sourceTypeCount}
        >
          <WebSourcesList metadata={mapGitHubToWebsearchMetadata(metadata_by_source.github)} />
        </SourceSection>
      )}

      {/* Notion Sources */}
      {metadata_by_source.notion && metadata_by_source.notion.length > 0 && (
        <SourceSection title={SOURCES_SECTION_TITLES.NOTION_SOURCES} showSeparator={false}>
          <WebSourcesList metadata={mapNotionToWebsearchMetadata(metadata_by_source.notion)} />
        </SourceSection>
      )}

      {/* Context Modal */}
      <ContextModal
        isVisible={modalState.isVisible}
        onClose={closeModal}
        title={modalState.title}
        content={modalState.content}
      />
    </div>
  );
};

export default SourcesTab;
