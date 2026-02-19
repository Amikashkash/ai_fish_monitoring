/**
 * useAuth — singleton auth composable.
 * Module-level refs so state is shared across all components.
 */
import { ref, computed } from "vue";
import axios from "axios";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";
const STORAGE_KEY = "fm_admin_token";

// ── State (module-level → shared across all components) ──────────────────────
const _token = ref(localStorage.getItem(STORAGE_KEY) || "");

// ── Helpers ───────────────────────────────────────────────────────────────────
function _parseExp(token) {
  try {
    const payload = JSON.parse(atob(token.split(".")[1]));
    return payload.exp || 0;          // seconds since epoch
  } catch {
    return 0;
  }
}

function _isValid(token) {
  if (!token) return false;
  const exp = _parseExp(token);
  return exp > Date.now() / 1000;    // not expired
}

// ── Public API ────────────────────────────────────────────────────────────────
export function useAuth() {
  const isAdmin = computed(() => _isValid(_token.value));

  async function login(password) {
    try {
      const res = await axios.post(`${API_URL}/api/auth/login`, { password });
      _token.value = res.data.token;
      localStorage.setItem(STORAGE_KEY, _token.value);
      return true;
    } catch {
      return false;
    }
  }

  function logout() {
    _token.value = "";
    localStorage.removeItem(STORAGE_KEY);
  }

  function getToken() {
    return _isValid(_token.value) ? _token.value : "";
  }

  return { isAdmin, login, logout, getToken };
}
