/**
 * Digital Dukan - Main JS Engine (v8.0 Premium)
 * Handles Global UI components, Tracking, and QuickView Modal
 */

// 1. GLOBAL TRACKING ENGINE
function trackProductView(productId) {
    if (!productId) return;
    let realId = parseInt(productId);
    if (realId > 1000) realId = realId - 1000; // Map D.No to DB ID
    fetch(`/track-view/${realId}`, { method: 'POST' }).catch(e => console.error(e));
}

function trackInquiry(productId) {
    if (!productId) return;
    let realId = parseInt(productId);
    if (realId > 1000) realId = realId - 1000;
    fetch(`/track-inquiry/${realId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
    }).catch(e => console.error(e));
}

// 2. QUICK VIEW MODAL CONTROLLER (Premium B2B Version)
function openQuickView(el) {
    // Data Extraction (Supports both Card and Button triggers)
    const qv = {
        id: el.getAttribute('data-id'),
        dno: el.getAttribute('data-dno') || el.getAttribute('data-id'),
        name: el.getAttribute('data-name') || el.getAttribute('data-product-name'),
        img: el.getAttribute('data-img') || el.getAttribute('data-image') || el.getAttribute('data-product-image'),
        fabric: el.getAttribute('data-fabric') || 'Premium Textile',
        work: el.getAttribute('data-work') || 'Surat Work',
        price: el.getAttribute('data-price') || '0',
        moq: el.getAttribute('data-moq') || '4',
        stock: el.getAttribute('data-stock') || 'READY'
    };

    // Update Modal UI Elements
    const modalImg = document.getElementById('qv-image');
    const modalName = document.getElementById('qv-name');
    const modalDno = document.getElementById('qv-dno-badge');
    const modalFabric = document.getElementById('qv-fabric');
    const modalWork = document.getElementById('qv-work');
    const modalPrice = document.getElementById('qv-price');
    const modalMoq = document.getElementById('qv-moq');

    if(modalImg) modalImg.src = qv.img;
    if(modalName) modalName.textContent = qv.name;
    if(modalDno) modalDno.textContent = 'D.NO: ' + qv.dno;
    if(modalFabric) modalFabric.textContent = qv.fabric;
    if(modalWork) modalWork.textContent = qv.work;
    if(modalPrice) modalPrice.textContent = '₹' + qv.price + '/pc';
    if(modalMoq) modalMoq.textContent = qv.moq + ' pcs';

    // WhatsApp Message Logic
    const waBtn = document.getElementById('qv-whatsapp-btn');
    if(waBtn) {
        let waMsg = "";
        if (qv.stock === 'SOLD OUT') {
            waMsg = `*SOLD OUT INQUIRY*\n\n` +
                    `*Design No:* ${qv.dno}\n` +
                    `*Product:* ${qv.name}\n\n` +
                    `I see this design is currently SOLD OUT. Please notify me when it's back in stock or suggest similar ready designs.`;
            waBtn.innerHTML = '<i class="fab fa-whatsapp me-2"></i> NOTIFY WHEN READY';
            waBtn.classList.remove('btn-whatsapp-premium');
            waBtn.classList.add('btn-outline-danger');
        } else {
            waMsg = `*B2B BULK INQUIRY*\n\n` +
                    `*Design No:* ${qv.dno}\n` +
                    `*Product:* ${qv.name}\n` +
                    `*MOQ:* ${qv.moq} pcs\n\n` +
                    `I'm interested in bulk booking this design. Please share details.`;
            waBtn.innerHTML = '<i class="fab fa-whatsapp me-2"></i> CHECK RATE ON WHATSAPP';
            waBtn.classList.add('btn-whatsapp-premium');
            waBtn.classList.remove('btn-outline-danger');
        }
        
        const contactNo = el.getAttribute('data-whatsapp') || '919081653925';
        waBtn.href = `https://wa.me/${contactNo.replace(/[^0-9]/g, '')}?text=${encodeURIComponent(waMsg)}`;
    }

    // Add To Inquiry Button Logic
    const addBtn = document.getElementById('qv-add-btn');
    if(addBtn && typeof cartManager !== 'undefined') {
        if (qv.stock === 'SOLD OUT') {
            addBtn.innerHTML = '<i class="fas fa-exclamation-triangle me-2"></i> CURRENTLY UNAVAILABLE';
            addBtn.classList.add('btn-outline-secondary', 'disabled');
            addBtn.onclick = function(e) {
                e.preventDefault();
                showToast("This design is currently Sold Out. You can check the 'Notify me' option for updates.", "warning");
            };
        } else {
            const isInCart = cartManager.items.some(i => i.id === qv.id);
            updateQuickViewButtonState(addBtn, isInCart);
            addBtn.classList.remove('disabled', 'btn-outline-secondary');
            
            addBtn.onclick = function() {
                cartManager.toggleItem({
                    dataset: {
                        id: qv.id,
                        name: qv.name,
                        image: qv.img,
                        price: qv.price,
                        moq: qv.moq
                    }
                });
                bootstrap.Modal.getInstance(document.getElementById('quickViewModal')).hide();
            };
        }
    }

    // Show Modal
    const modalEl = document.getElementById('quickViewModal');
    if(modalEl) {
        const modal = new bootstrap.Modal(modalEl);
        modal.show();
        // Track View (3s rule is handled by caller or local timer)
        trackProductView(qv.id);
    }
}

// 3. UI HELPER FUNCTIONS
function updateQuickViewButtonState(btn, isInCart) {
    if (isInCart) {
        btn.innerHTML = '<i class="fas fa-check me-2"></i> IN LIST';
        btn.classList.remove('btn-outline-light-glass');
        btn.classList.add('btn-gold-premium', 'active-b2b');
    } else {
        btn.innerHTML = '<i class="fas fa-file-invoice me-2"></i> ADD TO INQUIRY LIST';
        btn.classList.add('btn-outline-light-glass');
        btn.classList.remove('btn-gold-premium', 'active-b2b');
    }
}

function showToast(message, type = 'info') {
    const toastEl = document.getElementById('premiumToast');
    const msgEl = document.getElementById('toastMessage');
    const iconEl = document.getElementById('toastIcon');
    const progressEl = document.getElementById('toastProgress');
    
    if (!toastEl) return;

    // Set Message
    msgEl.textContent = message;

    // Set Icon and Color
    let icon = '<i class="fas fa-info-circle text-info"></i>';
    let progressColor = 'var(--accent)';
    
    if (type === 'success') {
        icon = '<i class="fas fa-check-circle text-success"></i>';
        progressColor = '#27ae60';
    } else if (type === 'warning') {
        icon = '<i class="fas fa-exclamation-triangle text-warning"></i>';
        progressColor = '#f1c40f';
    } else if (type === 'error') {
        icon = '<i class="fas fa-times-circle text-danger"></i>';
        progressColor = '#e74c3c';
    }
    
    iconEl.innerHTML = icon;
    progressEl.style.backgroundColor = progressColor;
    progressEl.style.width = '0%';

    // Initialize Toast
    const toast = new bootstrap.Toast(toastEl, { delay: 3500 });
    toast.show();

    // Progress bar animation
    setTimeout(() => {
        progressEl.style.width = '100%';
    }, 100);

    // Reset progress when closed
    toastEl.addEventListener('hidden.bs.toast', () => {
        progressEl.style.width = '0%';
    });
}

// 4. AUTO-TRACKING OBSERVER (Home Viewport Tracking)
document.addEventListener("DOMContentLoaded", function () {
    const observer = new IntersectionObserver((entries) => {
        entries.forEach((entry) => {
            if (entry.isIntersecting) {
                const productId = entry.target.getAttribute("data-product-id");
                if(productId) trackProductView(productId);
                observer.unobserve(entry.target);
            }
        });
    }, { threshold: 0.5 });

    document.querySelectorAll("[data-product-id]").forEach((card) => {
        observer.observe(card);
    });
});
