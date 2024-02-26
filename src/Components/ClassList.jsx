import { useState } from 'react';
import ClassListDisplay from './ClassListDisplay';

const ClassSearchBar = () => {
  const [searchTerm, setSearchTerm] = useState('');

  const handleSearchChange = (event) => {
    setSearchTerm(event.target.value);
  };

  return (
    <div className="p-4">
      <input
        type="text"
        className="mb-4 w-full rounded-lg border
         border-gray-300 p-3 shadow-sm transition duration-300
          hover:shadow-lg focus:outline-none focus:ring-2
           focus:ring-blue-500 active:border-blue-500"
        placeholder="Search for classes..."
        value={searchTerm}
        onChange={handleSearchChange}
      />
      <ClassListDisplay searchTerm={searchTerm} />
    </div>
  );
};

export default ClassSearchBar;
