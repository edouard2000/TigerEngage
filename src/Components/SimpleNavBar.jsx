import { Link } from 'react-router-dom';
import PropTypes from 'prop-types';

const Navbar = ({ title, to, chatLink }) => {
  return (
    <nav className="bg-sky-950 p-4 text-white sm:p-6 md:flex md:items-center md:justify-between">
    <div className="flex items-center justify-between w-full">
      <div className="text-lg font-bold">
        <Link to={to}>{title}</Link>
      </div>
      {chatLink && (
        <Link to={chatLink} className="text-lg font-bold">
          Live Chat
        </Link>
      )}
    </div>
  </nav>
  
  );
};

export default Navbar;

Navbar.propTypes = {
  title: PropTypes.string.isRequired,
  to: PropTypes.string.isRequired,
  chatLink: PropTypes.string,
};
