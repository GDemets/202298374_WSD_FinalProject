import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import "./Home.css";

function Home() {
    const navigate = useNavigate();
    return (
    <>
        <h1>Hello world V2 !</h1>
        <button onClick={() => navigate("/register")}>Créer un compte</button>
    </>
  );
}

export default Home;
