import PropTypes from 'prop-types';

export default function CorrectAnswer({ correctAnswer }) {
  return (
    <div className="m-5 rounded-lg bg-black p-3">
      <p className="text-white">{correctAnswer}</p>
    </div>
  );
}

CorrectAnswer.propTypes = {
  correctAnswer: PropTypes.string.isRequired,
};
