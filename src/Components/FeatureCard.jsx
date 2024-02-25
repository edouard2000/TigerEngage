import PropTypes from 'prop-types'; 

const FeatureCard = ({ title, description }) => (
  <div className="rounded-lg bg-white p-6 shadow-lg">
    <h3 className="mb-4 text-2xl font-bold">{title}</h3>
    <p>{description}</p>
  </div>
);

FeatureCard.propTypes = {
  title: PropTypes.string.isRequired, 
  description: PropTypes.string.isRequired, 
};

export default FeatureCard;
