export default {
  async fetch(request, env, ctx) {
    // This file is just for compatibility flags
    // Actual worker is in .vercel/output/static/_worker.js
  }
}

export const config = {
  compatibility_date: "2025-10-14",
  compatibility_flags: ["nodejs_compat"]
}
