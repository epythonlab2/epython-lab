function initializeAllQuillEditors() {
  const editors = {};

  document.querySelectorAll('.quill-wrapper').forEach((wrapper, index) => {
    const editorEl = wrapper.querySelector('.editor');
    const inputEl = wrapper.querySelector('input[type="hidden"]');

    if (!editorEl || !inputEl) return;

    if (!editorEl.id) {
      editorEl.id = `editor-${index}`;
    }

    const quill = new Quill(editorEl, {
      theme: 'snow',
      modules: {
        // Remove syntax module to disable syntax highlighting
        // syntax: true,
        toolbar: [
          [{ header: [1, 2, 3, false] }],
          ['bold', 'italic', 'underline', 'strike'],
          ['blockquote', 'code-block'],  // You can keep or remove 'code-block' here if you want
          [{ list: 'ordered' }, { list: 'bullet' }],
          ['link', 'image'],
          ['clean']
        ]
      },
      placeholder: 'Write your content here...'
    });

    editors[editorEl.id] = quill;

    // Remove syntax highlighting calls completely

    quill.on('text-change', () => {
      inputEl.value = quill.root.innerHTML.trim();
    });
  });

  return editors;
}

window.initializeAllQuillEditors = initializeAllQuillEditors;
