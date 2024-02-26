import { useState } from 'react';
import PropTypes from 'prop-types';

const AnswerSubmissionForm = ({ question, isActive }) => {
  const [answer, setAnswer] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();

    console.log('Submitted answer:', answer);

    setAnswer('');
  };

  if (!isActive) {
    return null;
  }

  return (
    <div className="my-8 rounded-lg border-2 border-sky-900 bg-white p-6 shadow-2xl">
      <h2 className="mb-4 text-lg font-semibold">Answer the Question</h2>
      <p className="mb-4">{question}</p>
      <form onSubmit={handleSubmit} className="space-y-4">
        <textarea
          className=" w-full resize-none rounded border border-gray-300 p-2"
          rows="4"
          placeholder="Type your answer here..."
          value={answer}
          onChange={(e) => setAnswer(e.target.value)}
        />
        <button
          type="submit"
          className="rounded bg-sky-900 px-4 py-2 text-white hover:bg-blue-900"
        >
          Submit Answer
        </button>
      </form>
    </div>
  );
};

AnswerSubmissionForm.propTypes = {
  question: PropTypes.string.isRequired,
  isActive: PropTypes.string.isRequired,
};

export default AnswerSubmissionForm;
