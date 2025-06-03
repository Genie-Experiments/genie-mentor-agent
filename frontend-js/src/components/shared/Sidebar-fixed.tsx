import React, { useState } from "react";
import ActionButton from "../ui/ActionButton";
import HamburgerIcon from "../ui/HamburgerIcon";
import PlusIcon from "../ui/PlusIcon";
import { cn } from "@/lib/utils";

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
    console.log("New chat started");
  };
  
  return (
    <div 
      className={cn(
        "relative flex flex-col h-screen bg-[#00A599] transition-all duration-300 ease-in-out overflow-hidden",
        isCollapsed ? "w-[90px]" : "w-[300px]",
        "rounded-r-[26px]"
      )}
    >
      {/* Hamburger Menu - positioned absolute */}
      <div className="absolute top-[35px] left-6 z-10">
        <HamburgerIcon isOpen={false} onClick={toggleSidebar} />
      </div>

      {/* Main Content */}
      <div className={cn(
        "flex flex-col p-6 pt-[90px] w-full",
        isCollapsed ? "items-center" : "items-start"
      )}>
        {/* Title */}
        <div className={cn(
          "text-white mb-6 transition-all duration-200 ease-in-out overflow-hidden",
          isCollapsed ? "opacity-0 w-0 h-0 absolute invisible" : "opacity-100 relative visible"
        )}
          style={{
            transitionDelay: isCollapsed ? "0ms" : "150ms"
          }}
        >
          <h1 className="text-3xl font-bold leading-normal">GEN AI</h1>
          <h2 className="text-3xl font-medium leading-normal">MENTOR AGENT</h2>
        </div>
        
        {/* Button Container - with fixed width to prevent overflow */}
        <div className={cn(
          "transition-all duration-300 ease-in-out",
          isCollapsed ? "w-[44px]" : "w-full"
        )}
          style={{
            transitionDelay: "50ms" // Slight delay to sync with sidebar animation
          }}
        >
          {isCollapsed ? (
            <PlusIcon 
              onClick={handleNewChat} 
              className="flex-shrink-0 cursor-pointer"
            />
          ) : (
            <ActionButton 
              onClick={handleNewChat}
              className="mb-6 cursor-pointer"
            >
              Start New Chat
            </ActionButton>
          )}
        </div>
        
        {/* Separator with improved animation */}
        <div className={cn(
          "h-[1px] bg-white mb-6 transition-all duration-200 ease-in-out -ml-6 px-6 transform",
          isCollapsed ? 
            "w-0 opacity-0 absolute invisible scale-x-0 origin-left" : 
            "w-[300px] opacity-80 relative visible scale-x-100"
        )}
          style={{
            transitionDelay: isCollapsed ? "0ms" : "150ms",
            transitionProperty: "width, opacity, transform, visibility"
          }}
        ></div>
        
        {/* History Section with improved animation */}
        <div className={cn(
          "w-full transition-all duration-200 ease-in-out overflow-hidden",
          isCollapsed ? "opacity-0 max-h-0 invisible" : "opacity-100 max-h-[2000px] visible"
        )}
          style={{
            transitionDelay: isCollapsed ? "0ms" : "150ms"
          }}
        >
          <h3 className="overflow-hidden text-white text-overflow-ellipsis font-[Inter] text-[16px] font-medium leading-normal opacity-50 mb-4">History</h3>
          
          <div className="flex flex-col gap-2">
            {conversations.length > 0 ? (
              conversations.map((convo) => (
                <div 
                  key={convo.id}
                  className="w-[266px] h-[57px] flex items-center px-4 rounded-[8px] bg-[rgba(255,232,223,0.19)] mb-2"
                >
                  <p className="overflow-hidden text-white text-overflow-ellipsis whitespace-nowrap font-[Inter] text-[18px] font-medium leading-normal w-full truncate">
                    {convo.title}
                  </p>
                </div>
              ))
            ) : (
              <div className="text-white text-sm opacity-50">No conversation history</div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Sidebar;
