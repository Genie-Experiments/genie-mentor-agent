import './App.css';
import Sidebar from './components/shared/Sidebar';
import WelcomeScreen from './WelcomeScreen';

function App() {
  const sampleConversations = [{ id: '1', title: 'Machine learning algorithms' }];

  return (
    <div className="flex h-screen w-full overflow-hidden">
      <Sidebar conversations={sampleConversations} />
      <div className="flex-1 overflow-auto">
        <WelcomeScreen />
      </div>
    </div>
  );
}

export default App;
