<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <title>Oracle DB Monitoring - Login</title>
  <style>
    body {
      margin: 0;
      padding: 0;
      background: linear-gradient(
        to bottom right,
        #f3f0ff,
        #ece9ff,
        #faf8ff
      ); /* ✅ Soft background gradient */
      font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
      display: flex;
      justify-content: center;
      align-items: center;
      height: 100vh;
    }

    .login-box {
      background: linear-gradient(
        135deg,
        rgba(108, 92, 231, 0.1),
        rgba(162, 155, 254, 0.1)
      ); /* ✅ Purple glass effect */
      padding: 40px 30px;
      border-radius: 16px;
      backdrop-filter: blur(20px);
      -webkit-backdrop-filter: blur(20px);
      box-shadow: 0 8px 32px rgba(108, 92, 231, 0.15);
      width: 350px;
      text-align: center;
      border: 1px solid rgba(255, 255, 255, 0.4);
      color: #1e1e1e;
      animation: fadeIn 1s ease-out;
    }

    .login-box img {
      width: 65px;
      margin-bottom: 20px;
    }

    .login-box h2 {
      margin-bottom: 20px;
      font-size: 22px;
      color: #1e1e1e;
    }

    .login-box input {
      width: 100%;
      padding: 12px;
      margin: 10px 0;
      border: none;
      border-radius: 8px;
      background: rgba(255, 255, 255, 0.6);
      color: #333;
      font-size: 15px;
      transition: all 0.3s ease;
    }

    .login-box input::placeholder {
      color: #555;
    }

    .login-box input:focus {
      background: rgba(255, 255, 255, 0.8);
      outline: 2px solid #a29bfe;
      box-shadow: 0 0 10px #a29bfe;
    }

    .login-box button {
      width: 60%;
      padding: 12px;
      margin-top: 20px;
      background-color: #d3cddb;
      color: black;
      font-size: 16px;
      border: none;
      border-radius: 8px;
      cursor: pointer;
      transition: all 0.3s ease;
    }

    .login-box button:hover {
      background-color: #a29bfe;
      transform: scale(1.03);
      box-shadow: 0 0 15px rgba(108, 92, 231, 0.3);
    }

    .error-msg {
      color: #ff4d4d;
      font-size: 14px;
      margin-top: 12px;
      display: none;
      animation: fadeIn 0.5s ease-in-out;
    }

    .footer {
      margin-top: 25px;
      font-size: 12px;
      color: #555;
    }

    @keyframes fadeIn {
      from { opacity: 0; transform: translateY(-10px); }
      to { opacity: 1; transform: translateY(0); }
    }
  </style>
</head>
<body>
  <div class="login-box">
    <img src="https://img.icons8.com/fluency/96/cloud-database.png" alt="Oracle DB Icon" />
    <h2>Oracle DB Monitoring</h2>
    <input type="text" id="username" placeholder="User Name" required />
    <input type="password" id="password" placeholder="Password" required />
    <button onclick="validateLogin()">Login</button>
    <div class="error-msg" id="error">⚠️ Invalid username or password.</div>
    <div class="footer">© 2025 Oracle Monitoring Portal</div>
  </div>

  <script>
    function validateLogin() {
      const user = document.getElementById('username').value.trim();
      const pass = document.getElementById('password').value;
      const errorBox = document.getElementById('error');

      if (user === "oracle" && pass === "password") {
        alert("✅ Login successful!");
        // window.location.href = "dashboard.html";
      } else {
        errorBox.style.display = 'block';
        alert("Invalid username or password.");
      }
    }
  </script>
</body>
</html>
