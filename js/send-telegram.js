// Конфигурация (ЗАМЕНИТЕ значения!)
const BOT_TOKEN = '7763273598:AAFpDkG7beD4ow6nPD6o6-VLncJfbaV0wF0';
const CHAT_ID = '660109551'; // Получите через @userinfobot

// Функция отправки в Telegram (без изменений)
async function sendToTelegram(formData) {
  let message = `📌 Новая заявка\nТип: ${formData.form_type || 'Не указан'}\nИмя: ${formData.name}`;
  
  // Добавляем поля, если они есть в форме
  if (formData.phone) message += `\nТелефон: ${formData.phone}`;
  if (formData.email) message += `\nEmail: ${formData.email}`;
  if (formData.message) message += `\nСообщение: ${formData.message}`;
  if (formData.service) message += `\nУслуга: ${formData.service}`;
  
  const url = `https://api.telegram.org/bot${BOT_TOKEN}/sendMessage`;
  const body = new URLSearchParams();
  body.append('chat_id', CHAT_ID);
  body.append('text', message);
  
  try {
    const img = new Image();
    img.src = `${url}?${body.toString()}`;
    return true;
  } catch (error) {
    console.error('Telegram Error:', error);
    return false;
  }
}

// Обработчик для всех форм
function setupForm(formId, modalId = null) {
  const form = document.getElementById(formId);
  if (!form) return;

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const button = form.querySelector('button[type="submit"]');
    button.disabled = true;
    const originalText = button.textContent;
    button.textContent = 'Отправка...';

    // Собираем данные формы
    const formData = {
      form_type: form.querySelector('[name="form_type"]')?.value || formId,
      name: form.querySelector('[name="name"]')?.value,
      phone: form.querySelector('[name="phone"]')?.value,
      email: form.querySelector('[name="email"]')?.value,
      message: form.querySelector('[name="message"]')?.value,
      service: form.querySelector('[name="service"]')?.value
    };

    try {
      const success = await sendToTelegram(formData);
      if (success) {
        alert('✅ Спасибо! Мы скоро свяжемся с вами.');
        form.reset();
        if (modalId) {
          document.getElementById(modalId)?.classList.remove('active');
          document.body.style.overflow = '';
        }
      } else {
        throw new Error('Не удалось отправить заявку');
      }
    } catch (error) {
      console.error('Form Error:', error);
      alert('⚠️ Ошибка отправки. Позвоните нам напрямую!');
    } finally {
      button.disabled = false;
      button.textContent = originalText;
    }
  });
}

// Инициализация всех форм при загрузке
document.addEventListener('DOMContentLoaded', () => {
  // Существующие формы
  setupForm('consultation-form', 'consultation-modal');
  setupForm('callback-form', 'callback-modal');
  setupForm('contact-form'); // Для формы без модального окна
  
  // Новая форма заказа из блока цен
  setupForm('order-form', 'order-modal');
  
  // Табы для блока цен
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
  
  // Обработка кнопок "Заказать" в карточках цен
  const orderButtons = document.querySelectorAll('[data-modal="order"]');
  const orderModal = document.getElementById('order-modal');
  const serviceName = document.getElementById('service-name');
  const serviceInput = document.getElementById('service-input');
  
  orderButtons.forEach(button => {
    button.addEventListener('click', () => {
      const service = button.getAttribute('data-service');
      serviceName.textContent = service;
      serviceInput.value = service;
      
      // Show modal
      orderModal.classList.add('active');
      document.body.style.overflow = 'hidden';
    });
  });
  
  // Закрытие модальных окон
  const closeButtons = document.querySelectorAll('.modal__close');
  closeButtons.forEach(button => {
    button.addEventListener('click', () => {
      document.querySelectorAll('.modal').forEach(modal => {
        modal.classList.remove('active');
      });
      document.body.style.overflow = '';
    });
  });
  
  // Закрытие при клике вне модального окна
  document.querySelectorAll('.modal').forEach(modal => {
    modal.addEventListener('click', (e) => {
      if (e.target === modal) {
        modal.classList.remove('active');
        document.body.style.overflow = '';
      }
    });
  });
});