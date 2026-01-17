"use client";

import { useState } from "react";
import { supabase } from "@/lib/supabase";

export default function AuthPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [message, setMessage] = useState("");

  const signUp = async () => {
    setMessage("Signing up...");
    const { error } = await supabase.auth.signUp({
      email,
      password,
    });
    setMessage(error ? error.message : "Signup successful");
  };

  const login = async () => {
    setMessage("Logging in...");
    const { error } = await supabase.auth.signInWithPassword({
      email,
      password,
    });
    setMessage(error ? error.message : "Login successful");
  };

  return (
    <div style={{ padding: 40, maxWidth: 400 }}>
      <h2>Auth Test</h2>

      <input
        placeholder="Email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
      />
      <br /><br />

      <input
        placeholder="Password"
        type="password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
      />
      <br /><br />

      <button onClick={signUp}>Sign Up</button>
      <br /><br />
      <button onClick={login}>Log In</button>

      <p>{message}</p>
    </div>
  );
}
