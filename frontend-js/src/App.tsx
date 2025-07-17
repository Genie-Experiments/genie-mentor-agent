import './App.css';
import Sidebar from './components/shared/Sidebar';
import Chat from './features/Chat/Chat';
import WelcomeScreen from './WelcomeScreen';
import InputField from './components/ui/InputField';
import { useState, useCallback } from 'react';
import { GRADIENT_STYLE, LAYOUT_CONSTANTS } from './constant';

function App() {
  const [showWelcomeScreen, setShowWelcomeScreen] = useState(true);
  const [question, setQuestion] = useState('');
  const [questionId, setQuestionId] = useState(0);
  const [isLoading, setIsLoading] = useState(false);

  const handleQuestionSubmit = useCallback((value: string) => {
    if (!value.trim()) return;

    setQuestion(value);
    setQuestionId((prevId) => prevId + 1);
    setShowWelcomeScreen(false);
    setIsLoading(true);
  }, []);

  const handleLoadingStateChange = useCallback((isLoading: boolean) => {
    setIsLoading(isLoading);
  }, []);

  const handleStartNewChat = useCallback(() => {
    setQuestion('');
    setShowWelcomeScreen(true);
    setIsLoading(false);
    setQuestionId(0);
  }, []);

  return (
    <div className="flex h-screen w-full overflow-hidden">
      <Sidebar onNewChat={handleStartNewChat} />
      <main className="relative flex flex-1 flex-col overflow-hidden">
        <div
          className={`scrollbar-hide flex-1 overflow-y-auto ${!showWelcomeScreen ? 'pb-32' : ''}`}
          role="main"
          aria-label="Chat interface"
        >
          {showWelcomeScreen ? (
            <WelcomeScreen onQuestionSubmit={handleQuestionSubmit} />
          ) : (
            <Chat
              question={question}
              questionId={questionId}
              onLoadingStateChange={handleLoadingStateChange}
            />
          )}
        </div>
        {!showWelcomeScreen && (
          <div
            className="absolute right-0 bottom-0 left-0 w-full"
            style={{ zIndex: LAYOUT_CONSTANTS.Z_INDEX.OVERLAY }}
          >
            <div
              className="pointer-events-none absolute right-0 bottom-0 left-0"
              style={{
                height: LAYOUT_CONSTANTS.GRADIENT_HEIGHT,
                ...GRADIENT_STYLE,
              }}
              aria-hidden="true"
            />
            <div
              className="relative flex items-center justify-center pt-4 pb-10"
              style={{ zIndex: LAYOUT_CONSTANTS.Z_INDEX.INPUT }}
            >
              <div
                className="flex justify-center"
                style={{ width: LAYOUT_CONSTANTS.INPUT_CONTAINER_WIDTH }}
              >
                <InputField
                  onSubmit={handleQuestionSubmit}
                  placeholder="Ask Anything..."
                  isLoading={isLoading}
                  width={LAYOUT_CONSTANTS.INPUT_FIELD_WIDTH}
                />
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}

export default App;
