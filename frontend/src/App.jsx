import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar';
import Dashboard from './pages/Dashboard';
import FoodTracker from './pages/FoodTracker';
import AIFoodAnalyzer from './pages/AIFoodAnalyzer';
import WaterTracker from './pages/WaterTracker';
import ExerciseTracker from './pages/ExerciseTracker';
import Profile from './pages/Profile';
import Login from './pages/Login';
import Register from './pages/Register';
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-gray-50">
        <Navbar />
        <main className="container mx-auto px-4 py-8">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/food" element={<FoodTracker />} />
            <Route path="/food-ai" element={<AIFoodAnalyzer />} />
            <Route path="/water" element={<WaterTracker />} />
            <Route path="/exercise" element={<ExerciseTracker />} />
            <Route path="/profile" element={<Profile />} />
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
          </Routes>
        </main>
        <ToastContainer position="bottom-right" />
      </div>
    </Router>
  );
}

export default App;
