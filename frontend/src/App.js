import React from 'react';
import Navbar from './components/Navbar/Navbar';
import Footer from './components/Footer/Footer';
import ErrorComponent from './components/ErrorAndLoading/ErrorComponent';
import LoadingComponent from './components/ErrorAndLoading/LoadingComponent';

function App() {
  return (
    <div className="App">
      <Navbar />
      {/* Main content will go here */}
      <Footer />
    </div>
  );
}

export default App;

