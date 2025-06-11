// Initialize Quill editor
const quill = new Quill('#editor', {
  theme: 'snow',
  modules: {
    toolbar: {
      container: [
        [{ header: [1, 2, 3, false] }],
        ['bold', 'italic', 'underline', 'strike'],
        ['blockquote', 'code-block'],
        [{ list: 'ordered' }, { list: 'bullet' }],
        ['link', 'image'],
        [{ 'custom-block': ['note', 'tip', 'warning'] }],
        ['clean']
      ],
      handlers: {
        'custom-block': function (value) {
          if (!value) return;
          const range = quill.getSelection();
          if (!range) return;

          if (range.length > 0) {
            const selectedText = quill.getText(range.index, range.length);
            quill.deleteText(range.index, range.length);

            quill.insertEmbed(range.index, 'custom-alert', {
              type: value,
              content: selectedText
            }, Quill.sources.USER);

            quill.setSelection(range.index + 1);
          } else {
            quill.insertEmbed(range.index, 'custom-alert', {
              type: value,
              content: `${value.charAt(0).toUpperCase() + value.slice(1)}: Your message here...`
            }, Quill.sources.USER);
            quill.setSelection(range.index + 1);
          }
        }
      }
    }
  },
  placeholder: 'Write your content here...'
});

// Define custom alert blot (multi-line support)
const BlockEmbed = Quill.import('blots/block/embed');

class CustomAlert extends BlockEmbed {
  static create(value) {
    const node = super.create();
    node.setAttribute('class', `alert ${value.type}`);
    node.setAttribute('contenteditable', 'true');
    node.innerHTML = value.content
      ? value.content.replace(/\n/g, '<br>')
      : `${value.type.charAt(0).toUpperCase() + value.type.slice(1)}: Your message here...`;
    return node;
  }

  static value(node) {
    return {
      type: node.classList.contains('note') ? 'note' :
            node.classList.contains('tip') ? 'tip' :
            node.classList.contains('warning') ? 'warning' : '',
      content: node.innerHTML.replace(/<br\s*\/?>/g, '\n')
    };
  }
}

CustomAlert.blotName = 'custom-alert';
CustomAlert.tagName = 'div';
CustomAlert.className = 'alert';

Quill.register(CustomAlert);

// Handle Enter key inside custom alerts (insert line break)
quill.root.addEventListener('keydown', function (e) {
  const selection = quill.getSelection();
  if (!selection) return;

  const [blot] = quill.getLine(selection.index);
  if (blot && blot.domNode && blot.domNode.classList.contains('alert')) {
    if (e.key === 'Enter') {
      e.preventDefault();
      const range = quill.getSelection();
      if (range) {
        quill.insertText(range.index, '\n', Quill.sources.USER);
        quill.setSelection(range.index + 1, Quill.sources.SILENT);
      }
    }
  }
});

// Enhance code blocks with <code> tag
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

// Export content as HTML
window.getEditorContent = function () {
  let html = quill.root.innerHTML;
  html = html.replace(/<pre class="ql-syntax"[^>]*>([\s\S]*?)<\/pre>/g,
    (match, code) => `<pre class="ql-syntax"><code class="language-python">${code}</code></pre>`
  );
  return html;
};

function disableAllAlerts() {
  document.querySelectorAll('.alert').forEach(el => {
    el.setAttribute('contenteditable', 'false');
  });
}

quill.on('text-change', () => {
  disableAllAlerts();
});

// Also call once after initialization
disableAllAlerts();
