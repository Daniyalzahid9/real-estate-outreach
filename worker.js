export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    
    // Clean route for Demo Portal: /demo, /demo?1, /demo/?id=L01
    if (url.pathname === '/demo' || url.pathname === '/demo/') {
      const targetUrl = new URL('/demo/index.html' + url.search, request.url);
      return env.ASSETS.fetch(new Request(targetUrl, request));
    }
    
    // Serve all other static assets (Dashboard, app.js, style.css, leads.json, etc.)
    return env.ASSETS.fetch(request);
  }
};
