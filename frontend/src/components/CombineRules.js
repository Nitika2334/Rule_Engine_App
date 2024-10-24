import React, { useState } from 'react';
import axios from 'axios';
import RuleList from './RuleList';

const CombineRules = () => {
    const [ruleName, setRuleName] = useState('');
    const [rules, setRules] = useState(['']);
    const [message, setMessage] = useState('');
    const [error, setError] = useState('');

    const handleAddRule = () => {
        setRules([...rules, '']);
    };

    const handleRemoveRule = (index) => {
        const newRules = [...rules];
        newRules.splice(index, 1);
        setRules(newRules);
    };

    const handleRuleChange = (index, value) => {
        const newRules = [...rules];
        newRules[index] = value;
        setRules(newRules);
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            const response = await axios.post('http://127.0.0.1:5000/api/v1/combine_rules', {
                rule_name: ruleName,
                rules
            });
            setMessage(response.data.message);
            setError('');
        } catch (error) {
            console.error('Error combining rules:', error);
            setError(error.response?.data?.error || 'Failed to combine rules');
        }
    };

    return (
        <div className="flex min-h-screen bg-gray-900 text-white">
            <div className="p-4 w-full bg-white rounded shadow-md flex flex-col items-center justify-start mx-6">
                <h2 className="text-5xl text-black font-extrabold mb-6">Combine Rules</h2>
                <form onSubmit={handleSubmit} className="w-full">
                    <div className="mb-6">
                        <label className="block text-gray-900 text-2xl font-bold">Rule Name</label>
                        <input
                            type="text"
                            className="border rounded w-full py-3 px-3 bg-gray-900 text-gray-200 text-2xl"
                            value={ruleName}
                            onChange={(e) => setRuleName(e.target.value)}
                            required
                        />
                    </div>
                    {rules.map((rule, index) => (
                        <div key={index} className="mb-6 flex items-center">
                            <label className="block text-gray-900 mr-2 w-20 text-2xl font-bold">Rule {index + 1}</label>
                            <input
                                type="text"
                                className="border rounded w-full py-3 px-3 bg-gray-900 text-gray-200 text-2xl"
                                value={rule}
                                onChange={(e) => handleRuleChange(index, e.target.value)}
                                required
                            />
                            <button
                                type="button"
                                className="bg-red-500 text-white px-4 py-2 rounded text-2xl ml-2"
                                onClick={() => handleRemoveRule(index)}
                            >
                                Remove
                            </button>
                        </div>
                    ))}
                    <div>
                        <button
                            type="button"
                            className="bg-gray-900 text-white px-4 py-2 rounded text-3xl font-bold my-6 mx-2"
                            onClick={handleAddRule}
                        >
                            Add Rule
                        </button>
                        <button
                            type="submit"
                            className="bg-gray-900 text-white px-4 py-2 rounded text-3xl font-bold my-6"
                        >
                            Combine Rules
                        </button>
                    </div>
                </form>
                {message && <p className="mt-4 text-green-400 text-3xl font-bold">{message}</p>}
                {error && <p className="mt-4 text-red-400 text-3xl font-bold">{error}</p>}
            </div>
            <RuleList />
        </div>
    );
};

export default CombineRules;