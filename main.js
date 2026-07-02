(function () {
  'use strict';

  let content = null;
  let currentLang = 'fr';
  let careersData = null;
  let currentOffers = [];
  let lastFocusedEl = null;

  // ============================================================
  // INIT
  // ============================================================
  initPhotoCarousel(); // images statiques — pas besoin d'attendre content.json

  fetch('content.json', { cache: 'no-cache' })
    .then(r => r.json())
    .then(data => {
      content = data;
      initScrollReveal();   // observer doit exister avant render()
      render(currentLang);
      initNavScroll();
      initNavActive();
      initBurger();
      initLangSwitch();
      // initHeroSnap();

      if (document.getElementById('careersGrid')) {
        initOfferModal();
        fetch('careers.json', { cache: 'no-cache' })
          .then(r => r.json())
          .then(data => { careersData = data; renderCareers(currentLang); })
          .catch(err => console.error('Impossible de charger careers.json', err));
      }
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
    renderHistory(lang);
    renderTechAdvantages(lang);
    renderServices(lang);
    renderMarkets(lang);
    renderTrust(lang);
    renderSupporters(lang);
    renderContact(lang);
    renderCareers(lang);
  }

  // ============================================================
  // HISTOIRE — frise verticale alternée
  // ============================================================
  function renderHistory(lang) {
    const timeline = document.getElementById('timeline');
    if (!timeline || !content.history) return;
    const items = content.history[lang].items;
    timeline.innerHTML = items.map((item, i) => `
      <div class="timeline__item timeline__item--${i % 2 === 0 ? 'left' : 'right'} reveal">
        <div class="timeline__node"></div>
        <div class="timeline__year">${item.year}</div>
        <div class="timeline__card">
          <ul class="timeline__events">
            ${item.events.map(e => `<li>${e}</li>`).join('')}
          </ul>
        </div>
      </div>
    `).join('');
    timeline.querySelectorAll('.reveal').forEach(el => observer.observe(el));
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
    const flipLabel = lang === 'fr' ? 'Voir le produit associé' : 'View associated product';
    grid.innerHTML = items.map((item, i) => `
      <div class="market-card reveal reveal--delay-${i}">
        <button type="button" class="market-card__flip-trigger" aria-expanded="false" aria-label="${flipLabel} — ${item.title}">
          <div class="market-card__inner">
            <div class="market-card__face market-card__face--front">
              <img class="market-card__bg" src="${item.img}" alt="${item.title}">
              <div class="market-card__overlay"></div>
              <div class="market-card__label">${item.title}</div>
              <div class="market-card__content">
                <div class="market-card__metric">${item.metric}</div>
                <div class="market-card__desc">${item.desc}</div>
              </div>
              <svg class="market-card__flip-hint" xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 2v6h-6"/><path d="M3 12a9 9 0 0 1 15-6.7L21 8"/><path d="M3 22v-6h6"/><path d="M21 12a9 9 0 0 1-15 6.7L3 16"/></svg>
            </div>
            <div class="market-card__face market-card__face--back">
              <img class="market-card__bg" src="${item.product_img}" alt="${item.title}">
              <div class="market-card__overlay"></div>
              <div class="market-card__label">${item.title}</div>
              <div class="market-card__content">
                <div class="market-card__desc market-card__desc--product">${item.product_desc}</div>
              </div>
            </div>
          </div>
        </button>
      </div>
    `).join('');
    grid.querySelectorAll('.reveal').forEach(el => observer.observe(el));

    if (!grid.dataset.flipBound) {
      grid.dataset.flipBound = 'true';
      grid.addEventListener('click', e => {
        const trigger = e.target.closest('.market-card__flip-trigger');
        if (!trigger) return;
        const card = trigger.closest('.market-card');
        const flipped = card.classList.toggle('is-flipped');
        trigger.setAttribute('aria-expanded', String(flipped));
      });
    }
  }

  // ============================================================
  // TRUST — grille logos partenaires
  // ============================================================
  function renderTrust(lang) {
    const grid = document.getElementById('trustGrid');
    if (!grid || !content.trust) return;
    const partners = content.trust[lang].partners;
    const cards = partners.map(p => `
      <div class="trust-card">
        <img src="${p.img}" alt="${p.name}" title="${p.name}">
      </div>
    `).join('');
    grid.innerHTML = `<div class="trust__track">${cards}${cards}</div>`;
  }

  // ============================================================
  // SUPPORTERS — bandeau logos partenaires institutionnels
  // ============================================================
  function renderSupporters(lang) {
    const grid = document.getElementById('supportersGrid');
    if (!grid || !content.supporters) return;
    const partners = content.supporters[lang].partners;
    const cards = partners.map(p => `
      <div class="trust-card${p.color ? ' trust-card--color' : ''}">
        <img src="${p.img}" alt="${p.name}" title="${p.name}">
      </div>
    `).join('');
    grid.innerHTML = `<div class="trust__track">${cards}${cards}</div>`;
  }

  // ============================================================
  // CONTACT — e-mail unique
  // ============================================================
  function renderContact(lang) {
    const link = document.getElementById('contactEmail');
    if (!link || !content.contact) return;
    const email = content.contact[lang].email;
    link.textContent = email;
    link.href = `mailto:${email}`;
  }

  // ============================================================
  // CARRIÈRES — liste des offres d'emploi (page carriere.html)
  // ============================================================
  function renderCareers(lang) {
    const grid = document.getElementById('careersGrid');
    const introEl = document.getElementById('careersIntro');
    if (!grid || !careersData || !content.careers) return;
    const t = content.careers[lang];

    if (introEl) {
      const hasIntro = Boolean(careersData.intro_title || careersData.intro_text);
      introEl.hidden = !hasIntro;
      introEl.innerHTML = hasIntro ? `
        <div class="careers__intro-col">
          ${careersData.intro_title ? `<h2 class="careers__intro-title">${careersData.intro_title}</h2>` : ''}
          <div class="careers__intro-text">${formatDescription(careersData.intro_text || '')}</div>
        </div>
        ${careersData.intro_img ? `<img class="careers__intro-img" src="${careersData.intro_img}" alt="">` : ''}
      ` : '';
    }

    currentOffers = (careersData.offers || []).filter(o => o.active);

    if (!currentOffers.length) {
      grid.innerHTML = `<p class="careers__empty reveal">${t.empty_message}</p>`;
      grid.querySelectorAll('.reveal').forEach(el => observer.observe(el));
      return;
    }

    grid.innerHTML = currentOffers.map((o, i) => `
      <button type="button" class="career-card reveal reveal--delay-${i % 3}" data-offer-index="${i}">
        <h3 class="career-card__title">${o.title}</h3>
        <div class="career-card__tags">
          <span class="career-card__tag">${t.contract_label} · ${o.contract_type}</span>
          <span class="career-card__tag">${t.location_label} · ${o.location}</span>
        </div>
      </button>
    `).join('');
    grid.querySelectorAll('.reveal').forEach(el => observer.observe(el));

    if (!grid.dataset.bound) {
      grid.dataset.bound = 'true';
      grid.addEventListener('click', e => {
        const card = e.target.closest('.career-card');
        if (!card) return;
        openOfferModal(Number(card.dataset.offerIndex));
      });
    }
  }

  // Fenêtre de détail d'une offre — ouverte au clic sur une carte compacte.
  function openOfferModal(index) {
    const o = currentOffers[index];
    const modal = document.getElementById('offerModal');
    const body = document.getElementById('offerModalContent');
    if (!o || !modal || !body) return;
    const t = content.careers[currentLang];
    const email = careersData.contact_email;

    body.innerHTML = `
      <h2 class="offer-modal__title" id="offerModalTitle">${o.title}</h2>
      <div class="career-card__tags">
        <span class="career-card__tag">${t.contract_label} · ${o.contract_type}</span>
        <span class="career-card__tag">${t.location_label} · ${o.location}</span>
      </div>
      <div class="offer-modal__desc">${formatDescription(o.description)}</div>
      ${email
        ? `<a class="btn btn--primary offer-modal__apply" href="mailto:${email}?subject=${encodeURIComponent('Candidature - ' + o.title)}">${t.apply_cta}</a>`
        : ''}
    `;

    lastFocusedEl = document.activeElement;
    modal.classList.add('is-open');
    modal.setAttribute('aria-hidden', 'false');
    document.body.classList.add('modal-open');
    modal.querySelector('.offer-modal__close').focus();
  }

  function closeOfferModal() {
    const modal = document.getElementById('offerModal');
    if (!modal || !modal.classList.contains('is-open')) return;
    modal.classList.remove('is-open');
    modal.setAttribute('aria-hidden', 'true');
    document.body.classList.remove('modal-open');
    if (lastFocusedEl) lastFocusedEl.focus();
  }

  function initOfferModal() {
    const modal = document.getElementById('offerModal');
    if (!modal) return;
    modal.addEventListener('click', e => {
      if (e.target.closest('[data-close]')) closeOfferModal();
    });
    document.addEventListener('keydown', e => {
      if (e.key === 'Escape') closeOfferModal();
    });
  }

  // Rendu sécurisé de la description : gras/italique/liste autorisés (saisis via career-admin.html,
  // y compris collés depuis Word/Google Docs), le reste (script, style, attributs…) est retiré.
  // Compatible avec l'ancien format texte brut (\n).
  const RICHTEXT_BLOCK_TAGS = new Set(['P', 'DIV', 'UL', 'OL', 'LI', 'BR']);
  const RICHTEXT_STRIP_TAGS = new Set(['SCRIPT', 'STYLE', 'HEAD', 'TITLE', 'META', 'LINK', 'NOSCRIPT', 'OBJECT', 'IFRAME', 'EMBED']);

  function isBoldStyle(el) {
    const style = el.getAttribute('style') || '';
    if (/font-weight\s*:\s*(normal|[1-5]00)\b/i.test(style)) return false;
    if (/font-weight\s*:\s*(bold|bolder|[6-9]00)\b/i.test(style)) return true;
    return el.tagName === 'B' || el.tagName === 'STRONG';
  }
  function isItalicStyle(el) {
    const style = el.getAttribute('style') || '';
    if (/font-style\s*:\s*normal\b/i.test(style)) return false;
    if (/font-style\s*:\s*italic\b/i.test(style)) return true;
    return el.tagName === 'I' || el.tagName === 'EM';
  }

  function sanitizeRichText(html) {
    const tmp = document.createElement('div');
    tmp.innerHTML = html;
    (function clean(node) {
      Array.from(node.childNodes).forEach(child => {
        if (child.nodeType === Node.TEXT_NODE) return;
        if (child.nodeType !== Node.ELEMENT_NODE) { node.removeChild(child); return; }
        if (RICHTEXT_STRIP_TAGS.has(child.tagName)) { node.removeChild(child); return; }
        clean(child);
        if (RICHTEXT_BLOCK_TAGS.has(child.tagName)) {
          while (child.attributes.length) child.removeAttribute(child.attributes[0].name);
          return;
        }
        const bold = isBoldStyle(child);
        const italic = isItalicStyle(child);
        let frag = document.createDocumentFragment();
        while (child.firstChild) frag.appendChild(child.firstChild);
        if (italic) { const em = document.createElement('em'); em.appendChild(frag); frag = em; }
        if (bold) { const strong = document.createElement('strong'); strong.appendChild(frag); frag = strong; }
        node.insertBefore(frag, child);
        node.removeChild(child);
      });
    })(tmp);
    return tmp.innerHTML;
  }

  function escapeHtml(text) {
    return text.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
  }

  function formatDescription(text) {
    const html = /<[a-z][\s\S]*>/i.test(text)
      ? text
      : text.split(/\n{2,}/).map(p => p.trim()).filter(Boolean)
          .map(p => `<p>${escapeHtml(p).replace(/\n/g, '<br>')}</p>`).join('');
    return sanitizeRichText(html);
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
    }, 8000);
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
