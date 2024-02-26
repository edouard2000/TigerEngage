import { Link } from 'react-router-dom';
import Navbar from './Navbar';
import FeaturesSection from './FeaturesSection';
import Footer from './Footer';

const HomePage = () => {
  return (
    <div>
      <Navbar />
      <div className="bg-sky-900 py-20 text-center text-white">
        <h1 className="mb-4 text-5xl font-bold">Welcome to TigerEngage</h1>
        <p className="mb-8 text-xl">
          Transforming the educational experience through streamlined classroom
          interactions and engagement.
        </p>
        <Link
          to="/role-selection"
          className="rounded-full bg-white px-4 py-2 font-bold text-sky-950 hover:bg-gray-100"
        >
          Get Started
        </Link>
      </div>
      <div className="my-20 px-10">
        <FeaturesSection />
      </div>
      <Footer />
    </div>
  );
};

export default HomePage;
