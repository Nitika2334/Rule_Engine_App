import React, { useEffect, useState } from 'react';
import axios from 'axios';
import RulesLoader from './RulesLoader';

const RuleList = () => {
  const [rules, setRules] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [expandedRuleId, setExpandedRuleId] = useState(null);
  const [error, setError] = useState(null); // State to track errors

  useEffect(() => {
    const fetchRules = async () => {
      try {
        const response = await axios.get('http://127.0.0.1:5000/api/v1/getRules');
        const formattedRules = response.data.map(rule => ({
          _id: rule.id,
          ruleName: rule.rule_name,
          rule: rule.rule,
          root: rule.root,
          postfixExpr: rule.postfixExpr
        }));
        setIsLoading(false);
        setRules(formattedRules);
      } catch (error) {
        console.error('Error fetching rules:', error);
        setError('Failed to load rules. Please try again later.');
      } finally {
        setIsLoading(false); // Ensure loading state is stopped
      }
    };

    fetchRules();
  }, []);

  const handleRuleClick = (id) => {
    setExpandedRuleId(expandedRuleId === id ? null : id);
  };

  const handleCloseDescription = () => {
    setExpandedRuleId(null);
  };

  if (isLoading) {
    return (
      <div className='text-white flex justify-center'>
        <RulesLoader text={"Loading Rules"} />
      </div>
    );
  }

  if (error) {
    return (
      <div className='text-red-500 flex justify-center'>
        {error}
      </div>
    );
  }

  return (
    <div className="bg-white shadow-md rounded-lg p-4">
      <h2 className="text-3xl text-black font-bold mb-4">Rule List</h2>
      <ul className='text-gray-900'>
        {rules.map((rule) => (
          <li key={rule._id} className="mb-2 text-2xl">
            <div
              className="cursor-pointer"
              onClick={() => handleRuleClick(rule._id)}
            >
              <strong>{rule.ruleName}</strong>
            </div>
            {expandedRuleId === rule._id && (
              <div className="ml-4 text-gray-900 bg-slate-300 p-4 text-lg">
                <div>{rule.rule}</div>
                <div><strong>Root:</strong> {rule.root}</div>
                <div><strong>Postfix Expression:</strong> {Array.isArray(rule.postfixExpr) ? rule.postfixExpr.join(' ') : rule.postfixExpr}</div>
                <button
                  className="mt-2 bg-red-500 text-white px-2 py-1 rounded"
                  onClick={handleCloseDescription}
                >
                  Close
                </button>
              </div>
            )}
          </li>
        ))}
      </ul>
    </div>
  );
};

export default RuleList;
