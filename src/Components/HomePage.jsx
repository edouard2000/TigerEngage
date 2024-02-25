import { Link } from 'react-router-dom';
import Navbar from './Navbar';
import FeatureCard from './FeatureCard';
import Footer from './Footer';

const HomePage = () => {
  return (
    <div>
      <Navbar />
      <div className="bg-sky-900 py-20 text-center text-white">
        <h1 className="mb-4 text-5xl font-bold">Welcome to TigerEngage</h1>
        <p className="mb-8 text-xl">
          Transforming the educational experience through streamlined classroom
          interactions and engagement.
        </p>
        <Link
          to="/login-selection"
          className="rounded-full bg-white px-4 py-2 font-bold text-blue-600 hover:bg-gray-100"
        >
          Get Started
        </Link>
      </div>
      <div className="my-20 px-10">
        <h2 className="mb-12 text-center text-4xl font-bold">Features</h2>
        <div className="grid grid-cols-1 gap-10 md:grid-cols-3">
          <FeatureCard
            title="Answer Summarization"
            description="Leveraging advanced AI, our platform provides concise summaries of classroom Q&As and discussions.
             This tool helps in capturing the essence of classroom interactions,
             making study and revision more efficient by highlighting key points and answers provided during the session."
          />
          <FeatureCard
            title="Live Chat"
            description="Engage in real-time discussions with peers and instructors during class sessions to clarify doubts, ask questions, and enhance your learning experience.
             Our live chat feature ensures that everyone can participate and contribute to the classroom conversation, even from afar."
          />
          <FeatureCard
            title="Attendance Tracking"
            description="Simplify the attendance process with our automated check-in system.
             Students can mark their presence within a designated range or timeframe,
             ensuring accurate and hassle-free attendance tracking for both online and physical classes"
          />
          <FeatureCard
            title="Permission Requests"
            description="Easily submit requests to be excused from lectures or precepts through our platform.
             Supporting documents can be uploaded for evidence,
             streamlining the process for both students and instructors and ensuring transparency and understanding in excusal requests"
          />
          <FeatureCard
            title="End Class Pop-up Survey"
            description="Provide immediate feedback at the end of each class session with our pop-up survey feature. Share your thoughts on the lecture materials, teaching methods, and overall class experience. 
            This feedback is invaluable for instructors to adapt and improve the learning experience in real-time"
          />
        </div>
      </div>
      <Footer />
    </div>
  );
};

export default HomePage;
