import PropTypes from 'prop-types';

export default function StudentAnswer({ studentAnswer }) {
  return (
    <div className="m-5 rounded-lg bg-black p-3">
      <p className="text-white">{studentAnswer}</p>
    </div>
  );
}

StudentAnswer.propTypes = {
  studentAnswer: PropTypes.string.isRequired,
};
