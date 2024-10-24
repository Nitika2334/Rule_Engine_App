import React, { useState } from 'react';
import axios from 'axios';
import RuleList from '../components/RuleList';
const CreateRule = () => {
  const [ruleName, setRuleName] = useState('');
  const [rule, setRule] = useState('');
  const [response, setResponse] = useState(null);
  const [error, setError] = useState(null);
  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setResponse(null);
    try {
      const res = await axios.post('http://127.0.0.1:5000/api/v1/create', {
        rule_name: ruleName,
        rule,
      });
      setResponse(res.data);
    } catch (err) {
      setError(err.response?.data?.error || 'Something went wrong');
    }
  };
  return (
    <div className="flex min-h-screen bg-gray-900 text-black">
      {/* Create Rule Section (Left Side) */}
      <div className="p-2 w-full bg-white rounded shadow-md flex flex-col items-center justify-start mx-6">
        <h2 className="text-5xl font-extrabold mb-6">Create Rule</h2>
        <form onSubmit={handleSubmit} className="w-full">
          <div className="mb-6">
            <label className="block text-gray-900 text-2xl font-bold">Rule Name:</label>
            <input
              type="text"
              value={ruleName}
              placeholder='Write Your rule name please'
              onChange={(e) => setRuleName(e.target.value)}
              className="w-full p-3 border rounded w-96 bg-gray-900 text-white text-2xl"
            />
          </div>
          <div className="mb-6">
            <label className="block text-gray-900 text-2xl font-bold">Rule:</label>
            <textarea
              value={rule}
              onChange={(e) => setRule(e.target.value)}
              className="w-full p-3 border text-gray-200 text-2xl rounded bg-gray-900"
              rows="4"
            />
          </div>
          <div className="flex justify-between items-center mb-4">
            <button type="submit" className="bg-gray-900 px-6 py-3 text-3xl font-bold text-white rounded shadow-md hover:bg-blue-600 transition duration-300">
              Create Rule
            </button>
          </div>
        </form>
        {/* Display the response or error after form submission */}
        {response && (
          <div className="mt-4 p-4 bg-green-100 text-black rounded">
            <pre>{JSON.stringify(response, null, 2)}</pre>
          </div>
        )}
        {error && (
          <div className="mt-4 p-4 bg-red-100 text-red-700 rounded text-3xl font-bold">
            {error}
          </div>
        )}
      </div>
      {/* Sidebar with Rule List (Right Side) */}
      <div className="w-1/3 bg-gray-900 p-4 rounded shadow-md">
        <RuleList />
      </div>
    </div>
  );
};
export default CreateRule;
