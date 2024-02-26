const questionData = {
  question:
    "Explain the concept of 'Inheritance' in Object-Oriented Programming.",
  summary:
    'Inheritance is a mechanism wherein a new class is derived from an existing class.',
  studentAnswer:
    'Inheritance allows a class to use methods and properties of another class.',
  correctAnswer:
    'Inheritance is a fundamental concept of OOP that allows a class to inherit properties and behavior (methods) from another class.',
};

const QuestionAnswerDisplay = () => {
  return (
    <div className="my-8 rounded-lg bg-white p-6 shadow">
      <div className="mb-8">
        <h2 className="mb-4 text-xl font-semibold">Question</h2>
        <p className="mb-4">{questionData.question}</p>
        <h3 className="text-lg font-semibold">Summary of Answers</h3>
        <p>{questionData.summary}</p>
      </div>

      <div className="flex flex-col md:flex-row">
        <div className="mb-4 md:mb-0 md:w-1/2 md:pr-2">
          {questionData.studentAnswer && (
            <>
              <h3 className="text-lg font-semibold">Your Answer</h3>
              <p className="rounded bg-gray-100 p-4">
                {questionData.studentAnswer}
              </p>
            </>
          )}
        </div>
        <div className="md:w-1/2 md:pl-2">
          <h3 className="text-lg font-semibold">Correct Answer</h3>
          <p className="rounded bg-gray-100 p-4">
            {questionData.correctAnswer}
          </p>
        </div>
      </div>
    </div>
  );
};

export default QuestionAnswerDisplay;
