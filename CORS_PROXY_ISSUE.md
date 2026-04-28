# CORS Proxy Issue - Temporary Outage

**Status:** 🔴 All free CORS proxy services are currently down or rate-limited  
**Date:** April 28, 2026  
**Impact:** Yahoo Finance data cannot load (stock prices, charts, news)

---

## What's Happening

The app uses free CORS proxy services to fetch stock data from Yahoo Finance. These services are currently failing with:

- **401 Unauthorized** errors
- **"Edge: Too many requests"** rate limiting  
- **Server 500** errors

### Errors in Console:
```
Failed to load resource: the server responded with a status of 401 ()
All proxies failed for: https://query2.finance.yahoo.com/...
Last error: Unexpected token 'E', "Edge: Too "... is not valid JSON
```

---

## Fixes Completed

✅ **Fixed JavaScript Error:** Added missing `esc()` HTML escape function  
✅ **Improved Proxy Fallback:** Now tries 4 different proxies with better error handling  
✅ **Better Timeouts:** 10-second timeout per proxy attempt  
✅ **Error Logging:** Console warnings show which proxies failed and why  

---

## Solutions

### Option 1: Wait for Proxy Services to Recover (Easiest)
The free proxy services usually recover within a few hours. Try refreshing the page later.

### Option 2: Use Your Own CORS Proxy (Recommended)
Deploy your own CORS proxy using one of these:
- [CORS Anywhere](https://github.com/Rob--W/cors-anywhere) (Free, Heroku)
- [Cloudflare Workers](https://workers.cloudflare.com/) (Free tier available)
- [Vercel Edge Functions](https://vercel.com/docs/functions/edge-functions)

Then update line ~1280 in `docs/index.html`:
```javascript
const proxies = [
  u => `https://your-proxy.herokuapp.com/${u}`,  // Your proxy here
  u => u,  // Try direct
  // ... other fallbacks
];
```

### Option 3: Switch to Alpha Vantage API (Alternative Data Source)
You already have Alpha Vantage configured. We could switch the primary data source from Yahoo Finance to Alpha Vantage.

**Pros:**
- More reliable
- No CORS issues
- You already have an API key configured

**Cons:**
- Stricter rate limits (5 calls/minute on free tier)
- Need to refactor `fetchStock()` function
- Different data format

**Would you like me to implement this?**

### Option 4: Add Mock Data Fallback (Development Mode)
Add fake stock data so the UI works even when APIs are down (for demo/testing).

---

## Immediate Workaround

The app will keep retrying. You can:
1. Wait 30-60 minutes and hard refresh (Ctrl+Shift+R)
2. Check if `https://corsproxy.io/` is back online
3. Choose one of the solutions above

---

## Technical Details

**Proxies Tried (in order):**
1. Direct Yahoo Finance (usually blocked by CORS)
2. api.allorigins.win (currently: "Edge: Too many requests")
3. corsproxy.io (currently: 401 Unauthorized)
4. api.codetabs.com (currently: 401 Unauthorized)

**Root Cause:** Free proxy services are shared by thousands of users. When overloaded, they return error pages instead of JSON data, breaking the app.

**Long-term Fix:** Host your own backend proxy or use a paid API service with guaranteed uptime.

---

## Next Steps

Let me know which solution you'd prefer:
- 🔵 **Option 1:** Wait it out (no changes needed)
- 🟢 **Option 2:** Help me deploy my own CORS proxy
- 🟡 **Option 3:** Switch to Alpha Vantage API (requires refactoring)
- 🟣 **Option 4:** Add mock data fallback for testing

I recommend **Option 3** (Alpha Vantage) for a reliable long-term solution since you already have it configured.
