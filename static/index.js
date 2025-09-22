const observer = new IntersectionObserver((entries) => {
    entries.forEach((entry) =>{
        console.log(entry) 
        if (entry.isIntersecting) {
            entry.target.classList.add('show');
        } else {
            entry.target.classList.remove('show');
        }
    });
});

const hiddenElements = document.querySelectorAll('.hidden');
hiddenElements.forEach((el) => observer.observe(el));


const scrollers = document.querySelectorAll(".scroller");

if (!window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
    addAnimation();
}

function addAnimation() {
    scrollers.forEach((scroller) => {
        scroller.setAttribute("data-animated", true);
    
        const scrollerInner = scroller.querySelector('.scroller_inner');
        const scrollerContent = Array.from(scrollerInner.children);
        
        scrollerContent.forEach(item => {
            const duplicatedItem = item.cloneNode(true);
            duplicatedItem.setAttribute('aria-hidden', true);
            scrollerInner.appendChild(duplicatedItem);

        })
    }); 
}

/* === Contact form submit handler === */
(function(){
  const form = document.getElementById('contact-form');
  if (!form) return;

  const statusEl = document.getElementById('form-status');
  const submitBtn = document.getElementById('contact-submit');

  form.addEventListener('submit', async (e) => {
    e.preventDefault();

    const data = {
      name: form.elements.name.value.trim(),
      email: form.elements.email.value.trim(),
      phone: form.elements.phone.value.trim(),
      subject: form.elements.subject.value.trim(),
      message: form.elements.message.value.trim(),
      _gotcha: form.elements._gotcha.value.trim()
    };

    if (!data.name || !data.email || !data.subject || !data.message) {
      statusEl.textContent = 'Please fill out name, email, subject, and message.';
      return;
    }

    statusEl.textContent = 'Sending...';
    submitBtn.disabled = true;

    try {
      const res = await fetch('/api/contact', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
        credentials: 'same-origin'
      });

      if (res.ok) {
        form.reset();
        statusEl.textContent = 'Thanks! Your message was sent.';
      } else {
        const err = await res.json().catch(() => ({}));
        statusEl.textContent = err?.error?.message || 'Could not send your message.';
      }
    } catch (err) {
      statusEl.textContent = 'Network error—please try again.';
    } finally {
      submitBtn.disabled = false;
    }
  });
})();