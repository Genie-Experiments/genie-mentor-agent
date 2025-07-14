import React from 'react';
import type { LoadingIndicatorProps } from '@/types/chatTypes';
import { CHAT_THEME, UI_TEXT } from '@/constant/chatTheme';

const LoadingIndicator: React.FC<LoadingIndicatorProps> = ({
  message = UI_TEXT.processing,
  className = '',
}) => {
  return (
    <div
      className={`my-4 flex w-full items-center justify-center ${className}`}
      role="status"
      aria-live="polite"
      aria-label={message}
    >
      <div
        className="mr-2 h-5 w-5 animate-spin rounded-full border-2 border-t-transparent"
        style={{
          borderColor: CHAT_THEME.colors.primary,
          borderTopColor: 'transparent',
        }}
        aria-hidden="true"
      />
      <span
        className="text-[16px]"
        style={{
          fontFamily: CHAT_THEME.typography.fontFamily,
          color: CHAT_THEME.colors.text.primary,
        }}
      >
        {message}
      </span>
    </div>
  );
};

export default LoadingIndicator;
