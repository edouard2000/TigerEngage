import { Routes, Route } from 'react-router-dom';
import './App.css';
import HomePage from './Components/HomePage';
import RoleSelection from './Components/RoleSelection';
import StudentDashboard from './Components/StudentDashboard';
import ClassPage from './Components/ClassPage';

function App() {
  return (
    <div>
      <Routes>
        <Route index element={<HomePage />} />
        <Route path="/role-selection" element={<RoleSelection />} />
        <Route path="/student-Dashboard" element={<StudentDashboard />} />
        <Route path="/class-page/:classId" element={<ClassPage />} />
      </Routes>
    </div>
  );
}

export default App;
