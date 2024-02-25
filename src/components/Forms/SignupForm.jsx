const SignupForm = () => {
    return (
      <div className="flex min-h-screen items-center justify-center bg-gray-100">
        <div className="w-full max-w-md space-y-3 rounded-xl bg-white p-8 shadow-lg">
          <h2 className="text-center text-2xl font-bold">Create an Account</h2>
          <form className="space-y-6">
            <div>
              <label htmlFor="first-name" className="text-sm font-medium text-gray-700">
                First Name
              </label>
              <input
                type="text"
                id="first-name"
                name="first-name"
                className="mt-1 w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-indigo-500 focus:outline-none focus:ring-indigo-500"
                required
              />
            </div>
            <div>
              <label htmlFor="last-name" className="text-sm font-medium text-gray-700">
                Last Name
              </label>
              <input
                type="text"
                id="last-name"
                name="last-name"
                className="mt-1 w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-indigo-500 focus:outline-none focus:ring-indigo-500"
                required
              />
            </div>
            <div>
              <label htmlFor="email" className="text-sm font-medium text-gray-700">
                Email
              </label>
              <input
                type="email"
                id="email"
                name="email"
                className="mt-1 w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-indigo-500 focus:outline-none focus:ring-indigo-500"
                required
              />
            </div>
            <div>
              <label htmlFor="password" className="text-sm font-medium text-gray-700">
                Password
              </label>
              <input
                type="password"
                id="password"
                name="password"
                className="mt-1 w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-indigo-500 focus:outline-none focus:ring-indigo-500"
                required
              />
            </div>
            <div>
              <label htmlFor="password-confirm" className="text-sm font-medium text-gray-700">
                Confirm Password
              </label>
              <input
                type="password"
                id="password-confirm"
                name="password-confirm"
                className="mt-1 w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-indigo-500 focus:outline-none focus:ring-indigo-500"
                required
              />
            </div>
            <div className="flex justify-center">
              <button
                type="submit"
                className="w-1/2 rounded-md border border-transparent bg-blue-600 px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2"
              >
                Sign Up
              </button>
            </div>
          </form>
        </div>
      </div>
    );
  };
  
  export default SignupForm;
  