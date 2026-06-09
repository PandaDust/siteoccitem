(function () {
  'use strict';

  let content = null;
  let currentLang = 'fr';

  // ============================================================
  // INIT
  // ============================================================
  initPhotoCarousel(); // images statiques — pas besoin d'attendre content.json

  fetch('content.json')
    .then(r => r.json())
    .then(data => {
      content = data;
      initScrollReveal();   // observer doit exister avant render()
      render(currentLang);
      initNavScroll();
      initNavActive();
      initBurger();
      initLangSwitch();
      initHeroSnap();
    })
    .catch(err => console.error('Impossible de charger content.json', err));

  // ============================================================
  // RENDER — injecte les textes dans le DOM
  // ============================================================
  function render(lang) {
    // Textes simples via data-key
    document.querySelectorAll('[data-key]').forEach(el => {
      const keys = el.getAttribute('data-key').split('.');
      const section = keys[0];
      const key = keys[1];
      if (content[section] && content[section][lang] && content[section][lang][key] !== undefined) {
        el.textContent = content[section][lang][key];
      }
    });

    // Langue sur <html>
    document.documentElement.lang = lang;

    // Bouton langue
    const btn = document.getElementById('langSwitch');
    if (btn) btn.textContent = lang === 'fr' ? 'EN' : 'FR';

    // Sections dynamiques
    renderTechAdvantages(lang);
    renderServices(lang);
    renderMarkets(lang);
    renderTrust(lang);
    renderContact(lang);
  }

  // ============================================================
  // TECH — grille des 6 avantages
  // ============================================================
  function renderTechAdvantages(lang) {
    const grid = document.getElementById('techAdvantages');
    if (!grid || !content.tech) return;
    const items = content.tech[lang].advantages;
    grid.innerHTML = items.map((item, i) => `
      <div class="tech__card reveal${i >= 3 ? ' reveal--delay-1' : ''}" data-counter-target="${item.value}">
        <div class="tech__card-value" data-counter="${item.value}">
          <span class="counter-display">${item.value}</span>
        </div>
        <div class="tech__card-label">${item.label}</div>
        <div class="tech__card-desc">${item.desc}</div>
      </div>
    `).join('');
    // Ré-observer les nouvelles cartes
    grid.querySelectorAll('.reveal').forEach(el => observer.observe(el));
  }

  // ============================================================
  // SERVICES — 3 cartes + liste
  // ============================================================
  function renderServices(lang) {
    const grid = document.getElementById('servicesGrid');
    const list = document.getElementById('servicesExtra');
    if (!grid || !content.services) return;
    const items = content.services[lang].items;
    grid.innerHTML = items.map((item, i) => `
      <div class="service-card reveal reveal--delay-${i}">
        <img class="service-card__img" src="${item.img}" alt="${item.title}">
        <div class="service-card__body">
          <div class="service-card__title">${item.title}</div>
          <div class="service-card__desc">${item.desc}</div>
        </div>
      </div>
    `).join('');
    if (list) {
      const extras = content.services[lang].extra;
      list.innerHTML = extras.map(e => `<li>${e}</li>`).join('');
    }
    grid.querySelectorAll('.reveal').forEach(el => observer.observe(el));
  }

  // ============================================================
  // MARCHÉS — 3 cartes
  // ============================================================
  function renderMarkets(lang) {
    const grid = document.getElementById('marketsGrid');
    if (!grid || !content.markets) return;
    const items = content.markets[lang].items;
    grid.innerHTML = items.map((item, i) => `
      <div class="market-card reveal reveal--delay-${i}">
        <img class="market-card__img" src="${item.img}" alt="${item.title}">
        <div class="market-card__title">${item.title}</div>
        <div class="market-card__desc">${item.desc}</div>
      </div>
    `).join('');
    grid.querySelectorAll('.reveal').forEach(el => observer.observe(el));
  }

  // ============================================================
  // TRUST — grille logos partenaires
  // ============================================================
  function renderTrust(lang) {
    const grid = document.getElementById('trustGrid');
    if (!grid || !content.trust) return;
    const partners = content.trust[lang].partners;
    grid.innerHTML = partners.map((p, i) => `
      <div class="trust-card reveal reveal--delay-${i % 4}">
        <img src="${p.img}" alt="${p.name}" title="${p.name}">
      </div>
    `).join('');
    grid.querySelectorAll('.reveal').forEach(el => observer.observe(el));
  }

  // ============================================================
  // CONTACT — 2 cartes
  // ============================================================
  function renderContact(lang) {
    const grid = document.getElementById('contactGrid');
    if (!grid || !content.contact) return;
    const contacts = content.contact[lang].contacts;
    grid.innerHTML = contacts.map((c, i) => `
      <div class="contact-card reveal reveal--delay-${i}">
        <div class="contact-card__name">${c.name}</div>
        <div class="contact-card__role">${c.role}</div>
        <div class="contact-card__links">
          <a class="contact-card__link" href="mailto:${c.email}">
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect width="20" height="16" x="2" y="4" rx="2"/><path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7"/></svg>
            ${c.email}
          </a>
          <a class="contact-card__link" href="tel:${c.phone.replace(/\s|\(0\)/g, '')}">
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07A19.5 19.5 0 0 1 4.69 13a19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 3.6 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"/></svg>
            ${c.phone}
          </a>
        </div>
      </div>
    `).join('');
    grid.querySelectorAll('.reveal').forEach(el => observer.observe(el));
  }

  // ============================================================
  // DIAPORAMA PHOTOS — section À propos
  // ============================================================
  function initPhotoCarousel() {
    const photos = Array.from(document.querySelectorAll('.about__photo'));
    if (photos.length < 2) return;

    let current = 0;
    photos[0].classList.add('is-active');

    setInterval(() => {
      photos[current].classList.remove('is-active');
      current = (current + 1) % photos.length;
      photos[current].classList.add('is-active');
    }, 4000);
  }

  // ============================================================
  // SCROLL REVEAL — IntersectionObserver
  // ============================================================
  let observer;

  function initScrollReveal() {
    observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('is-visible');
          observer.unobserve(entry.target);
          // Déclenche les compteurs si la carte en a un
          if (entry.target.dataset.counterTarget) {
            animateCounter(entry.target);
          }
        }
      });
    }, { threshold: 0.12 });

    document.querySelectorAll('.reveal').forEach(el => observer.observe(el));
  }

  // ============================================================
  // COMPTEURS ANIMÉS
  // ============================================================
  function animateCounter(card) {
    const display = card.querySelector('.counter-display');
    if (!display) return;
    const raw = card.dataset.counterTarget;

    // Extrait le chiffre et le préfixe/suffixe
    const match = raw.match(/^([+\-<>]?)(\d+)(.*)$/);
    if (!match) return;
    const prefix = match[1] || '';
    const target = parseInt(match[2], 10);
    const suffix = match[3] || '';

    const duration = 1400;
    const start = performance.now();

    function step(now) {
      const elapsed = now - start;
      const progress = Math.min(elapsed / duration, 1);
      const ease = 1 - Math.pow(1 - progress, 3);
      const current = Math.round(ease * target);
      display.textContent = prefix + current + suffix;
      if (progress < 1) requestAnimationFrame(step);
    }
    requestAnimationFrame(step);
  }

  // ============================================================
  // HERO SNAP — snap vers le haut ou la section suivante
  // ============================================================
  function scrollTo(target, duration) {
    const start = window.scrollY;
    const delta = target - start;
    const startTime = performance.now();

    function easeOutExpo(t) {
      return t === 1 ? 1 : 1 - Math.pow(2, -10 * t);
    }

    function step(now) {
      const elapsed = now - startTime;
      const progress = Math.min(elapsed / duration, 1);
      window.scrollTo(0, start + delta * easeOutExpo(progress));
      if (progress < 1) requestAnimationFrame(step);
    }
    requestAnimationFrame(step);
  }

  function initHeroSnap() {
    const hero = document.getElementById('accueil');
    if (!hero) return;

    let snapTimer = null;
    let isSnapping = false;

    window.addEventListener('scroll', () => {
      if (isSnapping) return;

      const heroHeight = hero.offsetHeight;
      const scrollY = window.scrollY;

      if (scrollY <= 0 || scrollY >= heroHeight) return;

      clearTimeout(snapTimer);
      snapTimer = setTimeout(() => {
        const currentY = window.scrollY;
        if (currentY < heroHeight * 0.5 || currentY >= heroHeight) return;
        isSnapping = true;
        const target = heroHeight;
        scrollTo(target, 750);
        setTimeout(() => { isSnapping = false; }, 800);
      }, 150);
    }, { passive: true });
  }

  // ============================================================
  // NAV — fond au scroll
  // ============================================================
  function initNavScroll() {
    const nav = document.getElementById('nav');
    if (!nav) return;
    window.addEventListener('scroll', () => {
      nav.classList.toggle('scrolled', window.scrollY > 60);
    }, { passive: true });
  }

  // ============================================================
  // NAV — lien actif selon section visible
  // ============================================================
  function initNavActive() {
    const sections = document.querySelectorAll('section[id]');
    const links = document.querySelectorAll('.nav__links a[href^="#"]');

    const sectionObserver = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          links.forEach(l => l.classList.remove('active'));
          const active = document.querySelector(`.nav__links a[href="#${entry.target.id}"]`);
          if (active) active.classList.add('active');
        }
      });
    }, { rootMargin: '-40% 0px -55% 0px' });

    sections.forEach(s => sectionObserver.observe(s));
  }

  // ============================================================
  // BURGER MENU mobile
  // ============================================================
  function initBurger() {
    const burger = document.getElementById('navBurger');
    const links = document.querySelector('.nav__links');
    if (!burger || !links) return;

    burger.addEventListener('click', () => {
      const open = links.classList.toggle('open');
      burger.setAttribute('aria-expanded', open);
    });

    links.querySelectorAll('a').forEach(a => {
      a.addEventListener('click', () => links.classList.remove('open'));
    });
  }

  // ============================================================
  // SWITCH LANGUE
  // ============================================================
  function initLangSwitch() {
    const btn = document.getElementById('langSwitch');
    if (!btn) return;
    btn.addEventListener('click', () => {
      currentLang = currentLang === 'fr' ? 'en' : 'fr';
      render(currentLang);
      // Ré-observer les éléments dynamiquement générés (déjà visibles → forcer is-visible)
      document.querySelectorAll('.reveal:not(.is-visible)').forEach(el => observer.observe(el));
    });
  }

})();
