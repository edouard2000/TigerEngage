import PropTypes from 'prop-types';

export default function AnswersSummary({ answers }) {
  return (
    <div className="m-5 rounded-lg bg-black p-3">
      <p className="text-white">{answers}</p>
    </div>
  );
}

AnswersSummary.propTypes = {
  answers: PropTypes.string.isRequired,
};
