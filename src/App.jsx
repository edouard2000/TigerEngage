import { Routes, Route } from 'react-router-dom';
import './App.css';
import HomePage from './Components/HomePage';



function App() {
  return (
    <div>
      <Routes>
        <Route index element={<HomePage />} />
      </Routes>
    </div>
  );
}

export default App;
