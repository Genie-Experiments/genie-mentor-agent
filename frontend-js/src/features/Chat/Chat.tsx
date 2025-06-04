import React, { useState, useRef, useEffect } from 'react';
import InputField from '../../components/ui/InputField';
import { mockAgentResponses } from '../../mocks/api-response';

// Define types for the evaluation result items
interface EvaluationResultItem {
  Fact: string;
  Reasoning: string;
  Judgement: "yes" | "no";
}


const TABS = ['Answer', 'Research', 'Sources'];

const Chat: React.FC = () => {
  const [activeTab, setActiveTab] = useState('Answer');
  const [question, setQuestion] = useState('What is Genie AI Mentor?'); // Example question
  const [showBadge, setShowBadge] = useState(true);
  const [responses, setResponses] = useState<string[]>([]);
  const chatAreaRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (responses.length > 0) {
      setShowBadge(true);
      if (chatAreaRef.current) {
        chatAreaRef.current.scrollTop = 0;
      }
    }
  }, [responses]);

  const handleQuestionSubmit = (value: string) => {
    setQuestion(value);
    setShowBadge(true);
    setResponses((prev) => [
      `Response to: ${value}`,
      ...prev,
    ]);
  };

  // Extract all sources from different agents
  const allSources = [
    ...(mockAgentResponses.knowledge_base_agent.metadata || []).map(source => ({
      title: source.title,
      source: source.page_number,
      type: 'Knowledge Base'
    })),
    ...(mockAgentResponses.web_search_agent.metadata || []).map(source => ({
      title: source.web_title,
      url: source.web_url,
      description: source.web_page_description,
      type: 'Web Search'
    })),
    ...(mockAgentResponses.github_agent.metadata || []).map(source => ({
      repo_name: source.repo_name,
      repo_link: source.repo_link,
      type: 'GitHub'
    })),
    ...(mockAgentResponses.notion_agent.metadata || []).map(source => ({
      link: source.notion_document_link,
      type: 'Notion'
    }))
  ];

  return (
    <div className="w-full flex justify-center">
      <div className="max-w-[760px] w-full flex flex-col items-start px-4 relative min-h-screen">
        {/* Badge */}
        {showBadge && (
          <div
            className="flex px-[9px] py-[5px] justify-center items-center gap-[10px] rounded-[50px] bg-[#00A599] mb-0 mt-8"
          >
            <span className="text-white font-['Inter'] text-[14px] font-semibold">Question</span>
          </div>
        )}
        {/* User Question */}
        <div className="mt-[16px]">
          <span className="text-[#002835] font-['Inter'] text-[28px] font-semibold">{question}</span>
        </div>
        {/* Info Text */}
        <div className="mt-[21px]">
          <span className="text-[#002835] font-['Inter'] text-[18px] font-normal">
            It takes less than a minute to gather and compile best answers for you.
          </span>
        </div>
        {/* Tabs */}
        <div className="flex mt-[51px] gap-[76px] w-full">
          {TABS.map((tab) => (
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
        <div className="relative w-[760px] h-[1px] mt-[15px] mb-4" style={{background: '#9CBFBC'}}>
          <div
            className="absolute h-full transition-all duration-300"
            style={{
              left: `${TABS.indexOf(activeTab) * (760 / TABS.length)}px`,
              width: `${760 / TABS.length}px`,
              background: '#00A599',
              top: 0,
            }}
          />
        </div>
        {/* Mocked Tab Content */}
        <div className="w-full min-h-[80px] mb-4">
          {activeTab === 'Answer' && (
            <div className="flex flex-col gap-8 w-full">
              {/* Top Sources Section */}
              <div>
                <div className="mb-4" style={{
                  color: '#002835', fontFamily: 'Inter', fontSize: 16, fontWeight: 500, textTransform: 'uppercase', opacity: 0.4
                }}>Top sources</div>
                <div className="flex gap-4 w-full" style={{rowGap: 13}}>
                  {[1,2,3].map((i) => (
                    <div
                      key={i}
                      className="flex flex-col justify-center items-start gap-[10px] rounded-[8px] border border-[#9CBFBC] bg-white transition-shadow hover:shadow-[0px_12px_21px_0px_#CDE6E5]"
                      style={{width:243, padding:'15px 18px'}}
                    >
                      <div className="flex items-center gap-2">
                        {/* Star Icon */}
                        <span style={{width:16, height:16, display:'inline-flex', alignItems:'center'}}>
                          <svg xmlns="http://www.w3.org/2000/svg" width="12" height="11" viewBox="0 0 12 11" fill="none">
                            <path d="M5.04894 0.927049C5.3483 0.00573826 6.6517 0.00573993 6.95106 0.927051L7.5716 2.83688C7.70547 3.2489 8.08943 3.52786 8.52265 3.52786H10.5308C11.4995 3.52786 11.9023 4.76748 11.1186 5.33688L9.49395 6.51722C9.14347 6.77187 8.99681 7.22323 9.13068 7.63525L9.75122 9.54508C10.0506 10.4664 8.9961 11.2325 8.21238 10.6631L6.58778 9.48278C6.2373 9.22813 5.7627 9.22814 5.41221 9.48278L3.78761 10.6631C3.0039 11.2325 1.94942 10.4664 2.24878 9.54508L2.86932 7.63526C3.00319 7.22323 2.85653 6.77186 2.50604 6.51722L0.881445 5.33688C0.0977311 4.76748 0.500508 3.52786 1.46923 3.52786H3.47735C3.91057 3.52786 4.29453 3.2489 4.4284 2.83688L5.04894 0.927049Z" fill="#00A599"/>
                          </svg>
                        </span>
                        <span style={{color:'#002835', fontFamily:'Inter', fontSize:13, fontWeight:400, opacity:0.6}}>Source Title {i}</span>
                      </div>
                      <div style={{color:'#002835', fontFamily:'Inter', fontSize:14, fontWeight:400, overflow:'hidden', textOverflow:'ellipsis', whiteSpace:'nowrap', maxWidth: 200}}>
                        This is a truncated source description for source {i}.
                      </div>
                    </div>
                  ))}
                </div>
              </div>
              {/* Context Section */}
              <div>
                <div className="mb-4" style={{
                  color: '#002835', fontFamily: 'Inter', fontSize: 16, fontWeight: 500, textTransform: 'uppercase', opacity: 0.4
                }}>Context</div>
                <div className="flex gap-4 w-full" style={{rowGap: 13}}>
                  {[1,2,3].map((i) => (
                    <div
                      key={i}
                      className="flex flex-col justify-center items-start gap-[10px] rounded-[8px] border border-[#9CBFBC] bg-white transition-shadow hover:shadow-[0px_12px_21px_0px_#CDE6E5]"
                      style={{width:243, padding:'15px 18px'}}
                    >
                      <div className="flex items-center gap-2">
                        <span style={{width:16, height:16, display:'inline-flex', alignItems:'center'}}>
                          <svg xmlns="http://www.w3.org/2000/svg" width="12" height="11" viewBox="0 0 12 11" fill="none">
                            <path d="M5.04894 0.927049C5.3483 0.00573826 6.6517 0.00573993 6.95106 0.927051L7.5716 2.83688C7.70547 3.2489 8.08943 3.52786 8.52265 3.52786H10.5308C11.4995 3.52786 11.9023 4.76748 11.1186 5.33688L9.49395 6.51722C9.14347 6.77187 8.99681 7.22323 9.13068 7.63525L9.75122 9.54508C10.0506 10.4664 8.9961 11.2325 8.21238 10.6631L6.58778 9.48278C6.2373 9.22813 5.7627 9.22814 5.41221 9.48278L3.78761 10.6631C3.0039 11.2325 1.94942 10.4664 2.24878 9.54508L2.86932 7.63526C3.00319 7.22323 2.85653 6.77186 2.50604 6.51722L0.881445 5.33688C0.0977311 4.76748 0.500508 3.52786 1.46923 3.52786H3.47735C3.91057 3.52786 4.29453 3.2489 4.4284 2.83688L5.04894 0.927049Z" fill="#00A599"/>
                          </svg>
                        </span>
                        <span style={{color:'#002835', fontFamily:'Inter', fontSize:13, fontWeight:400, opacity:0.6}}>Context Title {i}</span>
                      </div>
                      <div style={{color:'#002835', fontFamily:'Inter', fontSize:14, fontWeight:400, overflow:'hidden', textOverflow:'ellipsis', whiteSpace:'nowrap', maxWidth: 200}}>
                        This is a truncated context description for context {i}.
                      </div>
                    </div>
                  ))}
                </div>
              </div>
              {/* Answer Section */}
              <div>
                <div className="mb-2" style={{
                  color: '#002835', fontFamily: 'Inter', fontSize: 16, fontWeight: 500, textTransform: 'uppercase', opacity: 0.4
                }}>Answer</div>
                <div className="mb-1" style={{color:'#002835', fontFamily:'Inter', fontSize:18, fontWeight:600, lineHeight:'23px'}}>
                  What is Genie AI Mentor?
                </div>
                <div style={{color:'#002835', fontFamily:'Inter', fontSize:16, fontWeight:400, lineHeight:'23px'}}>
                  {mockAgentResponses.final_answer}
                </div>
              </div>
            </div>
          )}
          
          {activeTab === 'Research' && (
            <div className="flex flex-col gap-10 w-full text-[#002835] font-['Inter']">
              {/* Planner Agent - Step 1 */}
              <div className="flex flex-col gap-3 w-full">
                <div className="flex items-center gap-2">
                  <div className="flex items-center justify-center w-[32px] h-[32px] rounded-full bg-[#E5FFFC] border border-[#00A599]">
                    <span className="text-[#00A599] font-semibold">1</span>
                  </div>
                  <div className="font-semibold text-[18px]">Query Planning</div>
                </div>
                <div className="pl-10 text-[16px]">
                  <div className="mb-2">
                    <span className="font-medium">Query Intent:</span> {mockAgentResponses.planner_agent.query_intent}
                  </div>
                  <div className="mb-2">
                    <span className="font-medium">Data Sources:</span> {mockAgentResponses.planner_agent.data_sources.join(', ')}
                  </div>
                  <div className="mb-2">
                    <span className="font-medium">Query Components:</span>
                    <ul className="list-disc pl-5 mt-1">
                      {mockAgentResponses.planner_agent.query_components.map((comp, idx) => (
                        <li key={idx} className="mb-1">
                          {comp.sub_query} <span className="text-[#00A599]">({comp.source})</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                  <div className="mt-3 p-3 bg-[#F9FFFF] rounded-lg">
                    <div className="font-medium mb-1">Thinking Process:</div>
                    <ul className="list-disc pl-5 text-[14px] opacity-80">
                      <li>Query Analysis: {mockAgentResponses.planner_agent.thinking_process.query_analysis}</li>
                      <li>Sub-query Reasoning: {mockAgentResponses.planner_agent.thinking_process.sub_query_reasoning}</li>
                      <li>Source Selection: {mockAgentResponses.planner_agent.thinking_process.source_selection}</li>
                      <li>Execution Strategy: {mockAgentResponses.planner_agent.thinking_process.execution_strategy}</li>
                    </ul>
                  </div>
                </div>
              </div>

              {/* Planner Refiner Agent - Step 2 */}
              <div className="flex flex-col gap-3 w-full">
                <div className="flex items-center gap-2">
                  <div className="flex items-center justify-center w-[32px] h-[32px] rounded-full bg-[#E5FFFC] border border-[#00A599]">
                    <span className="text-[#00A599] font-semibold">2</span>
                  </div>
                  <div className="font-semibold text-[18px]">Query Refinement</div>
                </div>
                <div className="pl-10 text-[16px]">
                  <div className="mb-2">
                    <span className="font-medium">Refinement Required:</span> {mockAgentResponses.planner_refiner_agent.refinement_required}
                  </div>
                  <div className="mb-2">
                    <span className="font-medium">Feedback Summary:</span> {mockAgentResponses.planner_refiner_agent.feedback_summary}
                  </div>
                  <div className="p-3 bg-[#F9FFFF] rounded-lg">
                    <div className="font-medium mb-1">Reasoning:</div>
                    <ul className="list-disc pl-5 text-[14px] opacity-80">
                      {mockAgentResponses.planner_refiner_agent.feedback_reasoning.map((reason, idx) => (
                        <li key={idx}>{reason}</li>
                      ))}
                    </ul>
                  </div>
                </div>
              </div>

              {/* Knowledge Base Agent - Step 3 */}
              <div className="flex flex-col gap-3 w-full">
                <div className="flex items-center gap-2">
                  <div className="flex items-center justify-center w-[32px] h-[32px] rounded-full bg-[#E5FFFC] border border-[#00A599]">
                    <span className="text-[#00A599] font-semibold">3</span>
                  </div>
                  <div className="font-semibold text-[18px]">Knowledge Base Research</div>
                </div>
                <div className="pl-10 text-[16px]">
                  <div className="mb-3 italic opacity-80">
                    Retrieved information from internal knowledge base in {mockAgentResponses.knowledge_base_agent.execution_time_ms}ms
                  </div>
                  {mockAgentResponses.knowledge_base_agent.sources.length > 0 && (
                    <div className="p-3 bg-[#F9FFFF] rounded-lg">
                      <div className="font-medium mb-1">Sources Excerpts:</div>
                      <ul className="list-disc pl-5 text-[14px] opacity-80">
                        {mockAgentResponses.knowledge_base_agent.sources.map((source, idx) => (
                          <li key={idx} className="mb-1">{source}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              </div>

              {/* Web Search Agent - Step 4 */}
              <div className="flex flex-col gap-3 w-full">
                <div className="flex items-center gap-2">
                  <div className="flex items-center justify-center w-[32px] h-[32px] rounded-full bg-[#E5FFFC] border border-[#00A599]">
                    <span className="text-[#00A599] font-semibold">4</span>
                  </div>
                  <div className="font-semibold text-[18px]">Web Search</div>
                </div>
                <div className="pl-10 text-[16px]">
                  <div className="mb-3 italic opacity-80">
                    Searched the web for complementary information in {mockAgentResponses.web_search_agent.execution_time_ms}ms
                  </div>
                  {mockAgentResponses.web_search_agent.sources.length > 0 && (
                    <div className="p-3 bg-[#F9FFFF] rounded-lg">
                      <div className="font-medium mb-1">Web Content:</div>
                      <ul className="list-disc pl-5 text-[14px] opacity-80">
                        {mockAgentResponses.web_search_agent.sources.map((source, idx) => (
                          <li key={idx} className="mb-1">{source}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              </div>

              {/* Github Agent - Step 5 */}
              <div className="flex flex-col gap-3 w-full">
                <div className="flex items-center gap-2">
                  <div className="flex items-center justify-center w-[32px] h-[32px] rounded-full bg-[#E5FFFC] border border-[#00A599]">
                    <span className="text-[#00A599] font-semibold">5</span>
                  </div>
                  <div className="font-semibold text-[18px]">GitHub Repository Analysis</div>
                </div>
                <div className="pl-10 text-[16px]">
                  <div className="mb-3 italic opacity-80">
                    Analyzed GitHub repositories in {mockAgentResponses.github_agent.execution_time_ms}ms
                  </div>
                  <div className="p-3 bg-[#F9FFFF] rounded-lg">
                    <div className="font-medium mb-1">Repository: {mockAgentResponses.github_agent.metadata[0].repo_name}</div>
                    <div className="text-[14px] opacity-80">
                      <a href={mockAgentResponses.github_agent.metadata[0].repo_link} target="_blank" className="text-[#00A599] hover:underline">{mockAgentResponses.github_agent.metadata[0].repo_link}</a>
                    </div>
                  </div>
                </div>
              </div>

              {/* Evaluation Agent - Step 6 */}
              <div className="flex flex-col gap-3 w-full">
                <div className="flex items-center gap-2">
                  <div className="flex items-center justify-center w-[32px] h-[32px] rounded-full bg-[#E5FFFC] border border-[#00A599]">
                    <span className="text-[#00A599] font-semibold">6</span>
                  </div>
                  <div className="font-semibold text-[18px]">Answer Evaluation</div>
                </div>
                <div className="pl-10 text-[16px]">
                  <div className="mb-2">
                    <span className="font-medium">Initial Score:</span> {mockAgentResponses.evaluation_agent[0].output.score} / 1.0
                  </div>
                  <div className="mb-2">
                    <span className="font-medium">Final Score:</span> {mockAgentResponses.evaluation_agent[1].output.score} / 1.0
                  </div>
                  <div className="p-3 bg-[#F9FFFF] rounded-lg mb-3">
                    <div className="font-medium mb-1">Initial Assessment:</div>
                    <div className="text-[14px] opacity-80 whitespace-pre-line">
                      {(JSON.parse(mockAgentResponses.evaluation_agent[0].output.reasoning) as { Result: EvaluationResultItem[] }).Result.map((item, idx) => (
                        <div key={idx} className="mb-1">
                          {item.Fact} - <span className={item.Judgement === "yes" ? "text-green-600" : "text-red-500"}>{item.Judgement}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                  <div className="p-3 bg-[#F9FFFF] rounded-lg">
                    <div className="font-medium mb-1">Final Assessment:</div>
                    <div className="text-[14px] opacity-80 whitespace-pre-line">
                      {(JSON.parse(mockAgentResponses.evaluation_agent[1].output.reasoning) as { Result: EvaluationResultItem[] }).Result.map((item, idx) => (
                        <div key={idx} className="mb-1">
                          {item.Fact} - <span className={item.Judgement === "yes" ? "text-green-600" : "text-red-500"}>{item.Judgement}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </div>

              {/* Final Answer - Step 7 */}
              <div className="flex flex-col gap-3 w-full">
                <div className="flex items-center gap-2">
                  <div className="flex items-center justify-center w-[32px] h-[32px] rounded-full bg-[#00A599] border border-[#00A599]">
                    <span className="text-white font-semibold">✓</span>
                  </div>
                  <div className="font-semibold text-[18px]">Final Answer</div>
                </div>
                <div className="pl-10 text-[16px]">
                  <div className="p-4 bg-[#E5FFFC] rounded-lg border border-[#00A599]">
                    {mockAgentResponses.final_answer}
                  </div>
                  <div className="mt-2 text-[14px] opacity-70 text-right">
                    Total processing time: {mockAgentResponses.total_time.toFixed(2)}s
                  </div>
                </div>
              </div>
            </div>
          )}
          
          {activeTab === 'Sources' && (
            <div className="flex flex-col gap-6 w-full text-[#002835] font-['Inter']">
              <div className="text-[16px] opacity-80">
                {allSources.length} sources were used to answer your question
              </div>
              
              {/* Knowledge Base Sources */}
              {mockAgentResponses.knowledge_base_agent.metadata.length > 0 && (
                <div className="flex flex-col gap-3">
                  <div style={{ color: '#002835', fontFamily: 'Inter', fontSize: 16, fontWeight: 500, textTransform: 'uppercase', opacity: 0.4 }}>
                    Knowledge Base Sources
                  </div>
                  <div className="flex flex-col gap-3">
                    {mockAgentResponses.knowledge_base_agent.metadata.map((source, idx) => (
                      <div key={idx} className="p-4 border border-[#9CBFBC] rounded-lg">
                        <div className="flex items-center gap-3 mb-2">
                          <div className="flex items-center justify-center w-[28px] h-[28px] rounded-full bg-[#E5FFFC] text-[#00A599] font-semibold text-sm">
                            {idx + 1}
                          </div>
                          <div className="font-medium text-[16px]">{source.title}</div>
                        </div>
                        <div className="pl-10 text-[14px] opacity-80">
                          <div>Source: {source.source}</div>
                          <div>Page: {source.page_number}</div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
              
              {/* Web Search Sources */}
              {mockAgentResponses.web_search_agent.metadata.length > 0 && (
                <div className="flex flex-col gap-3">
                  <div style={{ color: '#002835', fontFamily: 'Inter', fontSize: 16, fontWeight: 500, textTransform: 'uppercase', opacity: 0.4 }}>
                    Web Sources
                  </div>
                  <div className="flex flex-col gap-3">
                    {mockAgentResponses.web_search_agent.metadata.map((source, idx) => (
                      <div key={idx} className="p-4 border border-[#9CBFBC] rounded-lg">
                        <div className="flex items-center gap-3 mb-2">
                          <div className="flex items-center justify-center w-[28px] h-[28px] rounded-full bg-[#E5FFFC] text-[#00A599] font-semibold text-sm">
                            {mockAgentResponses.knowledge_base_agent.metadata.length + idx + 1}
                          </div>
                          <div className="font-medium text-[16px]">{source.web_title}</div>
                        </div>
                        <div className="pl-10 text-[14px] opacity-80">
                          <div className="mb-1">{source.web_page_description}</div>
                          <a href={source.web_url} target="_blank" className="text-[#00A599] hover:underline">{source.web_url}</a>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
              
              {/* GitHub Sources */}
              {mockAgentResponses.github_agent.metadata.length > 0 && (
                <div className="flex flex-col gap-3">
                  <div style={{ color: '#002835', fontFamily: 'Inter', fontSize: 16, fontWeight: 500, textTransform: 'uppercase', opacity: 0.4 }}>
                    GitHub Sources
                  </div>
                  <div className="flex flex-col gap-3">
                    {mockAgentResponses.github_agent.metadata.map((source, idx) => (
                      <div key={idx} className="p-4 border border-[#9CBFBC] rounded-lg">
                        <div className="flex items-center gap-3 mb-2">
                          <div className="flex items-center justify-center w-[28px] h-[28px] rounded-full bg-[#E5FFFC] text-[#00A599] font-semibold text-sm">
                            {mockAgentResponses.knowledge_base_agent.metadata.length + mockAgentResponses.web_search_agent.metadata.length + idx + 1}
                          </div>
                          <div className="font-medium text-[16px]">{source.repo_name}</div>
                        </div>
                        <div className="pl-10 text-[14px] opacity-80">
                          <a href={source.repo_link} target="_blank" className="text-[#00A599] hover:underline">{source.repo_link}</a>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
              
              {/* Notion Sources */}
              {mockAgentResponses.notion_agent.metadata.length > 0 && (
                <div className="flex flex-col gap-3">
                  <div style={{ color: '#002835', fontFamily: 'Inter', fontSize: 16, fontWeight: 500, textTransform: 'uppercase', opacity: 0.4 }}>
                    Notion Documents
                  </div>
                  <div className="flex flex-col gap-3">
                    {mockAgentResponses.notion_agent.metadata.map((source, idx) => (
                      <div key={idx} className="p-4 border border-[#9CBFBC] rounded-lg">
                        <div className="flex items-center gap-3 mb-2">
                          <div className="flex items-center justify-center w-[28px] h-[28px] rounded-full bg-[#E5FFFC] text-[#00A599] font-semibold text-sm">
                            {mockAgentResponses.knowledge_base_agent.metadata.length + mockAgentResponses.web_search_agent.metadata.length + mockAgentResponses.github_agent.metadata.length + idx + 1}
                          </div>
                          <div className="font-medium text-[16px]">Notion Document</div>
                        </div>
                        <div className="pl-10 text-[14px] opacity-80">
                          <a href={source.notion_document_link} target="_blank" className="text-[#00A599] hover:underline">{source.notion_document_link}</a>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
        {/* Chat Area with input fixed at bottom and content behind (no scroll) */}
        <div className="w-full flex justify-center relative" style={{ width: 851, height: 202, flexShrink: 0, marginTop: 41 }}>
          {/* Chat content behind input, NOT scrollable */}
          <div
            className="absolute left-0 top-0 w-full h-full pr-2"
            style={{
              zIndex: 1,
            }}
          >
            <div className="flex flex-col items-end w-full" style={{ minHeight: 200, paddingBottom: 80 }}>
              {/* Responses */}
              {responses.map((resp, idx) => (
                <div
                  key={idx}
                  className="mb-2 px-4 py-2 bg-[#F9FFFF] rounded-lg text-right max-w-[90%] text-[#002835] font-['Inter'] text-[16px] shadow"
                >
                  {resp}
                </div>
              ))}
            </div>
          </div>
          {/* Gradient overlay at the bottom */}
          <div
            className="absolute left-0 bottom-0 w-full h-[80px] pointer-events-none"
            style={{
              background: 'linear-gradient(180deg, rgba(240, 255, 254, 0.00) 0%, #F0FFFE 41.99%)',
              zIndex: 2,
            }}
          />
          {/* Chat Input sticky at the bottom */}
          <div className="sticky left-0 bottom-0 w-full flex justify-end z-10" style={{bottom: 0}}>
            <div className="w-full max-w-[760px] mx-auto">
              <InputField onSubmit={handleQuestionSubmit} />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Chat;
