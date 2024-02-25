const SearchBar = () => {
  return (
    <div className="fixed top-0 z-10 w-full px-4 py-2"> 
      <input
        type="text"
        className="w-auto rounded-full  border-transparent bg-white px-10 py-2 shadow-md focus:border-4 focus:border-blue-600 focus:outline-none"
        placeholder="Search..."
        style={{ marginRight: '1rem', width: 'calc(100% - 1rem)' }} 
      />
    </div>
  );
};


export default SearchBar;
