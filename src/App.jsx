import { Routes, Route } from 'react-router-dom';
import './App.css';
import WelcomePage from './components/WelcomePage';
import StudendPage from "./components/StudentPage/StudentPage"



function App() {
  return (
    <div>
      <Routes>
        <Route index element={<WelcomePage />} />
        <Route path="/student" element={<StudendPage />} />
      </Routes>
    </div>
  );
}

export default App;
