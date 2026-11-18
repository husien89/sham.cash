// ==========================================
// بيانات الدخول والصلاحيات — خاصة بك
// عدّل الأسماء وكلمات المرور كما تشاء
// ==========================================

const USERS = [
    {
        id: 1,
        username: "ahmed",      // ✅ ضع اسم المستخدم هنا
        password: "_99155729614",      // ✅ ضع كلمة المرور هنا
        role: "owner",
        name: "أنت — المالك الكامل",
        permissions: ["all"]
    },
    {
        id: 2,
        username: "مراقب",
        password: "monitor123",
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