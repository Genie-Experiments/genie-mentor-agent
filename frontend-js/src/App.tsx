import './App.css';
import Sidebar from './components/shared/Sidebar';
import Chat from './features/Chat/Chat';
import WelcomeScreen from './WelcomeScreen';
import InputField from './components/ui/InputField';
import { useState } from 'react';

function App() {
  const sampleConversations = [{ id: '1', title: 'Machine learning algorithms' }];  // Use true to show WelcomeScreen by default
  const [showWelcomeScreen, setShowWelcomeScreen] = useState(true);
  const [question, setQuestion] = useState('');

  // Handle question submission from any component
  const handleQuestionSubmit = (value: string) => {
    setQuestion(value);
    // When a question is submitted, switch to chat view
    setShowWelcomeScreen(false);
  };  // Function to handle "Start New Chat" from sidebar
  const handleStartNewChat = () => {
    setQuestion(''); // Clear any previous question
    setShowWelcomeScreen(false); // Switch to empty chat view
  };
  
  return (
    <div className="flex h-screen w-full overflow-hidden">
      {/* Sidebar - fixed on the left side with full height */}
      <Sidebar conversations={sampleConversations} onNewChat={handleStartNewChat} />
      
      {/* Main content area with relative positioning for chat input */}
      <div className="flex-1 relative flex flex-col overflow-hidden">
        {/* Scrollable content area */}
        <div className="flex-1 overflow-y-auto pb-32">
          {showWelcomeScreen ? (
            <WelcomeScreen onQuestionSubmit={handleQuestionSubmit} /> 
          ) : (            <Chat onQuestionSubmit={handleQuestionSubmit} question={question} />
          )}
        </div>
        {/* Fixed chat input at the bottom with improved styling */}
        <div className="absolute bottom-0 left-0 right-0 z-10 w-full">
          {/* Gradient overlay - enhanced blur effect */}
          <div 
            className="absolute bottom-0 left-0 right-0 h-40 pointer-events-none"
            style={{ 
              background: 'linear-gradient(180deg, rgba(240, 255, 254, 0.00) 0%, #F0FFFE 41.99%)',
              backdropFilter: 'blur(5px)'
            }}>
          </div>
          
          {/* Chat input container */}
          <div className="flex justify-center items-center pb-10 pt-4 relative z-20">
            <div className="w-full max-w-[760px] px-4">
              <InputField 
                onSubmit={handleQuestionSubmit} 
                placeholder={showWelcomeScreen ? "Ask your first question..." : "Ask a question..."} 
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
