// pagination.js
export default class Pagination {
    constructor({ containerId, onPageChange, total = 0, page = 1, perPage = 20 }) {
      this.container = document.getElementById(containerId);
      this.onPageChange = onPageChange;
      this.total = total;
      this.page = page;
      this.perPage = perPage;
  
      this.render();
    }
  
    setTotal(total) {
      this.total = total;
      this.render();
    }
  
    setPage(page) {
      if (page < 1) page = 1;
      if (page > this.totalPages()) page = this.totalPages();
      this.page = page;
      this.render();
      this.onPageChange(this.page);
    }
  
    totalPages() {
      return Math.ceil(this.total / this.perPage) || 1;
    }
  
    render() {
      if (!this.container) return;
      const totalPages = this.totalPages();
  
      this.container.innerHTML = '';
  
      // Previous button
      const prevBtn = document.createElement('button');
      prevBtn.textContent = 'Prev';
      prevBtn.disabled = this.page === 1;
      prevBtn.addEventListener('click', () => this.setPage(this.page - 1));
      this.container.appendChild(prevBtn);
  
      // Page indicator
      const pageIndicator = document.createElement('span');
      pageIndicator.textContent = ` Page ${this.page} of ${totalPages} `;
      this.container.appendChild(pageIndicator);
  
      // Next button
      const nextBtn = document.createElement('button');
      nextBtn.textContent = 'Next';
      nextBtn.disabled = this.page === totalPages;
      nextBtn.addEventListener('click', () => this.setPage(this.page + 1));
      this.container.appendChild(nextBtn);
    }
  }
  