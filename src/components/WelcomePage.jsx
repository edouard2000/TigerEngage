import { Link } from 'react-router-dom'; 

const WelcomePage = () => {
  return (
    <div className="flex h-screen">
      <div className="m-auto">
        <div className="rounded-lg bg-sky-50 p-8 shadow-lg">
          <div className="flex flex-col items-center space-y-12">
            <div className="text-center text-blue-700">
              <h4 className="font-medium">Welcome to TigerEngage</h4>
            </div>

            <div className="flex flex-row items-center space-x-4">
              <Link to="/professor" className="inline-block rounded bg-blue-500 px-5 py-2 text-white hover:bg-sky-700">
                Professor
              </Link>
              <Link to="/preceptor" className="inline-block rounded bg-blue-500 px-5 py-2 text-white hover:bg-sky-700">
                Preceptor
                </Link>
                <Link to="/student" className="inline-block rounded bg-blue-500 px-5 py-2 text-white hover:bg-sky-700">
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
