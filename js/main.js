// Main JavaScript for the website (2025)

document.addEventListener('DOMContentLoaded', function() {
  // Mobile menu toggle
  const navToggle = document.querySelector('.nav__toggle');
  const navList = document.querySelector('.nav__list');
  
  if (navToggle && navList) {
    navToggle.addEventListener('click', function() {
      navToggle.classList.toggle('active');
      navList.classList.toggle('active');
      document.body.classList.toggle('no-scroll');
    });
  }

  // Close mobile menu when clicking on a link
  const navLinks = document.querySelectorAll('.nav__link');
  navLinks.forEach(link => {
    link.addEventListener('click', function() {
      if (navList.classList.contains('active')) {
        navToggle.classList.remove('active');
        navList.classList.remove('active');
        document.body.classList.remove('no-scroll');
      }
    });
  });

  // Modal functionality
  const modalTriggers = document.querySelectorAll('[data-modal]');
  const modals = document.querySelectorAll('.modal');
  const modalCloseButtons = document.querySelectorAll('.modal__close');
  
  // Open modal
  modalTriggers.forEach(trigger => {
    trigger.addEventListener('click', function() {
      const modalId = this.getAttribute('data-modal');
      const modal = document.getElementById(`${modalId}-modal`);
      
      if (modal) {
        modal.classList.add('active');
        document.body.classList.add('no-scroll');
      }
    });
  });
  
  // Close modal
  function closeModal(modal) {
    modal.classList.remove('active');
    document.body.classList.remove('no-scroll');
  }
  
  modalCloseButtons.forEach(button => {
    button.addEventListener('click', function() {
      const modal = this.closest('.modal');
      closeModal(modal);
    });
  });
  
  // Close modal when clicking outside
  modals.forEach(modal => {
    modal.addEventListener('click', function(e) {
      if (e.target === this) {
        closeModal(modal);
      }
    });
  });
  
  // Close modal with Escape key
  document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
      modals.forEach(modal => {
        if (modal.classList.contains('active')) {
          closeModal(modal);
        }
      });
    }
  });

  // Form submission with Fetch API
  const forms = document.querySelectorAll('.form');
  
  forms.forEach(form => {
    form.addEventListener('submit', async function(e) {
      e.preventDefault();
      
      const formData = new FormData(this);
      const submitButton = this.querySelector('button[type="submit"]');
      const originalButtonText = submitButton.textContent;
      
      // Show loading state
      submitButton.disabled = true;
      submitButton.textContent = 'Отправка...';
      
      try {
        // Simulate API call (replace with actual fetch)
        await new Promise(resolve => setTimeout(resolve, 1500));
        
        // Show success message
        submitButton.textContent = 'Отправлено!';
        
        // Reset form
        setTimeout(() => {
          this.reset();
          submitButton.textContent = originalButtonText;
          submitButton.disabled = false;
          
          // Close modal if form is in modal
          const modal = this.closest('.modal');
          if (modal) {
            closeModal(modal);
          }
        }, 1500);
      } catch (error) {
        console.error('Error:', error);
        submitButton.textContent = 'Ошибка';
        setTimeout(() => {
          submitButton.textContent = originalButtonText;
          submitButton.disabled = false;
        }, 1500);
      }
    });
  });

  // Smooth scrolling for anchor links
  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
      e.preventDefault();
      
      const targetId = this.getAttribute('href');
      if (targetId === '#') return;
      
      const targetElement = document.querySelector(targetId);
      if (targetElement) {
        const headerHeight = document.querySelector('.header').offsetHeight;
        const targetPosition = targetElement.getBoundingClientRect().top + window.pageYOffset - headerHeight;
        
        window.scrollTo({
          top: targetPosition,
          behavior: 'smooth'
        });
      }
    });
  });

  // Intersection Observer for animations
  const animateOnScroll = function() {
    const elements = document.querySelectorAll('.service-card, .portfolio-item, .advantage');
    
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('animate');
          observer.unobserve(entry.target);
        }
      });
    }, {
      threshold: 0.1
    });
    
    elements.forEach(element => {
      observer.observe(element);
    });
  };
  
  // Initialize animations
  animateOnScroll();
  
  // Add class to header on scroll
  const header = document.querySelector('.header');
  if (header) {
    window.addEventListener('scroll', function() {
      if (window.scrollY > 100) {
        header.classList.add('scrolled');
      } else {
        header.classList.remove('scrolled');
      }
    });
  }
});


// JavaScript for Tabs and Modal
document.addEventListener('DOMContentLoaded', function() {
  // Tab switching
  const tabs = document.querySelectorAll('.pricing__tab');
  const contents = document.querySelectorAll('.pricing__content');
  
  tabs.forEach(tab => {
    tab.addEventListener('click', () => {
      // Remove active class from all tabs and contents
      tabs.forEach(t => t.classList.remove('active'));
      contents.forEach(c => c.classList.remove('active'));
      
      // Add active class to clicked tab
      tab.classList.add('active');
      
      // Show corresponding content
      const tabId = tab.getAttribute('data-tab');
      document.getElementById(`${tabId}-tab`).classList.add('active');
    });
  });
});