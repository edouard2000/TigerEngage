import { useNavigate } from 'react-router-dom';
import SimpleNavBar from './SimpleNavBar';

const RoleSelection = () => {
  const navigate = useNavigate();

  const handleRoleSelect = (role) => {
    switch (role) {
      case 'student':
        navigate('/student-dashboard');
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
    <>
      <SimpleNavBar />
      <div className="mt-60 flex justify-center">
        <div
          className="w-full max-w-md rounded-lg bg-white px-8
         py-10 shadow-lg transition-shadow duration-300 hover:shadow-2xl"
        >
          <h2 className="mb-10 text-center text-3xl font-semibold">
            Select Your Role
          </h2>
          <div className="flex justify-center space-x-4">
            <button
              onClick={() => handleRoleSelect('student')}
              className="rounded bg-blue-500 px-4 py-2 font-bold
               text-white transition-all duration-300 hover:scale-105
                hover:bg-blue-700 hover:py-3"
            >
              Student
            </button>
            <button
              onClick={() => handleRoleSelect('professor')}
              className="rounded bg-blue-500 px-4 py-2 font-bold
               text-white transition-all duration-300 hover:scale-105
                hover:bg-blue-700 hover:py-3"
            >
              Professor
            </button>
            <button
              onClick={() => handleRoleSelect('preceptor')}
              className="rounded bg-blue-500 px-4 py-2 font-bold
               text-white transition-all duration-300 
               hover:scale-105 hover:bg-blue-700 hover:py-3"
            >
              Preceptor
            </button>
          </div>
        </div>
      </div>
    </>
  );
};

export default RoleSelection;
