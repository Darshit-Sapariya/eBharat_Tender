import re

base_path = r"c:\Users\Darshit\OneDrive\Desktop\eBharat_Tender\eBhatat_Tender\coreadmin\templates\coreadmin_base.html"
dash_path = r"c:\Users\Darshit\OneDrive\Desktop\eBharat_Tender\eBhatat_Tender\coreadmin\templates\deshbord.html"

with open(base_path, "r", encoding="utf-8") as f:
    base_html = f.read()

# 1. Update <head> to handle dynamic themes and new root definitions
new_head = r"""<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{% block title %}Control Center{% endblock %} · Super Admin</title>
  
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Space+Mono:ital,wght@0,400;0,700;1,400&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css">
  
  <script src="https://cdn.tailwindcss.com"></script>
  <script>
    tailwind.config = {
      darkMode: 'class',
      theme: {
        extend: {
          fontFamily: {
            sans: ['Inter', 'sans-serif'],
            mono: ['Space Mono', 'monospace'],
          },
          colors: {
            navy: {
              800: '#111827',
              900: '#030712',
            },
            saffron: {
              400: '#fb923c',
              500: '#f97316',
              600: '#ea580c',
            }
          }
        }
      }
    }
  </script>
  <script>
    if (localStorage.theme === 'dark' || (!('theme' in localStorage) && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  </script>
  
  <style type="text/tailwindcss">
    @layer base {
      :root {
        --bg: #f8fafc;
        --bg2: #ffffff;
        --bg3: #f1f5f9;
        --bg4: #e2e8f0;
        --border: rgba(148,163,184,0.2);
        --border2: rgba(148,163,184,0.4);
        --text: #0f172a;
        --muted: #64748b;
        --muted2: #475569;
        --accent: #f97316;
        --accent2: #ea580c;
        --blue: #0ea5e9;
        --green: #10b981;
        --red: #f43f5e;
        --yellow: #f59e0b;
        --purple: #6366f1;
        --cyan: #06b6d4;
      }
      .dark {
        --bg: #030712;
        --bg2: #0f172a;
        --bg3: rgba(30,41,59,0.5);
        --bg4: #334155;
        --border: rgba(51,65,85,0.5);
        --border2: rgba(51,65,85,0.8);
        --text: #f8fafc;
        --muted: #94a3b8;
        --muted2: #cbd5e1;
      }
      body {
        background-color: var(--bg);
        color: var(--text);
        @apply font-sans antialiased min-h-screen flex flex-col overflow-x-hidden transition-colors duration-300;
      }
      ::-webkit-scrollbar { @apply w-1.5 h-1.5; }
      ::-webkit-scrollbar-track { @apply bg-transparent; }
      ::-webkit-scrollbar-thumb { @apply bg-slate-200 dark:bg-slate-700/50 rounded-full; }
    }

    @layer components {
      .layout { @apply flex h-screen relative z-10; }
      
      /* Sidebar */
      .sidebar {
        @apply w-[260px] bg-white dark:bg-slate-900/95 dark:backdrop-blur-xl border-r border-slate-200 dark:border-slate-800/60 flex flex-col shrink-0 fixed top-0 left-0 bottom-0 z-[100] transition-transform duration-300 shadow-sm dark:shadow-none;
      }
      .sidebar-logo {
        @apply h-[62px] flex items-center gap-3 px-5 border-b-2 border-saffron-500/80 shrink-0 bg-slate-50 dark:bg-slate-900/90;
      }
      .logo-mark {
        @apply w-8 h-8 rounded-md bg-gradient-to-br from-saffron-400 to-saffron-600 flex items-center justify-center font-mono text-[11px] font-bold text-white shadow-sm dark:shadow-[0_0_20px_rgba(249,115,22,0.3)];
      }
      .logo-text { @apply font-mono text-[11px] font-bold text-slate-800 dark:text-slate-100 uppercase tracking-widest leading-tight; }
      .logo-text span { @apply text-saffron-600 dark:text-saffron-500; }
      
      .sidebar-section { @apply px-4 py-2 mt-4 text-[10px] font-bold uppercase tracking-widest text-slate-400 dark:text-slate-500 font-mono; }
      .sidebar-nav { @apply flex-1 overflow-y-auto py-2; }
      
      .nav-item {
        @apply flex items-center gap-3 px-5 py-2.5 text-[13px] font-medium text-slate-600 dark:text-slate-400 hover:text-saffron-600 dark:hover:text-slate-100 hover:bg-slate-50 dark:hover:bg-white/5 transition-all relative cursor-pointer no-underline;
      }
      .nav-item.active { @apply text-saffron-600 dark:text-saffron-500 bg-saffron-50 dark:bg-saffron-500/10 font-semibold; }
      .nav-item.active::before {
        content: '';
        @apply absolute left-0 top-1.5 bottom-1.5 w-[3px] bg-saffron-500 rounded-r shadow-sm dark:shadow-[0_0_10px_rgba(249,115,22,0.5)];
      }
      .nav-item i { @apply w-4 text-center text-sm; }
      
      .sidebar-footer { @apply p-4 border-t border-slate-200 dark:border-slate-800/60 shrink-0; }
      .admin-profile {
        @apply flex items-center gap-3 p-2 rounded-xl bg-slate-50 dark:bg-slate-800/40 border border-slate-200 dark:border-slate-700/50 cursor-pointer hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors;
      }
      .admin-avatar { @apply w-8 h-8 rounded-lg bg-gradient-to-br from-saffron-500 to-red-600 flex items-center justify-center text-xs font-bold text-white font-mono shrink-0 shadow-inner; }
      .admin-name { @apply text-[13px] font-semibold text-slate-800 dark:text-slate-200 tracking-tight; }
      .admin-role { @apply text-[10px] text-saffron-600 dark:text-saffron-500 font-mono uppercase tracking-wider; }
      .admin-caret { @apply ml-auto text-slate-400 dark:text-slate-500 text-[10px]; }

      /* Main */
      .main { @apply ml-[260px] flex-1 flex flex-col min-h-screen min-w-0 transition-all duration-300 transform-gpu; }
      
      /* Topbar */
      .topbar {
        @apply h-[62px] bg-white/80 dark:bg-slate-900/80 backdrop-blur-md border-b border-slate-200 dark:border-slate-800/60 flex items-center px-6 gap-4 shrink-0 sticky top-0 z-50;
      }
      .topbar-hamburger { @apply hidden w-8 h-8 flex-shrink-0 rounded-lg text-slate-500 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800 hover:text-slate-800 dark:hover:text-slate-200 transition-colors justify-center items-center cursor-pointer border-none bg-transparent; }
      .breadcrumb { @apply flex items-center gap-2 text-[13px] text-slate-500; }
      .breadcrumb span { @apply text-slate-800 dark:text-slate-200 font-semibold; }
      .breadcrumb i { @apply text-[10px]; }
      
      .topbar-right { @apply ml-auto flex items-center gap-3; }
      .topbar-btn {
        @apply w-9 h-9 bg-white dark:bg-slate-800/50 border border-slate-200 dark:border-slate-700/50 rounded-xl flex items-center justify-center text-slate-500 dark:text-slate-400 cursor-pointer text-sm relative transition-all hover:bg-slate-50 dark:hover:bg-slate-700 hover:text-slate-800 dark:hover:text-slate-200 hover:border-slate-300 dark:hover:border-slate-600 shadow-sm dark:shadow-none;
      }
      .topbar-notif { @apply absolute -top-1 -right-1 w-2.5 h-2.5 rounded-full bg-red-500 border-2 border-white dark:border-slate-900 animate-pulse; }
      .topbar-status {
        @apply hidden sm:flex items-center gap-2 bg-slate-50 dark:bg-slate-800/40 border border-slate-200 dark:border-slate-700/50 rounded-xl px-3 h-9 text-[11px] text-slate-500 dark:text-slate-400 font-mono shadow-sm dark:shadow-none;
      }
      .status-dot { @apply w-1.5 h-1.5 rounded-full bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.8)] animate-pulse; }

      /* Page Content */
      .page-content { @apply flex-1 p-4 sm:p-6 lg:p-8 overflow-y-auto animate-[fadeInPage_0.4s_ease-out]; }
      .page-header { @apply flex flex-col sm:flex-row sm:items-start justify-between mb-8 gap-4; }
      .page-title { @apply font-mono text-[19px] font-bold text-slate-800 dark:text-white uppercase tracking-wider; }
      .page-subtitle { @apply text-[13px] text-slate-500 dark:text-slate-400 mt-1.5; }

      /* Cards */
      .card {
        @apply bg-white dark:bg-slate-800/30 dark:backdrop-blur-sm border border-slate-200 dark:border-slate-700/50 rounded-2xl overflow-hidden shadow-sm dark:shadow-[0_8px_32px_rgba(0,0,0,0.2)] transition-colors duration-300;
      }
      .card-head { @apply flex items-center justify-between px-5 py-4 border-b border-slate-200 dark:border-slate-700/50 bg-slate-50/50 dark:bg-slate-800/50; }
      .card-title { @apply font-mono text-[11px] font-bold uppercase tracking-widest text-slate-500 dark:text-slate-300; }
      .card-body { @apply p-5; }

      /* Stat Cards */
      .stats-grid { @apply grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-6 mb-8; }
      .stat-card {
        @apply bg-white dark:bg-slate-800/40 dark:backdrop-blur-md border border-slate-200 dark:border-slate-700/50 rounded-2xl p-5 relative overflow-hidden transition-all duration-300 hover:border-slate-300 dark:hover:border-slate-600 hover:-translate-y-1 shadow-sm dark:shadow-lg group dark:hover:shadow-2xl dark:hover:shadow-slate-900/50;
      }
      .stat-card::after { content: ''; @apply absolute top-0 left-0 right-0 h-0.5 opacity-0 dark:opacity-80 transition-opacity group-hover:opacity-100; }
      .stat-card.indigo::after { @apply bg-saffron-500 dark:shadow-[0_0_10px_rgba(249,115,22,0.8)]; }
      .stat-card.blue::after { @apply bg-sky-500 dark:shadow-[0_0_10px_rgba(14,165,233,0.8)]; }
      .stat-card.green::after { @apply bg-emerald-500 dark:shadow-[0_0_10px_rgba(16,185,129,0.8)]; }
      .stat-card.red::after { @apply bg-rose-500 dark:shadow-[0_0_10px_rgba(244,63,94,0.8)]; }
      .stat-card.yellow::after { @apply bg-amber-500 dark:shadow-[0_0_10px_rgba(245,158,11,0.8)]; }
      .stat-card.purple::after { @apply bg-indigo-500 dark:shadow-[0_0_10px_rgba(99,102,241,0.8)]; }
      .stat-card.cyan::after { @apply bg-cyan-400 dark:shadow-[0_0_10px_rgba(34,211,238,0.8)]; }

      .stat-icon { @apply w-10 h-10 rounded-xl flex items-center justify-center text-lg mb-4; }
      .stat-card.indigo .stat-icon { @apply bg-saffron-50 dark:bg-saffron-500/20 text-saffron-600 dark:text-saffron-400 border border-saffron-100 dark:border-saffron-500/20 shadow-inner; }
      .stat-card.blue .stat-icon { @apply bg-sky-50 dark:bg-sky-500/20 text-sky-600 dark:text-sky-400 border border-sky-100 dark:border-sky-500/20 shadow-inner; }
      .stat-card.green .stat-icon { @apply bg-emerald-50 dark:bg-emerald-500/20 text-emerald-600 dark:text-emerald-400 border border-emerald-100 dark:border-emerald-500/20 shadow-inner; }
      .stat-card.red .stat-icon { @apply bg-rose-50 dark:bg-rose-500/20 text-rose-600 dark:text-rose-400 border border-rose-100 dark:border-rose-500/20 shadow-inner; }
      .stat-card.yellow .stat-icon { @apply bg-amber-50 dark:bg-amber-500/20 text-amber-600 dark:text-amber-400 border border-amber-100 dark:border-amber-500/20 shadow-inner; }
      .stat-card.purple .stat-icon { @apply bg-indigo-50 dark:bg-indigo-500/20 text-indigo-600 dark:text-indigo-400 border border-indigo-100 dark:border-indigo-500/20 shadow-inner; }
      .stat-card.cyan .stat-icon { @apply bg-cyan-50 dark:bg-cyan-500/20 text-cyan-600 dark:text-cyan-400 border border-cyan-100 dark:border-cyan-500/20 shadow-inner; }

      .stat-val { @apply font-mono text-3xl font-bold text-slate-800 dark:text-white leading-none mb-1.5 tracking-tight; }
      .stat-label { @apply text-[12px] text-slate-500 dark:text-slate-400 font-medium whitespace-nowrap overflow-hidden text-ellipsis; }
      .stat-change { @apply text-[11px] mt-3 flex items-center gap-1.5 font-mono tracking-tight; }
      .stat-change.up { @apply text-emerald-600 dark:text-emerald-400 px-2 py-0.5 rounded-full bg-emerald-50 dark:bg-emerald-400/10 inline-flex w-max border border-emerald-200 dark:border-emerald-400/20; }
      .stat-change.down { @apply text-rose-600 dark:text-rose-400 px-2 py-0.5 rounded-full bg-rose-50 dark:bg-rose-400/10 inline-flex w-max border border-rose-200 dark:border-rose-400/20; }

      /* Table */
      .data-table { @apply w-full border-collapse text-left; }
      .data-table th {
        @apply px-4 py-3 text-[10px] font-bold uppercase tracking-widest text-slate-500 dark:text-slate-400 border-b border-slate-200 dark:border-slate-700/60 font-mono bg-slate-50 dark:bg-slate-800/40 whitespace-nowrap;
      }
      .data-table td {
        @apply px-4 py-3.5 text-[13px] text-slate-700 dark:text-slate-200 border-b border-slate-100 dark:border-slate-700/50 align-middle transition-colors group-hover:bg-slate-50 dark:group-hover:bg-white/5;
      }
      .data-table tr:hover td { @apply bg-slate-50 dark:bg-slate-800/40; }
      .data-table tr:last-child td { @apply border-b-0; }

      /* Badges */
      .badge {
        @apply inline-flex items-center justify-center gap-1.5 px-2.5 py-1 rounded-md text-[10px] font-bold uppercase tracking-widest font-mono whitespace-nowrap shadow-sm dark:backdrop-blur-sm;
      }
      .badge-green { @apply bg-emerald-50 dark:bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-200 dark:border-emerald-500/30; }
      .badge-red { @apply bg-rose-50 dark:bg-rose-500/10 text-rose-600 dark:text-rose-400 border border-rose-200 dark:border-rose-500/30; }
      .badge-yellow { @apply bg-amber-50 dark:bg-amber-500/10 text-amber-600 dark:text-amber-400 border border-amber-200 dark:border-amber-500/30; }
      .badge-blue { @apply bg-sky-50 dark:bg-sky-500/10 text-sky-600 dark:text-sky-400 border border-sky-200 dark:border-sky-500/30; }
      .badge-orange { @apply bg-saffron-50 dark:bg-saffron-500/10 text-saffron-600 dark:text-saffron-400 border border-saffron-200 dark:border-saffron-500/30; }
      .badge-purple { @apply bg-indigo-50 dark:bg-indigo-500/10 text-indigo-600 dark:text-indigo-400 border border-indigo-200 dark:border-indigo-500/30; }
      .badge-gray { @apply bg-slate-100 dark:bg-slate-500/10 text-slate-600 dark:text-slate-400 border border-slate-200 dark:border-slate-500/30; }
      .badge-dot::before { content: ''; @apply w-1.5 h-1.5 rounded-full bg-current inline-block shadow-sm; }

      /* Buttons */
      .btn {
        @apply inline-flex items-center gap-2 px-4 py-2 rounded-xl text-[13px] font-semibold cursor-pointer border-none no-underline transition-all duration-200 whitespace-nowrap hover:-translate-y-0.5 justify-center;
      }
      .btn-primary {
        @apply bg-gradient-to-r from-saffron-500 to-saffron-600 text-white shadow-[0_4px_14px_rgba(234,88,12,0.3)] hover:shadow-[0_6px_20px_rgba(234,88,12,0.4)] hover:from-saffron-400 hover:to-saffron-500;
      }
      .btn-secondary {
        @apply bg-white dark:bg-slate-800/80 text-slate-700 dark:text-slate-200 border border-slate-200 dark:border-slate-700/80 hover:bg-slate-50 dark:hover:bg-slate-700 hover:border-slate-300 dark:hover:border-slate-600 shadow-sm hover:shadow-md;
      }
      .btn-ghost {
        @apply bg-transparent text-slate-500 dark:text-slate-400 border border-slate-200 dark:border-slate-700/50 hover:bg-slate-50 dark:hover:bg-slate-800 hover:text-slate-800 dark:hover:text-slate-200 hover:border-slate-300 dark:hover:border-slate-600 rounded-xl;
      }
      .btn-danger {
        @apply bg-rose-50 dark:bg-rose-500/10 text-rose-600 dark:text-rose-400 border border-rose-200 dark:border-rose-500/20 hover:bg-rose-100 dark:hover:bg-rose-500/20;
      }
      .btn-sm { @apply px-3 py-1.5 text-xs rounded-lg; }
      .btn-icon { @apply p-2 w-8 h-8 justify-center rounded-lg; }

      /* Inputs */
      .input-field {
        @apply w-full bg-white dark:bg-slate-900/50 border border-slate-200 dark:border-slate-700/60 rounded-xl px-3.5 py-2 text-[13px] text-slate-800 dark:text-slate-200 font-sans outline-none transition-all duration-200 focus:border-saffron-500 dark:focus:border-saffron-500/80 focus:ring-2 focus:ring-saffron-500/20 placeholder-slate-400 dark:placeholder-slate-500 shadow-sm dark:shadow-inner;
      }
      .input-wrap { @apply relative inline-flex items-center w-full; }
      .input-icon { @apply absolute left-3.5 text-slate-400 dark:text-slate-500 text-xs; }
      .input-wrap .input-field { @apply pl-9; }
      select.input-field { @apply cursor-pointer appearance-none pr-8 bg-[url('data:image/svg+xml;charset=utf-8;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIGZpbGw9Im5vbmUiIHZpZXdCb3g9IjAgMCAyMCAyMCI+PHBhdGggc3Ryb2tlPSIjOTRhM2I4IiBzdHJva2UtbGluZWNhcD0icm91bmQiIHN0cm9rZS1saW5lam9pbj0icm91bmQiIHN0cm9rZS13aWR0aD0iMS41IiBkPSJtNiA4IDQgNCA0LTRIMnoiLz48L3N2Zz4=')] bg-no-repeat bg-[position:right_10px_center] bg-[length:18px]; }

      /* Toast */
      .toast-wrap { @apply fixed bottom-5 right-5 z-[9999] flex flex-col gap-2.5; }
      .toast {
        @apply flex items-center gap-3 bg-white dark:bg-slate-800/90 dark:backdrop-blur-xl border border-slate-200 dark:border-slate-700/80 rounded-xl px-4 py-3 text-[13px] text-slate-800 dark:text-slate-200 shadow-lg dark:shadow-2xl min-w-[280px] animate-[slideInToast_0.3s_cubic-bezier(0.16,1,0.3,1)];
      }

      /* Grid Helpers */
      .grid-2 { @apply grid grid-cols-1 sm:grid-cols-2 gap-4 sm:gap-6; }
      .grid-3 { @apply grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-6; }
      .grid-4 { @apply grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-6; }
      
      .sidebar-overlay { @apply hidden fixed inset-0 bg-slate-900/40 dark:bg-slate-900/80 backdrop-blur-sm z-[99] lg:hidden transition-opacity duration-300; }
      .sidebar-overlay.show { @apply block animate-[fadeIn_0.2s_ease-out]; }
    }

    @keyframes fadeInPage { from{ opacity:0; transform:translateY(10px); } to{ opacity:1; transform:translateY(0); } }
    @keyframes slideInToast { from{ transform:translateX(100%) scale(0.9); opacity:0; } to{ transform:translateX(0) scale(1); opacity:1; } }
    @keyframes fadeIn { from{ opacity:0; } to{ opacity:1; } }

    /* Responsive */
    @media (max-width: 1024px) {
      .sidebar { @apply -translate-x-full; }
      .sidebar.open { @apply translate-x-0 shadow-2xl; }
      .main { @apply ml-0; }
      .topbar-hamburger { @apply flex; }
    }
  </style>
  {% block extra_css %}{% endblock %}
</head>"""
base_html = re.sub(r"<head>.*?</head>", new_head, base_html, flags=re.DOTALL)

# Inject Toggle and Logout buttons into Topbar
# Find: <div class="topbar-right">
topbar_right = r"""<div class="topbar-right">
        <button onclick="toggleTheme()" class="topbar-btn" title="Toggle Light/Dark Mode">
          <i id="themeIcon" class="fas fa-moon"></i>
        </button>
        <a href="{% url 'accounts:logout' %}" class="topbar-btn text-rose-500 hover:text-rose-600 hover:bg-rose-50 dark:text-rose-400 dark:hover:bg-rose-500/10 border-none shadow-none" title="Logout">
          <i class="fas fa-sign-out-alt"></i>
        </a>"""
base_html = re.sub(r'<div class="topbar-right">', topbar_right, base_html)

# Add toggle theme JS at end of body
toggle_script = r"""<script>
  function toggleTheme() {
    if (localStorage.theme === 'dark') {
      localStorage.theme = 'light';
      document.documentElement.classList.remove('dark');
    } else {
      localStorage.theme = 'dark';
      document.documentElement.classList.add('dark');
    }
    updateThemeIcon();
    if(typeof updateChartsTheme === 'function') updateChartsTheme();
  }
  function updateThemeIcon() {
    const icon = document.getElementById('themeIcon');
    if(icon) {
      if(document.documentElement.classList.contains('dark')) {
        icon.className = 'fas fa-sun';
      } else {
        icon.className = 'fas fa-moon';
      }
    }
  }
  updateThemeIcon();
</script>"""
base_html = base_html.replace('</body>', toggle_script + '\n</body>')

with open(base_path, "w", encoding="utf-8") as f:
    f.write(base_html)


# 2. Re-structure dashboard HTML entirely to "Enterprise Proper Form"
with open(dash_path, "r", encoding="utf-8") as f:
    dash_html = f.read()

new_dash_style = r"""<style type="text/tailwindcss">
    @layer components {
      .dash-grid{ @apply grid grid-cols-1 lg:grid-cols-2 gap-4 lg:gap-6 mb-8; }
      .dash-grid.thirds{ @apply grid grid-cols-1 lg:grid-cols-3 gap-4 lg:gap-6 mb-8; }
      .dash-grid.thirds > .card:first-child { @apply lg:col-span-2; }
      
      .alert-item{ @apply flex items-start gap-4 py-3.5 border-b border-slate-100 dark:border-slate-700/50 hover:bg-slate-50 dark:hover:bg-white/5 px-3 -mx-3 rounded-xl transition-colors cursor-pointer; }
      .alert-item:last-child{ @apply border-b-0; }
      .alert-dot{ @apply w-2 h-2 rounded-full shrink-0 mt-1.5 shadow-sm; }
      .alert-dot.red{ @apply bg-rose-500 text-rose-500; }
      .alert-dot.yellow{ @apply bg-amber-500 text-amber-500; }
      .alert-dot.blue{ @apply bg-sky-500 text-sky-500; }
      .alert-title{ @apply text-[13px] font-semibold text-slate-800 dark:text-slate-200 mb-0.5; }
      .alert-time{ @apply text-[11px] text-slate-500 dark:text-slate-400 font-mono tracking-tight; }
      
      .mini-chart-wrap{ @apply h-[260px] w-full mt-2; }
      .donut-wrap{ @apply flex flex-col items-center justify-center py-4; }
      .donut-wrap canvas{ @apply max-w-[190px] hover:scale-[1.02] transition-transform duration-300; }
      .donut-legend{ @apply flex flex-col gap-2.5 w-full mt-6 bg-slate-50 dark:bg-slate-800/40 p-4 rounded-xl border border-slate-200 dark:border-slate-700/50; }
      .legend-row{ @apply flex items-center gap-3 text-[12px]; }
      .legend-dot{ @apply w-2 h-2 rounded-full shrink-0 shadow-sm; }
      .legend-label{ @apply text-slate-600 dark:text-slate-300 flex-1 font-medium; }
      .legend-val{ @apply font-mono text-[11px] text-slate-800 dark:text-slate-100 font-bold bg-white dark:bg-slate-700/50 px-2 py-0.5 rounded-md border border-slate-200 dark:border-slate-600; }
      
      .ticker-wrap{ @apply flex gap-4 overflow-x-auto pb-4 mb-6 hide-scroll-bar py-1; }
      .ticker-wrap::-webkit-scrollbar { display: none; }
      .ticker-card{ @apply bg-white dark:bg-slate-800/40 dark:backdrop-blur-md border border-slate-200 dark:border-slate-700/50 rounded-2xl p-4 shrink-0 min-w-[160px] shadow-sm dark:shadow-lg transition-all hover:-translate-y-1 hover:border-slate-300 dark:hover:border-slate-600 hover:shadow-md; }
      .ticker-lbl{ @apply text-[10px] text-slate-500 dark:text-slate-400 font-mono uppercase tracking-widest mb-1.5; }
      .ticker-val{ @apply font-mono text-[20px] font-bold text-slate-800 dark:text-white; }
      .ticker-change{ @apply font-mono text-[10px] mt-1.5 flex items-center gap-1 font-semibold; }
    }
  </style>"""

dash_html = re.sub(r'<style.*?</style>', new_dash_style, dash_html, flags=re.DOTALL)

# Refactor the JS to listen to theme changes
new_js = r"""<script>
let activityChartConf, donutChartConf;

function getChartColors() {
    const isDark = document.documentElement.classList.contains('dark');
    return {
        text: isDark ? '#94a3b8' : '#64748b',
        grid: isDark ? 'rgba(255,255,255,0.04)' : 'rgba(0,0,0,0.04)'
    };
}

const c = getChartColors();

activityChartConf = new Chart(document.getElementById('activityChart').getContext('2d'), {
  type: 'bar',
  data: {
    labels: {{ months|safe }},
    datasets: [
      { label: 'Tenders', data: {{ tender_activity|safe }}, backgroundColor: '#f97316', borderRadius: 4 },
      { label: 'Bids',    data: {{ bid_activity|safe }}, backgroundColor: '#0ea5e9', borderRadius: 4 }
    ]
  },
  options: {
    responsive: true, maintainAspectRatio: false,
    plugins: { legend: { labels: { color: c.text, font: { size: 11 } } } },
    scales: {
      x: { grid: { color: c.grid, drawBorder: false }, ticks: { color: c.text, font: { size: 10 } } },
      y: { grid: { color: c.grid, drawBorder: false }, ticks: { color: c.text, font: { size: 10 } } }
    }
  }
});

donutChartConf = new Chart(document.getElementById('donutChart').getContext('2d'), {
  type: 'doughnut',
  data: {
    labels: {{ cat_labels|safe }},
    datasets: [{ 
        data: {{ cat_counts|safe }}, 
        backgroundColor: [
            '#f97316','#10b981','#f59e0b','#6366f1','#64748b',
            '#06b6d4','#f43f5e','#ea580c','#14b8a6','#818cf8'
        ], 
        borderWidth: 2,
        borderColor: document.documentElement.classList.contains('dark') ? '#1e293b' : '#ffffff',
        hoverOffset: 4 
    }]
  },
  options: {
    responsive: false, cutout: '75%',
    plugins: { legend: { display: false } }
  }
});

function updateChartsTheme() {
    const nc = getChartColors();
    activityChartConf.options.plugins.legend.labels.color = nc.text;
    activityChartConf.options.scales.x.ticks.color = nc.text;
    activityChartConf.options.scales.y.ticks.color = nc.text;
    activityChartConf.options.scales.x.grid.color = nc.grid;
    activityChartConf.options.scales.y.grid.color = nc.grid;
    activityChartConf.update();

    donutChartConf.data.datasets[0].borderColor = document.documentElement.classList.contains('dark') ? '#1e293b' : '#ffffff';
    donutChartConf.update();
}
</script>"""

dash_html = re.sub(r'<script>\s*// Activity Chart.*?</script>', new_js, dash_html, flags=re.DOTALL)

with open(dash_path, "w", encoding="utf-8") as f:
    f.write(dash_html)

print("UI successfully rebuilt with full Light/Dark mode and modern dashboard!")
