import { useNavigate } from 'react-router-dom';

const RoleSelection = () => {
  const navigate = useNavigate();

  const handleRoleSelect = (role) => {
    switch (role) {
      case 'student':
        navigate('/student-Dashboard');
        break;
      case 'professor':
        navigate('/professor-info');
        break;
      case 'preceptor':
        navigate('/preceptor-info');
        break;
      default:
        break;
    }
  };

  return (
    <div className="mt-20 text-center">
      <h2 className="mb-10 text-3xl font-semibold">Select Your Role</h2>
      <div className="space-x-4">
        <button
          onClick={() => handleRoleSelect('student')}
          className="rounded bg-blue-500 px-4 py-2 font-bold text-white hover:bg-blue-700"
        >
          Student
        </button>
        <button
          onClick={() => handleRoleSelect('professor')}
          className="rounded bg-blue-500 px-4 py-2 font-bold text-white hover:bg-blue-700"
        >
          Professor
        </button>
        <button
          onClick={() => handleRoleSelect('preceptor')}
          className="rounded bg-blue-500 px-4 py-2 font-bold text-white hover:bg-blue-700"
        >
          Preceptor
        </button>
      </div>
    </div>
  );
};

export default RoleSelection;

import UAParser from 'ua-parser-js';

const parser = new UAParser();
const result = parser.getResult();
const osName = result.os.name;

console.log(osName);
