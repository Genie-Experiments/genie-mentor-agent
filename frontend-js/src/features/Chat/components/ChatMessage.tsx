import React from 'react';
import type { Message } from '../../../lib/types';

interface ChatMessageProps {
  message: Message;
}

const ChatMessage: React.FC<ChatMessageProps> = ({ message }) => {
  const isUser = message.sender === 'user';

  return (
    <div className={`mb-4 flex ${isUser ? 'justify-end' : 'justify-start'}`}>
      <div
        className={`max-w-[80%] rounded-lg px-4 py-3 ${
          isUser
            ? 'bg-[#E6F7F6] text-[#002835]'
            : 'border border-[#9CBFBC] bg-[#FFFFFF] text-[#002835]'
        }`}
      >
        <div className="font-['Inter'] text-[16px]">{message.content}</div>
        <div className="mt-1 text-right text-xs opacity-50">
          {new Date(message.timestamp).toLocaleTimeString([], {
            hour: '2-digit',
            minute: '2-digit',
          })}
        </div>
      </div>
    </div>
  );
};

export default ChatMessage;
