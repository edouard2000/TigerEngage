import { useState } from 'react';

const SearchBar = () => {
  const [isFocused, setIsFocused] = useState(false);

  return (
    <div className="flex items-center justify-center py-4">
      <input
        type="text"
        onFocus={() => setIsFocused(true)}
        onBlur={() => setIsFocused(false)}
        className={`border-2 px-4 py-2 transition-all duration-300 ease-in-out ${
          isFocused ? 'w-72 border-blue-500' : 'w-48 border-gray-300'
        }`}
        placeholder="Search..."
      />
    </div>
  );
};

export default SearchBar;
