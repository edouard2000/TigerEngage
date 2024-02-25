import PropTypes from 'prop-types';

const DisplayList = ({ classes }) => {
  return (
    <ul className="ml-3 flex flex-col items-center space-y-2 ">
      {classes.map((className, index) => (
        <li
          key={index}
          className="w-1/4 cursor-pointer rounded-md bg-blue-500 px-4 py-2
                     text-center text-white hover:bg-blue-600
                     focus:bg-blue-700 focus:outline-none"
          tabIndex={0}
        >
          {className}
        </li>
      ))}
    </ul>
  );
};

DisplayList.propTypes = {
  classes: PropTypes.arrayOf(PropTypes.string).isRequired,
};

export default DisplayList;
