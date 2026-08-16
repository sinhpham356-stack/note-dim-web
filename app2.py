import streamlit as st
from PIL import Image
from streamlit_drawable_canvas import st_canvas
import io
from pptx import Presentation
from pptx.util import Inches

# Cấu hình trang
st.set_page_config(page_title="Note-Dim Web V10", layout="wide")

# KHỞI TẠO BỘ NHỚ TẠM
if 'project_slides' not in st.session_state:
    st.session_state.project_slides = []

# CÁC HÀM XUẤT FILE
def create_pdf(images):
    buf = io.BytesIO()
    if images:
        rgb_images = [img.convert('RGB') for img in images]
        rgb_images[0].save(buf, format='PDF', save_all=True, append_images=rgb_images[1:])
    buf.seek(0)
    return buf.getvalue()

def create_pptx(images):
    prs = Presentation()
    for img in images:
        slide = prs.slides.add_slide(prs.slide_layouts[6])
        img_io = io.BytesIO()
        img.save(img_io, format='PNG')
        img_io.seek(0)
        slide.shapes.add_picture(img_io, Inches(0), Inches(0), width=prs.slide_width)
    buf = io.BytesIO()
    prs.save(buf)
    buf.seek(0)
    return buf.getvalue()

# GIAO DIỆN CỘT BÊN TRÁI (QUẢN LÝ SLIDE)
with st.sidebar:
    st.header("📑 Danh sách Trang (Slide)")
    st.write(f"Đang có: **{len(st.session_state.project_slides)}** ảnh")
    
    if len(st.session_state.project_slides) > 0:
        for i, img in enumerate(st.session_state.project_slides):
            st.image(img, caption=f"Trang {i+1}", use_container_width=True)
            
        st.write("---")
        st.subheader("📥 Xuất Dự Án")
        
        st.download_button(
            label="📄 Tải xuống file PDF",
            data=create_pdf(st.session_state.project_slides),
            file_name="Du_An_Note_Dim.pdf",
            mime="application/pdf"
        )
        
        st.download_button(
            label="📊 Tải xuống file PowerPoint",
            data=create_pptx(st.session_state.project_slides),
            file_name="Du_An_Note_Dim.pptx",
            mime="application/vnd.openxmlformats-officedocument.presentationml.presentation"
        )
        
        if st.button("🗑️ Xóa toàn bộ dự án"):
            st.session_state.project_slides = []
            st.rerun()

# GIAO DIỆN CHÍNH
st.title("📏 Công cụ Note-Dim (Bản Web có Canvas)")
st.markdown("Dùng chuột để vẽ trực tiếp lên ảnh. Sau khi ưng ý, nhấn **Thêm vào Dự Án**.")

uploaded_file = st.file_uploader("📂 Tải ảnh bản vẽ lên", type=["png", "jpg", "jpeg"])

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    
    st.write("---")
    col1, col2, col3 = st.columns([2, 2, 2])
    with col1:
        # Các công cụ vẽ bằng chuột
        drawing_mode = st.selectbox("🖱️ Chọn công cụ:", ("freedraw", "line", "rect", "transform", "polygon"))
    with col2:
        stroke_width = st.slider("📐 Độ dày nét:", 1, 10, 3)
    with col3:
        stroke_color = st.color_picker("🎨 Màu nét:", "#FF0000")

    # Hiển thị bảng vẽ Canvas
    canvas_width = 1000
    canvas_height = int((image.height / image.width) * canvas_width)
    
    st.write("### 🖼️ Trình chỉnh sửa (Dùng chuột để vẽ)")
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

    # Chốt ảnh và đẩy vào Slide
    if canvas_result.image_data is not None:
        drawn_image = Image.fromarray(canvas_result.image_data.astype("uint8"), "RGBA")
        drawn_image = drawn_image.resize(image.size, Image.Resampling.LANCZOS)
        
        final_img = image.convert("RGBA").copy()
        final_img.alpha_composite(drawn_image)
        final_img = final_img.convert("RGB")

        st.write("---")
        if st.button("➕ Thêm ảnh đã vẽ vào Dự Án", type="primary"):
            st.session_state.project_slides.append(final_img)
            st.success(f"Đã thêm thành công! Tổng cộng: {len(st.session_state.project_slides)} trang.")
            st.rerun()
