import sqlite3
import os
import shutil
import tempfile
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BUNDLED_DB_PATH = os.path.join(BASE_DIR, 'dcoolcafe.db')

def get_db_path():
    """
    Determine the appropriate database file path.
    In serverless platforms like Vercel or AWS Lambda, the application directory
    (/var/task) is mounted strictly read-only. SQLite will throw:
    'sqlite3.OperationalError: attempt to write a readonly database'.
    
    To fix this in serverless environments, we automatically detect the environment
    and use the writable temporary directory (/tmp/dcoolcafe.db).
    """
    custom_path = os.environ.get('DATABASE_PATH')
    if custom_path:
        return custom_path

    is_serverless = bool(
        os.environ.get('VERCEL')
        or os.environ.get('VERCEL_ENV')
        or os.environ.get('AWS_LAMBDA_FUNCTION_NAME')
        or not os.access(BASE_DIR, os.W_OK)
    )

    if is_serverless:
        tmp_dir = tempfile.gettempdir()
        tmp_db = os.path.join(tmp_dir, 'dcoolcafe.db')

        # If the tmp database doesn't exist yet, copy the pre-seeded bundled database
        if not os.path.exists(tmp_db):
            if os.path.exists(BUNDLED_DB_PATH):
                try:
                    shutil.copyfile(BUNDLED_DB_PATH, tmp_db)
                    try:
                        os.chmod(tmp_db, 0o666)
                    except Exception:
                        pass
                except Exception as e:
                    logger.error(f"Notice: Failed to copy bundled DB to {tmp_db}: {e}")
        return tmp_db

    return BUNDLED_DB_PATH

def get_db():
    conn = sqlite3.connect(get_db_path(), timeout=30.0, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()

    # Create menu_items table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS menu_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        category TEXT NOT NULL,
        description TEXT NOT NULL,
        price REAL NOT NULL,
        is_veg INTEGER DEFAULT 1,
        is_spicy INTEGER DEFAULT 0,
        is_bestseller INTEGER DEFAULT 0,
        image_url TEXT,
        available INTEGER DEFAULT 1
    )
    ''')

    # Create reservations table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS reservations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        guest_name TEXT NOT NULL,
        email TEXT DEFAULT '',
        phone TEXT NOT NULL,
        reservation_date TEXT NOT NULL,
        reservation_time TEXT NOT NULL,
        guests_count INTEGER NOT NULL,
        occasion TEXT DEFAULT 'Casual Hangout',
        special_requests TEXT,
        status TEXT DEFAULT 'Confirmed',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # Create reviews table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS reviews (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        author_name TEXT NOT NULL,
        rating INTEGER NOT NULL,
        comment TEXT NOT NULL,
        tag TEXT DEFAULT 'Cafe Enthusiast',
        is_approved INTEGER DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # Create contact messages table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS contact_messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT NOT NULL,
        phone TEXT,
        subject TEXT,
        message TEXT NOT NULL,
        is_read INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # Create admin_users table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS admin_users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # Seed default admin if not exists (username: admin, pass: dcool@burla2024)
    cursor.execute('SELECT COUNT(*) FROM admin_users')
    if cursor.fetchone()[0] == 0:
        import hashlib
        # Simple sha256 hash for portable setup
        pwd_hash = hashlib.sha256('dcool123'.encode('utf-8')).hexdigest()
        cursor.execute('INSERT INTO admin_users (username, password_hash) VALUES (?, ?)', ('admin', pwd_hash))

    # Seed initial menu items if empty
    cursor.execute('SELECT COUNT(*) FROM menu_items')
    if cursor.fetchone()[0] == 0:
        seed_menu_items(cursor)

    # Seed initial reviews if empty
    cursor.execute('SELECT COUNT(*) FROM reviews')
    if cursor.fetchone()[0] == 0:
        seed_reviews(cursor)

    conn.commit()
    conn.close()

def seed_menu_items(cursor):
    items = [
        # Coffee & Brews
        ("D Cool Signature Cold Coffee", "Coffee & Brews", "Our iconic blended thick cold coffee topped with chocolate drizzle & cocoa dust. Burla's all-time favorite!", 90, 1, 0, 1, "https://images.unsplash.com/photo-1517701604599-bb29b565090c?auto=format&fit=crop&w=600&q=80"),
        ("Hazelnut Chilled Frappe", "Coffee & Brews", "Rich espresso blended with silky cream, roasted hazelnut syrup & crunchy wafer bits.", 120, 1, 0, 1, "https://images.unsplash.com/photo-1572490122747-3968b75cc699?auto=format&fit=crop&w=600&q=80"),
        ("Vintage Cappuccino", "Coffee & Brews", "Velvety steamed milk poured over a double shot of dark aromatic espresso with cinnamon aroma.", 90, 1, 0, 0, "https://images.unsplash.com/photo-1534778101976-62847782c213?auto=format&fit=crop&w=600&q=80"),
        ("Dark Cafe Mocha", "Coffee & Brews", "Artisanal dark chocolate folded with espresso and frothy warm milk, topped with rich whipped cream.", 115, 1, 0, 0, "https://images.unsplash.com/photo-1578314675249-a6910f80cc4e?auto=format&fit=crop&w=600&q=80"),
        ("Irish Cream Cold Brew", "Coffee & Brews", "Slow-steeped cold coffee infused with non-alcoholic Irish cream notes and smooth cream float.", 130, 1, 0, 1, "https://images.unsplash.com/photo-1461023058943-07fcbe16d735?auto=format&fit=crop&w=600&q=80"),

        # Burgers & Sandwiches
        ("Crispy Veggie Crunch Burger", "Burgers & Sandwiches", "Golden spiced herb patty layered with crunchy iceberg lettuce, melted cheese, chipotle sauce & tomato.", 99, 1, 0, 1, "https://images.unsplash.com/photo-1568901346375-23c9450c58cd?auto=format&fit=crop&w=600&q=80"),
        ("Paneer Tikka Supreme Burger", "Burgers & Sandwiches", "Char-grilled tandoori spiced cottage cheese steak with mint mayonnaise, crisp red onions & capsicum.", 139, 1, 1, 1, "https://images.unsplash.com/photo-1550547660-d9450f859349?auto=format&fit=crop&w=600&q=80"),
        ("Fiery Peri-Peri Chicken Burger", "Burgers & Sandwiches", "Tender fried chicken breast fillet tossed in fiery African peri-peri spices with garlic mayo.", 159, 0, 1, 1, "https://images.unsplash.com/photo-1625813506062-0aeb1d7a094b?auto=format&fit=crop&w=600&q=80"),
        ("Double Decker BBQ Supreme", "Burgers & Sandwiches", "Double chicken patties grilled with smoky barbecue glaze, melted cheddar, pickles & caramelized onion.", 189, 0, 0, 0, "https://images.unsplash.com/photo-1586190848861-99aa4a171e90?auto=format&fit=crop&w=600&q=80"),
        ("Classic Cheese Melt Panini", "Burgers & Sandwiches", "Toasted Italian bread stuffed with molten mozzarella, bell peppers, sweet corn and herb butter.", 119, 1, 0, 0, "https://images.unsplash.com/photo-1528735602780-2552fd46c7af?auto=format&fit=crop&w=600&q=80"),

        # Handcrafted Pizzas
        ("Margherita Gold Pizza", "Handcrafted Pizzas", "Crispy 10-inch stone-baked crust with San Marzano tomato reduction, fragrant basil, and bubbling mozzarella.", 179, 1, 0, 1, "https://images.unsplash.com/photo-1604382355076-af4b0eb60143?auto=format&fit=crop&w=600&q=80"),
        ("Farmhouse Harvest Pizza", "Handcrafted Pizzas", "Loaded with crisp green capsicum, button mushrooms, sweet golden corn, black olives & red onions.", 229, 1, 0, 1, "https://images.unsplash.com/photo-1513104890138-7c749659a591?auto=format&fit=crop&w=600&q=80"),
        ("Spicy Tandoori Paneer Pizza", "Handcrafted Pizzas", "Tender paneer cubes tossed in tandoori marinade, red paprika, spiced onion rings and melted cheese.", 249, 1, 1, 1, "https://images.unsplash.com/photo-1565299624946-b28f40a0ae38?auto=format&fit=crop&w=600&q=80"),
        ("Smokey BBQ Chicken Pizza", "Handcrafted Pizzas", "Juicy marinated shredded chicken bathed in hickory barbecue sauce, jalapeños and extra mozzarella.", 279, 0, 1, 1, "https://images.unsplash.com/photo-1593560708920-61dd98c46a4e?auto=format&fit=crop&w=600&q=80"),
        ("Overloaded Cheese Burst", "Handcrafted Pizzas", "Double crust filled with a molten cheddar-mozzarella blend, seasoned with Italian herbs and garlic.", 269, 1, 0, 0, "https://images.unsplash.com/photo-1574071318508-1cdbab80d002?auto=format&fit=crop&w=600&q=80"),

        # Italian Pasta & Mains
        ("Creamy Penne Alfredo", "Italian Pastas", "Authentic rich garlic parmesan cream sauce gently tossed with penne, sautéed mushrooms, and oregano.", 169, 1, 0, 1, "https://images.unsplash.com/photo-1621996346565-e3d5d6281023?auto=format&fit=crop&w=600&q=80"),
        ("Fiery Arrabbiata Pasta", "Italian Pastas", "Zesty sun-ripened tomato sauce with red chili flakes, roasted garlic, basil leaves and black olives.", 159, 1, 1, 0, "https://images.unsplash.com/photo-1551183053-bf91a1d81141?auto=format&fit=crop&w=600&q=80"),
        ("Chef's Pink Sauce Fusilli", "Italian Pastas", "The best harmony of rich cream and tangy pomodoro tomato sauce loaded with veggies & mozzarella.", 179, 1, 0, 1, "https://images.unsplash.com/photo-1608897013039-887f21d8c804?auto=format&fit=crop&w=600&q=80"),
        ("Grilled Chicken Alfredo Penne", "Italian Pastas", "Herb-marinated grilled chicken breast strips tossed in rich creamy white garlic parmesan sauce.", 199, 0, 0, 1, "https://images.unsplash.com/photo-1546549032-9571cd6b27df?auto=format&fit=crop&w=600&q=80"),

        # Quick Bites & Loaded Fries
        ("Loaded Cheesy Mexican Fries", "Quick Bites", "Crispy golden shoestring fries drenched in house warm cheese sauce, spicy salsa, and jalapeños.", 129, 1, 1, 1, "https://images.unsplash.com/photo-1585109649139-366815a0d713?auto=format&fit=crop&w=600&q=80"),
        ("Spicy Peri-Peri Fries", "Quick Bites", "Hot, crispy potato fries tossed generously in our secret signature peri-peri seasoning.", 89, 1, 1, 0, "https://images.unsplash.com/photo-1573080496219-bb080dd4f877?auto=format&fit=crop&w=600&q=80"),
        ("Crunchy Garlic Bread Supreme", "Quick Bites", "Four toasted baguette slices brushed with herb garlic butter and crowned with bubbling mozzarella.", 109, 1, 0, 1, "https://images.unsplash.com/photo-1619895092538-128341789043?auto=format&fit=crop&w=600&q=80"),
        ("Peri-Peri Nachos Platter", "Quick Bites", "Crispy corn tortilla triangles topped with spiced beans, gooey cheese sauce, tangy salsa & mayo.", 129, 1, 1, 0, "https://images.unsplash.com/photo-1513456852971-30c0b8199d4d?auto=format&fit=crop&w=600&q=80"),
        ("D Cool Special Tadka Maggi", "Quick Bites", "The student favorite! Maggi cooked with butter, sautéed onions, tomatoes, sweet corn and cheese.", 69, 1, 0, 1, "https://images.unsplash.com/photo-1612927601601-6638404737ce?auto=format&fit=crop&w=600&q=80"),

        # Mocktails & Refreshers
        ("Electric Blue Lagoon", "Mocktails & Coolers", "Vibrant blue curacao, freshly squeezed lemon juice, mint sprigs topped with sparkling chilled soda.", 99, 1, 0, 1, "https://images.unsplash.com/photo-1513558161293-cdaf765ed2fd?auto=format&fit=crop&w=600&q=80"),
        ("Virgin Mint Mojito", "Mocktails & Coolers", "Muddled fresh garden mint, Persian lime chunks, crushed ice, cane sugar syrup and bubbling club soda.", 99, 1, 0, 1, "https://images.unsplash.com/photo-1551024709-8f23befc6f87?auto=format&fit=crop&w=600&q=80"),
        ("Crisp Green Apple Sparkler", "Mocktails & Coolers", "Tart green apple syrup infused with lime juice, black salt hint and ice-cold soda.", 109, 1, 0, 0, "https://images.unsplash.com/photo-1536935338788-846bb9981813?auto=format&fit=crop&w=600&q=80"),
        ("Chilled Peach Iced Tea", "Mocktails & Coolers", "Slow-brewed black tea infused with sweet peach essence, served over crystal clear ice cubes.", 89, 1, 0, 0, "https://images.unsplash.com/photo-1556679343-c7306c1976bc?auto=format&fit=crop&w=600&q=80"),

        # Shakes & Sweet Delights
        ("Oreo Overload Monster Shake", "Shakes & Desserts", "Creamy blend of whole milk, vanilla gelato, crushed Oreo cookies, topped with whipped cream and chocolate wafer.", 129, 1, 0, 1, "https://images.unsplash.com/photo-1572490122747-3968b75cc699?auto=format&fit=crop&w=600&q=80"),
        ("KitKat Crunch Shake", "Shakes & Desserts", "Chilled velvety chocolate shake blended with crunchy KitKat bars, chocolate pearls & fudge swirl.", 139, 1, 0, 1, "https://images.unsplash.com/photo-1579954115545-a95591f28bfc?auto=format&fit=crop&w=600&q=80"),
        ("Sizzling Brownie with Vanilla", "Shakes & Desserts", "Warm walnut brownie served on a cast-iron sizzler plate with a scoop of vanilla ice cream & hot molten fudge.", 149, 1, 0, 1, "https://images.unsplash.com/photo-1606313564200-e75d5e30476c?auto=format&fit=crop&w=600&q=80"),
        ("Warm Choco Lava Fantasy", "Shakes & Desserts", "Soft warm dark chocolate cake filled with a gooey erupting molten chocolate center.", 99, 1, 0, 0, "https://images.unsplash.com/photo-1624353365286-3f8d62daad51?auto=format&fit=crop&w=600&q=80")
    ]

    cursor.executemany('''
    INSERT INTO menu_items (name, category, description, price, is_veg, is_spicy, is_bestseller, image_url)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', items)

def seed_reviews(cursor):
    reviews = [
        ("Aayush Patnaik", 5, "Best hangout adda in Burla! The vintage vibe and fairy lights make it the coziest spot. The Cold Coffee and Loaded Cheese Fries are unmatched.", "VSSUT Student"),
        ("Sneha Mishra", 5, "Celebrated my best friend's birthday here! The staff was super warm and accommodating. Loved the Farmhouse Pizza and Oreo Monster Shake. 10/10 vibes!", "Local Regular"),
        ("Rahul Dash", 5, "Whenever we finish exams, D Cool Cafe is the default destination. Great food, great music, very reasonable prices, and proper cozy seating.", "VIMSAR Medico"),
        ("Priyanka Mohanty", 5, "Burla really needed a cafe like this with proper aesthetic decor and delicious food. The Tandoori Paneer Pizza and Virgin Mojito are top tier!", "Food Blogger")
    ]

    cursor.executemany('''
    INSERT INTO reviews (author_name, rating, comment, tag)
    VALUES (?, ?, ?, ?)
    ''', reviews)

if __name__ == '__main__':
    init_db()
    print("Database initialized successfully!")
