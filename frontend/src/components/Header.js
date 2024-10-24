import React, { useState } from 'react';
import { Link } from 'react-router-dom';

const Header = () => {
  const [dropdownOpen, setDropdownOpen] = useState(false);

  const toggleDropdown = () => {
    setDropdownOpen(!dropdownOpen);
  };

  return (
    <header className="bg-gray-900 shadow-lg p-4">
      <nav className="container mx-auto flex justify-between items-center text-white">
        <Link to="/" className="hover:text-pink-400">
          <h1 className="text-4xl font-bold tracking-wide">Rule Engine</h1>
        </Link>
        <div className="relative">
          {/* Dropdown Trigger */}
          <button
            onClick={toggleDropdown}
            className="text-xl font-medium hover:text-pink-400 focus:outline-none transition duration-300 ease-in-out"
          >
            Rules Menu
          </button>
          {/* Dropdown Content */}
          {dropdownOpen && (
            <div className="absolute right-0 mt-2 w-48 bg-gray-900 rounded-lg shadow-xl z-20">
              <Link
                to="/create-rule"
                className="block px-4 py-2 text-white hover:bg-white hover:text-black transition duration-300 ease-in-out"
                onClick={() => setDropdownOpen(false)}
              >
                Create Rule
              </Link>
              <Link
                to="/combine-rules"
                className="block px-4 py-2 text-white hover:bg-white hover:text-black transition duration-300 ease-in-out"
                onClick={() => setDropdownOpen(false)}
              >
                Combine Rules
              </Link>
              <Link
                to="/evaluate-rule"
                className="block px-4 py-2 hover:bg-white hover:text-black transition duration-300 ease-in-out"
                onClick={() => setDropdownOpen(false)}
              >
                Evaluate Rule
              </Link>
            </div>
          )}
        </div>
      </nav>
    </header>
  );
};

export default Header;