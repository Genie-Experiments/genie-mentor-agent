import './App.css'
import Sidebar from './components/shared/Sidebar'

function App() {
  // Sample conversation data
  const sampleConversations = [
    { id: '1', title: 'Introduction to AI concepts' },
    { id: '2', title: 'Machine learning algorithms' },
    { id: '3', title: 'Neural networks deep dive' },
  ]

  return (
    <div className="flex h-screen w-full overflow-hidden">
      <Sidebar conversations={sampleConversations} />
      <div className="flex-1 p-8">
        <h1 className="text-2xl font-bold">
          Welcome to the Genie Mentor App!
        </h1>
        <p className="mt-4">Select a conversation from the sidebar or start a new chat.</p>
      </div>
    </div>
  )
}

export default App
