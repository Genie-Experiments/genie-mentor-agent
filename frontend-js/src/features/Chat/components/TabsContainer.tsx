import React, { useState } from 'react';

interface TabsContainerProps {
  tabs: string[];
  defaultTab?: string;
  children: (activeTab: string) => React.ReactNode;
}

const TabsContainer: React.FC<TabsContainerProps> = ({ 
  tabs, 
  defaultTab = tabs[0], 
  children 
}) => {
  const [activeTab, setActiveTab] = useState(defaultTab);

  return (
    <div className="w-full">
      {/* Tabs Navigation */}
      <div className="flex mt-[51px] gap-[76px] w-full">
        {tabs.map((tab) => (
          <button
            key={tab}
            className={`font-['Inter'] text-[18px] font-normal focus:outline-none transition-colors relative pb-2 ${
              activeTab === tab ? 'text-[#00A599]' : 'text-[#002835]'
            }`}
            onClick={() => setActiveTab(tab)}
            style={{ minWidth: 80 }}
          >
            {tab}
          </button>
        ))}
      </div>
      
      {/* Separator with active tab highlight */}
      <div className="relative w-full h-[1px] mt-[15px] mb-4" style={{background: '#9CBFBC'}}>
        <div
          className="absolute h-full transition-all duration-300"
          style={{
            left: `${tabs.indexOf(activeTab) * (100 / tabs.length)}%`,
            width: `${100 / tabs.length}%`,
            background: '#00A599',
            top: 0,
          }}
        />
      </div>
      
      {/* Tab Content */}
      <div className="w-full min-h-[80px] mb-4">
        {children(activeTab)}
      </div>
    </div>
  );
};

export default TabsContainer;
