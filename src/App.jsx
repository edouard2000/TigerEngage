import { Routes, Route } from 'react-router-dom';
import './App.css';
import HomePage from './Components/HomePage';
import RoleSelection from './Components/RoleSelection';



function App() {
  return (
    <div>
      <Routes>
        <Route index element={<HomePage />} />
        <Route path='/role-selection' element={<RoleSelection />} />
      </Routes>
    </div>
  );
}

export default App;
