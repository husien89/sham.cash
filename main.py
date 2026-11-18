from flask import Flask, render_template, request, jsonify, redirect, url_for, session, make_response
from google.cloud import datastore
from werkzeug.security import generate_password_hash, check_password_hash
import datetime
import uuid
import os

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'sham-cash-secret-key-dev') # في الإنتاج، اجعلها متغير بيئة
client = datastore.Client()

# --- نظام المصادقة ---

def get_user_id():
    return session.get('user_id')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        # التحقق من المستخدم في Datastore
        query = client.query(kind='User', filters=[('email', '=', email)])
        user = list(query.fetch(limit=1))
        
        if user and check_password_hash(user[0]['password_hash'], password):
            session['user_id'] = user[0]['user_id']
            return redirect(url_for('index'))
        else:
            return "بيانات الدخول غير صحيحة", 401
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        # التحقق من عدم وجود البريد مسبقاً
        query = client.query(kind='User', filters=[('email', '=', email)])
        if list(query.fetch(limit=1)):
            return "البريد الإلكتروني مسجل مسبقاً", 400
            
        # إنشاء مستخدم جديد
        new_user = datastore.Entity(key=client.key('User'))
        new_user['user_id'] = str(uuid.uuid4())
        new_user['email'] = email
        new_user['password_hash'] = generate_password_hash(password)
        new_user['created_at'] = datetime.datetime.now()
        client.put(new_user)
        
        # إنشاء محفظة تلقائية
        wallet = datastore.Entity(key=client.key('Wallet', new_user['user_id']))
        wallet['balance'] = 1000.00
        wallet['currency'] = 'SHAM'
        wallet['created_at'] = datetime.datetime.now()
        client.put(wallet)
        
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# --- واجهة المحفظة والسجل ---

@app.route('/')
def index():
    if not get_user_id():
        return redirect(url_for('login'))
    return render_template('dashboard.html')

@app.route('/api/wallet', methods=['GET'])
def get_wallet():
    user_id = get_user_id()
    wallet_key = client.key('Wallet', user_id)
    wallet = client.get(wallet_key)
    if not wallet:
        return jsonify({'error': 'Wallet not found'}), 404
    return jsonify({
        'balance': wallet['balance'],
        'currency': wallet['currency'],
        'user_id': user_id
    })

@app.route('/api/transactions', methods=['GET'])
def get_transactions():
    user_id = get_user_id()
    query = client.query(kind='Transaction', filters=[
        ('sender', '=', user_id), ('recipient', '=', user_id) # جلب العمليات الصادرة والواردة
    ])
    # بما أن Datastore لا يدعم OR بسهولة في الاستعلام البسيط، سنقوم بجلب العمليات المتعلقة بالمستخدم
    # في التطبيق الحقيقي، يفضل استخدام Cloud Bigtable أو Firestore لهذه النوعية من الاستعلامات
    tx_sender = client.query(kind='Transaction', filters=[('sender', '=', user_id)])
    tx_recipient = client.query(kind='Transaction', filters=[('recipient', '=', user_id)])
    
    # تجميع وترتيب النتائج (محاكاة)
    transactions = []
    for tx in list(tx_sender.fetch(5)) + list(tx_recipient.fetch(5)):
        transactions.append({
            'amount': tx['amount'],
            'timestamp': tx['timestamp'].isoformat(),
            'type': 'sent' if tx['sender'] == user_id else 'received',
            'counterparty': tx['recipient'] if tx['sender'] == user_id else tx['sender']
        })
    
    # ترتيب حسب الأحدث
    transactions.sort(key=lambda x: x['timestamp'], reverse=True)
    return jsonify(transactions[:10]) # آخر 10 عمليات

@app.route('/api/transaction', methods=['POST'])
def send_transaction():
    if not get_user_id():
        return jsonify({'error': 'Unauthorized'}), 401

    data = request.json
    sender_id = get_user_id()
    amount = data.get('amount', 0)
    recipient_id = data.get('recipient')

    if amount <= 0:
        return jsonify({'error': 'Amount must be positive'}), 400

    sender_key = client.key('Wallet', sender_id)
    sender_wallet = client.get(sender_key)

    if not sender_wallet or sender_wallet['balance'] < amount:
        return jsonify({'error': 'Insufficient funds'}), 400

    # خصم المبلغ
    sender_wallet['balance'] -= amount
    
    # إضافة المستلم
    recipient_key = client.key('Wallet', recipient_id)
    recipient_wallet = client.get(recipient_key)

    if not recipient_wallet:
        return jsonify({'error': 'Recipient not found'}), 404

    recipient_wallet['balance'] += amount

    # حفظ التغييرات
    with client.transaction():
        client.put(sender_wallet)
        client.put(recipient_wallet)
        
        tx_log = datastore.Entity(key=client.key('Transaction'))
        tx_log['sender'] = sender_id
        tx_log['recipient'] = recipient_id
        tx_log['amount'] = amount
        tx_log['timestamp'] = datetime.datetime.now()
        client.put(tx_log)

    return jsonify({'success