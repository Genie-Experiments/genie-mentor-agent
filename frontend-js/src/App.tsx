import './App.css';
import Sidebar from './components/shared/Sidebar';
import Chat from './features/Chat/Chat';
import WelcomeScreen from './WelcomeScreen';
import InputField from './components/ui/InputField';
import { useState } from 'react';

function App() {
  const sampleConversations = [{ id: '1', title: 'Machine learning algorithms' }];
  const [showWelcomeScreen, setShowWelcomeScreen] = useState(true);
  const [question, setQuestion] = useState('');

  const handleQuestionSubmit = (value: string) => {
    if (value.trim()) {
      setQuestion(value);
      setShowWelcomeScreen(false);
    }
  };

  const handleStartNewChat = () => {
    setQuestion('');
    setShowWelcomeScreen(false);
  };
  return (
    <div className="flex h-screen w-full overflow-hidden">
      <Sidebar conversations={sampleConversations} onNewChat={handleStartNewChat} />
      <div className="relative flex flex-1 flex-col overflow-hidden">
        <div className="scrollbar-hide flex-1 overflow-y-auto pb-32">
          {showWelcomeScreen ? (
            <WelcomeScreen onQuestionSubmit={handleQuestionSubmit} />
          ) : (
            <Chat question={question} />
          )}
        </div>
        <div className="absolute right-0 bottom-0 left-0 z-10 w-full">
          <div
            className="pointer-events-none absolute right-0 bottom-0 left-0 h-[200px]"
            style={{
              background: 'linear-gradient(180deg, rgba(240, 255, 254, 0.00) 0%, #F0FFFE 41.99%)',
            }}
          ></div>
          <div className="relative z-20 flex items-center justify-center pt-4 pb-10">
            <div className="w-full max-w-[760px] px-4">
              <InputField
                onSubmit={handleQuestionSubmit}
                placeholder={showWelcomeScreen ? 'Ask your first question...' : 'Ask a question...'}
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
