import React, { useState } from 'react';
import axios from 'axios';
import RuleList from './RuleList';

const EvaluateRule = () => {
  const [ruleName, setRuleName] = useState('');
  const [conditions, setConditions] = useState('');
  const [result, setResult] = useState(null);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await axios.post('http://127.0.0.1:5000/api/v1/eval', {
        rule_name: ruleName,
        conditions: JSON.parse(conditions),
      });

      setResult(response.data);
      setMessage(response.data.message);
      setError('');
    } catch (error) {
      setError(error.response?.data?.error || 'Error Evaluating rules');
    }
  };

  return (
    <div className="flex min-h-screen bg-black text-white">
      <div className="p-4 w-full bg-white rounded shadow-md flex flex-col items-center justify-start mx-6">
        <h2 className="text-5xl text-black font-extrabold mb-6">Evaluate Rule</h2>
        <form onSubmit={handleSubmit} className="w-full">
          <div className="mb-6">
            <label className="block text-gray-900 text-2xl font-bold">Rule Name:</label>
            <input
              type="text"
              value={ruleName}
              onChange={(e) => setRuleName(e.target.value)}
              className="w-full p-3 border rounded bg-gray-900 text-gray-200 text-2xl"
              required
            />
          </div>
          <div className="mb-6">
            <label className="block text-gray-900 text-2xl font-bold">Conditions (JSON format):</label>
            <textarea
              value={conditions}
              onChange={(e) => setConditions(e.target.value)}
              className="w-full p-3 border rounded bg-gray-900 text-gray-200 text-2xl"
              rows="4"
              required
            />
          </div>
          <button
            type="submit"
            className="bg-gray-900 text-white p-3 text-3xl font-bold rounded my-6"
          >
            Evaluate Rule
          </button>
        </form>
        {result && (
          <div className="mt-4 p-4 bg-gray-600 rounded">
            <pre>{JSON.stringify(result, null, 2)}</pre>
          </div>
        )}
        {message && <p className="mt-4 text-green-400 text-3xl font-bold">{message}</p>}
        {error && <p className="mt-4 text-red-400 text-3xl font-bold">{error}</p>}
      </div>
      <RuleList />
    </div>
  );
};

export default EvaluateRule;