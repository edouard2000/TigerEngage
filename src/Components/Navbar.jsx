import { Link } from 'react-router-dom';

const Navbar = () => {
  return (
    <nav className="bg-sky-950 p-4 text-white sm:p-6 md:flex md:items-center md:justify-between">
      <div className="flex items-center justify-between">
        <div className="text-lg font-bold">
          <Link to="/">TigerEngage</Link>
        </div>
        <div className="sm:hidden">
          <button
            type="button"
            className="text-white hover:text-gray-200 focus:outline-none focus:ring-2 focus:ring-gray-200"
          ></button>
        </div>
      </div>

      <div className="mt-4 hidden gap-4 md:mt-0 md:flex">
        <Link to="/student-dashboard" className="hover:text-gray-200">
          Student Dashboard
        </Link>
        <Link to="/professor-dashboard" className="hover:text-gray-200">
          Professor Dashboard
        </Link>
        <Link to="/preceptor-dashboard" className="hover:text-gray-200">
          Preceptor Dashboard
        </Link>
      </div>
    </nav>
  );
};

export default Navbar;
