import { cn } from '@/lib/utils';
import React from 'react';

interface ActionButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary';
  size?: 'default' | 'small' | 'large';
  children: React.ReactNode;
  className?: string;
}

const ActionButton: React.FC<ActionButtonProps> = ({
  variant = 'primary',
  size = 'default',
  children,
  className,
  ...props
}) => {
  return (
    <button
      className={cn(
        'flex items-center justify-center gap-2.5 rounded-lg',
        variant === 'primary' && 'bg-white font-semibold text-[#00A599]',
        variant === 'secondary' && 'bg-transparent text-white',
        size === 'default' && 'w-[266px] px-[10px] py-[17px] text-lg',
        size === 'small' && 'p-1.5 text-sm',
        size === 'large' && 'p-4 text-xl',
        className
      )}
      {...props}
    >
      {children}
    </button>
  );
};

export default ActionButton;
