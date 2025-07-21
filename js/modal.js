class Modal {
  constructor(options) {
    this.modalId = options.id;
    this.modalElement = document.getElementById(this.modalId);
    this.openTriggers = document.querySelectorAll(`[data-modal="${this.modalId}"]`);
    this.closeButtons = this.modalElement.querySelectorAll('.modal__close');
    
    if (!this.modalElement) return;
    
    this.init();
  }
  
  init() {
    // Open modal
    this.openTriggers.forEach(trigger => {
      trigger.addEventListener('click', () => this.open());
    });
    
    // Close modal
    this.closeButtons.forEach(button => {
      button.addEventListener('click', () => this.close());
    });
    
    // Close when clicking outside
    this.modalElement.addEventListener('click', (e) => {
      if (e.target === this.modalElement) {
        this.close();
      }
    });
    
    // Close with Escape key
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && this.modalElement.classList.contains('active')) {
        this.close();
      }
    });
  }
  
  open() {
    this.modalElement.classList.add('active');
    document.body.classList.add('no-scroll');
  }
  
  close() {
    this.modalElement.classList.remove('active');
    document.body.classList.remove('no-scroll');
  }
}

// Initialize modals
document.addEventListener('DOMContentLoaded', () => {
  const modals = document.querySelectorAll('.modal');
  modals.forEach(modal => {
    new Modal({
      id: modal.id
    });
  });
});