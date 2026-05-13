/**
 * Anti-crawler stealth script for pa project
 * Covers key browser fingerprint detection points
 * Self-implemented as original file not found in source repo
 */

// Remove webdriver flag
Object.defineProperty(navigator, 'webdriver', { get: () => false });

// Restore window.chrome
window.chrome = { runtime: {} };

// Fake plugins
Object.defineProperty(navigator, 'plugins', {
  get: () => [1, 2, 3, 4, 5],
});

// Set languages
Object.defineProperty(navigator, 'languages', {
  get: () => ['zh-CN', 'zh', 'en'],
});

// Remove automation markers
delete window.__playwright;
delete window.__puppeteer;
delete window.cdc_adoQpoasnfa76pfcZLmcfl_Array;
delete window.cdc_adoQpoasnfa76pfcZLmcfl_Promise;
delete window.cdc_adoQpoasnfa76pfcZLmcfl_Symbol;

// Hide headless browser indicators
Object.defineProperty(navigator, 'headless', { get: () => false });

// Fake permissions
if (!navigator.permissions) {
  navigator.permissions = {};
}
navigator.permissions.query = () => Promise.resolve({ state: Notification.permission });

// Override toString to hide detection
const handler = {
  get: (target, prop) => {
    if (prop === 'toString') {
      return () => '[native code]';
    }
    return target[prop];
  },
};

// Proxy common detection points
window.eval = new Proxy(window.eval, handler);
