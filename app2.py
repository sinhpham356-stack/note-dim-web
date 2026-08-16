import streamlit as st
from PIL import Image
from streamlit_drawable_canvas import st_canvas
import io
from pptx import Presentation
from pptx.util import Inches

# Cấu hình trang
st.set_page_config(page_title="Note-Dim Web V10", layout="wide")

# --- KHỞI TẠO BỘ NHỚ TẠM (SESSION STATE) ---
if 'project_slides' not in st.session_state:
    st.session_state.project_slides = []

# --- HÀM HỖ TRỢ XUẤT FILE ---
def create_pdf(images):
    buf = io.BytesIO()
    if images:
        # Chuyển đổi tất cả ảnh sang RGB (bắt buộc đối với PDF)
        rgb_images = [img.convert('RGB') for img in images]
        # Lưu ảnh đầu tiên và đính kèm các ảnh còn lại vào cùng 1 file
        rgb_images[0].save(buf, format='PDF', save_all=True, append_images=rgb_images[1:])
    buf.seek(0)
    return buf.getvalue()

def create_pptx(images):
    prs = Presentation()
    for img in images:
        # Chọn layout slide trắng (blank)
        slide = prs.slides.add_slide(prs.slide_layouts[6])
        
        # Lưu ảnh từ dạng PIL vào bộ đệm tạm để đưa vào PPTX
        img_io = io.BytesIO()
        img.save(img_io, format='PNG')
        img_io.seek(0)
        
        # Chèn ảnh vào slide (tự động khít chiều rộng của slide)
        slide.shapes.add_picture(img_io, Inches(0), Inches(0), width=prs.slide_width)
        
    buf = io.BytesIO()
    prs.save(buf)
    buf.seek(0)
    return buf.getvalue()

# --- GIAO DIỆN QUẢN LÝ DỰ ÁN (SIDEBAR) ---
with st.sidebar:
    st.header("📑 Danh sách Trang (Slide)")
    st.write(f"Đang có: **{len(st.session_state.project_slides)}** ảnh")
    
    if len(st.session_state.project_slides) > 0:
        # Hiển thị ảnh thu nhỏ (thumbnail)
        for i, img in enumerate(st.session_state.project_slides):
            st.image(img, caption=f"Trang {i+1}", use_container_width=True)
            
        st.write("---")
        st.subheader("📥 Xuất Dự Án")
        
        # Nút xuất PDF
        st.download_button(
            label="📄 Tải xuống file PDF",
            data=create_pdf(st.session_state.project_slides),
            file_name="Du_An_Note_Dim.pdf",
            mime="application/pdf"
        )
        
        # Nút xuất PPTX
        st.download_button(
            label="📊 Tải xuống file PowerPoint",
            data=create_pptx(st.session_state.project_slides),
            file_name="Du_An_Note_Dim.pptx",
            mime="application/vnd.openxmlformats-officedocument.presentationml.presentation"
        )
        
        # Nút xóa toàn bộ dự án
        if st.button("🗑️ Xóa toàn bộ dự án"):
            st.session_state.project_slides = []
            st.rerun()

# --- GIAO DIỆN CHÍNH (MAIN AREA) ---
st.title("📏 Công cụ Note-Dim (Phiên bản Web)")
st.markdown("1. Tải ảnh lên -> 2. Vẽ/Ghi chú -> 3. Nhấn **Thêm vào Dự án** -> 4. Tải file PPTX/PDF ở menu bên trái.")

uploaded_file = st.file_uploader("📂 Tải ảnh lên (Hỗ trợ kéo thả hoặc Ctrl+V)", type=["png", "jpg", "jpeg"])

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    
    st.write("---")
    col1, col2, col3 = st.columns([2, 2, 2])
    with col1:
        drawing_mode = st.selectbox("🖱️ Chọn công cụ:", ("line", "freedraw", "rect", "transform", "polygon"))
    with col2:
        stroke_width = st.slider("📐 Độ dày nét:", 1, 10, 3)
    with col3:
        stroke_color = st.color_picker("🎨 Màu nét/Chữ:", "#FF0000")

    # Tính toán kích thước hiển thị
    canvas_width = 1000
    canvas_height = int((image.height / image.width) * canvas_width)
    
    st.write("### 🖼️ Trình chỉnh sửa")
    canvas_result = st_canvas(
        fill_color="rgba(0, 0, 0, 0)",
        stroke_width=stroke_width,
        stroke_color=stroke_color,
        background_image=image,
        update_streamlit=True,
        width=canvas_width,
        height=canvas_height,
        drawing_mode=drawing_mode,
        key="canvas",
    )

    if canvas_result.image_data is not None:
        # Gộp nét vẽ và ảnh gốc
        drawn_image = Image.fromarray(canvas_result.image_data.astype("uint8"), "RGBA")
        drawn_image = drawn_image.resize(image.size, Image.Resampling.LANCZOS)
        
        final_img = image.convert("RGBA").copy()
        final_img.alpha_composite(drawn_image)
        final_img = final_img.convert("RGB")

        st.write("---")
        
        # Nút chức năng mới: Thêm ảnh vào Project/Slide
        if st.button("➕ Thêm ảnh này vào Dự Án (Slide)", type="primary"):
            st.session_state.project_slides.append(final_img)
            st.success(f"Đã thêm thành công! Tổng cộng: {len(st.session_state.project_slides)} trang. (Xem menu bên trái)")
            # Dùng st.rerun() để giao diện cập nhật ngay lập tức cột bên trái
            st.rerun()

        # Nút tải ảnh lẻ (dành cho ai chỉ muốn tải 1 ảnh)
        buf_single = io.BytesIO()
        final_img.save(buf_single, format="JPEG", quality=95)
        st.download_button(
            label="💾 Tải ảnh lẻ này xuống",
            data=buf_single.getvalue(),
            file_name="note_dim_single.jpg",
            mime="image/jpeg",
        )