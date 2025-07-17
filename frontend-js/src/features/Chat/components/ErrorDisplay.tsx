import React from 'react';
import { AlertCircle } from 'lucide-react';
import type { ErrorDisplayProps } from '@/types/chatTypes';
import { CHAT_THEME } from '@/constant/chatTheme';

const ErrorDisplay: React.FC<ErrorDisplayProps> = ({ error, className = '' }) => {
  if (!error) return null;

  return (
    <div className={`mt-6 ${className}`} role="alert" aria-live="polite">
      <div
        className="flex items-center rounded-md border p-3"
        style={{
          borderColor: CHAT_THEME.colors.error.border,
          backgroundColor: CHAT_THEME.colors.error.background,
        }}
      >
        <AlertCircle
          className="mr-2 h-5 w-5 flex-shrink-0"
          style={{ color: CHAT_THEME.colors.error.primary }}
          aria-hidden="true"
        />
        <div className="text-[16px]" style={{ color: CHAT_THEME.colors.error.primary }}>
          {error}
        </div>
      </div>
    </div>
  );
};

export default ErrorDisplay;
