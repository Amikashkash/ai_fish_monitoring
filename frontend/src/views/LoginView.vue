<template>
  <div class="login-page">
    <div class="login-card">
      <div class="login-icon">🐟</div>
      <h2>Admin Login</h2>
      <p class="login-sub">Enter your password to enable write access.</p>

      <form @submit.prevent="submit" class="login-form">
        <input
          v-model="password"
          type="password"
          placeholder="Password"
          class="login-input"
          autofocus
          :disabled="loading"
        />
        <button type="submit" class="login-btn" :disabled="loading || !password">
          {{ loading ? "Checking..." : "Login" }}
        </button>
      </form>

      <p v-if="error" class="login-error">Wrong password — try again.</p>
    </div>
  </div>
</template>

<script>
import { ref } from "vue";
import { useRouter, useRoute } from "vue-router";
import { useAuth } from "../composables/useAuth.js";

export default {
  name: "LoginView",
  setup() {
    const password = ref("");
    const loading = ref(false);
    const error = ref(false);
    const router = useRouter();
    const route = useRoute();
    const { login } = useAuth();

    const submit = async () => {
      loading.value = true;
      error.value = false;
      const ok = await login(password.value);
      loading.value = false;
      if (ok) {
        const redirect = route.query.redirect || "/";
        router.push(redirect);
      } else {
        error.value = true;
        password.value = "";
      }
    };

    return { password, loading, error, submit };
  }
};
</script>

<style scoped>
.login-page {
  min-height: 70vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem;
}

.login-card {
  background: white;
  border-radius: 1rem;
  padding: 2.5rem 2rem;
  width: 100%;
  max-width: 360px;
  box-shadow: 0 4px 24px rgba(0,0,0,0.1);
  text-align: center;
}

.login-icon {
  font-size: 2.5rem;
  margin-bottom: 0.5rem;
}

.login-card h2 {
  font-size: 1.4rem;
  color: #1e293b;
  margin: 0 0 0.4rem;
}

.login-sub {
  font-size: 0.88rem;
  color: #64748b;
  margin: 0 0 1.5rem;
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.login-input {
  padding: 0.65rem 0.9rem;
  border: 1px solid #e2e8f0;
  border-radius: 0.5rem;
  font-size: 1rem;
  width: 100%;
  box-sizing: border-box;
  text-align: center;
  letter-spacing: 0.1em;
}

.login-input:focus {
  outline: none;
  border-color: #0ea5e9;
}

.login-btn {
  padding: 0.7rem;
  background: #0ea5e9;
  color: white;
  border: none;
  border-radius: 0.5rem;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
}

.login-btn:hover:not(:disabled) {
  background: #0284c7;
}

.login-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.login-error {
  margin-top: 0.75rem;
  font-size: 0.88rem;
  color: #dc2626;
  font-weight: 600;
}
</style>
