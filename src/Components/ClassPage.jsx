import { useParams } from 'react-router-dom';
import classData from '../utils/classData';
import ChatSystem from './ChatSystem';
import QuestionAnswerDisplay from './QuestionAnswerDisplay';
import AnswerSubmissionForm from './AnswerSubmissionForm';

const ClassPage = () => {
  const { classId } = useParams();
  const classInfo = classData.find((cls) => cls.id === Number(classId));

  if (!classInfo) {
    return <div>Class not found.</div>;
  }

  const isActiveQuestion = classInfo.isActiveQuestion;

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="mb-4 text-2xl font-bold"> Welcone to, {classInfo.name}</h1>
      <p className="mb-4">{classInfo.description}</p>
      <ChatSystem />
      {isActiveQuestion && (
        <>
          <QuestionAnswerDisplay question="What is Polymorphism in Object-Oriented Programming?" />
          <AnswerSubmissionForm />
        </>
      )}

      {!classInfo.started && <div>Class has not started yet.</div>}
    </div>
  );
};

export default ClassPage;
