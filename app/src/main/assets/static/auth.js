// auth.js - شام كاش - النسخة النهائية

function login(username, password) {
    username = username.trim();
    password = password.trim();
    if (!username || !password) {
        return { success: false, message: 'عبي اسم المستخدم وكلمة المرور' };
    }
    const users = {
        'admin': '123456',
        'husien': '123456',
        'test': 'test'
    };
    if (users[username] && users[username] === password) {
        localStorage.setItem('sham_user', username);
        localStorage.setItem('sham_logged', 'true');
        return { success: true, message: 'تم الدخول بنجاح' };
    } else {
        return { success: false, message: 'اسم المستخدم أو كلمة المرور غلط' };
    }
}

function logout() {
    localStorage.removeItem('sham_user');
    localStorage.removeItem('sham_logged');
    window.location.href = 'login.html';
}

function checkLogin() {
    if (localStorage.getItem('sham_logged') !== 'true') {
        window.location.href = 'login.html';
    }
}

function getCurrentUser() {
    return localStorage.getItem('sham_user') || 'ضيف';
}

// هاي للتوافق مع الكود القديم تبع dashboard
function checkAuth() {
    if (localStorage.getItem('sham_logged') !== 'true') {
        window.location.href = 'login.html';
        return null;
    }
    return { name: getCurrentUser() };
}