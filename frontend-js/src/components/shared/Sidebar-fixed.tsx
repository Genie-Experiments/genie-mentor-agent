import React, { useState } from 'react';
import ActionButton from '../ui/ActionButton';
import HamburgerIcon from '../ui/HamburgerIcon';
import PlusIcon from '../ui/PlusIcon';
import { cn } from '@/lib/utils';

interface Conversation {
  id: string;
  title: string;
}

interface SidebarProps {
  conversations?: Conversation[];
}

const Sidebar: React.FC<SidebarProps> = ({ conversations = [] }) => {
  const [isCollapsed, setIsCollapsed] = useState(false);

  const toggleSidebar = () => {
    setIsCollapsed(!isCollapsed);
  };

  const handleNewChat = () => {
    console.log('New chat started');
  };

  return (
    <div
      className={cn(
        'relative flex h-screen flex-col overflow-hidden bg-[#00A599] transition-all duration-300 ease-in-out',
        isCollapsed ? 'w-[90px]' : 'w-[300px]',
        'rounded-r-[26px]'
      )}
    >
      {/* Hamburger Menu - positioned absolute */}
      <div className="absolute top-[35px] left-6 z-10">
        <HamburgerIcon isOpen={false} onClick={toggleSidebar} />
      </div>

      {/* Main Content */}
      <div
        className={cn(
          'flex w-full flex-col p-6 pt-[90px]',
          isCollapsed ? 'items-center' : 'items-start'
        )}
      >
        {/* Title */}
        <div
          className={cn(
            'mb-6 overflow-hidden text-white transition-all duration-200 ease-in-out',
            isCollapsed ? 'invisible absolute h-0 w-0 opacity-0' : 'visible relative opacity-100'
          )}
          style={{
            transitionDelay: isCollapsed ? '0ms' : '150ms',
          }}
        >
          <h1 className="text-3xl leading-normal font-bold">GEN AI</h1>
          <h2 className="text-3xl leading-normal font-medium">MENTOR AGENT</h2>
        </div>

        {/* Button Container - with fixed width to prevent overflow */}
        <div
          className={cn(
            'transition-all duration-300 ease-in-out',
            isCollapsed ? 'w-[44px]' : 'w-full'
          )}
          style={{
            transitionDelay: '50ms', // Slight delay to sync with sidebar animation
          }}
        >
          {isCollapsed ? (
            <PlusIcon onClick={handleNewChat} className="flex-shrink-0 cursor-pointer" />
          ) : (
            <ActionButton onClick={handleNewChat} className="mb-6 cursor-pointer">
              Start New Chat
            </ActionButton>
          )}
        </div>

        {/* Separator with improved animation */}
        <div
          className={cn(
            'mb-6 -ml-6 h-[1px] transform bg-white px-6 transition-all duration-200 ease-in-out',
            isCollapsed
              ? 'invisible absolute w-0 origin-left scale-x-0 opacity-0'
              : 'visible relative w-[300px] scale-x-100 opacity-80'
          )}
          style={{
            transitionDelay: isCollapsed ? '0ms' : '150ms',
            transitionProperty: 'width, opacity, transform, visibility',
          }}
        ></div>

        {/* History Section with improved animation */}
        <div
          className={cn(
            'w-full overflow-hidden transition-all duration-200 ease-in-out',
            isCollapsed ? 'invisible max-h-0 opacity-0' : 'visible max-h-[2000px] opacity-100'
          )}
          style={{
            transitionDelay: isCollapsed ? '0ms' : '150ms',
          }}
        >
          <h3 className="text-overflow-ellipsis mb-4 overflow-hidden font-[Inter] text-[16px] leading-normal font-medium text-white opacity-50">
            History
          </h3>

          <div className="flex flex-col gap-2">
            {conversations.length > 0 ? (
              conversations.map((convo) => (
                <div
                  key={convo.id}
                  className="mb-2 flex h-[57px] w-[266px] items-center rounded-[8px] bg-[rgba(255,232,223,0.19)] px-4"
                >
                  <p className="text-overflow-ellipsis w-full truncate overflow-hidden font-[Inter] text-[18px] leading-normal font-medium whitespace-nowrap text-white">
                    {convo.title}
                  </p>
                </div>
              ))
            ) : (
              <div className="text-sm text-white opacity-50">No conversation history</div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Sidebar;
