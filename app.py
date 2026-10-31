import os
import hashlib
import logging
from datetime import datetime
from zoneinfo import ZoneInfo
from flask import (
    Flask, render_template, request, redirect, url_for, 
    flash, jsonify, session
)
from database import get_db, init_db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dcoolcafe_secret_burla_2024_vintage_key')

# Initialize DB if not present
try:
    init_db()
except Exception as e:
    logger.warning(f"Database initialization warning: {e}")

def is_cafe_open():
    """Check if D Cool Cafe is open right now based on Indian Standard Time (IST)."""
    try:
        now = datetime.now(ZoneInfo('Asia/Kolkata'))
    except Exception:
        now = datetime.now()
    
    current_hour = now.hour + now.minute / 60.0
    # Opening hours: 11:30 AM (11.5) to 10:30 PM (22.5)
    open_hour = 11.5
    close_hour = 22.5
    is_open = open_hour <= current_hour <= close_hour
    return {
        'is_open': is_open,
        'current_time': now.strftime('%I:%M %p'),
        'hours': '11:30 AM - 10:30 PM',
        'status_text': 'Open Now • Welcoming You' if is_open else 'Closed Now • Opens at 11:30 AM'
    }

@app.context_processor
def inject_global_data():
    cafe_status = is_cafe_open()
    return {
        'cafe_name': 'D Cool Cafe',
        'instagram_handle': 'd_cool_cafe',
        'instagram_url': 'https://www.instagram.com/d_cool_cafe/',
        'address_line1': 'Daily Market, Near NAC Office',
        'address_line2': '(Above Goocool), Burla, Sambalpur',
        'pincode': '768017',
        'state': 'Odisha, India',
        'phone_number': '+91 94392 12345',
        'whatsapp_number': '919439212345',
        'tagline': 'A vintage vibe, delicious food, friendly service, passionate team & Fun Experience.',
        'cafe_status': cafe_status,
        'current_year': datetime.now().year
    }

# ----------------- Public Routes -----------------

@app.route('/')
def index():
    conn = get_db()
    cursor = conn.cursor()
    
    # Fetch bestsellers
    cursor.execute('SELECT * FROM menu_items WHERE is_bestseller = 1 AND available = 1 LIMIT 8')
    bestsellers = cursor.fetchall()
    
    # Fetch approved reviews
    cursor.execute('SELECT * FROM reviews WHERE is_approved = 1 ORDER BY created_at DESC LIMIT 6')
    reviews = cursor.fetchall()
    
    # Fetch categories
    cursor.execute('SELECT DISTINCT category FROM menu_items')
    categories = [row['category'] for row in cursor.fetchall()]
    
    conn.close()
    return render_template('index.html', bestsellers=bestsellers, reviews=reviews, categories=categories)

@app.route('/menu')
def menu():
    category = request.args.get('category', 'All')
    search_query = request.args.get('q', '').strip()
    
    conn = get_db()
    cursor = conn.cursor()
    
    # Fetch all categories
    cursor.execute('SELECT DISTINCT category FROM menu_items ORDER BY category ASC')
    categories = [row['category'] for row in cursor.fetchall()]
    
    # Base query
    query = 'SELECT * FROM menu_items WHERE available = 1'
    params = []
    
    if category and category != 'All':
        query += ' AND category = ?'
        params.append(category)
        
    if search_query:
        query += ' AND (name LIKE ? OR description LIKE ?)'
        params.extend([f'%{search_query}%', f'%{search_query}%'])
        
    query += ' ORDER BY is_bestseller DESC, name ASC'
    cursor.execute(query, params)
    items = cursor.fetchall()
    
    conn.close()
    return render_template('menu.html', items=items, categories=categories, active_category=category, search_query=search_query)

@app.route('/reserve', methods=['GET', 'POST'])
def reserve():
    if request.method == 'POST':
        guest_name = request.form.get('guest_name', '').strip()
        email = request.form.get('email', '').strip()
        phone = request.form.get('phone', '').strip()
        reservation_date = request.form.get('reservation_date', '').strip()
        reservation_time = request.form.get('reservation_time', '').strip()
        guests_count = request.form.get('guests_count', 2, type=int)
        occasion = request.form.get('occasion', 'Casual Hangout').strip()
        special_requests = request.form.get('special_requests', '').strip()
        
        if not (guest_name and phone and reservation_date and reservation_time):
            flash('Please fill in all required fields (Name, Phone, Date, Time).', 'danger')
            return redirect(url_for('reserve'))
        
        try:
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute('''
            INSERT INTO reservations (guest_name, email, phone, reservation_date, reservation_time, guests_count, occasion, special_requests)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (guest_name, email, phone, reservation_date, reservation_time, guests_count, occasion, special_requests))
            conn.commit()
            booking_id = cursor.lastrowid
            conn.close()
            
            flash(f'Table Reserved Successfully! Your Booking ID is #DCC-{booking_id:04d}. We look forward to welcoming you!', 'success')
            return redirect(url_for('reservation_success', booking_id=booking_id))
        except Exception as e:
            logger.error(f"Error creating reservation: {e}", exc_info=True)
            flash('We encountered an issue saving your reservation online. Please reach out to us directly on WhatsApp or call us to confirm!', 'danger')
            return redirect(url_for('reserve'))
        
    return render_template('reserve.html')

@app.route('/reservation/success/<int:booking_id>')
def reservation_success(booking_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM reservations WHERE id = ?', (booking_id,))
    booking = cursor.fetchone()
    conn.close()
    
    if not booking:
        flash('Reservation not found.', 'warning')
        return redirect(url_for('reserve'))
        
    return render_template('reserve_success.html', booking=booking)

@app.route('/gallery')
def gallery():
    return render_template('gallery.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        phone = request.form.get('phone', '').strip()
        subject = request.form.get('subject', 'General Inquiry').strip()
        message = request.form.get('message', '').strip()
        
        if not (name and message and (email or phone)):
            flash('Please provide your name, message, and contact information.', 'danger')
            return redirect(url_for('contact'))
            
        try:
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute('''
            INSERT INTO contact_messages (name, email, phone, subject, message)
            VALUES (?, ?, ?, ?, ?)
            ''', (name, email, phone, subject, message))
            conn.commit()
            conn.close()
            
            flash('Thank you for reaching out! Your message has been sent to D Cool Cafe team.', 'success')
        except Exception as e:
            logger.error(f"Error saving contact message: {e}", exc_info=True)
            flash('Message could not be saved right now. Please reach out to us directly on WhatsApp or call.', 'danger')
            
        return redirect(url_for('contact'))
        
    return render_template('contact.html')

# ----------------- APIs for AJAX and Cart -----------------

@app.route('/api/menu')
def api_menu():
    category = request.args.get('category')
    conn = get_db()
    cursor = conn.cursor()
    
    if category and category != 'All':
        cursor.execute('SELECT * FROM menu_items WHERE category = ? AND available = 1', (category,))
    else:
        cursor.execute('SELECT * FROM menu_items WHERE available = 1')
        
    items = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify({'items': items})

@app.route('/api/reserve', methods=['POST'])
def api_reserve():
    data = request.get_json() or {}
    guest_name = data.get('guest_name')
    phone = data.get('phone')
    email = data.get('email', '')
    reservation_date = data.get('reservation_date')
    reservation_time = data.get('reservation_time')
    guests_count = int(data.get('guests_count', 2))
    occasion = data.get('occasion', 'Casual Hangout')
    special_requests = data.get('special_requests', '')
    
    if not (guest_name and phone and reservation_date and reservation_time):
        return jsonify({'success': False, 'message': 'Missing required fields'}), 400
        
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
        INSERT INTO reservations (guest_name, email, phone, reservation_date, reservation_time, guests_count, occasion, special_requests)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (guest_name, email, phone, reservation_date, reservation_time, guests_count, occasion, special_requests))
        conn.commit()
        booking_id = cursor.lastrowid
        conn.close()
        
        return jsonify({
            'success': True, 
            'booking_id': f'DCC-{booking_id:04d}',
            'message': f'Table reserved! Your booking code is DCC-{booking_id:04d}.'
        })
    except Exception as e:
        logger.error(f"API reserve error: {e}", exc_info=True)
        return jsonify({'success': False, 'message': 'Could not save reservation. Please book via WhatsApp!'}), 500

@app.route('/api/review', methods=['POST'])
def api_review():
    data = request.get_json() or {}
    author_name = data.get('author_name', '').strip()
    rating = int(data.get('rating', 5))
    comment = data.get('comment', '').strip()
    tag = data.get('tag', 'Cafe Lover').strip()
    
    if not (author_name and comment):
        return jsonify({'success': False, 'message': 'Please provide your name and review'}), 400
        
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
        INSERT INTO reviews (author_name, rating, comment, tag, is_approved)
        VALUES (?, ?, ?, ?, 1)
        ''', (author_name, rating, comment, tag))
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Thank you! Your review has been added to our wall.'})
    except Exception as e:
        logger.error(f"API review error: {e}", exc_info=True)
        return jsonify({'success': False, 'message': 'Could not submit review at this time.'}), 500

@app.route('/api/status')
def api_status():
    return jsonify(is_cafe_open())

# ----------------- Admin Management Routes -----------------

def is_admin():
    return session.get('is_admin') is True

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        pwd_hash = hashlib.sha256(password.encode('utf-8')).hexdigest()
        
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM admin_users WHERE username = ? AND password_hash = ?', (username, pwd_hash))
        user = cursor.fetchone()
        conn.close()
        
        if user:
            session['is_admin'] = True
            session['admin_user'] = username
            flash('Logged in to D Cool Cafe Admin Portal successfully!', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid username or password. Default is admin / dcool123', 'danger')
            
    return render_template('admin/login.html')

@app.route('/admin/logout')
def admin_logout():
    session.pop('is_admin', None)
    session.pop('admin_user', None)
    flash('Logged out successfully.', 'info')
    return redirect(url_for('admin_login'))

@app.route('/admin')
def admin_dashboard():
    if not is_admin():
        return redirect(url_for('admin_login'))
        
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM reservations ORDER BY created_at DESC')
    reservations = cursor.fetchall()
    
    cursor.execute('SELECT * FROM menu_items ORDER BY category ASC, name ASC')
    menu_items = cursor.fetchall()
    
    cursor.execute('SELECT * FROM reviews ORDER BY created_at DESC')
    reviews = cursor.fetchall()
    
    cursor.execute('SELECT * FROM contact_messages ORDER BY created_at DESC')
    messages = cursor.fetchall()
    
    conn.close()
    return render_template('admin/dashboard.html', 
                           reservations=reservations, 
                           menu_items=menu_items, 
                           reviews=reviews, 
                           messages=messages)

@app.route('/admin/reservation/status/<int:res_id>/<string:new_status>')
def update_reservation_status(res_id, new_status):
    if not is_admin():
        return redirect(url_for('admin_login'))
        
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('UPDATE reservations SET status = ? WHERE id = ?', (new_status, res_id))
        conn.commit()
        conn.close()
        flash(f'Reservation #{res_id} marked as {new_status}.', 'success')
    except Exception as e:
        logger.error(f"Error updating reservation status: {e}", exc_info=True)
        flash(f'Failed to update reservation: {e}', 'danger')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/menu/toggle/<int:item_id>')
def toggle_menu_item(item_id):
    if not is_admin():
        return redirect(url_for('admin_login'))
        
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('UPDATE menu_items SET available = CASE WHEN available = 1 THEN 0 ELSE 1 END WHERE id = ?', (item_id,))
        conn.commit()
        conn.close()
        flash('Menu item availability toggled.', 'info')
    except Exception as e:
        logger.error(f"Error toggling menu item: {e}", exc_info=True)
        flash(f'Failed to update menu item: {e}', 'danger')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/menu/add', methods=['POST'])
def add_menu_item():
    if not is_admin():
        return redirect(url_for('admin_login'))
        
    name = request.form.get('name')
    category = request.form.get('category')
    description = request.form.get('description')
    price = float(request.form.get('price', 0))
    is_veg = 1 if request.form.get('is_veg') else 0
    is_spicy = 1 if request.form.get('is_spicy') else 0
    is_bestseller = 1 if request.form.get('is_bestseller') else 0
    image_url = request.form.get('image_url') or 'https://images.unsplash.com/photo-1554118811-1e0d58224f24?auto=format&fit=crop&w=600&q=80'
    
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
        INSERT INTO menu_items (name, category, description, price, is_veg, is_spicy, is_bestseller, image_url)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (name, category, description, price, is_veg, is_spicy, is_bestseller, image_url))
        conn.commit()
        conn.close()
        flash('New menu item added successfully!', 'success')
    except Exception as e:
        logger.error(f"Error adding menu item: {e}", exc_info=True)
        flash(f'Failed to add menu item: {e}', 'danger')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/review/delete/<int:review_id>')
def delete_review(review_id):
    if not is_admin():
        return redirect(url_for('admin_login'))
        
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM reviews WHERE id = ?', (review_id,))
        conn.commit()
        conn.close()
        flash('Review deleted.', 'info')
    except Exception as e:
        logger.error(f"Error deleting review: {e}", exc_info=True)
        flash(f'Failed to delete review: {e}', 'danger')
    return redirect(url_for('admin_dashboard'))

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"Starting D Cool Cafe website at http://127.0.0.1:{port}")
    app.run(host='0.0.0.0', port=port, debug=True)
