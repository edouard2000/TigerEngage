import PropTypes from 'prop-types';
import { Link } from 'react-router-dom'; // Import Link from react-router-dom
import classData from '../utils/classData';

const ClassListDisplay = ({ searchTerm }) => {
  const filteredClasses = classData.filter((cls) =>
    cls.name.toLowerCase().includes(searchTerm.toLowerCase()),
  );

  return (
    <div className="flex flex-col items-center space-y-2">
      {filteredClasses.length > 0 ? (
        filteredClasses.map((cls) => (
          <div
            key={cls.id}
            className="hover:bg-animate mb-4 w-full max-w-md rounded-lg
             bg-sky-900 p-3 shadow-md transition-all duration-300 
             hover:scale-105"
          >
            <div className="flex items-center justify-between hover:py-2">
              <span className="text-lg font-medium text-white">{cls.name}</span>
              {cls.started ? (
                <Link
                  to={`/class-page/${cls.id}`}
                  className="rounded-full bg-blue-900 px-4 
                  py-2 text-sm font-semibold text-white 
                  shadow-sm hover:bg-blue-700"
                >
                  Join Class
                </Link>
              ) : (
                <span
                  className="rounded-full bg-gray-300 px-4 
                py-2 text-sm font-semibold text-gray-800 
                shadow-sm"
                >
                  Not Started
                </span>
              )}
            </div>
          </div>
        ))
      ) : (
        <p>No classes Added Yet.</p>
      )}
    </div>
  );
};

ClassListDisplay.propTypes = {
  searchTerm: PropTypes.string.isRequired,
};

export default ClassListDisplay;
