const API = "http://127.0.0.1:8000";

function getCurrentUser() {
  try {
    const raw = localStorage.getItem("user");
    if (!raw) return null;
    try {
      return JSON.parse(raw);
    } catch (e) {
      // If the data is corrupted we clear it to avoid intermittent parse failures
      console.warn("[Auth] Corrupted 'user' in localStorage — clearing it.", e);
      localStorage.removeItem("user");
      return null;
    }
  } catch (e) {
    console.error("[Auth] Failed to access localStorage:", e);
    return null;
  }
}

function requireAuth() {
  // Prevent redirect loops - if we're already on login/signup, don't redirect
  const currentPage = window.location.pathname.split('/').pop() || '';
  if (currentPage === 'login.html' || currentPage === 'signup.html') {
    return null; // Allow login/signup pages to load without redirect
  }
  
  const user = getCurrentUser();
  if (!user) {
    // Don't redirect automatically - let the page show a message instead
    // This prevents infinite redirect loops
    return null;
  }
  return user;
}

// -------- AUTH: SIGNUP + LOGIN --------

async function handleSignupSubmit(event) {
  event.preventDefault();
  const form = event.target;
  const formData = new FormData(form);
  const payload = {
    name: formData.get("name"),
    email: formData.get("email"),
    password: formData.get("password"),
  };

  const msg = document.getElementById("msg");
  
  // Show loading message
  if (msg) {
    msg.textContent = "Creating account...";
    msg.style.color = "#0d7377";
  }

  try {
    console.log("📝 Sending signup request to:", `${API}/signup`);
    console.log("📝 Payload:", payload);
    
    const res = await fetch(`${API}/signup`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    
    console.log("📥 Response status:", res.status);
    
    if (!res.ok) {
      throw new Error(`HTTP error! status: ${res.status}`);
    }
    
    const data = await res.json();
    console.log("📥 Response data:", data);

    if (data.success) {
      if (msg) {
        msg.textContent = "✅ Account created! Redirecting to login...";
        msg.style.color = "#14b8a6";
      }
      setTimeout(() => window.location.replace("login.html"), 800);
    } else {
      if (msg) {
        msg.textContent = data.message || "❌ User already exists or signup failed.";
        msg.style.color = "#dc3545";
      }
      console.error("❌ Signup failed:", data);
    }
  } catch (error) {
    console.error("❌ Signup error:", error);
    if (msg) {
      msg.textContent = `❌ Error: ${error.message}. Make sure backend is running on ${API}`;
      msg.style.color = "#dc3545";
    }
    alert(`Signup failed: ${error.message}\n\nMake sure:\n1. Backend is running (http://127.0.0.1:8000)\n2. Check browser console (F12) for details`);
  }
}

async function handleLoginSubmit(event) {
  event.preventDefault();
  const form = event.target;
  const formData = new FormData(form);
  const payload = {
    email: formData.get("email"),
    password: formData.get("password"),
  };

  const res = await fetch(`${API}/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  const data = await res.json();
  const msg = document.getElementById("msg");

  if (data.success) {
    // Persist user in localStorage for later use (profile, predictions, etc.)
    localStorage.setItem("user", JSON.stringify(data.user));
    if (msg) msg.textContent = "Login successful, redirecting...";
    setTimeout(() => window.location.replace("dashboard.html"), 500);
  } else {
    if (msg) msg.textContent = data.message || "Login failed.";
  }
}

// -------- DASHBOARD (Analytics + Charts) --------

async function loadDashboard() {
  // Prevent concurrent runs that could trigger repeated network requests or redirects
  if (window._dashboardFetchInProgress) {
    console.debug("[Dashboard] loadDashboard already in progress - skipping duplicate call.");
    return;
  }
  window._dashboardFetchInProgress = true;

  // Check auth first - don't redirect, just show message if not logged in
  const user = getCurrentUser();
  if (!user) {
    // If no user, show message instead of redirecting (prevents loops)
    const main = document.querySelector("main.page");
    if (main) {
      main.innerHTML = `
        <div style="text-align: center; padding: 40px;">
          <h2>Please Login</h2>
          <p>You need to be logged in to view the dashboard.</p>
          <a href="login.html" style="display: inline-block; margin-top: 20px; padding: 12px 24px; background: linear-gradient(135deg, #0d7377, #14b8a6); color: white; text-decoration: none; border-radius: 10px; font-weight: 600; box-shadow: 0 8px 20px rgba(13, 115, 119, 0.4); transition: all 0.2s ease;">Go to Login</a>
        </div>
      `;
    }
    window._dashboardFetchInProgress = false;
    return; // Exit early, don't try to load data
  }
  
  // Show loading indicator
  const loadingDiv = document.createElement("div");
  loadingDiv.id = "loadingIndicator";
  loadingDiv.style.cssText = "text-align: center; padding: 20px; color: #14b8a6; font-weight: 500;";
  loadingDiv.innerHTML = "🔄 Loading dashboard data...";
  const main = document.querySelector("main.page");
  if (main) {
    const existing = document.getElementById("loadingIndicator");
    if (existing) existing.remove();
    main.insertBefore(loadingDiv, main.firstChild);
  }
  
  try {
    console.log(`[Dashboard] Fetching from ${API}/dashboard`);
    
    const res = await fetch(`${API}/dashboard`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    }).catch(err => {
      console.error("[Dashboard] Network error:", err);
      throw new Error(`Cannot connect to backend at ${API}. Make sure FastAPI is running on port 8000.`);
    });
    
    console.log(`[Dashboard] Response status: ${res.status}`);
    
    if (!res.ok) {
      const errorText = await res.text();
      console.error("[Dashboard] HTTP error:", res.status, errorText);
      throw new Error(`HTTP ${res.status}: ${errorText || 'Unknown error'}`);
    }
    
    const data = await res.json();
    console.log("[Dashboard] Data received:", {
      invoice_count: data.stats?.invoice_count,
      has_charts: Object.values(data.charts || {}).filter(v => v !== null).length,
      error: data.error
    });

    const stats = data.stats || {};
    const charts = data.charts || {};
    
    // Remove loading indicator
    const loading = document.getElementById("loadingIndicator");
    if (loading) loading.remove();
    
    // If there's an error message, show it but continue to display what we can
    if (data.error && stats.invoice_count === 0) {
      console.warn("[Dashboard] Error from backend:", data.error);
    }

  const salesEl = document.getElementById("sales");
  const avgEl = document.getElementById("avg");
  const medianEl = document.getElementById("median");
  const countEl = document.getElementById("count");
  const welcomeEl = document.getElementById("welcomeName");

  // Use the authenticated user object
  if (welcomeEl && user) {
    welcomeEl.textContent = user.name || user.email;
  }

  if (salesEl) salesEl.textContent = stats.total_sales?.toFixed?.(2) ?? stats.total_sales ?? 0;
  if (avgEl) avgEl.textContent = stats.average_quantity?.toFixed?.(2) ?? stats.average_quantity ?? 0;
  if (medianEl) medianEl.textContent = stats.median_quantity?.toFixed?.(2) ?? stats.median_quantity ?? 0;
  if (countEl) countEl.textContent = stats.invoice_count ?? 0;

  const itemSalesImg = document.getElementById("itemSalesChart");
  const amountDistImg = document.getElementById("amountDistChart");
  const pieChartImg = document.getElementById("pieChart");

  // Helper to set chart with loading / error handlers
  function setChartImage(imgEl, b64, fallbackText) {
    const parentCard = imgEl?.closest('.chart-card');
    // Remove existing placeholder if any
    const existingNote = parentCard?.querySelector('.chart-note');
    if (existingNote) existingNote.remove();

    if (!imgEl) return;

    // Show spinner placeholder while loading
    imgEl.style.opacity = '0.0';
    imgEl.alt = 'Loading chart...';

    if (!b64) {
      // Show friendly message if chart missing
      const note = document.createElement('div');
      note.className = 'chart-note';
      note.style.cssText = 'text-align:center; padding:12px; color:#555; font-size:0.95rem;';
      note.textContent = fallbackText || 'Chart not available';
      parentCard?.appendChild(note);
      return;
    }

    imgEl.onload = () => {
      imgEl.style.opacity = '1.0';
      imgEl.alt = 'Chart image';
      console.log('[Dashboard] Chart loaded for', imgEl.id);
    };

    imgEl.onerror = (err) => {
      console.error('[Dashboard] Failed to load chart for', imgEl.id, err);
      imgEl.style.display = 'none';
      const note = document.createElement('div');
      note.className = 'chart-note';
      note.style.cssText = 'text-align:center; padding:12px; color:#c0392b; font-size:0.95rem;';
      note.textContent = 'Failed to load chart image.';
      parentCard?.appendChild(note);
    };

    imgEl.src = `data:image/png;base64,${b64}`;
  }

  setChartImage(itemSalesImg, charts.item_sales, 'No items chart available');
  setChartImage(amountDistImg, charts.amount_distribution, 'No amount distribution chart available');
  setChartImage(pieChartImg, charts.pie_chart, 'No pie chart available');

  // Log chart availability (not strictly 'loaded' state)
  console.log("[Dashboard] Charts availability:", {
    item_sales: charts.item_sales ? "present" : "missing",
    amount_distribution: charts.amount_distribution ? "present" : "missing",
    pie_chart: charts.pie_chart ? "present" : "missing"
  });

  // Display category frequencies (top categories) if present
  const catFreq = stats.category_frequencies || {};
  const existingCatCard = document.getElementById('categoryFrequenciesCard');
  if (Object.keys(catFreq).length > 0) {
    const container = existingCatCard || document.createElement('div');
    container.id = 'categoryFrequenciesCard';
    container.className = 'card';
    container.style.marginTop = '40px'; // Increased from 18px to 40px for more spacing
    container.innerHTML = `
      <h3>Top Categories</h3>
      <div id="categoryList" style="display:flex;flex-wrap:wrap;gap:8px;margin-top:10px;"></div>
    `;

    const list = container.querySelector('#categoryList');
    list.innerHTML = '';
    // Sort by value (frequency) descending and add rank numbers
    const sortedCategories = Object.entries(catFreq)
      .sort((a, b) => b[1] - a[1])
      .slice(0, 8);
    
    sortedCategories.forEach(([k, v], index) => {
      const pill = document.createElement('div');
      pill.style.cssText = 'background:linear-gradient(135deg, rgba(13, 115, 119, 0.2), rgba(13, 115, 119, 0.1));padding:12px 18px;border-radius:10px;font-size:1rem;color:#e5e7eb;font-weight:500;border:1px solid rgba(13, 115, 119, 0.3);box-shadow:0 4px 12px rgba(0, 0, 0, 0.2);transition:all 0.2s ease;';
      pill.textContent = `#${index + 1} ${k}: ${v}`;
      pill.onmouseenter = function() {
        this.style.transform = 'translateY(-2px)';
        this.style.boxShadow = '0 6px 16px rgba(13, 115, 119, 0.3)';
        this.style.borderColor = 'rgba(13, 115, 119, 0.5)';
      };
      pill.onmouseleave = function() {
        this.style.transform = 'translateY(0)';
        this.style.boxShadow = '0 4px 12px rgba(0, 0, 0, 0.2)';
        this.style.borderColor = 'rgba(13, 115, 119, 0.3)';
      };
      list.appendChild(pill);
    });

    // Insert after the last charts row
    const chartsRows = document.querySelectorAll('.charts-row');
    const lastCharts = chartsRows[chartsRows.length - 1];
    if (lastCharts) {
      if (!existingCatCard) lastCharts.parentNode.insertBefore(container, lastCharts.nextSibling);
    } else {
      // fallback: append to main
      const main = document.querySelector('main.page');
      if (main && !existingCatCard) main.appendChild(container);
    }
  } else {
    if (existingCatCard) existingCatCard.remove();
  }
  
  // Show message if no data
  if (stats.invoice_count === 0) {
    console.warn("[Dashboard] No data found - invoice_count is 0");
    const msgDiv = document.createElement("div");
    msgDiv.style.cssText = "background: #fff3cd; border: 1px solid #ffc107; padding: 20px; margin: 20px; border-radius: 8px; text-align: center; max-width: 700px; margin-left: auto; margin-right: auto;";
    msgDiv.innerHTML = `
      <strong style="font-size: 18px;">⚠️ No Data Found</strong><br><br>
      The dataset collection is empty. You can load it now:<br><br>
      <button id="loadDataBtn" style="background: linear-gradient(135deg, #0d7377, #14b8a6); color: white; border: none; padding: 12px 24px; border-radius: 10px; font-size: 16px; font-weight: 600; cursor: pointer; margin: 10px; box-shadow: 0 8px 20px rgba(13, 115, 119, 0.4); transition: all 0.2s ease;">
        🔄 Load Dataset Now
      </button>
      <br>
      <button id="testBackendBtn" style="background: #28a745; color: white; border: none; padding: 10px 20px; border-radius: 6px; font-size: 14px; cursor: pointer; margin: 5px;">
        🔍 Test Backend Connection
      </button>
      <br><br>
      <small style="color: #666;">
        Or run manually: <code style="background: #f0f0f0; padding: 4px 8px; border-radius: 4px;">python init_project.py</code>
      </small>
      <div id="loadStatus" style="margin-top: 15px;"></div>
    `;
    document.querySelector("main.page")?.prepend(msgDiv);
    
        // Add click handler for load button
    const loadBtn = document.getElementById("loadDataBtn");
    if (loadBtn) {
      loadBtn.onclick = async () => {
        loadBtn.disabled = true;
        loadBtn.textContent = "Loading...";
        const statusDiv = document.getElementById("loadStatus");
        statusDiv.innerHTML = "⏳ Loading dataset...";
        
        try {
          // Load dataset
          const res = await fetch(`${API}/load-dataset`, { method: 'POST' });
          const result = await res.json();
          
          if (result.success) {
            statusDiv.innerHTML = `<span style="color: green;">✅ ${result.message}</span><br>Reloading page in 2 seconds...`;
            setTimeout(() => {
              // Use replace to avoid adding history entries during an automated reload
              window.location.replace(window.location.href.split('?')[0]); // Reload without query params
            }, 2000);
          } else {
            statusDiv.innerHTML = `<span style="color: red;">❌ Error: ${result.error}</span><br><small>Check backend terminal for details</small>`;
            loadBtn.disabled = false;
            loadBtn.textContent = "🔄 Load Dataset Now";
          }
        } catch (err) {
          statusDiv.innerHTML = `<span style="color: red;">❌ Error: ${err.message}</span><br><small>Make sure backend is running on port 8000</small>`;
          loadBtn.disabled = false;
          loadBtn.textContent = "🔄 Load Dataset Now";
        }
      };
    }
    
    // Add click handler for test backend button
    const testBtn = document.getElementById("testBackendBtn");
    if (testBtn) {
      testBtn.onclick = async () => {
        testBtn.disabled = true;
        testBtn.textContent = "Testing...";
        const statusDiv = document.getElementById("loadStatus");
        statusDiv.innerHTML = "⏳ Testing backend connection...";
        
        try {
          const res = await fetch(`${API}/health`);
          const result = await res.json();
          
          if (res.ok && result.status === "healthy") {
            statusDiv.innerHTML = `
              <div style="text-align: left; background: #d4edda; padding: 15px; border-radius: 6px; margin-top: 10px;">
                <strong style="color: #155724;">✅ Backend is Healthy!</strong><br>
                MongoDB: ${result.mongodb}<br>
                Dataset: ${result.dataset_count} records<br>
                Models: ${result.model_count} model(s)<br>
                ${result.dataset_count === 0 ? '<br><strong>⚠️ Dataset is empty! Click "Load Dataset Now" above.</strong>' : ''}
              </div>
            `;
          } else {
            statusDiv.innerHTML = `<span style="color: orange;">⚠️ Backend responded but status: ${result.status}</span>`;
          }
        } catch (err) {
          statusDiv.innerHTML = `
            <div style="text-align: left; background: #f8d7da; padding: 15px; border-radius: 6px; margin-top: 10px;">
              <strong style="color: #721c24;">❌ Cannot Connect to Backend</strong><br>
              Error: ${err.message}<br><br>
              <strong>Solution:</strong><br>
              1. Open terminal<br>
              2. Run: <code style="background: #f0f0f0; padding: 2px 6px;">cd backend && uvicorn main:app --reload</code><br>
              3. Wait for "Uvicorn running on http://127.0.0.1:8000"<br>
              4. Click this button again
            </div>
          `;
        }
        
        testBtn.disabled = false;
        testBtn.textContent = "🔍 Test Backend Connection";
      };
    }
  }
  } catch (error) {
    console.error("Error loading dashboard:", error);
    
    // Show detailed error message
    const errorMsg = error.message || "Unknown error occurred";
    const msgDiv = document.createElement("div");
    msgDiv.style.cssText = "background: #f8d7da; border: 2px solid #dc3545; padding: 20px; margin: 20px; border-radius: 8px; text-align: center; max-width: 600px; margin-left: auto; margin-right: auto;";
    msgDiv.innerHTML = `
      <h3 style="color: #dc3545; margin-top: 0;">⚠️ Error Loading Dashboard</h3>
      <p style="color: #721c24; font-family: monospace; background: #f0f0f0; padding: 10px; border-radius: 4px;">${errorMsg}</p>
      <div style="margin-top: 15px; text-align: left;">
        <strong>Quick Fixes:</strong>
        <ol style="text-align: left;">
          <li>Make sure MongoDB is running</li>
          <li>Start FastAPI backend: <code style="background: #f0f0f0; padding: 2px 6px; border-radius: 3px;">cd backend && uvicorn main:app --reload</code></li>
          <li>Load dataset: <code style="background: #f0f0f0; padding: 2px 6px; border-radius: 3px;">cd ml && python train_model.py</code></li>
          <li>Check browser console (F12) for more details</li>
        </ol>
      </div>
    `;
    
    // Remove existing error messages
    const existing = document.querySelector(".error-message");
    if (existing) existing.remove();
    msgDiv.className = "error-message";
    
    const main = document.querySelector("main.page");
    if (main) {
      main.insertBefore(msgDiv, main.firstChild);
    } else {
      document.body.appendChild(msgDiv);
    }
  } finally {
    // Ensure we clear the in-progress flag even when errors occur
    window._dashboardFetchInProgress = false;
  }
}

// -------- PROFILE --------

async function loadProfile() {
  if (window._profileFetchInProgress) {
    console.debug("[Profile] loadProfile already in progress - skipping duplicate call.");
    return;
  }
  window._profileFetchInProgress = true;

  const user = getCurrentUser();
  if (!user) {
    // If no user, show message instead of redirecting (prevent loops)
    const main = document.querySelector("main.page");
    if (main) {
      main.innerHTML = `
        <div style="text-align: center; padding: 40px;">
          <h2>Please Login</h2>
          <p>You need to be logged in to view your profile.</p>
          <a href="login.html" style="display: inline-block; margin-top: 20px; padding: 12px 24px; background: linear-gradient(135deg, #0d7377, #14b8a6); color: white; text-decoration: none; border-radius: 10px; font-weight: 600; box-shadow: 0 8px 20px rgba(13, 115, 119, 0.4); transition: all 0.2s ease;">Go to Login</a>
        </div>
      `;
    }
    window._profileFetchInProgress = false;
    return;
  }

  try {
    const res = await fetch(`${API}/profile/${encodeURIComponent(user.id)}`);
    const data = await res.json();

    if (!data.success) {
      document.getElementById("profileInfo").textContent = "Unable to load profile.";
      return;
    }

    const profileUser = data.user;
    const profileInfo = document.getElementById("profileInfo");
    if (profileInfo) {
      const created = profileUser.created_at ? new Date(profileUser.created_at).toLocaleString() : "N/A";
      profileInfo.innerHTML = `
        <p><strong>Name:</strong> ${profileUser.name}</p>
        <p><strong>Email:</strong> ${profileUser.email}</p>
        <p><strong>Member since:</strong> ${created}</p>
      `;
    }
  } catch (error) {
    console.error("[Profile] Error loading profile:", error);
  } finally {
    window._profileFetchInProgress = false;
  }
}

async function handleDeleteAccount() {
  const user = getCurrentUser();
  if (!user) {
    alert("Please login first.");
    window.location.href = "login.html";
    return;
  }
  
  if (!confirm("Are you sure you want to permanently delete your account?")) {
    return;
  }

  try {
    const res = await fetch(`${API}/delete-account`, {
      method: "DELETE",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ user_id: user.id }),
    });

    const data = await res.json();
    if (data.success) {
      localStorage.removeItem("user");
      const msg = `Account deleted successfully. ${data.predictions_deleted || 0} predictions were also removed.`;
      alert(msg);
      window.location.replace("signup.html");
    } else {
      alert(`Failed to delete account: ${data.message || data.error || "Unknown error"}`);
    }
  } catch (error) {
    console.error("Error deleting account:", error);
    alert(`Error deleting account: ${error.message}`);
  }
}

// -------- PREDICTION FLOW --------

async function handlePredictSubmit(event) {
  event.preventDefault();
  const user = getCurrentUser();
  if (!user) {
    alert("Please login first.");
    window.location.href = "login.html";
    return;
  }

  const form = event.target;
  const formData = new FormData(form);
  const quantity = parseFloat(formData.get("quantity"));
  const salesPrice = parseFloat(formData.get("sales_price"));

  try {
    const res = await fetch(`${API}/predict`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        user_id: user.id,
        quantity,
        sales_price: salesPrice,
      }),
    });

    const data = await res.json();
    const resultDiv = document.getElementById("result");

    if (!data.success) {
      const errorMsg = data.message || data.error || "Prediction failed. Please try again.";
      if (resultDiv) {
        resultDiv.innerHTML = `<span style="color: red;">❌ ${errorMsg}</span>`;
      } else {
        alert(errorMsg);
      }
      console.error("Prediction error:", data);
      return;
    }

    if (resultDiv) {
      resultDiv.textContent = `Model (${data.model_version}) prediction: ${data.label.toUpperCase()}`;
    }

    // Redirect to dedicated result page
    if (data.label === "good") {
      window.location.href = "result_good.html";
    } else {
      window.location.href = "result_bad.html";
    }
  } catch (error) {
    console.error("Error making prediction:", error);
    const resultDiv = document.getElementById("result");
    if (resultDiv) {
      resultDiv.innerHTML = `<span style="color: red;">❌ Error: ${error.message}</span>`;
    } else {
      alert(`Error making prediction: ${error.message}`);
    }
  }
}

// -------- EVENT WIRING --------

document.addEventListener("DOMContentLoaded", () => {
  // Only attach handlers if forms exist (prevents errors on pages without forms)
  const signupForm = document.getElementById("signupForm");
  if (signupForm) {
    signupForm.addEventListener("submit", handleSignupSubmit);
  }

  const loginForm = document.getElementById("loginForm");
  if (loginForm) {
    loginForm.addEventListener("submit", handleLoginSubmit);
  }

  const predictForm = document.getElementById("predictForm");
  if (predictForm) {
    predictForm.addEventListener("submit", handlePredictSubmit);
  }

  const deleteBtn = document.getElementById("deleteBtn");
  if (deleteBtn) {
    deleteBtn.addEventListener("click", handleDeleteAccount);
  }
  
  // Prevent infinite redirects - if we're on login/signup and have a user, redirect to dashboard
  const currentPage = window.location.pathname.split('/').pop() || '';
  const user = getCurrentUser();
  
  // Only redirect if we're on login/signup pages AND user is logged in
  // Use a flag to prevent multiple redirects
  if (user && (currentPage === 'login.html' || currentPage === 'signup.html')) {
    // Check if we've already attempted a redirect in this session
    const redirectFlag = 'redirecting_' + currentPage;
    if (sessionStorage.getItem(redirectFlag)) {
      // Already redirecting, don't do it again
      console.debug('[Auth] Redirect already in progress, skipping.');
      return;
    }
    
    // Set flag and redirect
    sessionStorage.setItem(redirectFlag, 'true');
    // Clear flag after redirect completes (or fails)
    setTimeout(() => {
      sessionStorage.removeItem(redirectFlag);
    }, 3000);
    
    // Use location.href instead of replace to avoid history issues
    window.location.href = "dashboard.html";
    return; // Exit early to prevent page loaders from running
  }

  // Call page-specific loaders (do not rely on body onload attributes)
  try {
    if (currentPage === 'dashboard.html') loadDashboard();
    if (currentPage === 'profile.html') loadProfile();
  } catch (e) {
    console.error('[Page Loader] Error while calling page-specific loader:', e);
  }
});
