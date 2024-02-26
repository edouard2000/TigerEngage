import FeatureCard from './FeatureCard';
import FeatureData from '../utils/featureData';

const FeaturesSection = () => {
  return (
    <div className="my-20 px-10">
      <h2 className="mb-12 text-center text-3xl font-bold text-sky-900">
        Features
      </h2>
      <div className="grid grid-cols-1 gap-10 md:grid-cols-3">
        {FeatureData.map((feature, index) => (
          <FeatureCard
            key={index}
            title={feature.title}
            description={feature.description}
          />
        ))}
      </div>
    </div>
  );
};

export default FeaturesSection;
