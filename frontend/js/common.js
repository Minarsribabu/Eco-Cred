const API_BASE = window.location.origin + '/v1';

function getToken(){ return localStorage.getItem('authToken'); }
function setToken(t){ localStorage.setItem('authToken', t); }
function clearToken(){ localStorage.removeItem('authToken'); }

// User state management
function getCurrentUser(){ return JSON.parse(localStorage.getItem('currentUser') || 'null'); }
function setCurrentUser(user){ localStorage.setItem('currentUser', JSON.stringify(user)); }
function clearCurrentUser(){ localStorage.removeItem('currentUser'); }

async function apiGet(path){
  const res = await fetch(API_BASE + path, { headers: authHeaders() });
  if(!res.ok) throw new Error(await res.text());
  return res.json();
}
async function apiPost(path, body){
  const res = await fetch(API_BASE + path, { method:'POST', headers: { 'Content-Type':'application/json', ...authHeaders() }, body: JSON.stringify(body) });
  if(!res.ok) throw new Error(await res.text());
  return res.json();
}
function authHeaders(){ const t=getToken(); return t? { Authorization: `Bearer ${t}` } : {}; }

// Check if user is logged in
function isLoggedIn(){ return !!getToken(); }

// Logout function
function logout(){
  clearToken();
  clearCurrentUser();
  window.location.href = '/';
}

// Initialize navigation based on auth state
function initNavigation(){
  const isLoggedIn = !!getToken();
  const currentUser = getCurrentUser();
  
  // Update navigation elements based on login state
  document.querySelectorAll('.nav-not-logged-in').forEach(el => {
    el.style.display = isLoggedIn ? 'none' : 'inline-flex';
  });
  
  document.querySelectorAll('.nav-logged-in').forEach(el => {
    el.style.display = isLoggedIn ? 'inline-flex' : 'none';
  });
  
  document.querySelectorAll('.nav-user').forEach(el => {
    el.style.display = isLoggedIn ? 'inline-flex' : 'none';
    if (currentUser && currentUser.displayName) {
      el.textContent = currentUser.displayName;
    }
  });
  
  // Update dashboard welcome message
  const welcomeMsg = document.querySelector('.welcome-username');
  if (welcomeMsg && currentUser && currentUser.displayName) {
    welcomeMsg.textContent = currentUser.displayName;
  }
}

// Eco points animation effect
function showEcoPointsEffect(points, reason) {
  // Create floating points element
  const effectEl = document.createElement('div');
  effectEl.className = 'eco-points-effect';
  effectEl.innerHTML = `
    <div class="points-animation">
      <div class="points-value">+${points}</div>
      <div class="points-reason">${reason}</div>
    </div>
  `;
  
  // Add styles
  effectEl.style.cssText = `
    position: fixed;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    z-index: 1000;
    pointer-events: none;
  `;
  
  document.body.appendChild(effectEl);
  
  // Animate the effect
  setTimeout(() => {
    effectEl.style.opacity = '0';
    effectEl.style.transform = 'translate(-50%, -100px)';
    effectEl.style.transition = 'all 1.5s ease-out';
  }, 100);
  
  // Remove element after animation
  setTimeout(() => {
    if (effectEl.parentNode) {
      effectEl.parentNode.removeChild(effectEl);
    }
  }, 2000);
}

// Add CSS for eco points effect
function addEcoPointsStyles() {
  if (document.getElementById('eco-points-styles')) return;
  
  const styleEl = document.createElement('style');
  styleEl.id = 'eco-points-styles';
  styleEl.textContent = `
    .eco-points-effect {
      font-family: var(--font-family);
    }
    
    .points-animation {
      background: linear-gradient(135deg, var(--success-500), var(--success-600));
      color: white;
      padding: var(--space-lg) var(--space-xl);
      border-radius: var(--radius-lg);
      box-shadow: var(--shadow-xl);
      text-align: center;
      animation: ecoPointsPulse 0.5s ease-out;
    }
    
    .points-value {
      font-size: var(--font-size-3xl);
      font-weight: 700;
      margin-bottom: var(--space-xs);
    }
    
    .points-reason {
      font-size: var(--font-size-sm);
      opacity: 0.9;
    }
    
    @keyframes ecoPointsPulse {
      0% { transform: scale(0.5); opacity: 0; }
      50% { transform: scale(1.1); }
      100% { transform: scale(1); opacity: 1; }
    }
    
    /* Celebration effect */
    .eco-points-effect.celebrate::before {
      content: '🎉';
      position: absolute;
      top: -20px;
      left: 50%;
      transform: translateX(-50%);
      font-size: 2rem;
      animation: bounce 1s infinite;
    }
    
    @keyframes bounce {
      0%, 20%, 50%, 80%, 100% { transform: translateX(-50%) translateY(0); }
      40% { transform: translateX(-50%) translateY(-10px); }
      60% { transform: translateX(-50%) translateY(-5px); }
    }
  `;
  
  document.head.appendChild(styleEl);
}

window.eco = { 
  API_BASE, 
  getToken, 
  setToken, 
  clearToken, 
  getCurrentUser,
  setCurrentUser,
  clearCurrentUser,
  isLoggedIn,
  logout,
  initNavigation,
  showEcoPointsEffect,
  apiGet, 
  apiPost 
};

// Initialize styles on load
document.addEventListener('DOMContentLoaded', addEcoPointsStyles);

// Demo function to test eco points effect (can be called from browser console)
window.testEcoPointsEffect = function(points = 50, reason = 'Demo points earned!') {
  eco.showEcoPointsEffect(points, reason);
};

