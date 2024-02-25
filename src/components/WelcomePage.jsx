const WelcomePage = () => {
  return (
    <div className="flex h-screen">
      <div className="m-auto">
        <div className="bg-sky-50 shadow-lg rounded-lg p-8">
          <div className="flex flex-col items-center space-y-12">
            <div className="text-center text-blue-700">
              <h4>Welcome to TigerEngage</h4>
            </div>

            <div className="flex flex-row items-center space-x-4">
              <button className="bg-blue-500 px-5 py-2 rounded text-white hover:bg-sky-700">
                Professor
              </button>
              <button className="px-5 py-2 bg-blue-500 text-white rounded hover:bg-sky-700">
                Preceptor
              </button>
              <button className="px-5 py-2 bg-blue-500 text-white rounded hover:bg-sky-700">
                Student
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default WelcomePage;
