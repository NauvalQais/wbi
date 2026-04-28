import streamlit as st
import joblib
import numpy as np

# ── Load model ────────────────────────────────────────────────────────────────
model = joblib.load("model.pkl")   # ganti nama file sesuai .pkl kamu

# ── Setup halaman ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="WBI - Klasifikasi Pengelolaan Sampah",
    page_icon="♻️",
    layout="centered"
)

st.markdown(
    "<h1 style='text-align:center;'>♻️ Waste Burden Index Classifier</h1>"
    "<p style='text-align:center; color:gray;'>Klasifikasi Beban Pengelolaan Sampah per TPS – Kota Bandung</p>",
    unsafe_allow_html=True
)
st.divider()

# ── Pilihan mode input ────────────────────────────────────────────────────────
mode = st.radio(
    "Pilih metode input:",
    ["Input Volume Mentah (m³)", "Input Rasio Langsung (0–1)"],
    horizontal=True
)

st.markdown("### 📥 Data Input TPS")

COLOR_MAP  = {'KRITIS': '#E74C3C', 'WASPADA': '#F39C12', 'AMAN': '#27AE60'}
ICON_MAP   = {'KRITIS': '🔴', 'WASPADA': '🟡', 'AMAN': '🟢'}
SARAN_MAP  = {
    'KRITIS':  "Diperlukan intervensi segera: tambah armada pengangkutan, evaluasi kapasitas TPS, dan percepat pengolahan.",
    'WASPADA': "Perlu pemantauan rutin. Tingkatkan efisiensi pengangkutan dan kurangi sisa sampah harian.",
    'AMAN':    "Pengelolaan berjalan baik. Pertahankan performa dan lakukan monitoring berkala.",
}

if mode == "Input Volume Mentah (m³)":
    col1, col2 = st.columns(2)
    with col1:
        input_vol  = st.number_input("📦 Volume Input (m³)",  min_value=0.0, value=10.0, step=0.1)
        angkut_vol = st.number_input("🚛 Volume Diangkut (m³)", min_value=0.0, value=7.0, step=0.1)
    with col2:
        diolah_vol = st.number_input("⚙️ Volume Diolah (m³)",  min_value=0.0, value=5.0, step=0.1)
        sisa_vol   = st.number_input("🗑️ Volume Sisa (m³)",    min_value=0.0, value=3.0, step=0.1)

    jarak_km     = st.number_input("📍 Total Jarak ke TPA (km)", min_value=0.0, value=50.0, step=1.0)
    max_jarak_km = st.number_input(
        "📏 Jarak Maksimum di Dataset (km) — untuk normalisasi indeks_jarak",
        min_value=1.0, value=100.0, step=1.0,
        help="Isi dengan nilai max jarak di seluruh dataset agar indeks_jarak konsisten dengan training."
    )

    # Hitung rasio
    rasio_angkut = angkut_vol / input_vol  if input_vol  > 0 else 0.0
    rasio_diolah = diolah_vol / angkut_vol if angkut_vol > 0 else 0.0
    rasio_sisa   = sisa_vol   / input_vol  if input_vol  > 0 else 0.0
    indeks_jarak = jarak_km   / max_jarak_km

    st.markdown("#### 🔢 Rasio yang Dihitung Otomatis")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("rasio_angkut", f"{rasio_angkut:.3f}")
    c2.metric("rasio_diolah", f"{rasio_diolah:.3f}")
    c3.metric("rasio_sisa",   f"{rasio_sisa:.3f}")
    c4.metric("indeks_jarak", f"{indeks_jarak:.3f}")

else:  # Input Rasio Langsung
    st.info("Masukkan nilai rasio antara 0.0 hingga 1.0")
    col1, col2 = st.columns(2)
    with col1:
        rasio_angkut = st.slider("🚛 rasio_angkut (proporsi terangkut)",  0.0, 1.0, 0.70, 0.01)
        rasio_diolah = st.slider("⚙️ rasio_diolah (proporsi diolah)",      0.0, 1.0, 0.50, 0.01)
    with col2:
        rasio_sisa   = st.slider("🗑️ rasio_sisa (proporsi sisa)",          0.0, 1.0, 0.30, 0.01)
        indeks_jarak = st.slider("📍 indeks_jarak (jarak ternormalisasi)", 0.0, 1.0, 0.50, 0.01)

st.divider()

# ── Tombol prediksi ───────────────────────────────────────────────────────────
if st.button("🔍 Prediksi Klasifikasi", use_container_width=True, type="primary"):
    # Validasi
    if mode == "Input Volume Mentah (m³)" and input_vol == 0:
        st.warning("Volume Input tidak boleh 0.")
        st.stop()

    X_input = np.array([[rasio_angkut, rasio_diolah, rasio_sisa, indeks_jarak]])
    label   = model.predict(X_input)[0]
    color   = COLOR_MAP.get(label, '#888888')
    icon    = ICON_MAP.get(label, '⚪')
    saran   = SARAN_MAP.get(label, '')

    st.markdown(f"""
        <div style='background-color:{color}22; border-left: 6px solid {color};
                    padding:20px; border-radius:10px; margin-top:10px;'>
            <h2 style='color:{color}; text-align:center;'>{icon} {label}</h2>
            <p style='text-align:center; font-size:15px; color:#333;'>{saran}</p>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("### 📊 Ringkasan Input Model")
    st.table({
        "Fitur": ["rasio_angkut", "rasio_diolah", "rasio_sisa", "indeks_jarak"],
        "Nilai": [
            f"{rasio_angkut:.4f}",
            f"{rasio_diolah:.4f}",
            f"{rasio_sisa:.4f}",
            f"{indeks_jarak:.4f}",
        ],
        "Keterangan": [
            "Proporsi sampah berhasil diangkut",
            "Proporsi dari yang diangkut, berhasil diolah",
            "Proporsi sampah yang tidak terangkut (sisa)",
            "Jarak ke TPA ternormalisasi [0–1]",
        ]
    })

# ── Panduan nilai ─────────────────────────────────────────────────────────────
with st.expander("📖 Panduan Interpretasi Nilai"):
    st.markdown("""
    | Fitur | Nilai Ideal | Catatan |
    |---|---|---|
    | `rasio_angkut` | ≥ 0.70 | Semakin tinggi semakin baik |
    | `rasio_diolah` | ≥ 0.50 | Semakin tinggi semakin baik |
    | `rasio_sisa`   | ≤ 0.30 | Semakin rendah semakin baik |
    | `indeks_jarak` | ≤ 0.50 | Semakin rendah semakin baik |
    
    **Threshold WBI (untuk referensi):**
    - 🔴 **KRITIS**  : WBI ≥ 0.60
    - 🟡 **WASPADA** : WBI 0.30 – 0.59
    - 🟢 **AMAN**    : WBI < 0.30
    """)

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("""
<hr style='margin-top:30px; border-top: 1px solid #bbb;'>
<div style='text-align:center; color:#888; font-size:13px;'>
    Developed by <strong>Dsloven Group 7</strong> – DS Batch 49
</div>
""", unsafe_allow_html=True)