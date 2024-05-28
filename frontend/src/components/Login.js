import React, { useState } from 'react';
import './Login.css';  // Ensure this import statement is correct

const Login = () => {
  const [isLogin, setIsLogin] = useState(true);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [username, setUsername] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    const url = isLogin ? '/auth/api/auth/login' : '/auth/api/auth/signup';
    const data = isLogin ? { email, password } : { email, password, username };

    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      const errorMessage = await response.text();
      console.error('Error:', errorMessage);
      return;
    }

    const result = await response.json();
    console.log(result);
  };

  return (
    <div className="wrapper fadeInDown">
      <div id="formContent">
        <h2
          className={isLogin ? 'active' : 'inactive underlineHover'}
          onClick={() => setIsLogin(true)}
        >
          Sign In
        </h2>
        <h2
          className={!isLogin ? 'active' : 'inactive underlineHover'}
          onClick={() => setIsLogin(false)}
        >
          Sign Up
        </h2>

        <div className="fadeIn first">
          <img src="icon.svg" id="icon" alt="User Icon" />
        </div>

        <form onSubmit={handleSubmit}>
          {!isLogin && (
            <input
              type="text"
              id="signupUsername"
              className="fadeIn second"
              name="username"
              placeholder="username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required={!isLogin}
            />
          )}
          <input
            type="email"
            id="loginEmail"
            className="fadeIn second"
            name="email"
            placeholder="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
          <input
            type="password"
            id="loginPassword"
            className="fadeIn third"
            name="password"
            placeholder="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
          <input type="submit" className="fadeIn fourth" value={isLogin ? 'Log In' : 'Sign Up'} />
        </form>

        <div id="formFooter">
          <button className="underlineHover" onClick={() => alert('Forgot Password clicked')}>Forgot Password?</button>
        </div>
      </div>
    </div>
  );
};

export default Login;
