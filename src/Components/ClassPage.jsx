import { useState } from 'react';
import { useParams } from 'react-router-dom';
import classData from '../utils/classData';
import ChatSystem from './ChatSystem';
import AnswerSubmissionForm from './AnswerSubmissionForm';
import SimpleNavBar from './SimpleNavBar';
import Question from './Questions';
import StudentAnswer from './StudentAnswer';
import CorrectAnswer from './CorrectAnswer';
import AnswersSummary from './AnswersSummary';

const ClassPage = () => {
  const { classId } = useParams();
  const classInfo = classData.find((cls) => cls.id === Number(classId));
  const [isChat, setChat] = useState(false);

  if (!classInfo) {
    return <div>Class not found.</div>;
  }

  const isActiveQuestion = classInfo.isActiveQuestion;

  return (
    <>
      <SimpleNavBar
        title={classInfo.name}
        chatLink={`/class-page/${classId}/chat`}
      />
      <div className="flex">
        <div className="w-1/2">
          <Question
            question="What are the advantages and disadvantages o
          f each, and in what scenarios would you prefer to use one over the other?"
          />
        </div>
      </div>
    </>
  );
};

export default ClassPage;
