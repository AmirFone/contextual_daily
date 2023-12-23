import './App.css';
import FileUpload from './FileUpload'; //
import ChatInterface from './ChatInterface'; // This is a placeholder for your new chat component
function App() {
  return (
    <div className="App">
      <div className="main-container">
        <FileUpload />
        <ChatInterface />
      </div>
    </div>
  );
}


export default App;