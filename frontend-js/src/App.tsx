import './App.css';
import Sidebar from './components/shared/Sidebar';
import Chat from './features/Chat/Chat';

function App() {
  const sampleConversations = [{ id: '1', title: 'Machine learning algorithms' }];

  return (
    <div className="flex h-screen w-full overflow-hidden">
      <Sidebar conversations={sampleConversations} />
      <div className="flex-1 overflow-auto">
        {/* Replace WelcomeScreen with Chat for chat UI */}
        <Chat />
      </div>
    </div>
  );
}

export default App;
