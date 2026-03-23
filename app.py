from flask import Flask, render_template, redirect, url_for, request, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from model.models import db, User, Classroom, Reservation, Message
from flask_socketio import SocketIO, emit, join_room, leave_room
from datetime import datetime
import os
import requests
from dotenv import load_dotenv
from werkzeug.utils import secure_filename
from fpdf import FPDF
from flask import send_file
import io
from flask_dance.contrib.google import make_google_blueprint, google

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'), override=True)


app = Flask(__name__)
socketio = SocketIO(app)

app.config['SECRET_KEY'] = 'your_secret_key' # Change this to a random secret key
# SQL Server Connection
app.config['SQLALCHEMY_DATABASE_URI'] = r'mssql+pyodbc://@ALEXIS\SQLEXPRESS/Integradora?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'

# Ensure upload directory exists
os.makedirs(os.path.join(app.root_path, app.config['UPLOAD_FOLDER']), exist_ok=True)

# Google OAuth Config
google_bp = make_google_blueprint(
    client_id=os.environ.get("GOOGLE_OAUTH_CLIENT_ID"),
    client_secret=os.environ.get("GOOGLE_OAUTH_CLIENT_SECRET"),
    scope=["openid", "https://www.googleapis.com/auth/userinfo.email", "https://www.googleapis.com/auth/userinfo.profile"],
    redirect_to="google_login"
)
app.register_blueprint(google_bp, url_prefix="/login")

db.init_app(app)

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.context_processor
def inject_unread_count():
    if current_user.is_authenticated:
        unread_count = Message.query.filter_by(
            recipient_id=current_user.id,
            is_read=False
        ).count()
        return {'unread_message_count': unread_count}
    return {'unread_message_count': 0}


@app.route('/')
def index():
    if current_user.is_authenticated:
        return render_template('dashboard.html', user=current_user)
    return redirect(url_for('login'))


@app.route('/reservations', methods=['GET'])
@login_required
def reservations():
    # Only show what is happening RIGHT NOW on the grid
    now = datetime.now()

    classrooms = Classroom.query.all()
    
    # Check for active reservations at this exact moment
    overlaps = Reservation.query.filter(
        Reservation.start_time <= now,
        Reservation.end_time >= now
    ).all()
    
    # Create lookup dictionary: classroom_id -> reservation object
    active_reservations = {r.classroom_id: r for r in overlaps}
    
    # Enrich classroom objects for display
    for room in classrooms:
        room.active_reservation = active_reservations.get(room.id)
        room.is_reserved = room.id in active_reservations
        
    return render_template('reservations.html', 
                           classrooms=classrooms, 
                           user=current_user)

@app.route('/reservations/book/<int:room_id>', methods=['POST'])
@login_required
def book_reservation(room_id):
    start_str = request.form.get('start_time')
    end_str = request.form.get('end_time')
    
    start_time = datetime.fromisoformat(start_str)
    end_time = datetime.fromisoformat(end_str)
    
    # Check overlap again
    overlap = Reservation.query.filter(
        Reservation.classroom_id == room_id,
        Reservation.start_time < end_time,
        Reservation.end_time > start_time
    ).first()
    
    if overlap:
        flash('Error: Esta sala ya está reservada en ese horario.')
    else:
        res = Reservation(
            user_id=current_user.id,
            classroom_id=room_id,
            start_time=start_time,
            end_time=end_time
        )
        db.session.add(res)
        db.session.commit()
        flash('Reserva realizada exitosamente.')
        
    return redirect(url_for('reservations'))

@app.route('/reservations/cancel/<int:room_id>', methods=['POST'])
@login_required
def cancel_reservation(room_id):
    start_str = request.form.get('start_time')
    end_str = request.form.get('end_time')
    start_time = datetime.fromisoformat(start_str)
    
    # Find the specific reservation for this room by this user at this approximate time
    # (Simplified cancellation logic: just find any overlapping reservation by this user)
    res = Reservation.query.filter(
        Reservation.classroom_id == room_id,
        Reservation.user_id == current_user.id,
        Reservation.start_time <= start_time,
        Reservation.end_time >= start_time
    ).first()
    
    if res:
        db.session.delete(res)
        db.session.commit()
        flash('Reserva cancelada.')
    else:
        flash('No se encontró tu reserva para cancelar.')
        
    return redirect(url_for('reservations'))

@app.route('/videocall')
@login_required
def videocall():
    return render_template('videocall.html', user=current_user)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('index'))
        flash('Invalid username or password')
    return render_template('login.html')

@app.route('/login/google_auth')
def google_login():
    if not google.authorized:
        return redirect(url_for('google.login'))
        
    resp = google.get('/oauth2/v2/userinfo')
    if not resp.ok:
        flash('Hubo un error al obtener la información de Google.')
        return redirect(url_for('login'))
        
    user_info = resp.json()
    email = user_info['email']
    
    user = User.query.filter_by(username=email).first()
    if not user:
        # Create a new user using the Google email
        random_pwd = generate_password_hash('google_oauth_placeholder', method='scrypt')
        user = User(username=email, password=random_pwd)
        db.session.add(user)
        db.session.commit()
        
    login_user(user)
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        if user:
            flash('Username already exists')
            return redirect(url_for('register'))
            
        new_user = User(username=username, password=generate_password_hash(password, method='scrypt'))
        db.session.add(new_user)
        db.session.commit()
        
        login_user(new_user)
        return redirect(url_for('index'))
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        profile_picture = request.files.get('profile_picture')

        # Update username
        if username != current_user.username:
            existing_user = User.query.filter_by(username=username).first()
            if existing_user:
                flash('El nombre de usuario ya existe.')
                return redirect(url_for('settings'))
            current_user.username = username

        # Update password
        if password:
            current_user.password = generate_password_hash(password, method='scrypt')

        # Update profile picture
        if profile_picture and profile_picture.filename:
            filename = secure_filename(profile_picture.filename)
            # Save file
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            profile_picture.save(os.path.join(app.root_path, file_path))
            current_user.profile_picture = filename

        db.session.commit()
        flash('Configuraciones actualizadas correctamente.')
        return redirect(url_for('settings'))

    return render_template('settings.html', user=current_user)

@app.route('/chat')
@login_required
def chat_list():
    users = User.query.filter(User.id != current_user.id).all()
    
    # Calculate unread messages and last message per user
    for user in users:
        user.unread_count = Message.query.filter_by(
            sender_id=user.id,
            recipient_id=current_user.id,
            is_read=False
        ).count()
        
        # Get last message in conversation with this user
        last_message = Message.query.filter(
            ((Message.sender_id == current_user.id) & (Message.recipient_id == user.id)) |
            ((Message.sender_id == user.id) & (Message.recipient_id == current_user.id))
        ).order_by(Message.timestamp.desc()).first()
        
        user.last_message = last_message
    
    return render_template('chat_list.html', users=users)

@app.route('/chat/<int:user_id>')
@login_required
def chat_room(user_id):
    recipient = User.query.get_or_404(user_id)
    
    # Fetch conversation history
    messages = Message.query.filter(
        ((Message.sender_id == current_user.id) & (Message.recipient_id == user_id)) |
        ((Message.sender_id == user_id) & (Message.recipient_id == current_user.id))
    ).order_by(Message.timestamp).all()
    
    # Mark all messages from this sender as read
    Message.query.filter_by(
        sender_id=user_id,
        recipient_id=current_user.id,
        is_read=False
    ).update({'is_read': True})
    db.session.commit()
    
    return render_template('chat.html', recipient=recipient, messages=messages, user=current_user)


@socketio.on('send_message')
def handle_message(data):
    recipient_id = data['recipient_id']
    body = data['message']
    
    # Save to DB
    new_msg = Message(
        sender_id=current_user.id,
        recipient_id=recipient_id,
        body=body
    )
    db.session.add(new_msg)
    db.session.commit()
    
    # Prepare payload for chat window
    payload = {
        'sender_id': current_user.id,
        'body': body,
        'timestamp': new_msg.timestamp.strftime('%H:%M')
    }
    
    # Emit to recipient's room (using their user_id as room name)
    emit('receive_message', payload, room=str(recipient_id))
    emit('receive_message', payload, room=str(current_user.id))
    
    # Prepare payload for chat list update
    chat_list_payload = {
        'user_id': current_user.id,
        'username': current_user.username,
        'profile_picture': current_user.profile_picture,
        'last_message': body,
        'timestamp': new_msg.timestamp.strftime('%I:%M %p'),
        'unread_count': 1  # Increment for recipient
    }
    
    # Emit chat list update to recipient
    emit('chat_list_update', chat_list_payload, room=str(recipient_id))
    
    # Also update sender's chat list (with unread_count = 0 for them)
    sender_payload = {
        'user_id': recipient_id,
        'username': User.query.get(recipient_id).username,
        'profile_picture': User.query.get(recipient_id).profile_picture,
        'last_message': body,
        'timestamp': new_msg.timestamp.strftime('%I:%M %p'),
        'unread_count': 0
    }
    emit('chat_list_update', sender_payload, room=str(current_user.id))


@app.route('/stats')
@login_required
def stats():
    now = datetime.now()
    
    # Get total classrooms
    total_classrooms = Classroom.query.count()
    
    # Get active reservations
    occupied_count = Reservation.query.filter(
        Reservation.start_time <= now,
        Reservation.end_time >= now
    ).count()
    
    vacant_count = max(0, total_classrooms - occupied_count)
    
    # Calculate percentages
    occupied_percent = (occupied_count / total_classrooms * 100) if total_classrooms > 0 else 0
    vacant_percent = (vacant_count / total_classrooms * 100) if total_classrooms > 0 else 0
    
    return render_template('stats.html', 
                           occupied_percent=round(occupied_percent, 1), 
                           vacant_percent=round(vacant_percent, 1),
                           occupied_count=occupied_count,
                           vacant_count=vacant_count,
                           user=current_user)

@app.route('/download_report')
@login_required
def download_report():
    reservations = db.session.query(Reservation, Classroom, User).join(
        Classroom, Reservation.classroom_id == Classroom.id
    ).join(
        User, Reservation.user_id == User.id
    ).order_by(Reservation.start_time.desc()).all()

    # Create PDF
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "Reporte de Reservas de Salas", ln=True, align="C")
    pdf.ln(10)

    # Table Header
    pdf.set_font("Arial", "B", 12)
    pdf.cell(40, 10, "Sala", 1)
    pdf.cell(60, 10, "Usuario", 1)
    pdf.cell(45, 10, "Inicio", 1)
    pdf.cell(45, 10, "Fin", 1)
    pdf.ln()

    # Table Content
    pdf.set_font("Arial", "", 12)
    for res, room, user in reservations:
        pdf.cell(40, 10, room.name, 1)
        pdf.cell(60, 10, user.username, 1)
        pdf.cell(45, 10, res.start_time.strftime('%Y-%m-%d %H:%M'), 1)
        pdf.cell(45, 10, res.end_time.strftime('%Y-%m-%d %H:%M'), 1)
        pdf.ln()

    output = io.BytesIO()
    pdf_str = pdf.output()
    if isinstance(pdf_str, str): 
        output.write(pdf_str.encode('latin-1'))
    else:
        output.write(pdf_str)
    output.seek(0)

    current_date = datetime.now().strftime('%Y-%m-%d')
    return send_file(output, 
                     as_attachment=True, 
                     download_name=f'reporte_reservas_{current_date}.pdf',
                     mimetype='application/pdf')

@app.route('/videos', methods=['GET', 'POST'])
@login_required
def videos():
    search_query = request.form.get('query') or request.args.get('query', 'programacion')
    
    api_key = os.environ.get('YOUTUBE_API_KEY')
    videos = []
    error = None

    if api_key:
        try:
            url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&q={search_query}&type=video&maxResults=9&key={api_key}"
            response = requests.get(url)
            response.raise_for_status() # Raise exception for bad status codes
            videos_data = response.json()
            
            if 'items' in videos_data:
                for item in videos_data['items']:
                    video_info = {
                        'id': item['id']['videoId'],
                        'title': item['snippet']['title'],
                        'thumbnail': item['snippet']['thumbnails']['high']['url'],
                        'description': item['snippet']['description']
                    }
                    videos.append(video_info)
        except requests.exceptions.RequestException as e:
            error = "Hubo un problema al contactar con YouTube. Intenta de nuevo más tarde."
            print(f"YouTube API Error: {e}")
    else:
        error = "La clave de la API de YouTube no está configurada."

    return render_template('videos.html', videos=videos, search_query=search_query, error=error, user=current_user)

@socketio.on('join')
def on_join(data):
    # User joins their own room (identified by user_id) to receive messages
    join_room(str(current_user.id))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    socketio.run(app, debug=True)
# End of file
