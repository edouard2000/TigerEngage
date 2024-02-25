import DisplayList from './DisplayClass';
import PropTypes from 'prop-types';

const ClassList = ({ classes }) => {
  return (
    <div>
      <DisplayList classes={classes} />
    </div>
  );
};

// silencing pro type warning form eslint
ClassList.propTypes = {
  classes: PropTypes.arrayOf(PropTypes.string).isRequired,
};

export default ClassList;
