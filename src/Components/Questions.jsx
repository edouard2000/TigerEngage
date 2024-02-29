import React, { useState } from 'react';
import PropTypes from 'prop-types';

export default function Questions({ question }) {
  const [answer, setAnswer] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    console.log(answer);
  };

  return (
    <form
      className="absolute inset-0 my-32 rounded-sm p-3"
      onSubmit={handleSubmit}
    >
      <p className="my-2 font-bold text-sky-950">{question}</p>
      <textarea
        placeholder="Enter your answer"
        value={answer}
        onChange={(e) => setAnswer(e.target.value)}
        className="h-48 w-full rounded-md border-2 border-sky-950 text-left shadow-sm focus:border-transparent focus:outline-none focus:ring-2 focus:ring-sky-500"
        style={{ padding: '6px 12px', resize: 'none' }}
      />
      <button
        type="submit"
        className="mt-4  rounded bg-sky-950 px-4 py-2 font-bold text-white hover:bg-sky-600"
      >
        Submit
      </button>
    </form>
  );
}

Questions.propTypes = {
  question: PropTypes.string.isRequired,
};
