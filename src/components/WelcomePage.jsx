import { Link } from 'react-router-dom';

const WelcomePage = () => {
  return (
    <div className="flex h-screen">
      <div className="m-auto">
        <div
          tabIndex="0"
          className="rounded-lg border-4 border-transparent bg-sky-50 
          p-8 shadow-lg focus:border-2 focus:border-blue-600 focus:outline-none"
        >
          <div className="flex flex-col items-center space-y-12">
            <div className="text-center text-blue-700">
              <h4 className="font-medium">Welcome to TigerEngage</h4>
            </div>

            <div className="flex flex-row items-center space-x-4">
              <Link
                to="/professor"
                className="inline-block rounded bg-blue-500 px-5 py-2
                 text-white hover:bg-sky-700"
              >
                Professor
              </Link>
              <Link
                to="/preceptor"
                className="inline-block rounded bg-blue-500 px-5 
                py-2 text-white hover:bg-sky-700"
              >
                Preceptor
              </Link>
              <Link
                to="/student"
                className="inline-block rounded bg-blue-500 px-5 py-2
                 text-white hover:bg-sky-700"
              >
                Student
              </Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default WelcomePage;
