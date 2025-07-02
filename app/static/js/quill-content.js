// Initialize Quill editor with custom toolbar and handlers
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
        [{ 'custom-block': ['note', 'tip', 'warning'] }], // Custom alert blocks
        ['clean']
      ],
      handlers: {
        // Handler for inserting custom alert blocks
        'custom-block': function (value) {
          if (!value) return;
          const range = quill.getSelection();
          if (!range) return;

          // Prepare content: either selected text or default placeholder
          const content = range.length > 0
            ? quill.getText(range.index, range.length)
            : `${value.charAt(0).toUpperCase() + value.slice(1)}: Your message here...`;

          // If there is selected text, delete it first
          if (range.length > 0) {
            quill.deleteText(range.index, range.length, Quill.sources.USER);
          }

          // Insert the custom alert embed at the current cursor position
          quill.insertEmbed(range.index, 'custom-alert', { type: value, content }, Quill.sources.USER);

          // Move cursor right after the inserted blot
          quill.setSelection(range.index + 1, Quill.sources.USER);
        }
      }
    }
  },
  placeholder: 'Write your content here...'
});

// Define the custom alert blot extending BlockEmbed to allow block-level custom alerts
const BlockEmbed = Quill.import('blots/block/embed');

class CustomAlert extends BlockEmbed {
  static create(value) {
    const node = super.create();

    // Assign CSS classes for styling (alert + alert type)
    node.classList.add('alert', value.type);

    // Make alert content editable by the user
    node.setAttribute('contenteditable', 'true');

    // Set content, replacing line breaks with <br> for HTML
    node.innerHTML = value.content
      ? value.content.replace(/\n/g, '<br>')
      : `${value.type.charAt(0).toUpperCase() + value.type.slice(1)}: Your message here...`;

    return node;
  }

  static value(node) {
    // Detect alert type by CSS class
    const type = ['note', 'tip', 'warning'].find(cls => node.classList.contains(cls)) || '';

    // Return content with <br> replaced back to newlines
    const content = node.innerHTML.replace(/<br\s*\/?>/gi, '\n');

    return { type, content };
  }
}

CustomAlert.blotName = 'custom-alert';
CustomAlert.tagName = 'div';
CustomAlert.className = 'alert';

Quill.register(CustomAlert);

// Handle Enter key inside alert blocks to insert a newline instead of creating a new block
quill.root.addEventListener('keydown', (e) => {
  if (e.key !== 'Enter') return;

  const selection = quill.getSelection();
  if (!selection) return;

  // Get the blot (block) where the cursor is
  const [blot] = quill.getLine(selection.index);
  if (blot?.domNode?.classList.contains('alert')) {
    e.preventDefault();
    // Insert a newline at current cursor position within the alert
    quill.insertText(selection.index, '\n', Quill.sources.USER);
    // Move cursor forward after inserted newline
    quill.setSelection(selection.index + 1, Quill.sources.SILENT);
  }
});

// Utility to get sanitized editor content:
// Transforms Quill's multi-div code blocks into single <pre><code> blocks for syntax highlighting
window.getEditorContent = function () {
  const container = document.createElement('div');
  container.innerHTML = quill.root.innerHTML;

  // Find and transform Quill code block containers
  container.querySelectorAll('div.ql-code-block-container').forEach(containerEl => {
    const lines = Array.from(containerEl.querySelectorAll('div.ql-code-block'))
      .map(div => div.textContent);
    const codeText = lines.join('\n');

    const pre = document.createElement('pre');
    pre.classList.add('ql-code-block-container');

    const code = document.createElement('code');
    code.classList.add('language-python'); // TODO: dynamically detect language if needed
    code.textContent = codeText;

    pre.appendChild(code);
    containerEl.replaceWith(pre);
  });

  return container.innerHTML;
};

// Disable editing on all alert blocks to prevent accidental modification after insertion
function disableAllAlerts() {
  document.querySelectorAll('.alert').forEach(el => {
    el.setAttribute('contenteditable', 'false');
  });
}

// Disable alert editing after every text change to keep alerts stable
quill.on('text-change', disableAllAlerts);

// Disable alert editing initially
disableAllAlerts();
