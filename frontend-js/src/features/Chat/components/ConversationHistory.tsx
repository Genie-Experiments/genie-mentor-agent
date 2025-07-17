import React from 'react';
import MessageItem from './MessageItem';
import type { ConversationItem } from '@/types/chatTypes';

interface ConversationHistoryProps {
  conversations: ConversationItem[];
}

const ConversationHistory: React.FC<ConversationHistoryProps> = ({ conversations }) => {
  if (conversations.length === 0) return null;

  return (
    <div className="w-full">
      {conversations.map((item, index) => (
        <MessageItem key={item.id} item={item} index={index} />
      ))}
    </div>
  );
};

export default React.memo(ConversationHistory);
