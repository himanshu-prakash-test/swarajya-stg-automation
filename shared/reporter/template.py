"""
HTML Template and Rendering Engine for Playwright Test Reports.
Produces a modern, self-contained executive QA dashboard with zero external CDN dependencies.
"""

REPORT_HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en" data-theme="dark">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{{ summary.suite_title }} - Playwright Test Report</title>
  <style>
    :root {
      --font-sans: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
      --font-mono: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
      
      /* Dark Theme (Default) */
      --bg-primary: #0f111a;
      --bg-secondary: #181b28;
      --bg-card: #202438;
      --bg-hover: #292e47;
      --border-color: #2e344e;
      --border-focus: #4f5b8a;
      
      --text-main: #f1f3f9;
      --text-muted: #9ba3be;
      --text-dim: #6c7493;
      
      --accent-primary: #6366f1;
      --accent-hover: #4f46e5;
      
      --pass-color: #10b981;
      --pass-bg: rgba(16, 185, 129, 0.12);
      --pass-border: rgba(16, 185, 129, 0.3);
      
      --fail-color: #f43f5e;
      --fail-bg: rgba(244, 63, 94, 0.12);
      --fail-border: rgba(244, 63, 94, 0.3);
      
      --skip-color: #f59e0b;
      --skip-bg: rgba(245, 158, 11, 0.12);
      --skip-border: rgba(245, 158, 11, 0.3);
      
      --badge-bg: #2d334e;
      --code-bg: #121420;
      --shadow-sm: 0 2px 4px rgba(0,0,0,0.25);
      --shadow-md: 0 4px 12px rgba(0,0,0,0.35);
      --shadow-lg: 0 10px 25px rgba(0,0,0,0.5);
    }

    [data-theme="light"] {
      --bg-primary: #f8fafc;
      --bg-secondary: #ffffff;
      --bg-card: #ffffff;
      --bg-hover: #f1f5f9;
      --border-color: #e2e8f0;
      --border-focus: #94a3b8;
      
      --text-main: #0f172a;
      --text-muted: #475569;
      --text-dim: #94a3b8;
      
      --accent-primary: #4f46e5;
      --accent-hover: #4338ca;
      
      --pass-color: #059669;
      --pass-bg: rgba(5, 150, 105, 0.1);
      --pass-border: rgba(5, 150, 105, 0.25);
      
      --fail-color: #e11d48;
      --fail-bg: rgba(225, 29, 72, 0.1);
      --fail-border: rgba(225, 29, 72, 0.25);
      
      --skip-color: #d97706;
      --skip-bg: rgba(217, 119, 6, 0.1);
      --skip-border: rgba(217, 119, 6, 0.25);
      
      --badge-bg: #f1f5f9;
      --code-bg: #1e293b;
      --shadow-sm: 0 1px 3px rgba(0,0,0,0.08);
      --shadow-md: 0 4px 6px -1px rgba(0,0,0,0.1);
      --shadow-lg: 0 10px 15px -3px rgba(0,0,0,0.1);
    }

    * { box-sizing: border-box; margin: 0; padding: 0; transition: background-color 0.2s ease, border-color 0.2s ease; }
    body {
      font-family: var(--font-sans);
      background-color: var(--bg-primary);
      color: var(--text-main);
      line-height: 1.5;
      min-height: 100vh;
      padding-bottom: 60px;
    }

    /* Container */
    .container {
      max-width: 1380px;
      margin: 0 auto;
      padding: 0 24px;
    }

    /* Header */
    header {
      background: var(--bg-secondary);
      border-bottom: 1px solid var(--border-color);
      padding: 24px 0;
      position: relative;
      z-index: 40;
      box-shadow: var(--shadow-sm);
    }
    .header-content {
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 20px;
      flex-wrap: wrap;
    }
    .header-title-area {
      display: flex;
      align-items: center;
      gap: 16px;
    }
    .logo-badge {
      width: 52px;
      height: 52px;
      border-radius: 12px;
      overflow: hidden;
      display: flex;
      align-items: center;
      justify-content: center;
      background: #0099cc;
      box-shadow: 0 4px 14px rgba(0, 153, 204, 0.35);
      border: 1px solid rgba(255, 255, 255, 0.15);
      flex-shrink: 0;
    }
    .logo-img {
      width: 100%;
      height: 100%;
      object-fit: cover;
      display: block;
    }
    .header-text h1 {
      font-size: 22px;
      font-weight: 700;
      letter-spacing: -0.02em;
      display: flex;
      align-items: center;
      gap: 10px;
    }
    .header-text p {
      font-size: 13px;
      color: var(--text-muted);
      margin-top: 2px;
    }

    /* Header Action Buttons */
    .header-actions {
      display: flex;
      align-items: center;
      gap: 12px;
    }
    .btn {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      padding: 8px 16px;
      border-radius: 8px;
      font-size: 13px;
      font-weight: 600;
      cursor: pointer;
      border: 1px solid var(--border-color);
      background: var(--bg-card);
      color: var(--text-main);
      box-shadow: var(--shadow-sm);
      text-decoration: none;
    }
    .btn:hover {
      background: var(--bg-hover);
      border-color: var(--border-focus);
    }
    .btn-primary {
      background: var(--accent-primary);
      border-color: var(--accent-primary);
      color: #fff;
    }
    .btn-primary:hover {
      background: var(--accent-hover);
    }

    /* Verdict Pill */
    .verdict-pill {
      font-size: 12px;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      padding: 4px 12px;
      border-radius: 9999px;
      display: inline-flex;
      align-items: center;
      gap: 6px;
    }
    .verdict-pass {
      background: var(--pass-bg);
      color: var(--pass-color);
      border: 1px solid var(--pass-border);
    }
    .verdict-fail {
      background: var(--fail-bg);
      color: var(--fail-color);
      border: 1px solid var(--fail-border);
    }

    /* Metrics Grid */
    .metrics-section {
      margin-top: 28px;
    }
    .metrics-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(210px, 1fr));
      gap: 18px;
    }
    .metric-card {
      background: var(--bg-card);
      border: 1px solid var(--border-color);
      border-radius: 14px;
      padding: 20px;
      box-shadow: var(--shadow-sm);
      position: relative;
      overflow: hidden;
    }
    .metric-card::before {
      content: "";
      position: absolute;
      top: 0;
      left: 0;
      right: 0;
      height: 3px;
      background: var(--card-border-top, var(--accent-primary));
    }
    .metric-card.card-total { --card-border-top: var(--accent-primary); }
    .metric-card.card-pass { --card-border-top: var(--pass-color); }
    .metric-card.card-fail { --card-border-top: var(--fail-color); }
    .metric-card.card-skip { --card-border-top: var(--skip-color); }
    .metric-card.card-time { --card-border-top: #0ea5e9; }

    .metric-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 8px;
    }
    .metric-label {
      font-size: 12px;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      color: var(--text-muted);
    }
    .metric-icon {
      width: 28px;
      height: 28px;
      border-radius: 8px;
      display: flex;
      align-items: center;
      justify-content: center;
      background: var(--bg-secondary);
      color: var(--text-muted);
    }
    .metric-value {
      font-size: 32px;
      font-weight: 800;
      letter-spacing: -0.03em;
    }
    .metric-sub {
      font-size: 12px;
      color: var(--text-dim);
      margin-top: 4px;
      display: flex;
      align-items: center;
      gap: 6px;
    }
    .sub-pill {
      font-weight: 700;
      padding: 2px 6px;
      border-radius: 6px;
    }
    .sub-pass { background: var(--pass-bg); color: var(--pass-color); }
    .sub-fail { background: var(--fail-bg); color: var(--fail-color); }

    /* Visual Analytics & Environment Section */
    .dashboard-details {
      display: grid;
      grid-template-columns: 1.1fr 1fr;
      gap: 20px;
      margin-top: 24px;
    }
    @media (max-width: 960px) {
      .dashboard-details { grid-template-columns: 1fr; }
    }

    .detail-card {
      background: var(--bg-card);
      border: 1px solid var(--border-color);
      border-radius: 14px;
      padding: 22px;
      box-shadow: var(--shadow-sm);
    }
    .detail-card h3 {
      font-size: 14px;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      color: var(--text-muted);
      margin-bottom: 18px;
      display: flex;
      align-items: center;
      gap: 8px;
    }

    /* Donut & Module Stats */
    .charts-wrapper {
      display: flex;
      align-items: center;
      gap: 28px;
      flex-wrap: wrap;
    }
    .donut-container {
      position: relative;
      width: 140px;
      height: 140px;
      flex-shrink: 0;
    }
    .donut-svg {
      transform: rotate(-90deg);
      width: 100%;
      height: 100%;
    }
    .donut-center-text {
      position: absolute;
      top: 50%;
      left: 50%;
      transform: translate(-50%, -50%);
      text-align: center;
    }
    .donut-rate {
      font-size: 20px;
      font-weight: 800;
      line-height: 1;
    }
    .donut-caption {
      font-size: 10px;
      font-weight: 600;
      color: var(--text-muted);
      text-transform: uppercase;
    }

    .module-bars {
      flex-grow: 1;
      display: flex;
      flex-direction: column;
      gap: 12px;
    }
    .module-bar-item {
      display: flex;
      flex-direction: column;
      gap: 4px;
    }
    .module-bar-header {
      display: flex;
      justify-content: space-between;
      font-size: 12px;
    }
    .module-name {
      font-weight: 600;
      color: var(--text-main);
    }
    .module-count {
      color: var(--text-muted);
      font-weight: 500;
    }
    .progress-track {
      height: 8px;
      background: var(--bg-secondary);
      border-radius: 999px;
      overflow: hidden;
      display: flex;
    }
    .progress-fill-pass { background: var(--pass-color); }
    .progress-fill-fail { background: var(--fail-color); }
    .progress-fill-skip { background: var(--skip-color); }

    /* Environment Specs Grid */
    .env-grid {
      display: grid;
      grid-template-columns: repeat(2, 1fr);
      gap: 14px;
    }
    .env-item {
      background: var(--bg-secondary);
      padding: 10px 14px;
      border-radius: 10px;
      border: 1px solid var(--border-color);
    }
    .env-key {
      font-size: 11px;
      color: var(--text-dim);
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.04em;
    }
    .env-val {
      font-size: 13px;
      font-weight: 600;
      color: var(--text-main);
      margin-top: 2px;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }

    /* Controls & Filter Toolbar */
    .controls-toolbar {
      background: var(--bg-card);
      border: 1px solid var(--border-color);
      border-radius: 14px;
      padding: 16px 20px;
      margin-top: 24px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 16px;
      flex-wrap: wrap;
      box-shadow: var(--shadow-sm);
    }
    .filter-chips {
      display: flex;
      align-items: center;
      gap: 8px;
      flex-wrap: wrap;
    }
    .chip {
      background: var(--bg-secondary);
      border: 1px solid var(--border-color);
      color: var(--text-muted);
      font-size: 12px;
      font-weight: 600;
      padding: 6px 14px;
      border-radius: 9999px;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 6px;
    }
    .chip:hover {
      background: var(--bg-hover);
      color: var(--text-main);
    }
    .chip.active {
      background: var(--accent-primary);
      border-color: var(--accent-primary);
      color: #fff;
    }
    .chip-count {
      font-size: 11px;
      padding: 1px 6px;
      border-radius: 999px;
      background: rgba(255,255,255,0.15);
    }

    .search-sort-area {
      display: flex;
      align-items: center;
      gap: 12px;
      flex-grow: 1;
      max-width: 500px;
    }
    .search-wrapper {
      position: relative;
      flex-grow: 1;
    }
    .search-input {
      width: 100%;
      background: var(--bg-secondary);
      border: 1px solid var(--border-color);
      border-radius: 8px;
      padding: 8px 12px 8px 36px;
      font-size: 13px;
      color: var(--text-main);
      outline: none;
    }
    .search-input:focus {
      border-color: var(--accent-primary);
    }
    .search-icon {
      position: absolute;
      left: 11px;
      top: 50%;
      transform: translateY(-50%);
      color: var(--text-dim);
      pointer-events: none;
    }

    .select-dropdown {
      background: var(--bg-secondary);
      border: 1px solid var(--border-color);
      border-radius: 8px;
      padding: 8px 12px;
      font-size: 13px;
      color: var(--text-main);
      outline: none;
      cursor: pointer;
    }

    /* Test Cases Section */
    .test-cases-section {
      margin-top: 24px;
      display: flex;
      flex-direction: column;
      gap: 12px;
    }

    .test-card {
      background: var(--bg-card);
      border: 1px solid var(--border-color);
      border-radius: 12px;
      overflow: hidden;
      box-shadow: var(--shadow-sm);
    }
    .test-card:hover {
      border-color: var(--border-focus);
    }

    .test-header {
      padding: 14px 18px;
      display: flex;
      align-items: center;
      gap: 14px;
      cursor: pointer;
      user-select: none;
    }
    .status-badge {
      font-size: 11px;
      font-weight: 700;
      padding: 4px 10px;
      border-radius: 6px;
      text-transform: uppercase;
      letter-spacing: 0.04em;
      flex-shrink: 0;
    }
    .status-pass {
      background: var(--pass-bg);
      color: var(--pass-color);
      border: 1px solid var(--pass-border);
    }
    .status-fail {
      background: var(--fail-bg);
      color: var(--fail-color);
      border: 1px solid var(--fail-border);
    }
    .status-skip {
      background: var(--skip-bg);
      color: var(--skip-color);
      border: 1px solid var(--skip-border);
    }

    .tc-id-pill {
      font-family: var(--font-mono);
      font-size: 12px;
      font-weight: 700;
      color: var(--accent-primary);
      background: var(--badge-bg);
      padding: 3px 8px;
      border-radius: 6px;
      border: 1px solid var(--border-color);
      flex-shrink: 0;
    }
    .test-title-group {
      flex-grow: 1;
      min-width: 0;
    }
    .test-name {
      font-size: 14px;
      font-weight: 600;
      color: var(--text-main);
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }
    .test-module-sub {
      font-size: 11px;
      color: var(--text-muted);
      margin-top: 2px;
      display: flex;
      align-items: center;
      gap: 8px;
    }
    .tag-marker {
      background: var(--bg-secondary);
      border: 1px solid var(--border-color);
      font-size: 10px;
      padding: 1px 6px;
      border-radius: 4px;
      color: var(--text-dim);
    }

    .test-meta-right {
      display: flex;
      align-items: center;
      gap: 12px;
      flex-shrink: 0;
    }
    .duration-pill {
      font-family: var(--font-mono);
      font-size: 12px;
      color: var(--text-muted);
      background: var(--bg-secondary);
      padding: 3px 8px;
      border-radius: 6px;
    }
    .chevron-icon {
      color: var(--text-dim);
      transition: transform 0.25s ease;
    }
    .test-card.expanded .chevron-icon {
      transform: rotate(180deg);
    }

    /* Test Details Accordion Body */
    .test-details {
      display: none;
      padding: 18px;
      border-top: 1px solid var(--border-color);
      background: var(--bg-secondary);
      animation: fadeIn 0.2s ease-in-out;
    }
    .test-card.expanded .test-details {
      display: block;
    }

    @keyframes fadeIn {
      from { opacity: 0; transform: translateY(-4px); }
      to { opacity: 1; transform: translateY(0); }
    }

    /* Remarks Callout */
    .remark-callout {
      background: var(--bg-card);
      border-left: 4px solid var(--accent-primary);
      padding: 12px 16px;
      border-radius: 6px;
      font-size: 13px;
      margin-bottom: 14px;
      display: flex;
      align-items: flex-start;
      gap: 10px;
    }
    .remark-callout.fail-callout {
      border-left-color: var(--fail-color);
      background: var(--fail-bg);
      color: var(--text-main);
    }

    /* Stacktrace Container */
    .stacktrace-box {
      background: var(--code-bg);
      border: 1px solid var(--border-color);
      border-radius: 8px;
      margin-bottom: 14px;
      overflow: hidden;
    }
    .stacktrace-header {
      background: rgba(255,255,255,0.03);
      border-bottom: 1px solid var(--border-color);
      padding: 8px 14px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      font-size: 11px;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      color: var(--fail-color);
    }
    .copy-btn {
      background: transparent;
      border: 1px solid var(--border-color);
      color: var(--text-muted);
      font-size: 11px;
      padding: 2px 8px;
      border-radius: 4px;
      cursor: pointer;
    }
    .copy-btn:hover {
      background: var(--bg-card);
      color: var(--text-main);
    }
    .stacktrace-content {
      font-family: var(--font-mono);
      font-size: 12px;
      line-height: 1.6;
      color: #e2e8f0;
      padding: 14px;
      overflow-x: auto;
      white-space: pre-wrap;
      max-height: 360px;
    }

    /* Screenshot Gallery */
    .screenshot-area {
      margin-top: 14px;
    }
    .screenshot-title {
      font-size: 12px;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.04em;
      color: var(--text-muted);
      margin-bottom: 8px;
      display: flex;
      align-items: center;
      gap: 6px;
    }
    .screenshot-thumb-container {
      position: relative;
      display: inline-block;
      border: 1px solid var(--border-color);
      border-radius: 8px;
      overflow: hidden;
      cursor: pointer;
      max-width: 320px;
      box-shadow: var(--shadow-sm);
    }
    .screenshot-thumb {
      width: 100%;
      height: auto;
      display: block;
      transition: transform 0.2s ease;
    }
    .screenshot-thumb-container:hover .screenshot-thumb {
      transform: scale(1.03);
    }
    .screenshot-overlay {
      position: absolute;
      inset: 0;
      background: rgba(15, 17, 26, 0.65);
      display: flex;
      align-items: center;
      justify-content: center;
      opacity: 0;
      transition: opacity 0.2s ease;
      color: #fff;
      font-size: 13px;
      font-weight: 600;
      gap: 6px;
    }
    .screenshot-thumb-container:hover .screenshot-overlay {
      opacity: 1;
    }

    /* Lightbox Modal */
    .lightbox-modal {
      position: fixed;
      inset: 0;
      background: rgba(0, 0, 0, 0.88);
      backdrop-filter: blur(4px);
      z-index: 100;
      display: none;
      align-items: center;
      justify-content: center;
      padding: 24px;
    }
    .lightbox-modal.active {
      display: flex;
    }
    .lightbox-content {
      max-width: 92vw;
      max-height: 90vh;
      display: flex;
      flex-direction: column;
      background: var(--bg-card);
      border: 1px solid var(--border-color);
      border-radius: 12px;
      overflow: hidden;
      box-shadow: var(--shadow-lg);
    }
    .lightbox-header {
      padding: 12px 18px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      border-bottom: 1px solid var(--border-color);
      background: var(--bg-secondary);
    }
    .lightbox-header h4 {
      font-size: 14px;
      font-weight: 700;
      color: var(--text-main);
    }
    .lightbox-close {
      background: transparent;
      border: none;
      color: var(--text-muted);
      cursor: pointer;
      padding: 4px;
    }
    .lightbox-close:hover {
      color: var(--text-main);
    }
    .lightbox-body {
      overflow: auto;
      padding: 12px;
      display: flex;
      align-items: center;
      justify-content: center;
    }
    .lightbox-img {
      max-width: 100%;
      max-height: 80vh;
      border-radius: 6px;
      box-shadow: var(--shadow-md);
      object-fit: contain;
    }

    /* Empty state */
    .empty-results {
      padding: 40px;
      text-align: center;
      background: var(--bg-card);
      border: 1px dashed var(--border-color);
      border-radius: 12px;
      color: var(--text-muted);
      font-size: 14px;
      display: none;
    }

    /* Print styles */
    @media print {
      header { position: static; box-shadow: none; }
      .header-actions, .controls-toolbar, .btn { display: none !important; }
      .test-details { display: block !important; }
      body { background: #fff !important; color: #000 !important; }
      .metric-card, .test-card, .detail-card { border: 1px solid #ddd !important; box-shadow: none !important; }
    }
  </style>
</head>
<body>

  <!-- Header -->
  <header>
    <div class="container header-content">
      <div class="header-title-area">
        <div class="logo-badge">
          {% if coreco_logo_base64 %}
          <img src="{{ coreco_logo_base64 }}" alt="Coreco Technologies" class="logo-img" />
          {% else %}
          <svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
            <path d="m18 16 4-4-4-4"></path>
            <path d="m6 8-4 4 4 4"></path>
            <path d="m14.5 4-5 16"></path>
          </svg>
          {% endif %}
        </div>
        <div class="header-text">
          <h1>
            {{ summary.suite_title }}
            <span class="verdict-pill {% if summary.failed == 0 and summary.total > 0 %}verdict-pass{% else %}verdict-fail{% endif %}">
              {{ summary.overall_status }}
            </span>
          </h1>
          <p>Playwright Test Automation Report &bull; Executed on {{ summary.start_time }}</p>
        </div>
      </div>

      <div class="header-actions">
        <button class="btn" id="themeToggleBtn" title="Switch Theme">
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" id="themeIcon">
            <circle cx="12" cy="12" r="5"></circle>
            <line x1="12" y1="1" x2="12" y2="3"></line>
            <line x1="12" y1="21" x2="12" y2="23"></line>
            <line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line>
            <line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line>
            <line x1="1" y1="12" x2="3" y2="12"></line>
            <line x1="21" y1="12" x2="23" y2="12"></line>
            <line x1="4.22" y1="19.78" x2="5.64" y2="18.36"></line>
            <line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line>
          </svg>
          <span id="themeLabel">Light</span>
        </button>

        <button class="btn" onclick="window.print()">
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <polyline points="6 9 6 2 18 2 18 9"></polyline>
            <path d="M6 18H4a2 2 0 0 1-2-2v-5a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v5a2 2 0 0 1-2 2h-2"></path>
            <rect x="6" y="14" width="12" height="8"></rect>
          </svg>
          Print / PDF
        </button>
      </div>
    </div>
  </header>

  <main class="container">
    <!-- Executive KPI Metrics -->
    <section class="metrics-section">
      <div class="metrics-grid">
        <!-- Total Tests -->
        <div class="metric-card card-total">
          <div class="metric-header">
            <span class="metric-label">Total Tests</span>
            <div class="metric-icon">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line></svg>
            </div>
          </div>
          <div class="metric-value">{{ summary.total }}</div>
          <div class="metric-sub">Across {{ modules|length }} Test Module(s)</div>
        </div>

        <!-- Passed Tests -->
        <div class="metric-card card-pass">
          <div class="metric-header">
            <span class="metric-label">Passed</span>
            <div class="metric-icon" style="color: var(--pass-color);">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="20 6 9 17 4 12"></polyline></svg>
            </div>
          </div>
          <div class="metric-value" style="color: var(--pass-color);">{{ summary.passed }}</div>
          <div class="metric-sub">
            <span class="sub-pill sub-pass">{{ summary.pass_percentage }}%</span> success rate
          </div>
        </div>

        <!-- Failed Tests -->
        <div class="metric-card card-fail">
          <div class="metric-header">
            <span class="metric-label">Failed</span>
            <div class="metric-icon" style="color: var(--fail-color);">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>
            </div>
          </div>
          <div class="metric-value" style="color: var(--fail-color);">{{ summary.failed }}</div>
          <div class="metric-sub">
            {% if summary.failed > 0 %}
              <span class="sub-pill sub-fail">{{ summary.fail_percentage }}%</span> failure rate
            {% else %}
              Zero failures reported
            {% endif %}
          </div>
        </div>

        <!-- Skipped Tests -->
        <div class="metric-card card-skip">
          <div class="metric-header">
            <span class="metric-label">Skipped</span>
            <div class="metric-icon" style="color: var(--skip-color);">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><line x1="4.93" y1="4.93" x2="19.07" y2="19.07"></line></svg>
            </div>
          </div>
          <div class="metric-value" style="color: var(--skip-color);">{{ summary.skipped }}</div>
          <div class="metric-sub">{{ summary.skip_percentage }}% non-UI / skipped</div>
        </div>

        <!-- Duration -->
        <div class="metric-card card-time">
          <div class="metric-header">
            <span class="metric-label">Duration</span>
            <div class="metric-icon" style="color: #0ea5e9;">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline></svg>
            </div>
          </div>
          <div class="metric-value" style="color: #0ea5e9;">{{ summary.formatted_duration }}</div>
          <div class="metric-sub">
            {% if summary.total > 0 %}
              ~{{ (summary.duration / summary.total)|round(2) }}s / test avg
            {% else %}
              0.0s
            {% endif %}
          </div>
        </div>
      </div>
    </section>

    <!-- Visual Breakdown & Environment Specs -->
    <section class="dashboard-details">
      <!-- Test Distribution & Modules -->
      <div class="detail-card">
        <h3>
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><path d="M12 2a10 10 0 0 1 10 10h-10z"></path></svg>
          Distribution &amp; Module Coverage
        </h3>
        <div class="charts-wrapper">
          <!-- Dynamic SVG Donut Chart -->
          <div class="donut-container">
            <svg class="donut-svg" viewBox="0 0 36 36">
              <!-- Background Circle -->
              <path d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                    fill="none" stroke="var(--bg-secondary)" stroke-width="4.5" />
              <!-- Passed Stroke -->
              <path d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                    fill="none" stroke="var(--pass-color)" stroke-width="4.5"
                    stroke-dasharray="{{ summary.pass_percentage }}, 100" />
              <!-- Failed Stroke -->
              {% if summary.failed > 0 %}
              <path d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                    fill="none" stroke="var(--fail-color)" stroke-width="4.5"
                    stroke-dasharray="{{ summary.fail_percentage }}, 100"
                    stroke-dashoffset="-{{ summary.pass_percentage }}" />
              {% endif %}
            </svg>
            <div class="donut-center-text">
              <div class="donut-rate" style="color: var(--pass-color);">{{ summary.pass_percentage }}%</div>
              <div class="donut-caption">Pass Rate</div>
            </div>
          </div>

          <!-- Module Progress Breakdown -->
          <div class="module-bars">
            {% for mod in module_stats %}
            <div class="module-bar-item">
              <div class="module-bar-header">
                <span class="module-name">{{ mod.name }}</span>
                <span class="module-count">{{ mod.passed }}/{{ mod.total }} Passed</span>
              </div>
              <div class="progress-track">
                <div class="progress-fill-pass" style="width: {{ mod.pass_pct }}%;"></div>
                <div class="progress-fill-fail" style="width: {{ mod.fail_pct }}%;"></div>
                <div class="progress-fill-skip" style="width: {{ mod.skip_pct }}%;"></div>
              </div>
            </div>
            {% endfor %}
          </div>
        </div>
      </div>

      <!-- Environment & Run Specs -->
      <div class="detail-card">
        <h3>
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="2" y="3" width="20" height="14" rx="2" ry="2"></rect><line x1="8" y1="21" x2="16" y2="21"></line><line x1="12" y1="17" x2="12" y2="21"></line></svg>
          Environment &amp; Execution Profile
        </h3>
        <div class="env-grid">
          <div class="env-item">
            <div class="env-key">Automation Engine</div>
            <div class="env-val">Playwright {{ summary.environment_info.playwright_version }}</div>
          </div>
          <div class="env-item">
            <div class="env-key">Test Runner</div>
            <div class="env-val">Pytest {{ summary.environment_info.pytest_version }}</div>
          </div>
          <div class="env-item">
            <div class="env-key">Target Portal</div>
            <div class="env-val" title="{{ summary.environment_info.base_url }}">Swarajya Staging</div>
          </div>
          <div class="env-item">
            <div class="env-key">Browser &amp; Mode</div>
            <div class="env-val">{{ summary.environment_info.browser }} ({{ summary.environment_info.mode }})</div>
          </div>
          <div class="env-item">
            <div class="env-key">Platform / OS</div>
            <div class="env-val">{{ summary.environment_info.os }}</div>
          </div>
          <div class="env-item">
            <div class="env-key">Python Runtime</div>
            <div class="env-val">Python {{ summary.environment_info.python_version }}</div>
          </div>
        </div>
      </div>
    </section>

    <!-- Filter & Search Toolbar -->
    <section class="controls-toolbar">
      <!-- Filter Chips -->
      <div class="filter-chips">
        <button class="chip active" data-filter="all">
          All <span class="chip-count">{{ summary.total }}</span>
        </button>
        <button class="chip" data-filter="PASS">
          Passed <span class="chip-count">{{ summary.passed }}</span>
        </button>
        <button class="chip" data-filter="FAIL">
          Failed <span class="chip-count">{{ summary.failed }}</span>
        </button>
        <button class="chip" data-filter="SKIPPED">
          Skipped <span class="chip-count">{{ summary.skipped }}</span>
        </button>
      </div>

      <!-- Search & Dropdown -->
      <div class="search-sort-area">
        <div class="search-wrapper">
          <svg class="search-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg>
          <input type="text" id="searchInput" class="search-input" placeholder="Search by TC ID, test name, or error..." />
        </div>

        <select id="moduleFilter" class="select-dropdown">
          <option value="all">All Modules</option>
          {% for mod in modules %}
          <option value="{{ mod }}">{{ mod }}</option>
          {% endfor %}
        </select>
      </div>
    </section>

    <!-- Test Cases Accordion List -->
    <section class="test-cases-section" id="testCasesContainer">
      {% for test in summary.test_results %}
      <div class="test-card" data-status="{{ test.status }}" data-module="{{ test.module_name }}" data-text="{{ test.tc_id }} {{ test.name }} {{ test.error_message }}">
        <div class="test-header" onclick="toggleCard(this)">
          <span class="status-badge {{ test.status_css_class }}">{{ test.status }}</span>
          <span class="tc-id-pill" title="Excel Test Case ID">{{ test.tc_id }}</span>
          
          <div class="test-title-group">
            <div class="test-name" title="{{ test.name }}">{{ test.name }}</div>
            <div class="test-module-sub">
              <span>{{ test.module_name }}</span>
              {% for m in test.markers %}
              <span class="tag-marker">#{{ m }}</span>
              {% endfor %}
            </div>
          </div>

          <div class="test-meta-right">
            <span class="duration-pill">{{ test.formatted_duration }}</span>
            <svg class="chevron-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="6 9 12 15 18 9"></polyline></svg>
          </div>
        </div>

        <!-- Expanded Details -->
        <div class="test-details">
          <!-- Remark / Verdict Note -->
          {% if test.remarks %}
          <div class="remark-callout {% if test.status == 'FAIL' %}fail-callout{% endif %}">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="flex-shrink:0; margin-top:2px;">
              {% if test.status == 'FAIL' %}
              <circle cx="12" cy="12" r="10"></circle><line x1="12" y1="8" x2="12" y2="12"></line><line x1="12" y1="16" x2="12.01" y2="16"></line>
              {% else %}
              <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path><polyline points="22 4 12 14.01 9 11.01"></polyline>
              {% endif %}
            </svg>
            <div>
              <strong>Execution Remark:</strong> {{ test.remarks }}
              {% if test.auto_id %}
              <span style="display:block; margin-top:3px; font-size:11px; opacity:0.8;">Automation ID: <code>{{ test.auto_id }}</code></span>
              {% endif %}
            </div>
          </div>
          {% endif %}

          <!-- Failure Stacktrace -->
          {% if test.stacktrace %}
          <div class="stacktrace-box">
            <div class="stacktrace-header">
              <span>Failure Trace &amp; Assertion Diagnostic</span>
              <button class="copy-btn" onclick="copyTrace(this)">Copy Trace</button>
            </div>
            <pre class="stacktrace-content">{{ test.stacktrace }}</pre>
          </div>
          {% endif %}

          <!-- Screenshot Visual Evidence -->
          {% if test.screenshot_base64 or test.screenshot_path %}
          <div class="screenshot-area">
            <div class="screenshot-title">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect><circle cx="8.5" cy="8.5" r="1.5"></circle><polyline points="21 15 16 10 5 21"></polyline></svg>
              1-to-1 Test Evidence Screenshot
            </div>
            <div class="screenshot-thumb-container" onclick="openLightbox(`{{ test.screenshot_base64 or test.screenshot_path }}`, `{{ test.tc_id }} - {{ test.name }}`)">
              <img src="{{ test.screenshot_base64 or test.screenshot_path }}" alt="Test Screenshot" class="screenshot-thumb" loading="lazy" />
              <div class="screenshot-overlay">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line><line x1="11" y1="8" x2="11" y2="14"></line><line x1="8" y1="11" x2="14" y2="11"></line></svg>
                Click to Enlarge
              </div>
            </div>
          </div>
          {% endif %}
        </div>
      </div>
      {% endfor %}

      <div class="empty-results" id="emptyState">
        No test cases match the active filter or search criteria.
      </div>
    </section>
  </main>

  <!-- Fullscreen Lightbox Modal -->
  <div class="lightbox-modal" id="lightboxModal" onclick="closeLightbox(event)">
    <div class="lightbox-content" onclick="event.stopPropagation()">
      <div class="lightbox-header">
        <h4 id="lightboxTitle">Test Screenshot</h4>
        <button class="lightbox-close" onclick="closeLightbox()">&times;</button>
      </div>
      <div class="lightbox-body">
        <img src="" alt="Screenshot" id="lightboxImg" class="lightbox-img" />
      </div>
    </div>
  </div>

  <script>
    // Theme Management
    const html = document.documentElement;
    const themeBtn = document.getElementById('themeToggleBtn');
    const themeLabel = document.getElementById('themeLabel');

    function setTheme(theme) {
      html.setAttribute('data-theme', theme);
      localStorage.setItem('swarajya_report_theme', theme);
      themeLabel.textContent = theme === 'dark' ? 'Light' : 'Dark';
    }

    const savedTheme = localStorage.getItem('swarajya_report_theme') || 'dark';
    setTheme(savedTheme);

    themeBtn.addEventListener('click', () => {
      const current = html.getAttribute('data-theme');
      setTheme(current === 'dark' ? 'light' : 'dark');
    });

    // Accordion expand/collapse
    function toggleCard(header) {
      header.parentElement.classList.toggle('expanded');
    }

    // Filtering & Real-time Search
    let currentFilter = 'all';
    let currentModule = 'all';
    let searchQuery = '';

    const chips = document.querySelectorAll('.chip');
    const searchInput = document.getElementById('searchInput');
    const moduleFilter = document.getElementById('moduleFilter');
    const cards = document.querySelectorAll('.test-card');
    const emptyState = document.getElementById('emptyState');

    chips.forEach(chip => {
      chip.addEventListener('click', () => {
        chips.forEach(c => c.classList.remove('active'));
        chip.classList.add('active');
        currentFilter = chip.getAttribute('data-filter');
        applyFilters();
      });
    });

    searchInput.addEventListener('input', (e) => {
      searchQuery = e.target.value.toLowerCase().trim();
      applyFilters();
    });

    moduleFilter.addEventListener('change', (e) => {
      currentModule = e.target.value;
      applyFilters();
    });

    function applyFilters() {
      let visibleCount = 0;
      cards.forEach(card => {
        const status = card.getAttribute('data-status');
        const module = card.getAttribute('data-module');
        const text = card.getAttribute('data-text').toLowerCase();

        const matchesStatus = currentFilter === 'all' || status.includes(currentFilter);
        const matchesModule = currentModule === 'all' || module === currentModule;
        const matchesSearch = !searchQuery || text.includes(searchQuery);

        if (matchesStatus && matchesModule && matchesSearch) {
          card.style.display = 'block';
          visibleCount++;
        } else {
          card.style.display = 'none';
        }
      });

      emptyState.style.display = visibleCount === 0 ? 'block' : 'none';
    }

    // Lightbox modal logic
    const lightboxModal = document.getElementById('lightboxModal');
    const lightboxImg = document.getElementById('lightboxImg');
    const lightboxTitle = document.getElementById('lightboxTitle');

    function openLightbox(src, title) {
      lightboxImg.src = src;
      lightboxTitle.textContent = title;
      lightboxModal.classList.add('active');
    }

    function closeLightbox() {
      lightboxModal.classList.remove('active');
      lightboxImg.src = '';
    }

    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') closeLightbox();
    });

    function copyTrace(btn) {
      const box = btn.closest('.stacktrace-box');
      if (box) {
        const content = box.querySelector('.stacktrace-content');
        if (content) copyText(btn, content.innerText);
      }
    }

    // Copy to clipboard helper
    function copyText(btn, text) {
      navigator.clipboard.writeText(text).then(() => {
        const orig = btn.textContent;
        btn.textContent = 'Copied!';
        setTimeout(() => btn.textContent = orig, 1800);
      });
    }
  </script>
</body>
</html>
"""
