import React, { useState, useRef, useEffect } from 'react';

export interface TooltipContentProps {
  title: string;
  subtitle: string;
}

export interface TooltipProps {
  content: string | TooltipContentProps;
  children: React.ReactNode;
  position?: 'top' | 'bottom' | 'left' | 'right';
}

const Tooltip: React.FC<TooltipProps> = ({ content, children, position = 'top' }) => {
  const [visible, setVisible] = useState(false);
  const tooltipRef = useRef<HTMLDivElement>(null);
  const tooltipArrowRef = useRef<HTMLDivElement>(null);
  const childRef = useRef<HTMLSpanElement>(null);

  // Position the tooltip based on the child element
  useEffect(() => {
    if (visible && tooltipRef.current && childRef.current && tooltipArrowRef.current) {
      const childRect = childRef.current.getBoundingClientRect();
      const tooltipRect = tooltipRef.current.getBoundingClientRect();
      const arrowSize = 8; // Size of the triangle arrow

      let top = 0;
      let left = 0;
      let arrowLeft = 0;
      let arrowTop = 0;

      switch (position) {
        case 'top':
          top = childRect.top - tooltipRect.height - arrowSize;
          left = childRect.left + childRect.width / 2 - tooltipRect.width / 2;
          // Center the arrow on the child element
          arrowLeft = tooltipRect.width / 2 - arrowSize;
          arrowTop = tooltipRect.height;
          break;
        case 'bottom':
          top = childRect.bottom + arrowSize;
          left = childRect.left + childRect.width / 2 - tooltipRect.width / 2;
          arrowLeft = tooltipRect.width / 2 - arrowSize;
          arrowTop = -arrowSize;
          tooltipArrowRef.current.style.borderBottom = '8px solid #002835';
          tooltipArrowRef.current.style.borderTop = 'none';
          break;
        case 'left':
          top = childRect.top + childRect.height / 2 - tooltipRect.height / 2;
          left = childRect.left - tooltipRect.width - arrowSize;
          arrowLeft = tooltipRect.width;
          arrowTop = tooltipRect.height / 2 - arrowSize;
          tooltipArrowRef.current.style.borderLeft = '8px solid #002835';
          tooltipArrowRef.current.style.borderRight = 'none';
          break;
        case 'right':
          top = childRect.top + childRect.height / 2 - tooltipRect.height / 2;
          left = childRect.right + arrowSize;
          arrowLeft = -arrowSize;
          arrowTop = tooltipRect.height / 2 - arrowSize;
          tooltipArrowRef.current.style.borderRight = '8px solid #002835';
          tooltipArrowRef.current.style.borderLeft = 'none';
          break;
      }

      // Make sure tooltip stays within viewport
      const viewport = {
        width: window.innerWidth,
        height: window.innerHeight,
      };

      const originalLeft = left;

      if (left < 4) left = 4;
      if (top < 4) top = 4;
      if (left + tooltipRect.width > viewport.width - 4) {
        left = viewport.width - tooltipRect.width - 4;
      }
      if (top + tooltipRect.height > viewport.height - 4) {
        top = viewport.height - tooltipRect.height - 4;
      }

      // Adjust arrow if tooltip position was constrained by viewport
      if (position === 'top' || position === 'bottom') {
        arrowLeft += originalLeft - left;
      }

      // Position tooltip and arrow
      tooltipRef.current.style.top = `${top}px`;
      tooltipRef.current.style.left = `${left}px`;
      tooltipArrowRef.current.style.left = `${arrowLeft}px`;
      tooltipArrowRef.current.style.top = `${arrowTop}px`;
    }
  }, [visible, position]);

  // Render tooltip content based on type
  const renderContent = () => {
    if (typeof content === 'string') {
      return <div>{content}</div>;
    } else {
      return (
        <>
          <div
            style={{
              color: '#FFF',
              fontFamily: 'Inter, sans-serif',
              fontSize: '16px',
              fontStyle: 'normal',
              fontWeight: 600,
              lineHeight: '23px',
            }}
          >
            {content.title}
          </div>
          <div
            style={{
              color: '#FFF',
              fontFamily: 'Inter, sans-serif',
              fontSize: '14px',
              fontStyle: 'normal',
              fontWeight: 400,
              lineHeight: '23px',
            }}
          >
            {content.subtitle}
          </div>
        </>
      );
    }
  };

  return (
    <span
      ref={childRef}
      onMouseEnter={() => setVisible(true)}
      onMouseLeave={() => setVisible(false)}
      style={{ position: 'relative', display: 'inline' }}
    >
      {children}
      {visible && (
        <div
          ref={tooltipRef}
          style={{
            position: 'fixed',
            zIndex: 1000,
            backgroundColor: '#002835',
            color: 'white',
            padding: '7px 16px',
            borderRadius: '5px',
            boxShadow: '0 4px 8px rgba(0, 0, 0, 0.25)',
            pointerEvents: 'none',
            display: 'inline-flex',
            flexDirection: 'column',
            alignItems: 'flex-start',
            gap: '3px',
            opacity: 1,
            animation: 'tooltip-fade-in 0.2s ease-in-out',
          }}
        >
          {renderContent()}
          <div
            ref={tooltipArrowRef}
            style={{
              position: 'absolute',
              width: 0,
              height: 0,
              borderLeft: '8px solid transparent',
              borderRight: '8px solid transparent',
              borderTop: '8px solid #002835',
              filter: 'drop-shadow(0 2px 2px rgba(0, 0, 0, 0.2))',
            }}
          />
        </div>
      )}
    </span>
  );
};

export default Tooltip;
