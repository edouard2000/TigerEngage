import PropTypes from 'prop-types';

const classData = [
  { id: 1, name: 'Introduction to Computer Science', started: true },
  { id: 2, name: 'Advanced Algorithms', started: false },
  { id: 3, name: 'Operating Systems', started: true },
];

const ClassListDisplay = ({ searchTerm }) => {
  const filteredClasses = classData.filter((cls) =>
    cls.name.toLowerCase().includes(searchTerm.toLowerCase()),
  );

  return (
    <div className="flex flex-col items-center">
      {filteredClasses.length > 0 ? (
        filteredClasses.map((cls) => (
          <div
            key={cls.id}
            className="mb-4 w-full max-w-md rounded-lg bg-white p-3 shadow-md transition duration-300 hover:bg-gray-50 active:bg-gray-100"
          >
            <div className="flex items-center justify-between">
              <span className="text-lg font-medium">{cls.name}</span>
              <button
                className={`rounded-full px-4 py-2 text-sm font-semibold shadow-sm ${cls.started ? 'bg-blue-500 text-white hover:bg-blue-600' : 'bg-gray-300 text-gray-800'}`}
                disabled={!cls.started}
              >
                {cls.started ? 'Join Class' : 'Not Started'}
              </button>
            </div>
          </div>
        ))
      ) : (
        <p>No classes found.</p>
      )}
    </div>
  );
};

export default ClassListDisplay;

ClassListDisplay.propTypes = {
  searchTerm: PropTypes.string.isRequired,
};
