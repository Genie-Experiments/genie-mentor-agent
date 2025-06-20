import React from 'react';
import { Tabs, TabsList, TabsTrigger, TabsContent } from '@/components/ui/tabs';

interface TabItem {
  value: string;
  label: string;
  content: React.ReactNode;
}

interface TabsContainerProps {
  defaultValue?: string;
  children?: React.ReactNode;
  answerContent?: React.ReactNode;
  sourcesContent?: React.ReactNode;
  traceContent?: React.ReactNode;
}

const tabTriggerStyles =
  "relative w-[126px] cursor-pointer rounded-none bg-transparent px-0 py-[10px] font-['Inter'] text-[18px] font-normal shadow-none " +
  "hover:after:absolute hover:after:bottom-[-2px] hover:after:left-0 hover:after:h-[1px] hover:after:w-full hover:after:bg-[#00A599]/50 hover:after:content-[''] " +
  'data-[state=active]:bg-transparent data-[state=active]:font-semibold data-[state=active]:text-[#00A599] data-[state=active]:shadow-none ' +
  'data-[state=active]:after:absolute data-[state=active]:after:bottom-[-2px] data-[state=active]:after:left-0 data-[state=active]:after:h-[2px] ' +
  "data-[state=active]:after:w-full data-[state=active]:after:bg-[#00A599] data-[state=active]:after:content-[''] data-[state=inactive]:text-[#002835]";

const TabsContainer: React.FC<TabsContainerProps> = ({
  defaultValue = 'answer',
  children,
  answerContent,
  sourcesContent,
  traceContent,
}) => {
  const tabs: TabItem[] = [
    { value: 'answer', label: 'Answer', content: answerContent || children },
    { value: 'trace', label: 'Research', content: traceContent },
    { value: 'sources', label: 'All Sources', content: sourcesContent },
  ];

  return (
    <Tabs defaultValue={defaultValue} className="w-full">
      <div className="mt-[51px] border-b border-[#9CBFBC] pb-[1px]">
        <TabsList className="h-auto gap-[30px] bg-transparent p-0">
          {tabs.map((tab) => (
            <TabsTrigger key={tab.value} value={tab.value} className={tabTriggerStyles}>
              {tab.label}
            </TabsTrigger>
          ))}
        </TabsList>{' '}
      </div>

      <div className="mt-[27px]">
        {tabs.map((tab) => (
          <TabsContent key={tab.value} value={tab.value} className="mt-0 mb-4 min-h-[80px]">
            {tab.content}
          </TabsContent>
        ))}
      </div>
    </Tabs>
  );
};

export default TabsContainer;
