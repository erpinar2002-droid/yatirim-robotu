import streamlit as st
import yfinance as yf
import google.generativeai as genai

# 🔐 API anahtarını Streamlit secrets'tan al
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# Daha stabil model
model = genai.GenerativeModel('gemini-1.5-flash')

st.set_page_config(page_title="Yatırım Robotu")

st.title("Yatırım Robotu")
st.subheader("Borsa İstanbul Veri Analiz Asistanı")

# Kullanıcıdan hisse kodu al
hisse_kodu = st.text_input(
    "Analiz edilecek hisse kodu (Örn: ASELS.IS, TUPRS.IS):",
    "ASELS.IS"
)

if st.button("Verileri Çek ve Analiz Et"):
    try:
        # 📈 Veri çek
        ticker = yf.Ticker(hisse_kodu)
        info = ticker.info

        fiyat = info.get('currentPrice')
        fk_orani = info.get('trailingPE')

        temettu_raw = info.get('dividendYield')
        temettu = (temettu_raw * 100) if temettu_raw else 0

        # Eğer veri hiç gelmezse uyar
        if fiyat is None:
            st.error("Fiyat verisi alınamadı. Hisse kodu yanlış olabilir.")
            st.stop()

        # 🧠 Gemini promptu
        prompt = f"""
        Sen bir finansal analiz uzmanısın. Aşağıdaki verileri analiz et:

        Hisse: {hisse_kodu}
        Güncel Fiyat: {fiyat} TL
        F/K Oranı: {fk_orani}
        Temettü Verimi: %{temettu:.2f}

        Lütfen bu verileri yorumla. Hisse ucuz mu pahalı mı?
        Uzun vadeli biriktirmek mantıklı mı?

        Bir arkeoloji öğrencisinin anlayacağı dilden,
        kazı, katmanlar, stratigrafi ve antik değer gibi benzetmelerle anlat.
        """

        with st.spinner('Veriler inceleniyor, katmanlar kazılıyor...'):
            response = model.generate_content(prompt)

        # 📊 Teknik verileri göster
        st.write("### 📊 Teknik Veriler")
        col1, col2, col3 = st.columns(3)
        col1.metric("Fiyat", f"{fiyat} TL")
        col2.metric("F/K Oranı", fk_orani if fk_orani else "N/A")
        col3.metric("Temettü %", f"{temettu:.2f}")

        # 🧠 Gemini analizini güvenli çek
        try:
            analiz_text = response.candidates[0].content.parts[0].text
        except Exception:
            analiz_text = "Analiz üretilemedi. Model yanıtı boş döndü."

        st.write("### 🧠 Gemini Analizi")
        st.write(analiz_text)

    except Exception as e:
        st.error(f"Bir hata oluştu: {e}")

st.info("Not: Borsa İstanbul hisseleri için kodun sonuna '.IS' eklemeyi unutma (Örn: THYAO.IS)")
