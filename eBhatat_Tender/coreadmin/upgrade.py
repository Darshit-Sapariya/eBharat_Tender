import os
import re

base_path = r"c:\Users\Darshit\OneDrive\Desktop\eBharat_Tender\eBhatat_Tender\coreadmin\templates\coreadmin_base.html"
desh_path = r"c:\Users\Darshit\OneDrive\Desktop\eBharat_Tender\eBhatat_Tender\coreadmin\templates\deshbord.html"

# coreadmin_base.html upgrade
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
  
  <style type="text/tailwindcss">
    @layer base {
      body {
        @apply bg-navy-900 text-slate-200 font-sans antialiased min-h-screen flex flex-col overflow-x-hidden;
      }
      body::before {
        content: '';
        position: fixed; inset: 0; pointer-events: none; z-index: 0;
        background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='0.03'/%3E%3C/svg%3E");
        background-repeat: repeat;
        opacity: 0.4;
      }
      ::-webkit-scrollbar { @apply w-1.5 h-1.5; }
      ::-webkit-scrollbar-track { @apply bg-transparent; }
      ::-webkit-scrollbar-thumb { @apply bg-slate-700/50 rounded-full; }
    }

    @layer components {
      .layout { @apply flex h-screen relative z-10; }
      
      /* Sidebar */
      .sidebar {
        @apply w-[260px] bg-slate-900/95 backdrop-blur-xl border-r border-slate-800/60 flex flex-col shrink-0 fixed top-0 left-0 bottom-0 z-[100] transition-transform duration-300;
      }
      .sidebar-logo {
        @apply h-[62px] flex items-center gap-3 px-5 border-b-2 border-saffron-500/80 shrink-0 bg-slate-900/90;
      }
      .logo-mark {
        @apply w-8 h-8 rounded-md bg-gradient-to-br from-saffron-400 to-saffron-600 flex items-center justify-center font-mono text-[11px] font-bold text-black shadow-[0_0_20px_rgba(249,115,22,0.3)];
      }
      .logo-text { @apply font-mono text-[11px] font-bold text-slate-100 uppercase tracking-widest leading-tight; }
      .logo-text span { @apply text-saffron-500; }
      
      .sidebar-section { @apply px-4 py-2 mt-4 text-[10px] font-bold uppercase tracking-widest text-slate-500 font-mono; }
      .sidebar-nav { @apply flex-1 overflow-y-auto py-2; }
      
      .nav-item {
        @apply flex items-center gap-3 px-5 py-2.5 text-[13px] font-medium text-slate-400 hover:text-slate-100 hover:bg-white/5 transition-all relative cursor-pointer no-underline;
      }
      .nav-item.active { @apply text-saffron-500 bg-saffron-500/10 font-semibold; }
      .nav-item.active::before {
        content: '';
        @apply absolute left-0 top-1.5 bottom-1.5 w-[3px] bg-saffron-500 rounded-r shadow-[0_0_10px_rgba(249,115,22,0.5)];
      }
      .nav-item i { @apply w-4 text-center text-sm; }
      
      .sidebar-footer { @apply p-4 border-t border-slate-800/60 shrink-0; }
      .admin-profile {
        @apply flex items-center gap-3 p-2 rounded-xl bg-slate-800/40 border border-slate-700/50 cursor-pointer hover:bg-slate-800 transition-colors;
      }
      .admin-avatar { @apply w-8 h-8 rounded-lg bg-gradient-to-br from-saffron-500 to-red-600 flex items-center justify-center text-xs font-bold text-white font-mono shrink-0 shadow-inner; }
      .admin-name { @apply text-[13px] font-semibold text-slate-200 tracking-tight; }
      .admin-role { @apply text-[10px] text-saffron-500 font-mono uppercase tracking-wider; }
      .admin-caret { @apply ml-auto text-slate-500 text-[10px]; }

      /* Main */
      .main { @apply ml-[260px] flex-1 flex flex-col min-h-screen min-w-0 transition-all duration-300 transform-gpu; }
      
      /* Topbar */
      .topbar {
        @apply h-[62px] bg-slate-900/80 backdrop-blur-md border-b border-slate-800/60 flex items-center px-6 gap-4 shrink-0 sticky top-0 z-50;
      }
      .topbar-hamburger { @apply hidden w-8 h-8 flex-shrink-0 rounded-lg text-slate-400 hover:bg-slate-800 hover:text-slate-200 transition-colors justify-center items-center cursor-pointer border-none bg-transparent; }
      .breadcrumb { @apply flex items-center gap-2 text-[13px] text-slate-500; }
      .breadcrumb span { @apply text-slate-200 font-semibold; }
      .breadcrumb i { @apply text-[10px]; }
      
      .topbar-right { @apply ml-auto flex items-center gap-3; }
      .topbar-btn {
        @apply w-9 h-9 bg-slate-800/50 border border-slate-700/50 rounded-xl flex items-center justify-center text-slate-400 cursor-pointer text-sm relative transition-all hover:bg-slate-700 hover:text-slate-200 hover:border-slate-600;
      }
      .topbar-notif { @apply absolute -top-1 -right-1 w-2.5 h-2.5 rounded-full bg-red-500 border-2 border-slate-900 animate-pulse; }
      .topbar-status {
        @apply hidden sm:flex items-center gap-2 bg-slate-800/40 border border-slate-700/50 rounded-xl px-3 h-9 text-[11px] text-slate-400 font-mono;
      }
      .status-dot { @apply w-1.5 h-1.5 rounded-full bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.8)] animate-pulse; }

      /* Page Content */
      .page-content { @apply flex-1 p-4 sm:p-6 lg:p-8 overflow-y-auto animate-[fadeInPage_0.4s_ease-out]; }
      .page-header { @apply flex flex-col sm:flex-row sm:items-start justify-between mb-8 gap-4; }
      .page-title { @apply font-mono text-[19px] font-bold text-white uppercase tracking-wider shadow-sm; }
      .page-subtitle { @apply text-[13px] text-slate-400 mt-1.5; }

      /* Cards */
      .card {
        @apply bg-slate-800/30 backdrop-blur-sm border border-slate-700/50 rounded-2xl overflow-hidden shadow-xl;
        box-shadow: 0 8px 32px rgba(0,0,0,0.2);
      }
      .card-head { @apply flex items-center justify-between px-5 py-4 border-b border-slate-700/50 bg-slate-800/50; }
      .card-title { @apply font-mono text-[11px] font-bold uppercase tracking-widest text-slate-300; }
      .card-body { @apply p-5; }

      /* Stat Cards */
      .stats-grid { @apply grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-6 mb-8; }
      .stat-card {
        @apply bg-slate-800/40 backdrop-blur-md border border-slate-700/50 rounded-2xl p-5 relative overflow-hidden transition-all duration-300 hover:border-slate-600 hover:-translate-y-1 shadow-lg group hover:shadow-2xl hover:shadow-slate-900/50;
      }
      .stat-card::after { content: ''; @apply absolute top-0 left-0 right-0 h-0.5 opacity-80 transition-opacity group-hover:opacity-100; }
      .stat-card.indigo::after { @apply bg-saffron-500 shadow-[0_0_10px_rgba(249,115,22,0.8)]; }
      .stat-card.blue::after { @apply bg-sky-500 shadow-[0_0_10px_rgba(14,165,233,0.8)]; }
      .stat-card.green::after { @apply bg-emerald-500 shadow-[0_0_10px_rgba(16,185,129,0.8)]; }
      .stat-card.red::after { @apply bg-rose-500 shadow-[0_0_10px_rgba(244,63,94,0.8)]; }
      .stat-card.yellow::after { @apply bg-amber-500 shadow-[0_0_10px_rgba(245,158,11,0.8)]; }
      .stat-card.purple::after { @apply bg-indigo-500 shadow-[0_0_10px_rgba(99,102,241,0.8)]; }
      .stat-card.cyan::after { @apply bg-cyan-400 shadow-[0_0_10px_rgba(34,211,238,0.8)]; }

      .stat-icon { @apply w-10 h-10 rounded-xl flex items-center justify-center text-lg mb-4 shadow-inner; }
      .stat-card.indigo .stat-icon { @apply bg-saffron-500/20 text-saffron-400 border border-saffron-500/20; }
      .stat-card.blue .stat-icon { @apply bg-sky-500/20 text-sky-400 border border-sky-500/20; }
      .stat-card.green .stat-icon { @apply bg-emerald-500/20 text-emerald-400 border border-emerald-500/20; }
      .stat-card.red .stat-icon { @apply bg-rose-500/20 text-rose-400 border border-rose-500/20; }
      .stat-card.yellow .stat-icon { @apply bg-amber-500/20 text-amber-400 border border-amber-500/20; }
      .stat-card.purple .stat-icon { @apply bg-indigo-500/20 text-indigo-400 border border-indigo-500/20; }
      .stat-card.cyan .stat-icon { @apply bg-cyan-500/20 text-cyan-400 border border-cyan-500/20; }

      .stat-val { @apply font-mono text-3xl font-bold text-white leading-none mb-1.5 tracking-tight; }
      .stat-label { @apply text-[12px] text-slate-400 font-medium whitespace-nowrap overflow-hidden text-ellipsis; }
      .stat-change { @apply text-[11px] mt-3 flex items-center gap-1.5 font-mono tracking-tight; }
      .stat-change.up { @apply text-emerald-400 px-2 py-0.5 rounded-full bg-emerald-400/10 inline-flex w-max border border-emerald-400/20; }
      .stat-change.down { @apply text-rose-400 px-2 py-0.5 rounded-full bg-rose-400/10 inline-flex w-max border border-rose-400/20; }

      /* Table */
      .data-table { @apply w-full border-collapse text-left; }
      .data-table th {
        @apply px-4 py-3 text-[10px] font-bold uppercase tracking-widest text-slate-400 border-b border-slate-700/60 font-mono bg-slate-800/40 whitespace-nowrap;
      }
      .data-table td {
        @apply px-4 py-3.5 text-[13px] text-slate-200 border-b border-slate-700/50 align-middle transition-colors group-hover:bg-white/5;
      }
      .data-table tr:hover td { @apply bg-slate-800/40; }
      .data-table tr:last-child td { @apply border-b-0; }

      /* Badges */
      .badge {
        @apply inline-flex items-center justify-center gap-1.5 px-2.5 py-1 rounded-md text-[10px] font-bold uppercase tracking-widest font-mono whitespace-nowrap shadow-sm backdrop-blur-sm;
      }
      .badge-green { @apply bg-emerald-500/10 text-emerald-400 border border-emerald-500/30; }
      .badge-red { @apply bg-rose-500/10 text-rose-400 border border-rose-500/30; }
      .badge-yellow { @apply bg-amber-500/10 text-amber-400 border border-amber-500/30; }
      .badge-blue { @apply bg-sky-500/10 text-sky-400 border border-sky-500/30; }
      .badge-orange { @apply bg-saffron-500/10 text-saffron-400 border border-saffron-500/30; }
      .badge-purple { @apply bg-indigo-500/10 text-indigo-400 border border-indigo-500/30; }
      .badge-gray { @apply bg-slate-500/10 text-slate-400 border border-slate-500/30; }
      .badge-dot::before { content: ''; @apply w-1.5 h-1.5 rounded-full bg-current inline-block shadow-sm; }

      /* Buttons */
      .btn {
        @apply inline-flex items-center gap-2 px-4 py-2 rounded-xl text-[13px] font-semibold cursor-pointer border-none no-underline transition-all duration-200 whitespace-nowrap hover:-translate-y-0.5 justify-center;
      }
      .btn-primary {
        @apply bg-gradient-to-r from-saffron-500 to-saffron-600 text-white shadow-[0_4px_14px_rgba(234,88,12,0.4)] hover:shadow-[0_6px_20px_rgba(234,88,12,0.6)] hover:from-saffron-400 hover:to-saffron-500;
      }
      .btn-secondary {
        @apply bg-slate-800/80 text-slate-200 border border-slate-700/80 hover:bg-slate-700 hover:border-slate-600 hover:shadow-lg backdrop-blur-sm;
      }
      .btn-ghost {
        @apply bg-transparent text-slate-400 border border-slate-700/50 hover:bg-slate-800 hover:text-slate-200 hover:border-slate-600 rounded-xl;
      }
      .btn-danger {
        @apply bg-rose-500/10 text-rose-400 border border-rose-500/20 hover:bg-rose-500/20;
      }
      .btn-sm { @apply px-3 py-1.5 text-xs rounded-lg; }
      .btn-icon { @apply p-2 w-8 h-8 justify-center rounded-lg; }

      /* Inputs */
      .input-field {
        @apply w-full bg-slate-900/50 border border-slate-700/60 rounded-xl px-3.5 py-2 text-[13px] text-slate-200 font-sans outline-none transition-all duration-200 focus:border-saffron-500/80 focus:ring-2 focus:ring-saffron-500/20 placeholder-slate-500 backdrop-blur-sm shadow-inner;
      }
      .input-wrap { @apply relative inline-flex items-center w-full; }
      .input-icon { @apply absolute left-3.5 text-slate-500 text-xs; }
      .input-wrap .input-field { @apply pl-9; }
      select.input-field { @apply cursor-pointer appearance-none pr-8 bg-[url('data:image/svg+xml;charset=utf-8;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIGZpbGw9Im5vbmUiIHZpZXdCb3g9IjAgMCAyMCAyMCI+PHBhdGggc3Ryb2tlPSIjOTRhM2I4IiBzdHJva2UtbGluZWNhcD0icm91bmQiIHN0cm9rZS1saW5lam9pbj0icm91bmQiIHN0cm9rZS13aWR0aD0iMS41IiBkPSJtNiA4IDQgNCA0LTRIMnoiLz48L3N2Zz4=')] bg-no-repeat bg-[position:right_10px_center] bg-[length:18px]; }

      /* Toast */
      .toast-wrap { @apply fixed bottom-5 right-5 z-[9999] flex flex-col gap-2.5; }
      .toast {
        @apply flex items-center gap-3 bg-slate-800/90 backdrop-blur-xl border border-slate-700/80 rounded-xl px-4 py-3 text-[13px] text-slate-200 shadow-2xl min-w-[280px] animate-[slideInToast_0.3s_cubic-bezier(0.16,1,0.3,1)];
      }

      /* Grid Helpers */
      .grid-2 { @apply grid grid-cols-1 sm:grid-cols-2 gap-4 sm:gap-6; }
      .grid-3 { @apply grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-6; }
      .grid-4 { @apply grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-6; }
      
      .sidebar-overlay { @apply hidden fixed inset-0 bg-slate-900/80 backdrop-blur-sm z-[99] lg:hidden transition-opacity duration-300; }
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

with open(base_path, 'r', encoding='utf-8') as f:
    content = f.read()

content = re.sub(r'<head>.*?</head>', new_head, content, flags=re.DOTALL)

with open(base_path, 'w', encoding='utf-8') as f:
    f.write(content)


# dashboard update
new_dash_style = r"""<style type="text/tailwindcss">
    @layer components {
      .dash-grid{ @apply grid grid-cols-1 md:grid-cols-2 gap-4 lg:gap-6 mb-6; }
      .dash-grid.thirds{ @apply grid grid-cols-1 lg:grid-cols-3 gap-4 lg:gap-6 mb-6; }
      .dash-grid.thirds > .card:first-child { @apply lg:col-span-2; }
      
      .alert-item{ @apply flex items-start gap-4 py-3.5 border-b border-slate-700/50 hover:bg-white/5 px-2 -mx-2 rounded-lg transition-colors cursor-pointer; }
      .alert-item:last-child{ @apply border-b-0; }
      .alert-dot{ @apply w-2 h-2 rounded-full shrink-0 mt-1.5 shadow-[0_0_8px_currentColor]; }
      .alert-dot.red{ @apply bg-rose-500 text-rose-500; }
      .alert-dot.yellow{ @apply bg-amber-500 text-amber-500; }
      .alert-dot.blue{ @apply bg-sky-500 text-sky-500; }
      .alert-title{ @apply text-[13px] font-semibold text-slate-200 mb-0.5; }
      .alert-time{ @apply text-[11px] text-slate-400 font-mono tracking-tight; }
      
      .mini-chart-wrap{ @apply h-[220px] w-full; }
      .donut-wrap{ @apply flex flex-col items-center justify-center; }
      .donut-wrap canvas{ @apply max-w-[180px] hover:scale-105 transition-transform duration-300; }
      .donut-legend{ @apply flex flex-col gap-2 w-full mt-5 bg-slate-800/40 p-3 rounded-xl border border-slate-700/50; }
      .legend-row{ @apply flex items-center gap-2.5 text-[12px]; }
      .legend-dot{ @apply w-2 h-2 rounded-full shrink-0 shadow-sm; }
      .legend-label{ @apply text-slate-300 flex-1 font-medium; }
      .legend-val{ @apply font-mono text-[11px] text-slate-100 font-bold bg-slate-700/50 px-2 py-0.5 rounded-md; }
      
      .ticker-wrap{ @apply flex gap-4 overflow-x-auto pb-4 mb-6 hide-scroll-bar; }
      .ticker-wrap::-webkit-scrollbar { display: none; }
      .ticker-card{ @apply bg-slate-800/40 backdrop-blur-md border border-slate-700/50 rounded-2xl p-4 shrink-0 min-w-[160px] shadow-lg transition-all hover:-translate-y-1 hover:border-slate-600; }
      .ticker-lbl{ @apply text-[10px] text-slate-400 font-mono uppercase tracking-widest mb-1.5; }
      .ticker-val{ @apply font-mono text-[20px] font-bold text-white; }
      .ticker-change{ @apply font-mono text-[10px] mt-1.5 flex items-center gap-1; }
    }
  </style>"""

with open(desh_path, 'r', encoding='utf-8') as f:
    dcontent = f.read()

dcontent = re.sub(r'<style>.*?</style>', new_dash_style, dcontent, flags=re.DOTALL)

with open(desh_path, 'w', encoding='utf-8') as f:
    f.write(dcontent)

print("Styles upgraded.")
