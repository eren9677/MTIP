import webbrowser
import os

md_file = "user_manual.md"
html_file = "user_manual.html"

# Convert markdown to HTML using external library (marked.js)
with open(md_file, "r") as f:
    text = f.read()

html_content = f"""
<html>
<head>
  <meta charset="utf-8">
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/github-markdown-css/5.5.1/github-markdown-light.min.css">
  <style>
    body {{
      background: #f9f9f9;
      display: flex;
      justify-content: center;
    }}
    .markdown-body {{
      font-family: "Times New Roman", Times, serif;
      box-shadow: 0 2px 8px rgba(0,0,0,0.1);
      border-radius: 8px;
      background: #fff;
      padding: 40px;
      margin: 40px;
      max-width: 900px;
      width: 100%;
    }}
    .markdown-body * {{
      font-family: "Times New Roman", Times, serif !important;
    }}
  </style>
</head>
<body>
  <article id="content" class="markdown-body"></article>
  <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
  <script>
    document.getElementById('content').innerHTML = marked.parse({text!r});
  </script>
</body>
</html>
"""

with open(html_file, "w") as f:
    f.write(html_content)

# Open the HTML file in the default browser
webbrowser.open('file://' + os.path.realpath(html_file))
print("HTML file opened in your browser. Use 'Print' > 'Save as PDF' to create the PDF.")