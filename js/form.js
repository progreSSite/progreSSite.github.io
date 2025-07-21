class FormHandler {
  constructor(formElement) {
    this.form = formElement;
    this.submitButton = this.form.querySelector('button[type="submit"]');
    this.originalButtonText = this.submitButton.textContent;
    
    this.init();
  }
  
  init() {
    this.form.addEventListener('submit', (e) => this.handleSubmit(e));
    
    // Add input validation
    const inputs = this.form.querySelectorAll('input, textarea');
    inputs.forEach(input => {
      input.addEventListener('input', () => {
        this.validateInput(input);
      });
    });
  }
  
  validateInput(input) {
    if (input.required && !input.value.trim()) {
      input.classList.add('invalid');
      return false;
    }
    
    if (input.type === 'email' && !this.validateEmail(input.value)) {
      input.classList.add('invalid');
      return false;
    }
    
    input.classList.remove('invalid');
    return true;
  }
  
  validateEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
  }
  
  async handleSubmit(e) {
    e.preventDefault();
    
    // Validate all inputs
    let isValid = true;
    const inputs = this.form.querySelectorAll('input, textarea');
    inputs.forEach(input => {
      if (!this.validateInput(input)) {
        isValid = false;
      }
    });
    
    if (!isValid) return;
    
    // Show loading state
    this.submitButton.disabled = true;
    this.submitButton.textContent = 'Отправка...';
    
    try {
      const formData = new FormData(this.form);
      
      // Simulate API call (replace with actual fetch)
      await new Promise(resolve => setTimeout(resolve, 1500));
      
      // Show success
      this.submitButton.textContent = 'Отправлено!';
      
      // Reset form after delay
      setTimeout(() => {
        this.form.reset();
        this.submitButton.textContent = this.originalButtonText;
        this.submitButton.disabled = false;
      }, 1500);
    } catch (error) {
      console.error('Error:', error);
      this.submitButton.textContent = 'Ошибка';
      setTimeout(() => {
        this.submitButton.textContent = this.originalButtonText;
        this.submitButton.disabled = false;
      }, 1500);
    }
  }
}

// Initialize all forms
document.addEventListener('DOMContentLoaded', () => {
  const forms = document.querySelectorAll('.form');
  forms.forEach(form => {
    new FormHandler(form);
  });
});