import { useState } from 'react';
import PropTypes from 'prop-types';

const ClassSearchBar = ({ onSearch }) => {
  const [searchTerm, setSearchTerm] = useState('');

  const handleInputChange = (e) => {
    const term = e.target.value;
    setSearchTerm(term);

    onSearch(term);
  };

  return (
    <div className="my-4 flex justify-center">
      <input
        type="text"
        className="w-full max-w-xl rounded-lg border
         border-gray-300 px-4 py-2 shadow-sm transition duration-300 
         hover:shadow-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
        placeholder="Search for classes..."
        value={searchTerm}
        onChange={handleInputChange}
      />
    </div>
  );
};

export default ClassSearchBar;

ClassSearchBar.propTypes = {
  onSearch: PropTypes.string.isRequired,
};
