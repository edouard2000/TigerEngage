import { Link } from 'react-router-dom';

const Navbar = () => {
  return (
    <nav className="bg-sky-950 p-4 text-white sm:p-6 md:flex md:items-center md:justify-between">
      <div className="flex items-center justify-between">
        <div className="text-lg font-bold">
          <Link to="/">TigerEngage</Link>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
