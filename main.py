from flask import Flask, render_template, request, jsonify
from google.cloud import datastore
import datetime
import uuid

app = Flask(__name__)
client = datastore.Client()

# دالة مساعدة للتحقق من المستخدم (محاكاة)
def get_user_id():
    # في التطبيق الحقيقي، يتم استخدام نظام مصادقة (Auth)
    # هنا نستخدم UUID عشوائي للمحاكاة
    return request.cookies.get('user_id') or str(uuid.uuid4())

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/wallet', methods=['GET'])
def get_wallet():
    user_id = get_user_id()
    query = client.query(kind='Wallet', filters=[
        ('user_id', '=', user_id)
    ])
    
    # البحث عن محفظة المستخدم أو إنشاء جديدة
    wallet = list(query.fetch(limit=1))
    
    if not wallet:
        # إنشاء محفظة جديدة برصيد ابتدائي
        new_wallet = datastore.Entity(key=client.key('Wallet', user_id))
        new_wallet['balance'] = 1000.00  # رصيد افتراضي ترحيبي
        new_wallet['currency'] = 'SHAM'
        new_wallet['created_at'] = datetime.datetime.now()
        client.put(new_wallet)
        balance = 1000.00
    else:
        balance = wallet[0]['balance']

    return jsonify({
        'user_id': user_id,
        'balance': balance,
        'currency': 'SHAM'
    })

@app.route('/transaction', methods=['POST'])
def send_transaction():
    data = request.json
    sender_id = get_user_id()
    amount = data.get('amount', 0)
    recipient = data.get('recipient')

    if amount <= 0:
        return jsonify({'error': 'Amount must be positive'}), 400

    # 1. جلب محفظة المرسل
    sender_key = client.key('Wallet', sender_id)
    sender_wallet = client.get(sender_key)

    if not sender_wallet or sender_wallet['balance'] < amount:
        return jsonify({'error': 'Insufficient funds'}), 400

    # 2. خصم المبلغ من المرسل
    sender_wallet['balance'] -= amount
    
    # 3. إيجاد أو إنشاء محفظة المستلم
    recipient_query = client.query(kind='Wallet', filters=[
        ('user_id', '=', recipient)
    ])
    recipient_wallet = list(recipient_query.fetch(limit=1))

    if recipient_wallet:
        recipient_wallet = recipient_wallet[0]
    else:
        recipient_wallet = datastore.Entity(key=client.key('Wallet', recipient))
        recipient_wallet['balance'] = 0.00

    # 4. إضافة المبلغ للمستلم
    recipient_wallet['balance'] += amount

    # 5. حفظ التغييرات (معامل atomic)
    with client.transaction():
        client.put(sender_wallet)
        client.put(recipient_wallet)
        
        # تسجيل العملية في سجل المعاملات
        tx_log = datastore.Entity(key=client.key('Transaction'))
        tx_log['sender'] = sender_id
        tx_log['recipient'] = recipient
        tx_log['amount'] = amount
        tx_log['timestamp'] = datetime.datetime.now()
        client.put(tx_log)

    return jsonify({'success': True, 'new_balance': sender_wallet['balance']})

if __name__ == '__main__':
    app.run(debug=True, port=8080)