import { Routes, Route } from 'react-router-dom';
import './App.css';
import WelcomePage from './components/WelcomePage';
import StudendPage from "./components/StudentPage/StudentPage"
import LoginForm from './components/Forms/LoginForm';



function App() {
  return (
    <div>
      <Routes>
        <Route index element={<WelcomePage />} />
        <Route path="/student" element={<StudendPage />} />
        <Route path="/login" element={<LoginForm />} />
      </Routes>
    </div>
  );
}

export default App;
