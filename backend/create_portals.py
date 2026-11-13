import os
import re

def remove_between(text, start_marker, end_marker):
    pattern = re.compile(rf"{re.escape(start_marker)}[\s\S]*?{re.escape(end_marker)}", re.DOTALL)
    if not pattern.search(text):
        print(f"Warning: pattern between '{start_marker}' and '{end_marker}' not found!")
    return pattern.sub("", text)

def build_portals():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    index_path = os.path.join(base_dir, "index.html")
    
    with open(index_path, "r", encoding="utf-8") as f:
        master_html = f.read()

    # =========================================================================
    # 1. BUILD STUDENT.HTML (CỔNG SINH VIÊN - CHỈ CÓ TÍNH NĂNG CỦA SINH VIÊN)
    # =========================================================================
    # Sinh viên:
    # - TUYỆT ĐỐI KHÔNG CÓ tab "Xem bài & Chấm điểm" (nav-grading)
    # - TUYỆT ĐỐI KHÔNG CÓ tab "Quản lý Tài khoản" (nav-accounts)
    # - TUYỆT ĐỐI KHÔNG CÓ section tab-grading trong DOM
    # - TUYỆT ĐỐI KHÔNG CÓ section tab-accounts trong DOM
    # - TUYỆT ĐỐI KHÔNG CÓ nút Tạo / Hủy kỳ thi trong Contest (teacher-contest-action)
    # - TUYỆT ĐỐI KHÔNG CÓ các Modal của Giáo viên & Admin (Modals 2 - 9)
    student_html = master_html

    # Đổi title & logo subtitle
    student_html = student_html.replace(
        "<title>CodeArena - Nền tảng luyện tập lập trình trực tuyến & Chấm bài Sandbox</title>",
        "<title>CodeArena - Cổng Sinh Viên (Student Portal)</title>"
    )
    student_html = student_html.replace(
        '<span class="text-[10px] text-slate-400 block font-normal tracking-wide">AUTOMATED ONLINE JUDGE</span>',
        '<span class="text-[10px] text-emerald-400 block font-bold tracking-wide">CỔNG SINH VIÊN (STUDENT)</span>'
    )

    # Đặt người dùng mặc định là Sinh viên
    student_html = re.sub(
        r'let currentUser = [^;]+;',
        'let currentUser = {\n      id: "20240606239",\n      name: "Hoàng Anh Tú",\n      role: "Sinh viên",\n      avatar: "AT",\n      email: "20240606239@sv.haui.edu.vn",\n      status: "active"\n    };',
        student_html
    )

    # Xóa hoàn toàn nav-grading khỏi thanh menu
    student_html = remove_between(student_html, "<!-- NAV_GRADING_START -->", "<!-- NAV_GRADING_END -->")
    # Xóa hoàn toàn nav-accounts khỏi thanh menu
    student_html = remove_between(student_html, "<!-- NAV_ACCOUNTS_START -->", "<!-- NAV_ACCOUNTS_END -->")
    # Xóa hoàn toàn nav-logs khỏi thanh menu
    student_html = remove_between(student_html, "<!-- NAV_LOGS_START -->", "<!-- NAV_LOGS_END -->")
    # Xóa hoàn toàn section tab-grading khỏi DOM
    student_html = remove_between(student_html, "<!-- SECTION_GRADING_START -->", "<!-- SECTION_GRADING_END -->")
    # Xóa hoàn toàn section tab-accounts khỏi DOM
    student_html = remove_between(student_html, "<!-- SECTION_ACCOUNTS_START -->", "<!-- SECTION_ACCOUNTS_END -->")
    # Xóa hoàn toàn section tab-logs khỏi DOM
    student_html = remove_between(student_html, "<!-- SECTION_LOGS_START -->", "<!-- SECTION_LOGS_END -->")
    # Xóa hoàn toàn nút Tạo / Hủy kỳ thi trong Contest
    student_html = remove_between(student_html, "<!-- TEACHER_CONTEST_ACTION_START -->", "<!-- TEACHER_CONTEST_ACTION_END -->")

    # Xóa toàn bộ Modals 2 đến 9 (chỉ để lại Modal 1: Đăng nhập sinh viên)
    # Từ comment trước Modal 2 đến trước comment FOOTER
    student_html = re.sub(
        r'<!-- =+\s*-->\s*<!-- MODAL 2: TẠO KỲ THI[\s\S]*?(?=<!-- FOOTER -->)',
        '',
        student_html
    )

    # Chuyển header AI button thành static badge (không mở modal cấu hình AI key)
    student_html = student_html.replace(
        'onclick="openAIConfigModal()" id="header-ai-status" title="Bấm để xem hoặc cấu hình Google Gemini API Key" class="inline-flex items-center gap-1.5 px-2 py-0.5 text-xs font-semibold bg-indigo-500/10 hover:bg-indigo-500/20 text-indigo-300 rounded border border-indigo-500/30 whitespace-nowrap transition cursor-pointer"',
        'id="header-ai-status" title="Hệ thống Chấm Tự Động AI AST/Gemini Online" class="inline-flex items-center gap-1.5 px-2 py-0.5 text-xs font-semibold bg-indigo-500/10 text-indigo-300 rounded border border-indigo-500/30 whitespace-nowrap cursor-default"'
    )

    student_path = os.path.join(base_dir, "student.html")
    with open(student_path, "w", encoding="utf-8") as f:
        f.write(student_html)
    print("[*] Created student.html cleanly (Zero teacher/admin items in DOM)!")

    # =========================================================================
    # 2. BUILD TEACHER.HTML (CỔNG GIẢNG VIÊN - ĐẦY ĐỦ CHẤM ĐIỂM, KHÔNG CÓ ADMIN)
    # =========================================================================
    # Giảng viên:
    # - CÓ tab Sandbox IDE, Xem bài & Chấm điểm (nav-grading), Contest Arena, Báo cáo Kết quả Lớp, Hồ sơ HaUI
    # - TUYỆT ĐỐI KHÔNG CÓ tab "Quản lý Tài khoản" (nav-accounts)
    # - TUYỆT ĐỐI KHÔNG CÓ section tab-accounts trong DOM
    # - TUYỆT ĐỐI KHÔNG CÓ các Modal quản trị người dùng Admin (Modals 5, 6, 7)
    teacher_html = master_html

    teacher_html = teacher_html.replace(
        "<title>CodeArena - Nền tảng luyện tập lập trình trực tuyến & Chấm bài Sandbox</title>",
        "<title>CodeArena - Cổng Giảng Viên (Teacher Portal)</title>"
    )
    teacher_html = teacher_html.replace(
        '<span class="text-[10px] text-slate-400 block font-normal tracking-wide">AUTOMATED ONLINE JUDGE</span>',
        '<span class="text-[10px] text-amber-400 block font-bold tracking-wide">CỔNG GIẢNG VIÊN (TEACHER)</span>'
    )

    teacher_html = re.sub(
        r'let currentUser = [^;]+;',
        'let currentUser = {\n      id: "GV-HAUI-01",\n      name: "TS. Nguyễn Thị Hoa Huệ",\n      role: "Giáo viên",\n      avatar: "HH",\n      email: "gv.huenth@haui.edu.vn",\n      status: "active"\n    };',
        teacher_html
    )

    # Hiển thị mặc định nav-grading và teacher-contest-action trong HTML cho Giáo viên
    teacher_html = teacher_html.replace(
        'id="nav-grading" class="nav-btn px-3 sm:px-3.5 py-1.5 rounded-xl text-xs sm:text-sm font-medium transition items-center space-x-2 whitespace-nowrap text-slate-400 hover:text-white hover:bg-slate-800/80 border border-transparent shrink-0 hidden" style="display: none;"',
        'id="nav-grading" class="nav-btn px-3 sm:px-3.5 py-1.5 rounded-xl text-xs sm:text-sm font-semibold transition flex items-center space-x-2 whitespace-nowrap bg-amber-500/20 text-amber-300 border border-amber-500/40 shadow-sm shadow-amber-500/20 shrink-0"'
    )
    teacher_html = teacher_html.replace(
        'id="nav-logs" class="nav-btn px-3 sm:px-3.5 py-1.5 rounded-xl text-xs sm:text-sm font-medium transition items-center space-x-2 whitespace-nowrap text-slate-400 hover:text-white hover:bg-slate-800/80 border border-transparent shrink-0 hidden" style="display: none;"',
        'id="nav-logs" class="nav-btn px-3 sm:px-3.5 py-1.5 rounded-xl text-xs sm:text-sm font-medium transition flex items-center space-x-2 whitespace-nowrap text-slate-400 hover:text-white hover:bg-slate-800/80 border border-transparent shrink-0"'
    )
    # Đổi active tab sang tab-grading (Xem bài & Chấm điểm) ngay khi tải trang cho Giáo viên
    teacher_html = teacher_html.replace(
        'id="nav-ide" class="nav-btn px-3 sm:px-3.5 py-1.5 rounded-xl text-xs sm:text-sm font-semibold transition flex items-center space-x-2 whitespace-nowrap bg-indigo-600/20 text-indigo-300 border border-indigo-500/40 shadow-sm shadow-indigo-500/20 shrink-0"',
        'id="nav-ide" class="nav-btn px-3 sm:px-3.5 py-1.5 rounded-xl text-xs sm:text-sm font-medium transition flex items-center space-x-2 whitespace-nowrap text-slate-400 hover:text-white hover:bg-slate-800/80 border border-transparent shrink-0"'
    )
    teacher_html = teacher_html.replace(
        '<section id="tab-ide" class="space-y-4">',
        '<section id="tab-ide" class="hidden space-y-4" style="display: none;">'
    )
    teacher_html = teacher_html.replace(
        '<section id="tab-grading" class="hidden space-y-6" style="display: none;">',
        '<section id="tab-grading" class="space-y-6">'
    )
    teacher_html = teacher_html.replace(
        'id="teacher-contest-action" class="hidden items-center gap-2" style="display: none;"',
        'id="teacher-contest-action" class="flex items-center gap-2"'
    )

    # Xóa hoàn toàn nav-accounts khỏi thanh menu
    teacher_html = remove_between(teacher_html, "<!-- NAV_ACCOUNTS_START -->", "<!-- NAV_ACCOUNTS_END -->")
    # Xóa hoàn toàn section tab-accounts khỏi DOM
    teacher_html = remove_between(teacher_html, "<!-- SECTION_ACCOUNTS_START -->", "<!-- SECTION_ACCOUNTS_END -->")

    # Xóa các Modals của Admin (Modal 5: Thêm user, Modal 6: Sửa user, Modal 7: Xóa user)
    teacher_html = re.sub(
        r'<!-- =+\s*-->\s*<!-- MODAL 5: THÊM TÀI KHOẢN MỚI[\s\S]*?(?=<!-- =+\s*-->\s*<!-- MODAL 8: XÁC NHẬN XOÁ BÀI LÀM)',
        '',
        teacher_html
    )

    teacher_path = os.path.join(base_dir, "teacher.html")
    with open(teacher_path, "w", encoding="utf-8") as f:
        f.write(teacher_html)
    print("[*] Created teacher.html cleanly (Zero admin items in DOM)!")

    # =========================================================================
    # 3. BUILD ADMIN.HTML (CỔNG QUẢN TRỊ VIÊN - TOÀN QUYỀN HỆ THỐNG)
    # =========================================================================
    admin_html = master_html

    admin_html = admin_html.replace(
        "<title>CodeArena - Nền tảng luyện tập lập trình trực tuyến & Chấm bài Sandbox</title>",
        "<title>CodeArena - Cổng Quản Trị Viên (Admin Portal)</title>"
    )
    admin_html = admin_html.replace(
        '<span class="text-[10px] text-slate-400 block font-normal tracking-wide">AUTOMATED ONLINE JUDGE</span>',
        '<span class="text-[10px] text-purple-400 block font-bold tracking-wide">CỔNG QUẢN TRỊ (ADMIN)</span>'
    )

    admin_html = re.sub(
        r'let currentUser = [^;]+;',
        'let currentUser = {\n      id: "ADMIN-01",\n      name: "Quản trị viên Hệ thống",\n      role: "Admin",\n      avatar: "AD",\n      email: "admin@haui.edu.vn",\n      status: "active"\n    };',
        admin_html
    )

    # Hiển thị mặc định cả nav-grading, nav-accounts, teacher-contest-action trong HTML cho Admin
    admin_html = admin_html.replace(
        'id="nav-grading" class="nav-btn px-3 sm:px-3.5 py-1.5 rounded-xl text-xs sm:text-sm font-medium transition items-center space-x-2 whitespace-nowrap text-slate-400 hover:text-white hover:bg-slate-800/80 border border-transparent shrink-0 hidden" style="display: none;"',
        'id="nav-grading" class="nav-btn px-3 sm:px-3.5 py-1.5 rounded-xl text-xs sm:text-sm font-medium transition flex items-center space-x-2 whitespace-nowrap text-slate-400 hover:text-white hover:bg-slate-800/80 border border-transparent shrink-0"'
    )
    admin_html = admin_html.replace(
        'id="nav-accounts" class="nav-btn px-3 sm:px-3.5 py-1.5 rounded-xl text-xs sm:text-sm font-medium transition items-center space-x-2 whitespace-nowrap text-slate-400 hover:text-white hover:bg-slate-800/80 border border-transparent shrink-0 hidden" style="display: none;"',
        'id="nav-accounts" class="nav-btn px-3 sm:px-3.5 py-1.5 rounded-xl text-xs sm:text-sm font-medium transition flex items-center space-x-2 whitespace-nowrap text-slate-400 hover:text-white hover:bg-slate-800/80 border border-transparent shrink-0"'
    )
    admin_html = admin_html.replace(
        'id="nav-logs" class="nav-btn px-3 sm:px-3.5 py-1.5 rounded-xl text-xs sm:text-sm font-medium transition items-center space-x-2 whitespace-nowrap text-slate-400 hover:text-white hover:bg-slate-800/80 border border-transparent shrink-0 hidden" style="display: none;"',
        'id="nav-logs" class="nav-btn px-3 sm:px-3.5 py-1.5 rounded-xl text-xs sm:text-sm font-medium transition flex items-center space-x-2 whitespace-nowrap text-slate-400 hover:text-white hover:bg-slate-800/80 border border-transparent shrink-0"'
    )
    admin_html = admin_html.replace(
        'id="teacher-contest-action" class="hidden items-center gap-2" style="display: none;"',
        'id="teacher-contest-action" class="flex items-center gap-2"'
    )

    admin_path = os.path.join(base_dir, "admin.html")
    with open(admin_path, "w", encoding="utf-8") as f:
        f.write(admin_html)
    print("[*] Created admin.html successfully!")

if __name__ == "__main__":
    build_portals()
