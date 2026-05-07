/* ============================================================
   app.js — LOGIC LAYER (JavaScript)
   Edit this file to change how the page behaves:
   - Form validation rules
   - What happens when buttons are clicked
   - How the page talks to the Python backend
   ============================================================ */


// ============================================================
// CONFIG — Edit this section to point to your backend server
// ============================================================
const CONFIG = {
  apiBase: "http://localhost:5000",   // Change this when you deploy
  endpoints: {
    register: "/register",           // Must match your Python route
    stats:    "/stats",
  }
};


// ============================================================
// STATS — Fetches live economy numbers from Python backend
// ============================================================
async function loadStats() {
  try {
    const response = await fetch(CONFIG.apiBase + CONFIG.endpoints.stats);
    const data = await response.json();

    // Update the DOM with live numbers
    // To add a new stat: add a span with id="stat-X" in index.html
    // and add data.X here
    document.getElementById("stat-players").textContent   = data.players   ?? "—";
    document.getElementById("stat-companies").textContent = data.companies  ?? "—";
    document.getElementById("stat-wealth").textContent    = "$" + (data.total_wealth ?? "0");

  } catch (err) {
    // If the server isn't running, silently show placeholder dashes
    console.warn("Could not load stats:", err);
  }
}


// ============================================================
// REGISTRATION FORM — Handles signup and talks to backend
// ============================================================

// Validation rules — edit these without touching the submit logic
const VALIDATION_RULES = {
  username: {
    minLength: 3,
    maxLength: 20,
    pattern: /^[a-zA-Z0-9_]+$/,
    errorMessage: "Username must be 3–20 characters, letters/numbers/underscores only."
  },
  password: {
    minLength: 6,
    errorMessage: "Password must be at least 6 characters."
  }
};

function validateField(name, value) {
  const rule = VALIDATION_RULES[name];
  if (!rule) return null; // No rule = no error

  if (rule.minLength && value.length < rule.minLength) return rule.errorMessage;
  if (rule.maxLength && value.length > rule.maxLength) return rule.errorMessage;
  if (rule.pattern && !rule.pattern.test(value)) return rule.errorMessage;

  return null; // null = valid
}

function showMessage(message, type) {
  // type: "success" or "error"
  const el = document.getElementById("form-message");
  if (!el) return;
  el.textContent = message;
  el.className = "form-message " + type;
}

async function handleRegister(event) {
  event.preventDefault(); // Stop page from reloading

  const username = document.getElementById("username").value.trim();
  const password = document.getElementById("password").value;

  // Run validation before sending to server
  const usernameError = validateField("username", username);
  if (usernameError) { showMessage(usernameError, "error"); return; }

  const passwordError = validateField("password", password);
  if (passwordError) { showMessage(passwordError, "error"); return; }

  // Send to Python backend
  try {
    const response = await fetch(CONFIG.apiBase + CONFIG.endpoints.register, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, password })
    });

    const data = await response.json();

    if (response.ok) {
      showMessage("Account created! Welcome to the economy.", "success");
      window.location.href = "/dashboard";
    } else {
      showMessage(data.error ?? "Something went wrong.", "error");
    }

  } catch (err) {
    showMessage("Could not connect to server. Is the backend running?", "error");
  }
}


// ============================================================
// INIT — Runs when the page loads
// Add any new startup tasks here
// ============================================================
document.addEventListener("DOMContentLoaded", () => {
  loadStats();

  const form = document.getElementById("register-form");
  if (form) form.addEventListener("submit", handleRegister);
});
