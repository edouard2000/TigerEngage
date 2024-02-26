import PropTypes from 'prop-types';

const FeatureCard = ({ title, description }) => {
  return (
    <div
      className="rounded-lg bg-white p-4 shadow-lg 
    transition-colors duration-300 focus-within:bg-gray-100
     hover:bg-sky-900 hover:text-white "
    >
      <h3 className="mb-2 text-xl font-semibold text-sky-900 ">{title}</h3>
      <p>{description}</p>
    </div>
  );
};

FeatureCard.propTypes = {
  title: PropTypes.string.isRequired,
  description: PropTypes.string.isRequired,
};

export default FeatureCard;
