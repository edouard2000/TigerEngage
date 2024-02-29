import { useState } from 'react';
import ClassListDisplay from './ClassListDisplay';
import SimpleNavBar from './SimpleNavBar';

const ClassSearchBar = () => {
  const [searchTerm, setSearchTerm] = useState('');

  const handleSearchChange = (event) => {
    setSearchTerm(event.target.value);
  };

  return (
    <>
      <SimpleNavBar to="/" title="TigerEngage" />
      <div className="flex justify-center p-4">
        <div className="max-w-lg">
          <input
            type="text"
            className="mb-4 w-5/6 rounded-lg border border-gray-300
             p-3 shadow-sm duration-300 
             ease-in-out hover:translate-y-4 hover:shadow-lg focus:w-5/6 focus:scale-105
              focus:outline-none focus:ring-2 focus:ring-blue-500 active:border-blue-500"
            placeholder="Search for classes..."
            value={searchTerm}
            onChange={handleSearchChange}
          />
        </div>
      </div>
      <ClassListDisplay searchTerm={searchTerm} />
    </>
  );
};

export default ClassSearchBar;
