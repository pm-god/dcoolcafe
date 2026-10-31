/* ==========================================================================
   D COOL CAFE - JAVASCRIPT CONTROLLER
   Cart System, WhatsApp Order Generator, Nav & Dynamic Interactions
   ========================================================================== */

// ---------------- Cart State Management ----------------
const CART_STORAGE_KEY = 'dcoolcafe_cart_v1';
let cart = [];

function loadCart() {
    try {
        const stored = localStorage.getItem(CART_STORAGE_KEY);
        if (stored) {
            cart = JSON.parse(stored);
        }
    } catch (e) {
        console.error("Failed to load cart from storage", e);
        cart = [];
    }
    updateCartUI();
}

function saveCart() {
    try {
        localStorage.setItem(CART_STORAGE_KEY, JSON.stringify(cart));
    } catch (e) {
        console.error("Failed to save cart", e);
    }
    updateCartUI();
}

function addToCart(id, name, price, isVeg) {
    const existing = cart.find(item => item.id === id);
    if (existing) {
        existing.qty += 1;
    } else {
        cart.push({
            id: id,
            name: name,
            price: parseFloat(price),
            isVeg: isVeg,
            qty: 1
        });
    }
    saveCart();
    showToast(`Added "${name}" to your order!`, 'success');
    openCart();
}

function updateCartQty(id, delta) {
    const item = cart.find(i => i.id === id);
    if (!item) return;

    item.qty += delta;
    if (item.qty <= 0) {
        cart = cart.filter(i => i.id !== id);
    }
    saveCart();
}

function clearCart() {
    cart = [];
    saveCart();
    showToast('Your order has been cleared.', 'info');
}

function updateCartUI() {
    const badge = document.getElementById('cartBadge');
    const itemsList = document.getElementById('cartItemsList');
    const footer = document.getElementById('cartFooter');
    const subtotalEl = document.getElementById('cartSubtotal');
    const grandTotalEl = document.getElementById('cartGrandTotal');

    const totalCount = cart.reduce((sum, item) => sum + item.qty, 0);
    const totalPrice = cart.reduce((sum, item) => sum + (item.price * item.qty), 0);

    if (badge) {
        badge.textContent = totalCount;
    }

    if (!itemsList) return;

    if (cart.length === 0) {
        itemsList.innerHTML = `
            <div class="empty-cart-msg">
                <i class="fa-solid fa-bowl-food empty-icon"></i>
                <p>Your order is currently empty.</p>
                <a href="/menu" class="btn btn-secondary btn-sm mt-3" onclick="closeCart()">Explore Menu</a>
            </div>
        `;
        if (footer) footer.style.display = 'none';
        return;
    }

    if (footer) footer.style.display = 'block';

    itemsList.innerHTML = cart.map(item => `
        <div class="cart-item">
            <div class="cart-item-details">
                <h4>
                    <span style="color: ${item.isVeg ? '#2ecc71' : '#e74c3c'}; font-size: 0.8rem; margin-right: 4px;">●</span>
                    ${item.name}
                </h4>
                <div class="cart-item-price">₹${item.price.toFixed(0)} × ${item.qty} = ₹${(item.price * item.qty).toFixed(0)}</div>
            </div>
            <div class="cart-qty-ctrl">
                <button class="qty-btn" onclick="updateCartQty(${item.id}, -1)">-</button>
                <span class="qty-count">${item.qty}</span>
                <button class="qty-btn" onclick="updateCartQty(${item.id}, 1)">+</button>
            </div>
        </div>
    `).join('');

    if (subtotalEl) subtotalEl.textContent = `₹${totalPrice.toFixed(0)}`;
    if (grandTotalEl) grandTotalEl.textContent = `₹${totalPrice.toFixed(0)}`;
}

// ---------------- Cart Drawer Control ----------------
function openCart() {
    const drawer = document.getElementById('cartDrawer');
    const overlay = document.getElementById('cartOverlay');
    if (drawer) drawer.classList.add('active');
    if (overlay) overlay.classList.add('active');
}

function closeCart() {
    const drawer = document.getElementById('cartDrawer');
    const overlay = document.getElementById('cartOverlay');
    if (drawer) drawer.classList.remove('active');
    if (overlay) overlay.classList.remove('active');
}

// ---------------- WhatsApp Order Dispatcher ----------------
function sendWhatsAppOrder() {
    if (cart.length === 0) {
        showToast('Your order is empty. Please add items first.', 'warning');
        return;
    }

    const name = (document.getElementById('orderCustName')?.value || 'Guest').trim();
    const type = document.getElementById('orderType')?.value || 'Dine-in';
    const notes = (document.getElementById('orderTableNum')?.value || 'None').trim();

    let msg = `*--- D COOL CAFE ORDER REQUEST ---*\n\n`;
    msg += `👤 *Customer Name:* ${name}\n`;
    msg += `📍 *Order Type:* ${type}\n`;
    msg += `📝 *Table / Notes:* ${notes}\n`;
    msg += `🕒 *Time:* ${new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}\n\n`;
    msg += `*ITEMS ORDERED:*\n`;

    let total = 0;
    cart.forEach((item, index) => {
        const itemTotal = item.price * item.qty;
        total += itemTotal;
        msg += `${index + 1}. ${item.name} (x${item.qty}) - ₹${itemTotal}\n`;
    });

    msg += `\n*TOTAL AMOUNT: ₹${total}*\n`;
    msg += `---------------------------------\n`;
    msg += `_Please confirm this order. Thank you!_ ✨`;

    const encoded = encodeURIComponent(msg);
    const whatsappUrl = `https://wa.me/919439212345?text=${encoded}`;
    window.open(whatsappUrl, '_blank');
}

// ---------------- Toast Notifications ----------------
function showToast(message, type = 'info') {
    const container = document.querySelector('.flash-container') || document.body;
    const toast = document.createElement('div');
    toast.className = `alert alert-${type === 'warning' ? 'danger' : type}`;
    toast.style.position = 'fixed';
    toast.style.bottom = '90px';
    toast.style.right = '25px';
    toast.style.zIndex = '9999';
    toast.style.maxWidth = '360px';
    toast.style.boxShadow = '0 10px 25px rgba(0,0,0,0.6)';
    toast.style.animation = 'fadeIn 0.3s ease-in-out';
    
    let iconClass = 'fa-circle-info';
    if (type === 'success') iconClass = 'fa-circle-check';
    if (type === 'danger' || type === 'warning') iconClass = 'fa-circle-exclamation';

    toast.innerHTML = `
        <i class="fa-solid ${iconClass}"></i>
        <span>${message}</span>
        <button class="alert-close" onclick="this.parentElement.remove()">&times;</button>
    `;

    document.body.appendChild(toast);
    setTimeout(() => {
        if (toast.parentElement) toast.remove();
    }, 4000);
}

// ---------------- Modal Helper ----------------
function openModal(id) {
    const modal = document.getElementById(id);
    if (modal) modal.classList.add('active');
}

function closeModal(id) {
    const modal = document.getElementById(id);
    if (modal) modal.classList.remove('active');
}

// ---------------- Review Submission ----------------
async function submitReview(event) {
    event.preventDefault();
    const form = event.target;
    const author_name = form.author_name.value.trim();
    const rating = form.rating.value;
    const tag = form.tag.value.trim() || 'Burla Local';
    const comment = form.comment.value.trim();

    if (!author_name || !comment) {
        showToast('Please fill in your name and thoughts!', 'warning');
        return;
    }

    try {
        const res = await fetch('/api/review', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ author_name, rating, tag, comment })
        });
        const data = await res.json();
        if (data.success) {
            closeModal('reviewModal');
            showToast('Thank you! Your review has been added to our wall.', 'success');
            form.reset();
            setTimeout(() => window.location.reload(), 1200);
        } else {
            showToast(data.message || 'Error submitting review.', 'danger');
        }
    } catch (e) {
        showToast('Network error submitting review.', 'danger');
    }
}

// ---------------- DOM Event Bindings ----------------
document.addEventListener('DOMContentLoaded', () => {
    loadCart();

    // Mobile nav toggle
    const mobileToggle = document.getElementById('mobileToggle');
    const navLinks = document.getElementById('navLinks');
    if (mobileToggle && navLinks) {
        mobileToggle.addEventListener('click', () => {
            navLinks.classList.toggle('active');
        });
    }

    // Cart drawer buttons
    const openCartBtn = document.getElementById('openCartBtn');
    const closeCartBtn = document.getElementById('closeCartBtn');
    const cartOverlay = document.getElementById('cartOverlay');
    const sendWhatsAppBtn = document.getElementById('sendWhatsAppOrderBtn');

    if (openCartBtn) openCartBtn.addEventListener('click', openCart);
    if (closeCartBtn) closeCartBtn.addEventListener('click', closeCart);
    if (cartOverlay) cartOverlay.addEventListener('click', closeCart);
    if (sendWhatsAppBtn) sendWhatsAppBtn.addEventListener('click', sendWhatsAppOrder);

    // Navbar scroll background effect
    window.addEventListener('scroll', () => {
        const navbar = document.getElementById('navbar');
        if (navbar) {
            if (window.scrollY > 40) {
                navbar.style.boxShadow = '0 8px 25px rgba(0, 0, 0, 0.6)';
                navbar.style.borderBottomColor = 'rgba(229, 169, 80, 0.3)';
            } else {
                navbar.style.boxShadow = 'none';
                navbar.style.borderBottomColor = 'var(--border-color)';
            }
        }
    });

    // Close modals on clicking overlay
    document.querySelectorAll('.modal-overlay').forEach(overlay => {
        overlay.addEventListener('click', (e) => {
            if (e.target === overlay) {
                overlay.classList.remove('active');
            }
        });
    });
});
