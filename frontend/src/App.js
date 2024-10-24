import React from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import Home from './components/Home';
import CreateRule from './components/Create_Rule';
import CombineRules from './components/CombineRules';
import EvaluateRule from './components/Evaluateule';
import Header from './components/Header';

function App() {


  return (
    <Router>
      <div>
        <Header/>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/create-rule" element={<CreateRule />} />
          <Route path="/combine-rules" element={<CombineRules />} />
          <Route path="/evaluate-rule" element={<EvaluateRule />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;