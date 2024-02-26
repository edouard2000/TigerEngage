import ClassList from './ClassList';

const StudentDashboard = () => {
  return (
    <div>
      <div className="container mx-auto px-4 py-8">
        <h1 className="mb-8 text-center text-2xl font-bold">
          Student Dashboard
        </h1>

        <ClassList />
      </div>
    </div>
  );
};

export default StudentDashboard;
