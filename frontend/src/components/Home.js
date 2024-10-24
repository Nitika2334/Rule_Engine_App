import React from 'react';
// import Header from './Header';

const Home = () => {
  return (
    <>
      <div className="flex flex-col items-center justify-center min-h-screen bg-white text-black">
        <h1 className="text-5xl font-extrabold mb-4">Rule Engine Using AST</h1>
        <p className="text-2xl font-bold text-center px-4 mb-4">
          Welcome to the Rule Engine using Abstract Syntax Tree (AST). This engine enables you to create, combine, and evaluate rules effectively to determine user eligibility based on various attributes.
        </p>
        <p className="text-xl font-semibold text-center px-4">
          Whether you're developing complex business logic or simple conditional statements, our intuitive interface and robust backend make it easy to manage your rules efficiently. Dive into the world of rule management and unleash the power of decision-making in your applications!
        </p>
      </div>
    </>
  );
}

export default Home;