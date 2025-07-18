// App.jsx
import { Routes, Route, useLocation } from "react-router-dom";
import { AnimatePresence } from "framer-motion";
import Navbar from "./assets/components/Navbar.jsx";
import SetsForm from "./assets/components/sets-form.jsx";
import "./App.css";
import "./assets/css/all.css";

export default function App() {
  const location = useLocation();

  return (
    <>
      <Navbar />
      <AnimatePresence mode="wait">
        <Routes location={location} key={location.pathname}>
          <Route path="/sets" element={<SetsForm />} />
        </Routes>
      </AnimatePresence>
    </>
  );
}
