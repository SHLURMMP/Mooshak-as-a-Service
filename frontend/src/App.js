import './App.css';
import { BrowserRouter, Route, Routes } from 'react-router-dom';
import React, { useState } from 'react';
import MainPage from './mainPage';
import ContestDetails from './ContestDetails';
import ContestCreation from './ContestCreation';
import ContestStatus from './ContestStatus';
import ContestCreationError from './error_pages/ContestCreationError';
import TeamDetails from './TeamDetails';
import ContestEdit from './ContestEdit';




function App() {
  return (
    <div className="App">
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<MainPage/>} />
          <Route path="/contestdetails/:id" element={<ContestDetails/>} />
          <Route path="/contestcreation" element={<ContestCreation/>} />
          <Route path="/conteststatus/:id" element={<ContestStatus/>} />
          <Route path="/contestcreationerror" element={<ContestCreationError/>} />
          <Route path="/teamdetails/:id" element={<TeamDetails/>} />
          <Route path="/contestedit/:id" element={<ContestEdit/>} />
        </Routes>
      </BrowserRouter>
    </div>
  );
}
export default App;
