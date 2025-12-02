import { useState } from "react";
import { useNavigate } from "react-router-dom";
import "./Register.css";

function Register() {
  const navigate = useNavigate();

  const [pseudo, setPseudo] = useState("");
  const [mail, setMail] = useState("");
  const [password, setPassword] = useState("");
  const [message, setMessage] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();

    try {
      const res = await fetch("http://127.0.0.1:5000/users", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ pseudo, mail, password })
      });

      const data = await res.json();

      if (res.ok) {
        setMessage("Compte créé avec succès !");
        setTimeout(() => navigate("/"), 1500);
      } else {
        setMessage(data.error || "Erreur lors de la création du compte");
      }
    } catch (err) {
      console.error(err);
      setMessage("Erreur réseau !");
    }
  };

  return (
    <div className="register-container">
      <h1>Créez votre compte</h1>

      <form onSubmit={handleSubmit}>
        <label>Pseudo:</label>
        <input
          type="text"
          value={pseudo}
          onChange={(e) => setPseudo(e.target.value)}
          required
        />

        <label>Email:</label>
        <input
          type="email"
          value={mail}
          onChange={(e) => setMail(e.target.value)}
          required
        />

        <label>Mot de passe:</label>
        <input
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
        />

        <button type="submit">Créer un compte</button>
      </form>

      {message && <p className="message">{message}</p>}

      <button onClick={() => navigate("/")}>Retour page d'accueil</button>
    </div>
  );
}

export default Register;
