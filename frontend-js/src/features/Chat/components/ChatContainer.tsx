import { CHAT_THEME } from '@/constant/chatTheme';
import React from 'react';

interface ChatContainerProps {
  children: React.ReactNode;
  chatAreaRef: React.RefObject<HTMLDivElement | null>;
}

const ChatContainer: React.FC<ChatContainerProps> = ({ children, chatAreaRef }) => {
  return (
    <div className="flex w-full justify-center">
      <div
        ref={chatAreaRef}
        className="auto-scroll-chat flex w-full flex-col items-start px-4 pt-8"
        style={{
          maxWidth: CHAT_THEME.layout.maxWidth,
          maxHeight: CHAT_THEME.layout.chatHeight,
        }}
      >
        {children}
        <div className="w-full py-8" aria-hidden="true" />
      </div>
    </div>
  );
};

export default ChatContainer;
