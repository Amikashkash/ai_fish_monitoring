<template>
  <div id="app">
    <header class="app-header">
      <h1>Fish Monitor</h1>
      <nav class="nav-tabs">
        <router-link to="/" class="nav-tab">Home</router-link>
        <router-link to="/shipments" class="nav-tab">Shipments</router-link>
        <router-link to="/treatments" class="nav-tab">Treatments</router-link>
        <router-link to="/suppliers" class="nav-tab">Suppliers</router-link>
      </nav>
    </header>
    <main class="app-main">
      <router-view />
    </main>
  </div>
</template>

<script>
export default {
  name: "App"
};
</script>

<style>
.app-header {
  background: linear-gradient(135deg, #0ea5e9 0%, #0284c7 100%);
  color: white;
  padding: 1rem;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.app-header h1 {
  font-size: 1.5rem;
  margin-bottom: 0.5rem;
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

.app-main {
  padding: 1rem;
  max-width: 800px;
  margin: 0 auto;
}
</style>
