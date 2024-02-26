import ClassList from './ClassList';
import ChatSystem from './ChatSystem';
import QuestionAnswerDisplay from './QuestionAnswerDisplay';
import AnswerSubmissionForm from './AnswerSubmissionForm';

const dummyQuestion = 'What is Polymorphism in Object-Oriented Programming?';

const StudentDashboard = () => {
  const isActive = true;

  return (
    <div>
      <div className="container mx-auto px-4 py-8">
        <h1 className="mb-8 text-center text-2xl font-bold">
          Student Dashboard
        </h1>
        <ClassList />
        <ChatSystem />
        <QuestionAnswerDisplay question={dummyQuestion} isActive={isActive} />
        <AnswerSubmissionForm question={dummyQuestion} isActive={isActive} />
      </div>
    </div>
  );
};

export default StudentDashboard;
