import re

base_path = r"c:\Users\Darshit\OneDrive\Desktop\eBharat_Tender\eBhatat_Tender\coreadmin\templates\coreadmin_base.html"

with open(base_path, "r", encoding="utf-8") as f:
    text = f.read()

# Fix Shadows
text = text.replace("shadow-[0_0_20px_rgba(249,115,22,0.3)]", "shadow-md")
text = text.replace("shadow-[0_0_10px_rgba(249,115,22,0.5)]", "shadow-md")
text = text.replace("shadow-[0_0_8px_rgba(16,185,129,0.8)]", "shadow-sm")
text = text.replace("shadow-[0_8px_32px_rgba(0,0,0,0.2)]", "shadow-xl")
text = text.replace("shadow-[0_4px_14px_rgba(234,88,12,0.3)]", "shadow-lg")
text = text.replace("shadow-[0_6px_20px_rgba(234,88,12,0.4)]", "shadow-xl")

# Fix Color Glows
text = text.replace("shadow-[0_0_10px_rgba(249,115,22,0.8)]", "shadow-md")
text = text.replace("shadow-[0_0_10px_rgba(14,165,233,0.8)]", "shadow-md")
text = text.replace("shadow-[0_0_10px_rgba(16,185,129,0.8)]", "shadow-md")
text = text.replace("shadow-[0_0_10px_rgba(244,63,94,0.8)]", "shadow-md")
text = text.replace("shadow-[0_0_10px_rgba(245,158,11,0.8)]", "shadow-md")
text = text.replace("shadow-[0_0_10px_rgba(99,102,241,0.8)]", "shadow-md")
text = text.replace("shadow-[0_0_10px_rgba(34,211,238,0.8)]", "shadow-md")

# Fix Animations
text = text.replace("animate-[fadeInPage_0.4s_ease-out]", "")
text = text.replace("animate-[slideInToast_0.3s_cubic-bezier(0.16,1,0.3,1)]", "")
text = text.replace("animate-[fadeIn_0.2s_ease-out]", "")

# Restore standard CSS animations manually
css_append = """
    .page-content { animation: fadeInPage 0.4s ease-out; }
    .toast { animation: slideInToast 0.3s cubic-bezier(0.16,1,0.3,1); }
    .sidebar-overlay.show { animation: fadeIn 0.2s ease-out; }
"""
text = text.replace("    @keyframes fadeInPage", css_append + "    @keyframes fadeInPage")

# Fix SVG background
bad_svg = r"bg-\[url\('data:image/svg\+xml;charset=utf-8;base64,[^']+'\)\] bg-no-repeat bg-\[position:right_10px_center\] bg-\[length:18px\]"
def replace_svg(match):
    return ""
text = re.sub(bad_svg, "", text)

css_svg = """
      select.input-field {
        background-image: url('data:image/svg+xml;charset=utf-8;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIGZpbGw9Im5vbmUiIHZpZXdCb3g9IjAgMCAyMCAyMCI+PHBhdGggc3Ryb2tlPSIjOTRhM2I4IiBzdHJva2UtbGluZWNhcD0icm91bmQiIHN0cm9rZS1saW5lam9pbj0icm91bmQiIHN0cm9rZS13aWR0aD0iMS41IiBkPSJtNiA4IDQgNCA0LTRIMnoiLz48L3N2Zz4=');
        background-repeat: no-repeat;
        background-position: right 10px center;
        background-size: 18px;
      }
"""
text = text.replace("      select.input-field { @apply cursor-pointer appearance-none pr-8 ; }", css_svg)
text = text.replace("      select.input-field { @apply cursor-pointer appearance-none pr-8  ; }", css_svg)

with open(base_path, "w", encoding="utf-8") as f:
    f.write(text)

print("Tailwind arbitrary CSS fixed!")
