import React from 'react';

interface AnswerTabProps {
  finalAnswer: string;
}

const AnswerTab: React.FC<AnswerTabProps> = ({ finalAnswer }) => {
  return (
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
          {finalAnswer}
        </div>
      </div>
    </div>
  );
};

export default AnswerTab;
