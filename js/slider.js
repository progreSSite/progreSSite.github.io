class SimpleSlider {
  constructor(container, options = {}) {
    this.container = document.querySelector(container);
    if (!this.container) return;
    
    this.slides = Array.from(this.container.querySelectorAll('.review'));
    this.currentIndex = 0;
    this.interval = options.interval || 5000;
    this.autoPlay = options.autoPlay !== false;
    this.animationDuration = options.animationDuration || 500;
    
    this.init();
  }
  
  init() {
    // Создаем обертку для слайдов
    this.sliderWrapper = document.createElement('div');
    this.sliderWrapper.className = 'slider-wrapper';
    this.container.prepend(this.sliderWrapper);
    
    // Переносим слайды в обертку
    this.slides.forEach(slide => {
      this.sliderWrapper.appendChild(slide);
      slide.style.transition = `transform ${this.animationDuration}ms ease, opacity ${this.animationDuration}ms ease`;
      slide.style.position = 'absolute';
      slide.style.width = '100%';
      slide.style.left = '0';
      slide.style.top = '0';
    });
    
    // Рассчитываем высоту
    this.calculateMaxHeight();
    
    // Создаем навигационные стрелки
    this.createArrows();
    
    // Показываем первый слайд
    this.showSlide(this.currentIndex);
    
    // Автопрокрутка
    if (this.autoPlay) {
      this.startAutoPlay();
    }
    
    // Обработчики событий
    this.setupEventListeners();
    
    // Ресайз наблюдатель
    this.setupResizeObserver();
  }
  
  calculateMaxHeight() {
    // Временно показываем все слайды для измерения
    const originalDisplay = this.slides.map(slide => {
      const style = slide.style.display;
      slide.style.display = 'block';
      slide.style.opacity = '1';
      slide.style.position = 'relative';
      slide.style.transform = 'none';
      return style;
    });
    
    // Находим максимальную высоту
    this.maxHeight = Math.max(...this.slides.map(slide => slide.offsetHeight));
    this.sliderWrapper.style.height = `${this.maxHeight}px`;
    
    // Возвращаем исходное состояние
    this.slides.forEach((slide, i) => {
      slide.style.display = originalDisplay[i];
      slide.style.position = 'absolute';
      slide.style.opacity = i === this.currentIndex ? '1' : '0';
      slide.style.transform = `translateX(${100 * (i - this.currentIndex)}%)`;
    });
  }
  
  createArrows() {
    this.arrowsContainer = document.createElement('div');
    this.arrowsContainer.className = 'slider-arrows';
    this.sliderWrapper.appendChild(this.arrowsContainer);
    
    // Стрелка "назад"
    this.prevArrow = document.createElement('button');
    this.prevArrow.className = 'slider-arrow slider-arrow--prev';
    this.prevArrow.innerHTML = `
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M15 18L9 12L15 6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
      </svg>
    `;
    
    // Стрелка "вперед"
    this.nextArrow = document.createElement('button');
    this.nextArrow.className = 'slider-arrow slider-arrow--next';
    this.nextArrow.innerHTML = `
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M9 18L15 12L9 6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
      </svg>
    `;
    
    this.arrowsContainer.appendChild(this.prevArrow);
    this.arrowsContainer.appendChild(this.nextArrow);
    
    // Обработчики кликов
    this.prevArrow.addEventListener('click', () => this.prevSlide());
    this.nextArrow.addEventListener('click', () => this.nextSlide());
  }
  
  showSlide(index) {
    this.slides.forEach((slide, i) => {
      slide.style.transform = `translateX(${100 * (i - index)}%)`;
      slide.style.opacity = i === index ? '1' : '0';
      slide.style.zIndex = i === index ? '1' : '0';
    });
  }
  
  nextSlide() {
    this.currentIndex = (this.currentIndex + 1) % this.slides.length;
    this.showSlide(this.currentIndex);
    this.resetAutoPlay();
  }
  
  prevSlide() {
    this.currentIndex = (this.currentIndex - 1 + this.slides.length) % this.slides.length;
    this.showSlide(this.currentIndex);
    this.resetAutoPlay();
  }
  
  startAutoPlay() {
    this.intervalId = setInterval(() => {
      this.nextSlide();
    }, this.interval);
  }
  
  pauseAutoPlay() {
    clearInterval(this.intervalId);
  }
  
  resetAutoPlay() {
    this.pauseAutoPlay();
    if (this.autoPlay) {
      this.startAutoPlay();
    }
  }
  
  setupEventListeners() {
    // Пауза при наведении
    this.sliderWrapper.addEventListener('mouseenter', () => {
      this.pauseAutoPlay();
      this.arrowsContainer.style.opacity = '1';
    });
    
    this.sliderWrapper.addEventListener('mouseleave', () => {
      this.resetAutoPlay();
      this.arrowsContainer.style.opacity = '0';
    });
    
    // Свайпы для мобильных
    let touchStartX = 0;
    let touchEndX = 0;
    
    this.sliderWrapper.addEventListener('touchstart', (e) => {
      touchStartX = e.changedTouches[0].screenX;
    }, {passive: true});
    
    this.sliderWrapper.addEventListener('touchend', (e) => {
      touchEndX = e.changedTouches[0].screenX;
      this.handleSwipe();
    }, {passive: true});
  }
  
  setupResizeObserver() {
    const resizeObserver = new ResizeObserver(() => {
      this.calculateMaxHeight();
    });
    
    this.slides.forEach(slide => {
      resizeObserver.observe(slide);
    });
  }
  
  handleSwipe() {
    const threshold = 50;
    const diff = touchStartX - touchEndX;
    
    if (diff > threshold) {
      this.nextSlide();
    } else if (diff < -threshold) {
      this.prevSlide();
    }
  }
}

// Инициализация
document.addEventListener('DOMContentLoaded', () => {
  new SimpleSlider('.reviews__slider', {
    interval: 10000,
    autoPlay: true,
    animationDuration: 600
  });
});