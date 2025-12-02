import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { useState } from "react";
import "./App.css";
import Home from "./pages/Home";
import Register from "./pages/Register";

const App = () => {
  const [page, setPage] = useState("Home");

  const PageWrapper = ({ component: Component }) => {
    return <Component setPage={setPage} />;
  };

  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Navigate to="/home" replace />} />
        <Route path="/home" element={<PageWrapper component={Home} />} />
        <Route path="/register" element={<PageWrapper component={Register} />} />
      </Routes>
    </BrowserRouter>
  );
};

export default App;
