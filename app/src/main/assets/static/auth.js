// ==========================================
// بيانات الدخول والصلاحيات — خاصة بك
// عدّل الأسماء وكلمات المرور كما تشاء
// تنبيه: هذا الملف داخل التطبيق ويمكن لأي أحد قراءته،
// لذلك لا تضع هنا كلمات مرور حقيقية. للنسخة الفعلية استخدم خادماً.
// ==========================================

const USERS = [
    {
        id: 1,
        username: "ahmed",              // ✅ ضع اسم المستخدم هنا
        password: "99155729614",    // ✅ ضع كلمة المرور هنا
        role: "owner",
        name: "المالك الكامل — أنت",
        permissions: ["all"]
    },
    {
        id: 2,
        username: "مراقب",
        password: "CHANGE_ME_VIEWER",
        role: "viewer",
        name: "حساب للمتابعة فقط",
        permissions: ["read"]
    }
];

// التحقق من تسجيل الدخول
function login(username, password) {
    const user = USERS.find(u => u.username === username && u.password === password);
    if (user) {
        sessionStorage.setItem('currentUser', JSON.stringify(user));
        return { success: true, user: user };
    }
    return { success: false, message: "اسم المستخدم أو كلمة المرور غير صحيحة" };
}

// التحقق من وجود جلسة (تستخدمها لوحة التحكم)
function checkAuth() {
    const user = JSON.parse(sessionStorage.getItem('currentUser'));
    if (!user) {
        window.location.href = 'login.html';
        return null;
    }
    return user;
}

// الحصول على الصلاحيات
function getPermissions() {
    const user = JSON.parse(sessionStorage.getItem('currentUser'));
    if (!user) return [];
    return user.permissions;
}

// تسجيل الخروج
function logout() {
    sessionStorage.removeItem('currentUser');
    window.location.href = 'login.html';
}

// التحقق من الصلاحية
function hasPermission(permission) {
    const permissions = getPermissions();
    return permissions.includes('all') || permissions.includes(permission);
}