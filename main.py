import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import database
import auth

class ErrorHandler:
    """Centralized error handling for the application"""
    def __init__(self, root):
        self.root = root

    def show_error(self, title, message):
        """Show error dialog with consistent styling"""
        messagebox.showerror(title, message, parent=self.root)

    def show_warning(self, title, message):
        """Show warning dialog with consistent styling"""
        messagebox.showwarning(title, message, parent=self.root)

    def show_info(self, title, message):
        """Show info dialog with consistent styling"""
        messagebox.showinfo(title, message, parent=self.root)

    def handle_exception(self, exc, context=""):
        """Handle unexpected exceptions"""
        error_msg = f"An error occurred: {str(exc)}"
        if context:
            error_msg = f"{context}\n\n{error_msg}"
        self.show_error("Error", error_msg)
        print(f"Exception in {context}: {str(exc)}")  # For debugging

class CustomTooltip:
    """Custom tooltip implementation for Tkinter widgets"""
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip_window = None
        
        self.widget.bind("<Enter>", self.show_tooltip)
        self.widget.bind("<Leave>", self.hide_tooltip)

    def show_tooltip(self, event=None):
        """Display the tooltip"""
        if self.tooltip_window:
            return

        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 20

        self.tooltip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")

        label = tk.Label(tw, text=self.text, justify=tk.LEFT,
                         background="yellow", relief=tk.SOLID, borderwidth=1,
                         font=("tahoma", "8", "normal"))
        label.pack(ipadx=1)

    def hide_tooltip(self, event=None):
        """Hide the tooltip"""
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None

class ThemeConfig:
    """Theme configuration following Material Design principles"""
    COLORS = {
        'primary': '#1976D2',      # Blue 700
        'secondary': '#424242',    # Grey 800
        'background': '#FFFFFF',   # White
        'surface': '#F5F5F5',     # Grey 100
        'error': '#D32F2F',       # Red 700
        'text': '#212121',        # Grey 900
        'text_secondary': '#757575'# Grey 600
    }
    
    FONTS = {
        'heading': ('Helvetica', 16, 'bold'),
        'subheading': ('Helvetica', 14),
        'body': ('Helvetica', 12),
        'small': ('Helvetica', 10)
    }
    
    @classmethod
    def setup_theme(cls):
        """Configure ttk styles with the theme"""
        style = ttk.Style()
        
        # Configure common styles
        style.configure('.',
                      font=cls.FONTS['body'],
                      background=cls.COLORS['background'])
        
        # Primary button style
        style.configure('Primary.TButton',
                      padding=(10, 5),
                      font=cls.FONTS['body'])
        
        # Heading label style
        style.configure('Heading.TLabel',
                      font=cls.FONTS['heading'],
                      foreground=cls.COLORS['primary'])
        
        # Subheading label style
        style.configure('Subheading.TLabel',
                      font=cls.FONTS['subheading'],
                      foreground=cls.COLORS['secondary'])
        
        # Rating frame style
        style.configure('Rating.TLabelframe',
                      padding=10,
                      relief='solid')
        
        # Scale style
        style.configure('Rating.Horizontal.TScale',
                      sliderthickness=20)

class RegisterWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Register")
        self.geometry("300x250")
        self.resizable(False, False)
        
        # Center window
        self.center_window()
        
        # Create main frame with padding
        main_frame = ttk.Frame(self, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Username
        ttk.Label(main_frame, text="Username:").pack(fill=tk.X, pady=(0, 5))
        self.username_var = tk.StringVar()
        self.username_entry = ttk.Entry(main_frame, textvariable=self.username_var)
        self.username_entry.pack(fill=tk.X, pady=(0, 10))
        
        # Password
        ttk.Label(main_frame, text="Password:").pack(fill=tk.X, pady=(0, 5))
        self.password_var = tk.StringVar()
        self.password_entry = ttk.Entry(main_frame, textvariable=self.password_var, show="*")
        self.password_entry.pack(fill=tk.X, pady=(0, 10))
        
        # Confirm Password
        ttk.Label(main_frame, text="Confirm Password:").pack(fill=tk.X, pady=(0, 5))
        self.confirm_password_var = tk.StringVar()
        self.confirm_password_entry = ttk.Entry(main_frame, textvariable=self.confirm_password_var, show="*")
        self.confirm_password_entry.pack(fill=tk.X, pady=(0, 20))
        
        # Register button
        register_btn = ttk.Button(main_frame, text="Register", command=self.register)
        register_btn.pack(fill=tk.X)
        
        # Bind enter key
        self.bind('<Return>', lambda e: self.register())
        
        # Focus username entry
        self.username_entry.focus()

    def center_window(self):
        """Center the window on the screen"""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry('{}x{}+{}+{}'.format(width, height, x, y))

    def register(self):
        """Handle registration"""
        username = self.username_var.get().strip()
        password = self.password_var.get()
        confirm_password = self.confirm_password_var.get()
        
        # Validation
        if not username or not password or not confirm_password:
            messagebox.showerror("Error", "Please fill in all fields", parent=self)
            return
            
        if len(username) < 3:
            messagebox.showerror("Error", "Username must be at least 3 characters long", parent=self)
            return
            
        if len(password) < 6:
            messagebox.showerror("Error", "Password must be at least 6 characters long", parent=self)
            return
            
        if password != confirm_password:
            messagebox.showerror("Error", "Passwords do not match", parent=self)
            return
        
        success, message = auth.register_user(username, password)
        if success:
            messagebox.showinfo("Success", message, parent=self)
            self.destroy()
        else:
            messagebox.showerror("Error", message, parent=self)

class LoginWindow(tk.Toplevel):
    def __init__(self, parent, callback):
        super().__init__(parent)
        self.callback = callback
        self.title("Login")
        self.geometry("300x200")
        self.resizable(False, False)
        
        # Center window
        self.center_window()
        
        # Create main frame with padding
        main_frame = ttk.Frame(self, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Username
        ttk.Label(main_frame, text="Username:").pack(fill=tk.X, pady=(0, 5))
        self.username_var = tk.StringVar()
        self.username_entry = ttk.Entry(main_frame, textvariable=self.username_var)
        self.username_entry.pack(fill=tk.X, pady=(0, 10))
        
        # Password
        ttk.Label(main_frame, text="Password:").pack(fill=tk.X, pady=(0, 5))
        self.password_var = tk.StringVar()
        self.password_entry = ttk.Entry(main_frame, textvariable=self.password_var, show="*")
        self.password_entry.pack(fill=tk.X, pady=(0, 20))
        
        # Buttons frame
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X)
        
        # Login button
        login_btn = ttk.Button(btn_frame, text="Login", command=self.login)
        login_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Register button
        register_btn = ttk.Button(btn_frame, text="Register", command=self.show_register)
        register_btn.pack(side=tk.LEFT)
        
        # Bind enter key to login
        self.bind('<Return>', lambda e: self.login())
        
        # Focus username entry
        self.username_entry.focus()

    def center_window(self):
        """Center the window on the screen"""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry('{}x{}+{}+{}'.format(width, height, x, y))

    def show_register(self):
        """Show registration window"""
        RegisterWindow(self)

    def login(self):
        """Handle login"""
        username = self.username_var.get().strip()
        password = self.password_var.get()
        
        if not username or not password:
            messagebox.showerror("Error", "Please enter both username and password", parent=self)
            return
        
        success, result = auth.verify_login(username, password)
        if success:
            self.callback(username, result)
            self.destroy()
        else:
            messagebox.showerror("Error", result, parent=self)

class MovieApp:
    def __init__(self, root):
        self.root = root
        self.error_handler = ErrorHandler(root)
        
        try:
            # Initialize database connection
            conn = database.create_connection()
            if conn is None:
                raise Exception("Failed to connect to the database.")
            database.create_tables(conn)
            conn.close()
        except Exception as e:
            self.error_handler.handle_exception(e, "Database Initialization")
            return

        # Proceed with UI setup
        self.root.title("Movie Review System")
        self.root.geometry("1200x800")
        ThemeConfig.setup_theme()
        self.root.configure(bg=ThemeConfig.COLORS['background'])
        self.root.option_add('*TLabel*font', ThemeConfig.FONTS['body'])
        self.root.option_add('*TButton*font', ThemeConfig.FONTS['body'])
        self.current_user = None
        self.current_user_id = None
        self.create_menu()
        self.main_container = ttk.PanedWindow(root, orient=tk.HORIZONTAL)
        self.main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        self.setup_frames()
        self.setup_movie_list()
        self.setup_movie_details()
        self.load_movies()
        self.show_login()

    def setup_frames(self):
        """Setup main frames with proper styling"""
        # Left frame for movie list
        self.left_frame = ttk.Frame(self.main_container, style='Primary.TFrame')
        self.main_container.add(self.left_frame, weight=1)

        # Right frame for movie details
        self.right_frame = ttk.Frame(self.main_container, style='Primary.TFrame')
        self.main_container.add(self.right_frame, weight=2)

    def create_menu(self):
        """Create the application menu bar"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # Account menu
        self.account_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Account", menu=self.account_menu)
        self.account_menu.add_command(label="Login", command=self.show_login)
        self.account_menu.add_command(label="Logout", command=self.logout, state=tk.DISABLED)

    def show_login(self):
        """Show the login window"""
        LoginWindow(self.root, self.on_login_success)

    def on_login_success(self, username, user_id):
        """Handle successful login"""
        self.current_user = username
        self.current_user_id = user_id
        self.update_menu_state()
        self.update_rating_review_state()
        self.root.title(f"Movie Review System - {username}")
        messagebox.showinfo("Success", "Login successful!")

    def logout(self):
        """Handle logout"""
        self.current_user = None
        self.current_user_id = None
        self.update_menu_state()
        self.update_rating_review_state()
        self.root.title("Movie Review System")

    def update_menu_state(self):
        """Update menu items based on login state"""
        if self.current_user:
            self.account_menu.entryconfig("Login", state=tk.DISABLED)
            self.account_menu.entryconfig("Logout", state=tk.NORMAL)
        else:
            self.account_menu.entryconfig("Login", state=tk.NORMAL)
            self.account_menu.entryconfig("Logout", state=tk.DISABLED)

    def update_rating_review_state(self):
        """Update the state of rating and review widgets based on login status"""
        state = tk.NORMAL if self.current_user else tk.DISABLED
        self.rating_scale.config(state=state)
        self.rating_btn.config(state=state)
        self.review_text.config(state=state)
        self.review_btn.config(state=state)
        
        if not self.current_user:
            self.rating_var.set(5)  # Reset rating to default
            self.rating_value_label.config(text="5")
            self.review_text.delete("1.0", tk.END)  # Clear review text

    def setup_movie_list(self):
        """Setup the movie list with improved styling"""
        # Main list container
        list_container = ttk.Frame(self.left_frame)
        list_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Header with title and search
        header_frame = ttk.Frame(list_container)
        header_frame.pack(fill=tk.X, pady=(0, 10))

        # Title
        ttk.Label(header_frame, 
                 text="Movies Collection",
                 style='Heading.TLabel').pack(side=tk.LEFT)

        # Search frame
        search_frame = ttk.Frame(header_frame)
        search_frame.pack(side=tk.RIGHT)

        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.on_search_change)
        
        search_entry = ttk.Entry(search_frame, 
                               textvariable=self.search_var,
                               width=20)
        search_entry.pack(side=tk.LEFT, padx=5)
        CustomTooltip(search_entry, text="Search movies by title")
        
        # Create Treeview with enhanced styling
        style = ttk.Style()
        style.configure('MovieList.Treeview',
                       rowheight=30,
                       font=ThemeConfig.FONTS['body'])
        style.configure('MovieList.Treeview.Heading',
                       font=ThemeConfig.FONTS['subheading'])
        
        # Create container for Treeview and scrollbar
        tree_frame = ttk.Frame(list_container)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create horizontal scrollbar
        x_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL)
        x_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Create vertical scrollbar
        y_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL)
        y_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Create Treeview
        self.movie_tree = ttk.Treeview(tree_frame,
                                      columns=('ID', 'Title', 'Year', 'Rating'),
                                      show='headings',
                                      selectmode='browse',
                                      style='MovieList.Treeview',
                                      xscrollcommand=x_scrollbar.set,
                                      yscrollcommand=y_scrollbar.set)
        
        self.movie_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Configure scrollbars
        x_scrollbar.config(command=self.movie_tree.xview)
        y_scrollbar.config(command=self.movie_tree.yview)
        
        # Configure columns
        self.movie_tree.heading('ID', text='ID')
        self.movie_tree.heading('Title', text='Title')
        self.movie_tree.heading('Year', text='Year')
        self.movie_tree.heading('Rating', text='IMDB Rating')
        
        self.movie_tree.column('ID', width=0, stretch=False)
        self.movie_tree.column('Title', width=300, anchor=tk.W)
        self.movie_tree.column('Year', width=80, anchor=tk.CENTER)
        self.movie_tree.column('Rating', width=100, anchor=tk.CENTER)

        # Bind events
        self.movie_tree.bind('<<TreeviewSelect>>', self.on_select_movie)
        self.movie_tree.bind('<Double-1>', self.on_movie_double_click)

        # Configure tags for rating-based colors
        self.movie_tree.tag_configure('high_rating', 
                                    background='#E8F5E9')  # Green 50
        self.movie_tree.tag_configure('medium_rating', 
                                    background='#FFF3E0')  # Orange 50
        self.movie_tree.tag_configure('low_rating', 
                                    background='#FFEBEE')  # Red 50

    def setup_movie_details(self):
        """Setup the movie details display area"""
        details_frame = ttk.Frame(self.right_frame)
        details_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Movie info section
        info_frame = ttk.LabelFrame(details_frame, text="Movie Information")
        info_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Create Text widget for details with scrollbar
        details_scroll = ttk.Scrollbar(info_frame)
        details_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.details_text = tk.Text(info_frame, wrap=tk.WORD, width=50, height=15,
                                  yscrollcommand=details_scroll.set)
        self.details_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        details_scroll.config(command=self.details_text.yview)
        self.details_text.config(state=tk.DISABLED)

        # Rating section with improved UI
        rating_frame = ttk.LabelFrame(details_frame, text="Rate This Movie")
        rating_frame.pack(fill=tk.X, padx=5, pady=5)

        # Rating explanation
        ttk.Label(rating_frame, 
                 text="Rate this movie from 1 to 10",
                 font=('Helvetica', 10)).pack(pady=(5,0))
        
        # Rating scale label frame
        scale_frame = ttk.Frame(rating_frame)
        scale_frame.pack(fill=tk.X, padx=20, pady=5)
        
        # Scale labels
        labels_frame = ttk.Frame(scale_frame)
        labels_frame.pack(fill=tk.X)
        ttk.Label(labels_frame, text="1").pack(side=tk.LEFT)
        ttk.Label(labels_frame, text="10").pack(side=tk.RIGHT)

        # Rating scale with value display
        scale_value_frame = ttk.Frame(scale_frame)
        scale_value_frame.pack(fill=tk.X, pady=(0,5))
        
        self.rating_var = tk.IntVar(value=5)
        self.rating_scale = ttk.Scale(scale_value_frame, 
                                    from_=1, to=10,
                                    variable=self.rating_var,
                                    orient=tk.HORIZONTAL,
                                    command=self.update_rating_value)
        self.rating_scale.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.rating_value_label = ttk.Label(scale_value_frame, 
                                          text="5",
                                          width=3,
                                          anchor=tk.CENTER)
        self.rating_value_label.pack(side=tk.LEFT, padx=(10,0))

        # Rating descriptions
        desc_frame = ttk.Frame(rating_frame)
        desc_frame.pack(fill=tk.X, padx=20, pady=(0,5))
        ttk.Label(desc_frame, text="1-2: Poor", anchor=tk.W).pack(fill=tk.X)
        ttk.Label(desc_frame, text="3-4: Below Average", anchor=tk.W).pack(fill=tk.X)
        ttk.Label(desc_frame, text="5-6: Average", anchor=tk.W).pack(fill=tk.X)
        ttk.Label(desc_frame, text="7-8: Good", anchor=tk.W).pack(fill=tk.X)
        ttk.Label(desc_frame, text="9-10: Excellent", anchor=tk.W).pack(fill=tk.X)

        # Submit rating button
        self.rating_btn = ttk.Button(rating_frame, 
                                   text="Submit Rating",
                                   command=self.submit_rating,
                                   style='Accent.TButton')
        self.rating_btn.pack(pady=(5,10))

        # Review section
        review_frame = ttk.LabelFrame(details_frame, text="Write a Review")
        review_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Review guidelines
        ttk.Label(review_frame,
                 text="Share your thoughts about the movie (minimum 20 characters)",
                 font=('Helvetica', 10)).pack(pady=(5,0))

        # Review text with scrollbar
        review_scroll = ttk.Scrollbar(review_frame)
        review_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.review_text = tk.Text(review_frame, 
                                 wrap=tk.WORD, 
                                 height=4,
                                 yscrollcommand=review_scroll.set)
        self.review_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        review_scroll.config(command=self.review_text.yview)

        # Review button
        self.review_btn = ttk.Button(review_frame,
                                   text="Submit Review",
                                   command=self.submit_review,
                                   style='Accent.TButton')
        self.review_btn.pack(pady=(0,10))

        # Reviews display
        reviews_frame = ttk.LabelFrame(details_frame, text="Reviews")
        reviews_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Reviews text with scrollbar
        reviews_scroll = ttk.Scrollbar(reviews_frame)
        reviews_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.reviews_text = tk.Text(reviews_frame,
                                  wrap=tk.WORD,
                                  height=10,
                                  yscrollcommand=reviews_scroll.set)
        self.reviews_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        reviews_scroll.config(command=self.reviews_text.yview)
        self.reviews_text.config(state=tk.DISABLED)

        # Update states
        self.update_rating_review_state()

    def update_rating_value(self, *args):
        """Update the rating value label when scale changes"""
        value = self.rating_var.get()
        self.rating_value_label.config(text=str(value))

    def load_movies(self):
        """Load movies into the Treeview"""
        # Clear existing items
        for item in self.movie_tree.get_children():
            self.movie_tree.delete(item)

        # Get movies from database
        movies = database.get_all_movies()
        
        # Insert into Treeview
        for movie in movies:
            self.movie_tree.insert('', tk.END, values=movie)

    def submit_rating(self):
        """Submit a rating for the current movie"""
        try:
            if not self.current_user:
                raise ValueError("Please login to rate movies")

            selected_items = self.movie_tree.selection()
            if not selected_items:
                raise ValueError("Please select a movie to rate")

            movie_id = self.movie_tree.item(selected_items[0])['values'][0]
            score = self.rating_var.get()

            if not (1 <= score <= 10):
                raise ValueError("Rating must be between 1 and 10")

            success, message = database.add_rating(self.current_user_id, movie_id, score)
            if success:
                self.error_handler.show_info("Success", message)
                self.refresh_movie_details()
            else:
                raise Exception(message)
        except Exception as e:
            self.error_handler.handle_exception(e, "Submit Rating")

    def submit_review(self):
        """Submit a review for the current movie"""
        try:
            if not self.current_user:
                raise ValueError("Please login to review movies")

            selected_items = self.movie_tree.selection()
            if not selected_items:
                raise ValueError("Please select a movie to review")

            review_text = self.review_text.get("1.0", tk.END).strip()
            if len(review_text) < 20:
                raise ValueError("Review must be at least 20 characters long")

            movie_id = self.movie_tree.item(selected_items[0])['values'][0]
            success, message = database.add_review(self.current_user_id, movie_id, review_text)
            if success:
                self.error_handler.show_info("Success", message)
                self.review_text.delete("1.0", tk.END)
                self.refresh_movie_details()
            else:
                raise Exception(message)
        except Exception as e:
            self.error_handler.handle_exception(e, "Submit Review")

    def refresh_movie_details(self):
        """Refresh the movie details display"""
        selected_items = self.movie_tree.selection()
        if selected_items:
            self.on_select_movie(None)  # Reuse existing method to refresh details

    def on_select_movie(self, event):
        """Handle movie selection"""
        selected_items = self.movie_tree.selection()
        if not selected_items:
            return

        # Get the movie ID
        movie_id = self.movie_tree.item(selected_items[0])['values'][0]
        
        # Get movie details
        movie = database.get_movie_details(movie_id)
        if movie:
            # Enable text widget for editing
            self.details_text.config(state=tk.NORMAL)
            self.reviews_text.config(state=tk.NORMAL)
            
            # Clear current content
            self.details_text.delete(1.0, tk.END)
            self.reviews_text.delete(1.0, tk.END)
            
            # Get ratings info
            avg_rating, num_ratings = database.get_movie_ratings(movie_id)
            avg_rating_str = f"{avg_rating:.1f}" if avg_rating else "No ratings yet"
            
            # Format and insert movie details
            details = f"""Title: {movie[1]}
Release Year: {movie[2]}
Certificate: {movie[3]}
Runtime: {movie[4]}
Genre: {movie[5]}
IMDB Rating: {movie[6]}
User Rating: {avg_rating_str} ({num_ratings} {'rating' if num_ratings == 1 else 'ratings'})

Overview:
{movie[7]}

Director: {movie[8]}

Stars:
{movie[9]}

Number of Votes: {movie[10]}
Gross: {movie[11]}
"""
            self.details_text.insert(tk.END, details)
            
            # Get and display reviews
            reviews = database.get_movie_reviews(movie_id)
            if reviews:
                for review in reviews:
                    review_text = f"""
{review[2]} - {review[4]}:
{review[3]}
----------------------------------------
"""
                    self.reviews_text.insert(tk.END, review_text)
            else:
                self.reviews_text.insert(tk.END, "\nNo reviews yet.")
            
            # If user has already rated, show their rating
            if self.current_user:
                user_rating = database.get_user_rating(self.current_user_id, movie_id)
                if user_rating:
                    self.rating_var.set(user_rating)
            
            # Disable text widgets to prevent editing
            self.details_text.config(state=tk.DISABLED)
            self.reviews_text.config(state=tk.DISABLED)

    def on_search_change(self, *args):
        """Filter the movie list based on the search query"""
        query = self.search_var.get().strip().lower()

        # Clear existing items in the Treeview
        for item in self.movie_tree.get_children():
            self.movie_tree.delete(item)

        # Fetch all movies from the database
        movies = database.get_all_movies()

        # Filter movies based on the search query
        filtered_movies = [movie for movie in movies if query in movie[1].lower()]

        # Insert filtered movies into the Treeview
        for movie in filtered_movies:
            self.movie_tree.insert('', tk.END, values=movie)

    def on_movie_double_click(self, event):
        """Handle double-click on a movie to show detailed information"""
        selected_items = self.movie_tree.selection()
        if not selected_items:
            return

        # Get the movie ID
        movie_id = self.movie_tree.item(selected_items[0])['values'][0]

        # Fetch movie details
        movie = database.get_movie_details(movie_id)
        if movie:
            # Display movie details in a popup window
            details_window = tk.Toplevel(self.root)
            details_window.title(f"Details - {movie[1]}")
            details_window.geometry("600x400")

            # Create a Text widget to display details
            details_text = tk.Text(details_window, wrap=tk.WORD, width=70, height=20)
            details_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

            # Format and insert movie details
            details = f"""Title: {movie[1]}
Release Year: {movie[2]}
Certificate: {movie[3]}
Runtime: {movie[4]}
Genre: {movie[5]}
IMDB Rating: {movie[6]}

Overview:
{movie[7]}

Director: {movie[8]}

Stars:
{movie[9]}

Number of Votes: {movie[10]}
Gross: {movie[11]}"""
            details_text.insert(tk.END, details)
            details_text.config(state=tk.DISABLED)

if __name__ == '__main__':
    # Create and run the application
    root = tk.Tk()
    app = MovieApp(root)
    root.mainloop()