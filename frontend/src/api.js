// Central API configuration.
// The base URL is resolved once here so every page points at the same backend.
//
// Override it for deployed environments by creating a frontend/.env file:
//   VITE_API_BASE_URL=https://api.example.com
//
// Falls back to the local Flask dev server when unset.
const BASE_URL = (import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:5000").replace(
  /\/+$/,
  ""
);

export const API = {
  base: BASE_URL,
  predict: `${BASE_URL}/predict`,
  analysis: `${BASE_URL}/analysis`,
  contact: `${BASE_URL}/contact`,
};

export default API;
