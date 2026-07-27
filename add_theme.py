import os
import re

REPO = '/app/data/所有对话/主对话/c-workshop-repo'

LIGHT_CSS = '''[data-theme="light"] {
  --bg: #f0f4ff; --surface: #ffffff; --surface2: #e8edf5; --border: #d0d8e8;
  --accent: #5b4bd4; --accent2: #7c6df0; --green: #00b86b; --cyan: #0099cc;
  --orange: #e67e00; --pink: #d6336c; --red: #d93025; --yellow: #e6a800;
  --text: #1a1d3a; --text-dim: #6b6f8a;
}'''

TOGGLE_BTN = '''<button id="theme-toggle" style="margin-left:auto;background:none;border:1px solid var(--border);border-radius:8px;padding:6px 10px;cursor:pointer;font-size:1rem;color:var(--text-dim);transition:all 0.2s;" onclick="toggleTheme()" title="切换主题">🌙</button>'''

THEME_JS = '''<script>
(function() {
  const key = 'c-workshop-theme';
  const saved = localStorage.getItem(key);
  if (saved === 'light') {
    document.documentElement.setAttribute('data-theme', 'light');
    const btn = document.getElementById('theme-toggle');
    if (btn) btn.textContent = '☀️';
  }
})();
function toggleTheme() {
  const html = document.documentElement;
  const isLight = html.getAttribute('data-theme') === 'light';
  if (isLight) {
    html.removeAttribute('data-theme');
    localStorage.setItem('c-workshop-theme', 'dark');
    document.getElementById('theme-toggle').textContent = '🌙';
  } else {
    html.setAttribute('data-theme', 'light');
    localStorage.setItem('c-workshop-theme', 'light');
    document.getElementById('theme-toggle').textContent = '☀️';
  }
}
</script>'''

files = ['index.html'] + [f'courseware/{f}' for f in sorted(os.listdir(os.path.join(REPO, 'courseware'))) if f.endswith('.html')]

for fname in files:
    fpath = os.path.join(REPO, fname)
    with open(fpath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original = content
    
    # 1. Insert light CSS before </style>
    content = content.replace('</style>', f'{LIGHT_CSS}\n</style>', 1)
    
    # 2. Insert theme toggle button before the closing </div> of top-bar
    # Find the top-bar div and its closing tag
    # Strategy: find the last </div> that closes the top-bar
    # We'll find the opening <div class="top-bar" and then find the matching closing </div>
    
    # Simple approach: find the first top-bar div and insert before its closing </div>
    # The top-bar structure is: <div class="top-bar"> ... </div>
    # We need to find the matching </div> for the top-bar
    
    # Use regex to find the top-bar div and its content
    # Pattern: <div class="top-bar"[^>]*> ... </div>
    # We'll find the opening tag, then track nesting to find the matching close
    
    top_bar_match = re.search(r'<div\s+class="top-bar[^"]*"[^>]*>', content)
    if top_bar_match:
        start = top_bar_match.end()
        # Find the matching closing </div>
        depth = 1
        i = start
        while i < len(content) and depth > 0:
            open_tag = re.search(r'<div\s', content[i:])
            close_tag = re.search(r'</div>', content[i:])
            if open_tag and close_tag:
                if open_tag.start() < close_tag.start():
                    depth += 1
                    i += open_tag.end()
                else:
                    depth -= 1
                    if depth == 0:
                        # Found the matching close
                        insert_pos = i + close_tag.start()
                        content = content[:insert_pos] + '\n  ' + TOGGLE_BTN + '\n' + content[insert_pos:]
                        break
                    i += close_tag.end()
            elif close_tag:
                depth -= 1
                if depth == 0:
                    insert_pos = i + close_tag.start()
                    content = content[:insert_pos] + '\n  ' + TOGGLE_BTN + '\n' + content[insert_pos:]
                    break
                i += close_tag.end()
            elif open_tag:
                depth += 1
                i += open_tag.end()
            else:
                break
    
    # 3. Insert theme JS before </body>
    # Check if there's already a <script> before </body>
    body_close = content.rfind('</body>')
    if body_close > 0:
        # Insert before </body>
        content = content[:body_close] + '\n' + THEME_JS + '\n' + content[body_close:]
    
    if content != original:
        with open(fpath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f'✅ Updated: {fname}')
    else:
        print(f'⚠️  No changes: {fname}')

print('\nDone!')
