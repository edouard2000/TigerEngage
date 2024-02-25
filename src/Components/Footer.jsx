import { Link } from 'react-router-dom';

const Footer = () => {
  return (
    <footer className="mt-8 bg-sky-950 p-4 text-center text-white">
      <div className="container mx-auto flex items-center justify-between">
        <p>
          <Link to="/" className="hover:underline">
            &copy; {new Date().getFullYear()} TigerEngage. All rights reserved.
          </Link>
        </p>
        <div className="flex justify-center space-x-4">
          <Link to="/privacy-policy" className="hover:underline">
            Privacy Policy
          </Link>
          <Link to="/terms-of-service" className="hover:underline">
            Terms of Service
          </Link>
          <Link to="/contact" className="hover:underline">
            Contact Us
          </Link>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
