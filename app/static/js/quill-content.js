// quill-python-editor.js

// Initialize Quill editor
const quill = new Quill('#editor', {
    theme: 'snow',
    modules: {
      toolbar: [
        [{ header: [1, 2, 3, false] }],
        ['bold', 'italic', 'underline', 'strike'],
        ['blockquote', 'code-block'],
        [{ list: 'ordered' }, { list: 'bullet' }],
        ['link', 'image'],
        ['clean']
      ]
    },
    placeholder: 'Write your content here...'
  });
  
  // MutationObserver to wrap code blocks with <code class="language-python">
  const editor = document.querySelector('#editor');
  
  const observer = new MutationObserver(() => {
    editor.querySelectorAll('pre.ql-syntax').forEach(pre => {
      if (!pre.querySelector('code')) {
        const code = document.createElement('code');
        code.classList.add('language-python');
        code.innerHTML = pre.innerHTML;
        pre.innerHTML = '';
        pre.appendChild(code);
      }
    });
  });
  
  observer.observe(editor, { childList: true, subtree: true });
  
  // Optional: Expose quill instance and content export
  window.getEditorContent = function () {
    let html = quill.root.innerHTML;
    html = html.replace(/<pre class="ql-syntax"[^>]*>([\s\S]*?)<\/pre>/g,
      (match, code) => `<pre class="ql-syntax"><code class="language-python">${code}</code></pre>`
    );
    return html;
  };
  