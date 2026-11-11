# -*- coding: utf-8 -*-
"""
Script to:
1. Replace emojis with professional SVG icons and academic badges in index.html.
2. Add Gemini AI Configuration Badge & Modal to index.html.
3. Add JavaScript methods for AI status check and key configuration.
"""
import re

def main():
    with open('index.html', 'r', encoding='utf-8') as f:
        html = f.read()

    print(f"Original file length: {len(html)}")

    # 1. Editor Subtabs (L370, L374, L378)
    html = html.replace('<span>🖥️ Console / Terminal</span>', '<span>Terminal / Console</span>')
    html = html.replace('<span id="console-subtab-verdict-text">📊 Kết quả Chấm & AI</span>', '<span id="console-subtab-verdict-text">Kết quả Chấm & AI</span>')
    html = html.replace('<span>⚙️ Test Case tùy chỉnh</span>', '<span>Test Case tùy chỉnh</span>')

    # 2. Terminal Stats (L407, L408)
    old_term_stat = """                    <span id="terminal-runtime-badge" class="text-amber-400 font-mono whitespace-nowrap hidden">⏱ <span id="term-rt">0</span> ms</span>
                    <span id="terminal-memory-badge" class="text-cyan-400 font-mono whitespace-nowrap hidden">💾 <span id="term-mem">0</span> MB</span>"""
    
    new_term_stat = """                    <span id="terminal-runtime-badge" class="text-amber-400 font-mono whitespace-nowrap hidden inline-flex items-center gap-1"><svg class="w-3 h-3 text-amber-400 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"/></svg><span id="term-rt">0</span> ms</span>
                    <span id="terminal-memory-badge" class="text-cyan-400 font-mono whitespace-nowrap hidden inline-flex items-center gap-1"><svg class="w-3 h-3 text-cyan-400 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 3v2m6-2v2M9 19v2m6-2v2M5 9H3m2 6H3m18-6h-2m2 6h-2M7 19h10a2 2 0 002-2V7a2 2 0 00-2-2H7a2 2 0 00-2 2v10a2 2 0 002 2zM9 9h6v6H9V9z"/></svg><span id="term-mem">0</span> MB</span>"""
    html = html.replace(old_term_stat, new_term_stat)

    # 3. Contest cancelled warning badge (L733)
    old_c_warn = """          <div class="w-10 h-10 rounded-xl bg-rose-500/20 text-rose-400 flex items-center justify-center font-bold text-lg shrink-0">
            ⚠
          </div>"""
    new_c_warn = """          <div class="w-10 h-10 rounded-xl bg-rose-500/20 text-rose-400 flex items-center justify-center shrink-0">
            <svg class="w-6 h-6 text-rose-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/></svg>
          </div>"""
    html = html.replace(old_c_warn, new_c_warn)

    # 4. Modal Plagiarism Warning (L1356)
    html = html.replace(
        '<span class="font-bold text-rose-400 whitespace-nowrap">⚠ CẢNH BÁO GIAN LẬN:</span>',
        '<span class="font-bold text-rose-400 whitespace-nowrap flex items-center gap-1.5"><svg class="w-4 h-4 text-rose-400 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/></svg> CẢNH BÁO GIAN LẬN:</span>'
    )

    # 5. Rubric criteria in Teacher Modal (L1396-1404)
    old_rubric = """            <!-- Rubric Checklist -->
            <div id="modal-ai-rubric" class="space-y-1 text-[12px] pt-1 border-t border-indigo-900/40">
              <div class="flex items-center justify-between text-emerald-400">
                <span class="whitespace-nowrap">✓ Đáp ứng đúng yêu cầu & logic bài toán</span>
                <span class="font-bold whitespace-nowrap">Đạt 100%</span>
              </div>
              <div class="flex items-center justify-between text-emerald-400">
                <span class="whitespace-nowrap">✓ Tối ưu độ phức tạp thời gian O(N log N)</span>
                <span class="font-bold whitespace-nowrap">Tối ưu</span>
              </div>
              <div class="flex items-center justify-between text-emerald-400">
                <span class="whitespace-nowrap">✓ Xử lý tốt các trường hợp biên & ngoại lệ</span>
                <span class="font-bold whitespace-nowrap">Đạt</span>
              </div>
            </div>"""

    new_rubric = """            <!-- Rubric Checklist -->
            <div id="modal-ai-rubric" class="space-y-1.5 text-[12px] pt-1 border-t border-indigo-900/40">
              <div class="flex items-center justify-between text-emerald-400">
                <span class="whitespace-nowrap flex items-center gap-1.5"><svg class="w-3.5 h-3.5 text-emerald-400 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M5 13l4 4L19 7"/></svg> Đáp ứng đúng yêu cầu & logic bài toán</span>
                <span class="font-bold whitespace-nowrap">Đạt 100%</span>
              </div>
              <div class="flex items-center justify-between text-emerald-400">
                <span class="whitespace-nowrap flex items-center gap-1.5"><svg class="w-3.5 h-3.5 text-emerald-400 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M5 13l4 4L19 7"/></svg> Tối ưu độ phức tạp thời gian O(N log N)</span>
                <span class="font-bold whitespace-nowrap">Tối ưu</span>
              </div>
              <div class="flex items-center justify-between text-emerald-400">
                <span class="whitespace-nowrap flex items-center gap-1.5"><svg class="w-3.5 h-3.5 text-emerald-400 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M5 13l4 4L19 7"/></svg> Xử lý tốt các trường hợp biên & ngoại lệ</span>
                <span class="font-bold whitespace-nowrap">Đạt</span>
              </div>
            </div>"""
    html = html.replace(old_rubric, new_rubric)

    # 6. Cancel Contest Modal cross icon (L1472)
    old_cancel_icon = """        <div class="w-12 h-12 rounded-xl bg-rose-500/20 flex items-center justify-center font-bold text-xl shrink-0">
          ✕
        </div>"""
    new_cancel_icon = """        <div class="w-12 h-12 rounded-xl bg-rose-500/20 flex items-center justify-center text-rose-400 shrink-0">
          <svg class="w-6 h-6 text-rose-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
        </div>"""
    html = html.replace(old_cancel_icon, new_cancel_icon)

    # 7. Delete modal warnings (L1669, L1708)
    html = html.replace(
        '<p class="text-[11px] text-amber-400">⚠️ Lưu ý: Tất cả dữ liệu liên kết với tài khoản này trong CSDL SQLite sẽ bị xoá vĩnh viễn.</p>',
        '<p class="text-[11px] text-amber-400 flex items-center gap-1.5"><svg class="w-3.5 h-3.5 text-amber-400 shrink-0 inline" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/></svg> <span>Lưu ý: Tất cả dữ liệu liên kết với tài khoản này trong CSDL SQLite sẽ bị xoá vĩnh viễn.</span></p>'
    )
    html = html.replace(
        '<p class="text-[11px] text-emerald-400">ℹ️ Sau khi xóa, sinh viên sẽ được mở khóa quyền và có thể nộp lại bài làm mới cho bài tập này.</p>',
        '<p class="text-[11px] text-emerald-400 flex items-center gap-1.5"><svg class="w-3.5 h-3.5 text-emerald-400 shrink-0 inline" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/></svg> <span>Sau khi xóa, sinh viên sẽ được mở khóa quyền và có thể nộp lại bài làm mới cho bài tập này.</span></p>'
    )

    # 8. Seed submissions aiRubric text (L2049, L2077)
    html = html.replace(
        'aiRubric: "✓ Đáp ứng 100% yêu cầu đề bài; Tối ưu tra cứu Hash Map O(N); Code sạch sẽ."',
        'aiRubric: "Đáp ứng 100% yêu cầu đề bài; Tối ưu tra cứu Hash Map O(N); Code sạch sẽ."'
    )
    html = html.replace(
        'aiRubric: "✕ Vi phạm quy chế liêm chính học thuật: Độ trùng lặp 94.6% với bài nộp khác."',
        'aiRubric: "Cảnh báo liêm chính học thuật: Độ trùng lặp 94.6% vượt ngưỡng an toàn."'
    )

    # 9. showToast Utility (L2097-2114)
    old_show_toast = """    // Toast Notification Utility
    function showToast(message, type = 'success') {
      const container = document.getElementById('toast-container');
      const toast = document.createElement('div');
      toast.className = `p-3 rounded-xl border text-xs font-semibold shadow-xl flex items-center space-x-2 transition-all duration-300 pointer-events-auto ${
        type === 'success' 
          ? 'bg-slate-900 border-emerald-500/50 text-emerald-300' 
          : (type === 'warn' ? 'bg-slate-900 border-amber-500/50 text-amber-300' : 'bg-slate-900 border-rose-500/50 text-rose-300')
      }`;
      const icon = type === 'success' ? '✓' : (type === 'warn' ? '⚠' : '✕');
      toast.innerHTML = `<span class="font-bold shrink-0">${icon}</span><span class="whitespace-nowrap">${message}</span>`;
      container.appendChild(toast);

      setTimeout(() => {
        toast.style.opacity = '0';
        setTimeout(() => toast.remove(), 300);
      }, 3500);
    }"""

    new_show_toast = """    // Toast Notification Utility with Professional SVGs
    function showToast(message, type = 'success') {
      const container = document.getElementById('toast-container');
      if (!container) return;
      const toast = document.createElement('div');
      toast.className = `p-3 rounded-xl border text-xs font-semibold shadow-2xl flex items-center space-x-2.5 transition-all duration-300 pointer-events-auto backdrop-blur-md ${
        type === 'success' 
          ? 'bg-slate-900/95 border-emerald-500/50 text-emerald-300' 
          : (type === 'warn' ? 'bg-slate-900/95 border-amber-500/50 text-amber-300' : 'bg-slate-900/95 border-rose-500/50 text-rose-300')
      }`;
      
      const iconSvg = type === 'success'
        ? '<svg class="w-4 h-4 text-emerald-400 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M5 13l4 4L19 7"/></svg>'
        : (type === 'warn'
            ? '<svg class="w-4 h-4 text-amber-400 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/></svg>'
            : '<svg class="w-4 h-4 text-rose-400 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>');

      // Clean any accidental leading emoji
      const cleanMessage = String(message || '').replace(/^[⚠️ℹ️✓✕🚨⏱💾⏳📝🔒]+\\s*/u, '');
      toast.innerHTML = `<span class="shrink-0 flex items-center">${iconSvg}</span><span class="whitespace-nowrap">${cleanMessage}</span>`;
      container.appendChild(toast);

      setTimeout(() => {
        toast.style.opacity = '0';
        setTimeout(() => toast.remove(), 300);
      }, 3500);
    }"""
    html = html.replace(old_show_toast, new_show_toast)

    # 10. Toast warning calls with emoji prefixes
    html = html.replace('showToast("⚠️ Quyền bị từ chối! Chức năng này chỉ dành cho Quản trị viên (Admin).", "error");', 'showToast("Quyền bị từ chối! Chức năng này chỉ dành cho Quản trị viên (Admin).", "error");')
    html = html.replace('showToast("⚠️ Quyền bị từ chối! Chức năng này chỉ dành cho Giảng viên hoặc Quản trị viên.", "error");', 'showToast("Quyền bị từ chối! Chức năng này chỉ dành cho Giảng viên hoặc Quản trị viên.", "error");')
    html = html.replace('showToast("⚠️ Quyền truy cập bị từ chối! Tab Quản lý Tài khoản chỉ dành cho Quản trị viên (Admin).", "error");', 'showToast("Quyền truy cập bị từ chối! Tab Quản lý Tài khoản chỉ dành cho Quản trị viên (Admin).", "error");')
    html = html.replace('showToast("⚠️ Quyền truy cập bị từ chối! Tab Xem bài & Chấm điểm chỉ dành cho Giảng viên.", "error");', 'showToast("Quyền truy cập bị từ chối! Tab Xem bài & Chấm điểm chỉ dành cho Giảng viên.", "error");')
    html = html.replace('showToast("ℹ️ Vui lòng đăng nhập để xem Kết quả & Nhận xét các bài đã được chấm điểm của bạn!", "warn");', 'showToast("Vui lòng đăng nhập để xem Kết quả & Nhận xét các bài đã được chấm điểm của bạn!", "warn");')
    html = html.replace('showToast("⚠️ Bạn cần đăng nhập tài khoản Sinh viên hoặc Giảng viên để nộp bài thi!", "warn");', 'showToast("Bạn cần đăng nhập tài khoản Sinh viên hoặc Giảng viên để nộp bài thi!", "warn");')
    html = html.replace('showToast(`⚠️ Bạn đã nộp bài [${prob.name}] rồi (${alreadySubmitted.id})! Mỗi học sinh chỉ được nộp bài 1 lần duy nhất cho mỗi bài.`, "warn");', 'showToast(`Bạn đã nộp bài [${prob.name}] rồi (${alreadySubmitted.id})! Mỗi học sinh chỉ được nộp bài 1 lần duy nhất cho mỗi bài.`, "warn");')
    html = html.replace('showToast(`⚠️ ${errMsg}`, "error");', 'showToast(errMsg, "error");')

    # 11. Subtab label update in JS (L2221-2223)
    html = html.replace('subtabVerdictText.innerText = "📊 Kết quả Chấm & AI";', 'subtabVerdictText.innerText = "Kết quả Chấm & AI";')
    html = html.replace('subtabVerdictText.innerText = "📝 Trạng thái Nộp bài";', 'subtabVerdictText.innerText = "Trạng thái Nộp bài";')

    # 12. Terminal output execute process runtime badge (L4037, L4050, L4055, L4056, L4114)
    html = html.replace(
        '<span>⏱ ${data.runtime_ms} ms &bull; 💾 ${data.memory_mb} MB</span>',
        '<span>${data.runtime_ms} ms &bull; ${data.memory_mb} MB</span>'
    )
    html = html.replace(
        "${isSuccess ? '✓ Thực thi thành công (Success)' : '✕ ' + data.status}",
        "${isSuccess ? 'Thực thi thành công (Success)' : data.status}"
    )
    html = html.replace(
        '<span class="text-amber-400 whitespace-nowrap">⏱ ${data.runtime_ms} ms</span>',
        '<span class="text-amber-400 whitespace-nowrap font-mono">${data.runtime_ms} ms</span>'
    )
    html = html.replace(
        '<span class="text-cyan-400 whitespace-nowrap">💾 ${data.memory_mb} MB</span>',
        '<span class="text-cyan-400 whitespace-nowrap font-mono">${data.memory_mb} MB</span>'
    )
    html = html.replace(
        '<span>⏱ 18.0 ms &bull; 💾 12.5 MB</span>',
        '<span>18.0 ms &bull; 12.5 MB</span>'
    )

    # 13. Verdict card icon & tags (L4191, L4202, L4218, L4304, L4324, L4335, L4351)
    old_verdict_icon_teacher = """                    <div class="w-10 h-10 rounded-lg ${isAccepted ? 'bg-emerald-500/20 text-emerald-400' : 'bg-rose-500/20 text-rose-400'} flex items-center justify-center font-black text-lg shrink-0">
                      ${isAccepted ? '✓' : (isCheat ? '🚨' : '✕')}
                    </div>"""

    new_verdict_icon_teacher = """                    <div class="w-10 h-10 rounded-lg ${isAccepted ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30' : 'bg-rose-500/20 text-rose-400 border border-rose-500/30'} flex items-center justify-center shrink-0">
                      ${isAccepted 
                        ? '<svg class="w-6 h-6 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M5 13l4 4L19 7"/></svg>' 
                        : (isCheat 
                            ? '<svg class="w-6 h-6 text-rose-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/></svg>' 
                            : '<svg class="w-6 h-6 text-rose-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>')}
                    </div>"""
    html = html.replace(old_verdict_icon_teacher, new_verdict_icon_teacher)

    html = html.replace('<span class="text-amber-400">⏱ ${newSub.runtime}</span>', '<span class="text-amber-400 font-mono">${newSub.runtime}</span>')

    old_student_ac_icon = """                    <div class="w-11 h-11 rounded-xl bg-emerald-500/20 text-emerald-400 flex items-center justify-center font-black text-xl shrink-0 border border-emerald-500/30">
                      ✓
                    </div>"""
    new_student_ac_icon = """                    <div class="w-11 h-11 rounded-xl bg-emerald-500/20 text-emerald-400 flex items-center justify-center shrink-0 border border-emerald-500/30">
                      <svg class="w-6 h-6 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M5 13l4 4L19 7"/></svg>
                    </div>"""
    html = html.replace(old_student_ac_icon, new_student_ac_icon)

    # Local fallback card icons
    html = html.replace(
        'aiRubric: isAccepted ? "✓ Đạt 100% yêu cầu đề bài; Tối ưu giải thuật; Xử lý đầy đủ trường hợp biên." : "Chưa vượt qua toàn bộ Test Case của đề bài."',
        'aiRubric: isAccepted ? "Đạt 100% yêu cầu đề bài; Tối ưu giải thuật; Xử lý đầy đủ trường hợp biên." : "Chưa vượt qua toàn bộ Test Case của đề bài."'
    )

    old_fb_verdict_icon = """                  <div class="w-10 h-10 rounded-lg ${isAccepted ? 'bg-emerald-500/20 text-emerald-400' : 'bg-rose-500/20 text-rose-400'} flex items-center justify-center font-black text-lg shrink-0">
                    ${isAccepted ? '✓' : '✕'}
                  </div>"""
    new_fb_verdict_icon = """                  <div class="w-10 h-10 rounded-lg ${isAccepted ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30' : 'bg-rose-500/20 text-rose-400 border border-rose-500/30'} flex items-center justify-center shrink-0">
                    ${isAccepted 
                      ? '<svg class="w-6 h-6 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M5 13l4 4L19 7"/></svg>' 
                      : '<svg class="w-6 h-6 text-rose-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>'}
                  </div>"""
    html = html.replace(old_fb_verdict_icon, new_fb_verdict_icon)

    html = html.replace('<span class="text-amber-400">⏱ ${newSubmission.runtime}</span>', '<span class="text-amber-400 font-mono">${newSubmission.runtime}</span>')

    # 14. Grading Table Badges (L4440, L4445, L4447)
    old_grade_badges = """        let astBadge = isPlagiarized 
          ? `<span class="px-2 py-0.5 rounded text-[11px] font-bold bg-rose-950 text-rose-400 border border-rose-800 whitespace-nowrap">🚨 ${sub.similarityRate}%</span>` 
          : `<span class="px-2 py-0.5 rounded text-[11px] text-slate-400 bg-slate-800 whitespace-nowrap">${sub.similarityRate}%</span>`;

        let statusBadge = '';
        if (sub.isGradedByTeacher) {
          statusBadge = '<span class="px-2 py-0.5 rounded text-[11px] font-bold bg-emerald-950 text-emerald-400 border border-emerald-800 whitespace-nowrap">✓ Đã chấm</span>';
        } else {
          statusBadge = '<span class="px-2 py-0.5 rounded text-[11px] font-medium bg-amber-950 text-amber-300 border border-amber-800 whitespace-nowrap">⏳ Chờ chấm</span>';
        }"""

    new_grade_badges = """        let astBadge = isPlagiarized 
          ? `<span class="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[11px] font-bold bg-rose-950 text-rose-400 border border-rose-800 whitespace-nowrap"><svg class="w-3 h-3 text-rose-400 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/></svg> ${sub.similarityRate}%</span>` 
          : `<span class="px-2 py-0.5 rounded text-[11px] text-slate-400 bg-slate-800 whitespace-nowrap">${sub.similarityRate}%</span>`;

        let statusBadge = '';
        if (sub.isGradedByTeacher) {
          statusBadge = '<span class="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[11px] font-bold bg-emerald-950 text-emerald-400 border border-emerald-800 whitespace-nowrap"><svg class="w-3 h-3 text-emerald-400 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M5 13l4 4L19 7"/></svg> Đã chấm</span>';
        } else {
          statusBadge = '<span class="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[11px] font-medium bg-amber-950 text-amber-300 border border-amber-800 whitespace-nowrap"><svg class="w-3 h-3 text-amber-400 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"/></svg> Chờ chấm</span>';
        }"""
    html = html.replace(old_grade_badges, new_grade_badges)

    # 15. Student Results tab empty & pending screens (L4724, L4763, L4780, L4807, L4816, L4879)
    old_results_lock = """            <div class="w-16 h-16 mx-auto rounded-2xl bg-indigo-600/10 border border-indigo-500/20 flex items-center justify-center text-indigo-400 font-bold text-2xl shrink-0">
              🔒
            </div>"""
    new_results_lock = """            <div class="w-16 h-16 mx-auto rounded-2xl bg-indigo-600/10 border border-indigo-500/20 flex items-center justify-center text-indigo-400 shrink-0">
              <svg class="w-8 h-8 text-indigo-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"/></svg>
            </div>"""
    html = html.replace(old_results_lock, new_results_lock)

    old_results_empty = """              <div class="w-16 h-16 mx-auto rounded-2xl bg-indigo-600/10 border border-indigo-500/20 flex items-center justify-center text-indigo-400 font-bold text-2xl shrink-0">
                📝
              </div>"""
    new_results_empty = """              <div class="w-16 h-16 mx-auto rounded-2xl bg-indigo-600/10 border border-indigo-500/20 flex items-center justify-center text-indigo-400 shrink-0">
                <svg class="w-8 h-8 text-indigo-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/></svg>
              </div>"""
    html = html.replace(old_results_empty, new_results_empty)

    old_results_pending = """              <div class="w-16 h-16 mx-auto rounded-2xl bg-amber-500/10 border border-amber-500/30 flex items-center justify-center text-amber-400 font-bold text-2xl shrink-0">
                ⏳
              </div>"""
    new_results_pending = """              <div class="w-16 h-16 mx-auto rounded-2xl bg-amber-500/10 border border-amber-500/30 flex items-center justify-center text-amber-400 shrink-0">
                <svg class="w-8 h-8 text-amber-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
              </div>"""
    html = html.replace(old_results_pending, new_results_pending)

    html = html.replace(
        "opt.innerText = `✓ [ĐÃ CÓ ĐIỂM: ${sub.score}/10] ${sub.id}: ${sub.problemId} - ${sub.problemName}`;",
        "opt.innerText = `[ĐÃ CÓ ĐIỂM: ${sub.score}/10] ${sub.id}: ${sub.problemId} - ${sub.problemName}`;"
    )
    html = html.replace(
        "opt.innerText = `⏳ [ĐANG CHỜ CHẤM] ${sub.id}: ${sub.problemId} - ${sub.problemName}`;",
        "opt.innerText = `[ĐANG CHỜ CHẤM] ${sub.id}: ${sub.problemId} - ${sub.problemName}`;"
    )

    old_results_sub_pending = """            <div class="w-16 h-16 mx-auto rounded-2xl bg-amber-500/10 border border-amber-500/30 flex items-center justify-center text-amber-400 font-bold text-2xl shrink-0">
              ⏳
            </div>"""
    html = html.replace(old_results_sub_pending, new_results_pending)

    # 16. Rubric footer in results tab (L5023, L5027, L5031)
    old_res_rubric = """                  <div class="flex items-center justify-between text-emerald-400">
                    <span class="whitespace-nowrap">✓ Tính đúng đắn của giải thuật</span>
                    <span class="font-bold whitespace-nowrap">${sub.testPassed} Pass</span>
                  </div>
                  <div class="flex items-center justify-between text-emerald-400">
                    <span class="whitespace-nowrap">✓ Tối ưu độ phức tạp thuật toán</span>
                    <span class="font-bold whitespace-nowrap">Đạt chuẩn</span>
                  </div>
                  <div class="flex items-center justify-between text-emerald-400">
                    <span class="whitespace-nowrap">✓ Liêm chính học thuật (AST Winnowing)</span>
                    <span class="font-bold whitespace-nowrap">${sub.similarityRate}% (An toàn)</span>
                  </div>"""

    new_res_rubric = """                  <div class="flex items-center justify-between text-emerald-400">
                    <span class="whitespace-nowrap flex items-center gap-1.5"><svg class="w-3.5 h-3.5 text-emerald-400 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M5 13l4 4L19 7"/></svg> Tính đúng đắn của giải thuật</span>
                    <span class="font-bold whitespace-nowrap">${sub.testPassed} Pass</span>
                  </div>
                  <div class="flex items-center justify-between text-emerald-400">
                    <span class="whitespace-nowrap flex items-center gap-1.5"><svg class="w-3.5 h-3.5 text-emerald-400 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M5 13l4 4L19 7"/></svg> Tối ưu độ phức tạp thuật toán</span>
                    <span class="font-bold whitespace-nowrap">Đạt chuẩn</span>
                  </div>
                  <div class="flex items-center justify-between text-emerald-400">
                    <span class="whitespace-nowrap flex items-center gap-1.5"><svg class="w-3.5 h-3.5 text-emerald-400 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M5 13l4 4L19 7"/></svg> Liêm chính học thuật (AST Winnowing)</span>
                    <span class="font-bold whitespace-nowrap">${sub.similarityRate}% (An toàn)</span>
                  </div>"""
    html = html.replace(old_res_rubric, new_res_rubric)

    # 17. Add AI Engine Status Badge to Header next to backend-status
    old_backend_status = """              <span id="header-backend-status" class="inline-flex items-center gap-1.5 px-2 py-0.5 text-xs font-semibold bg-emerald-500/10 text-emerald-400 rounded border border-emerald-500/30 whitespace-nowrap">
                <span class="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
                <span>Backend: Online</span>
              </span>"""

    new_backend_status = """              <span id="header-backend-status" class="inline-flex items-center gap-1.5 px-2 py-0.5 text-xs font-semibold bg-emerald-500/10 text-emerald-400 rounded border border-emerald-500/30 whitespace-nowrap">
                <span class="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
                <span>Backend: Online</span>
              </span>
              <button onclick="openAIConfigModal()" id="header-ai-status" title="Bấm để xem hoặc cấu hình Google Gemini API Key" class="inline-flex items-center gap-1.5 px-2 py-0.5 text-xs font-semibold bg-indigo-500/10 hover:bg-indigo-500/20 text-indigo-300 rounded border border-indigo-500/30 whitespace-nowrap transition cursor-pointer">
                <svg class="w-3.5 h-3.5 text-indigo-400 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/></svg>
                <span id="ai-engine-label">AI: Khởi tạo...</span>
              </button>"""
    html = html.replace(old_backend_status, new_backend_status)

    # 18. Add Modal 9: AI Config Modal right before FOOTER
    ai_modal_code = """  <!-- ========================================================= -->
  <!-- MODAL 9: CẤU HÌNH GOOGLE GEMINI AI KEY (AI CONFIG MODAL)   -->
  <!-- ========================================================= -->
  <div id="ai-config-modal" class="fixed inset-0 bg-slate-950/80 backdrop-blur-md z-[130] hidden items-center justify-center p-4">
    <div class="bg-slate-900 border border-indigo-500/50 rounded-2xl max-w-md w-full p-6 shadow-2xl relative space-y-4">
      <div class="flex items-center space-x-3 text-indigo-400">
        <div class="w-12 h-12 rounded-xl bg-indigo-500/20 flex items-center justify-center text-indigo-400 font-bold text-xl shrink-0">
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/></svg>
        </div>
        <div>
          <h3 class="text-base font-bold text-white">Động cơ Chấm bài AI (Gemini / AST)</h3>
          <p class="text-xs text-indigo-300">Tích hợp Google Gemini REST API & AST Heuristic</p>
        </div>
      </div>

      <div class="bg-slate-950 border border-slate-800 p-4 rounded-xl text-xs space-y-3 text-slate-300">
        <div class="flex items-center justify-between pb-2 border-b border-slate-800">
          <span class="text-slate-400">Trạng thái AI Engine:</span>
          <span id="modal-ai-status-tag" class="px-2 py-0.5 rounded font-mono font-bold text-[11px] bg-slate-800 text-slate-300">Đang kiểm tra...</span>
        </div>
        <div class="flex items-center justify-between pb-2 border-b border-slate-800">
          <span class="text-slate-400">Mô hình AI:</span>
          <span id="modal-ai-model-tag" class="text-indigo-300 font-mono font-bold">gemini-1.5-flash</span>
        </div>
        <div>
          <label class="block text-slate-400 mb-1 font-medium">Google Gemini API Key:</label>
          <input type="password" id="input-gemini-key" placeholder="AIzaSy... (dán API Key vào đây)" class="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-white font-mono text-xs focus:outline-none focus:border-indigo-500">
          <p class="text-[11px] text-slate-400 mt-1.5 leading-relaxed">
            API Key lấy miễn phí tại <a href="https://aistudio.google.com" target="_blank" class="text-indigo-400 underline hover:text-indigo-300">Google AI Studio</a>. Nếu để trống hoặc offline, hệ thống tự động kích hoạt bộ phân tích tĩnh <strong>AST Static Heuristic Engine</strong> (chuẩn O(N), độ sâu vòng lặp, đệ quy, không bị ngắt quãng).
          </p>
        </div>
      </div>

      <div class="flex items-center justify-end gap-2 pt-2">
        <button type="button" onclick="closeAIConfigModal()" class="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-semibold rounded-xl transition whitespace-nowrap">
          Đóng
        </button>
        <button type="button" id="btn-save-ai-key" onclick="saveGeminiApiKey()" class="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white font-bold text-xs rounded-xl shadow-lg shadow-indigo-600/30 transition flex items-center gap-1.5 whitespace-nowrap">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/></svg>
          <span>Lưu & Kích hoạt</span>
        </button>
      </div>
    </div>
  </div>

  <!-- FOOTER -->"""

    html = html.replace('  <!-- FOOTER -->', ai_modal_code)

    # 19. Add AI Javascript functions at the end of the script tag
    js_ai_methods = """
    // ==========================================
    // AI ENGINE & GEMINI CONFIGURATION MANAGEMENT
    // ==========================================
    let aiEngineInfo = {
      is_gemini_active: false,
      model: "gemini-1.5-flash",
      backend_online: false
    };

    async function checkAIStatus() {
      const labelEl = document.getElementById('ai-engine-label');
      const tagEl = document.getElementById('modal-ai-status-tag');
      const modelEl = document.getElementById('modal-ai-model-tag');

      try {
        const res = await fetch('http://localhost:8000/api/config/ai-status', { signal: AbortSignal.timeout(3500) });
        if (res.ok) {
          const data = await res.json();
          aiEngineInfo = data;
          aiEngineInfo.backend_online = true;

          if (labelEl) {
            if (data.is_gemini_active) {
              labelEl.innerHTML = '<span class="text-indigo-300 font-semibold">AI: Gemini 1.5</span> <span class="text-emerald-400 font-bold">[Live]</span>';
            } else {
              labelEl.innerHTML = '<span class="text-slate-300 font-medium">AI: AST Engine</span> <span class="text-amber-400 font-medium">[Local]</span>';
            }
          }

          if (tagEl) {
            if (data.is_gemini_active) {
              tagEl.className = "px-2 py-0.5 rounded font-mono font-bold text-[11px] bg-emerald-950 text-emerald-400 border border-emerald-800";
              tagEl.innerText = "Gemini 1.5 Flash (Online REST API)";
            } else {
              tagEl.className = "px-2 py-0.5 rounded font-mono font-bold text-[11px] bg-amber-950 text-amber-300 border border-amber-800";
              tagEl.innerText = "AST Static Heuristic (Offline Fallback)";
            }
          }

          if (modelEl) {
            modelEl.innerText = data.model || "gemini-1.5-flash";
          }
          return;
        }
      } catch (e) {
        // Backend offline fallback
      }

      aiEngineInfo.backend_online = false;
      if (labelEl) {
        labelEl.innerHTML = '<span class="text-slate-400 font-medium">AI: Client AST</span>';
      }
      if (tagEl) {
        tagEl.className = "px-2 py-0.5 rounded font-mono font-bold text-[11px] bg-slate-800 text-slate-400";
        tagEl.innerText = "Client Offline Heuristics";
      }
    }

    function openAIConfigModal() {
      const modal = document.getElementById('ai-config-modal');
      if (modal) {
        modal.classList.remove('hidden');
        modal.classList.add('flex');
        checkAIStatus();
      }
    }

    function closeAIConfigModal() {
      const modal = document.getElementById('ai-config-modal');
      if (modal) {
        modal.classList.add('hidden');
        modal.classList.remove('flex');
      }
    }

    async function saveGeminiApiKey() {
      const inputEl = document.getElementById('input-gemini-key');
      const btn = document.getElementById('btn-save-ai-key');
      if (!inputEl) return;

      const apiKey = inputEl.value.trim();
      if (!apiKey) {
        showToast("Vui lòng nhập API Key hợp lệ từ Google AI Studio!", "warn");
        return;
      }

      if (btn) {
        btn.disabled = true;
        btn.innerHTML = '<span class="animate-spin inline-block mr-1">⌛</span> Đang xác thực...';
      }

      try {
        const res = await fetch('http://localhost:8000/api/config/gemini-key', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ api_key: apiKey })
        });

        if (res.ok) {
          const result = await res.json();
          showToast(result.message || "Đã lưu Gemini API Key thành công!", "success");
          inputEl.value = '';
          await checkAIStatus();
          closeAIConfigModal();
        } else {
          showToast("Không thể lưu API Key vào backend!", "error");
        }
      } catch (err) {
        showToast("Không thể kết nối tới backend để cập nhật API Key!", "error");
      } finally {
        if (btn) {
          btn.disabled = false;
          btn.innerHTML = '<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/></svg> <span>Lưu & Kích hoạt</span>';
        }
      }
    }
"""
    # Insert right before </script>
    html = html.replace('  </script>\n</body>', js_ai_methods + '\n  </script>\n</body>')

    # Also add checkAIStatus call inside init
    init_call = """      // Khởi tạo trạng thái ban đầu
      updateHeaderUserUI();
      checkAIStatus();"""
    html = html.replace('      // Khởi tạo trạng thái ban đầu\n      updateHeaderUserUI();', init_call)

    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"Updated file length: {len(html)}")

if __name__ == '__main__':
    main()
