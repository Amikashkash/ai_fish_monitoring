<template>
  <div id="app">
    <header class="app-header">
      <div class="header-top">
        <h1>Fish Monitor</h1>
        <div class="auth-area">
          <span v-if="isAdmin" class="admin-badge">Admin</span>
          <button v-if="isAdmin" @click="handleLogout" class="auth-btn logout-btn">Logout</button>
          <router-link v-else to="/login" class="auth-btn login-btn">Login</router-link>
        </div>
      </div>
      <nav class="nav-tabs">
        <router-link to="/" class="nav-tab">Home</router-link>
        <router-link v-if="isAdmin" to="/daily" class="nav-tab nav-highlight">Daily Rounds</router-link>
        <router-link to="/shipments-list" class="nav-tab">Shipments</router-link>
        <router-link v-if="isAdmin" to="/import" class="nav-tab">Import Invoice</router-link>
        <router-link to="/treatments" class="nav-tab">Treatments</router-link>
        <router-link to="/protocols" class="nav-tab">Drug Protocols</router-link>
        <router-link to="/suppliers" class="nav-tab">Suppliers</router-link>
      </nav>
    </header>
    <main class="app-main">
      <router-view />
    </main>
  </div>
</template>

<script>
import { useAuth } from "./composables/useAuth.js";
import { useRouter } from "vue-router";

export default {
  name: "App",
  setup() {
    const { isAdmin, logout } = useAuth();
    const router = useRouter();

    const handleLogout = () => {
      logout();
      router.push("/");
    };

    return { isAdmin, handleLogout };
  }
};
</script>

<style>
.app-header {
  background: linear-gradient(135deg, #0ea5e9 0%, #0284c7 100%);
  color: white;
  padding: 0.75rem 1rem;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.header-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.app-header h1 {
  font-size: 1.5rem;
  margin: 0;
}

.auth-area {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.admin-badge {
  font-size: 0.75rem;
  font-weight: 700;
  background: rgba(255,255,255,0.25);
  padding: 0.2rem 0.6rem;
  border-radius: 1rem;
  letter-spacing: 0.05em;
}

.auth-btn {
  font-size: 0.8rem;
  font-weight: 600;
  padding: 0.3rem 0.75rem;
  border-radius: 0.4rem;
  cursor: pointer;
  text-decoration: none;
  border: none;
}

.login-btn {
  background: white;
  color: #0284c7;
}

.login-btn:hover {
  background: #f0f9ff;
}

.logout-btn {
  background: rgba(255,255,255,0.2);
  color: white;
  border: 1px solid rgba(255,255,255,0.4);
}

.logout-btn:hover {
  background: rgba(255,255,255,0.3);
}

.nav-tabs {
  display: flex;
  gap: 0.5rem;
  overflow-x: auto;
}

.nav-tab {
  padding: 0.5rem 1rem;
  background: rgba(255,255,255,0.2);
  color: white;
  text-decoration: none;
  border-radius: 0.5rem;
  white-space: nowrap;
  transition: background 0.2s;
}

.nav-tab:hover,
.nav-tab.router-link-active {
  background: rgba(255,255,255,0.3);
}

.nav-highlight {
  background: rgba(255,255,255,0.35);
  font-weight: 700;
  border: 1px solid rgba(255,255,255,0.5);
}

.app-main {
  padding: 1rem;
  max-width: 800px;
  margin: 0 auto;
}
</style>
