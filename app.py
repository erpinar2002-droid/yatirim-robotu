import streamlit as st
import yfinance as yf
from google import genai

# API anahtarı
client = genai.Client(api_key=st.secrets["GOOGLE_API_KEY"])

st.set_page_config(page_title="Yatırım Robotu")
st.title("Yatırım Robotu")
st.subheader("Borsa İstanbul Veri Analiz Asistanı")

hisse_kodu = st.text_input("Analiz edilecek hisse kodu (Örn: ASELS.IS, TUPRS.IS):", "ASELS.IS")

if st.button("Verileri Çek ve Analiz Et"):
    try:
        ticker = yf.Ticker(hisse_kodu)
        info = ticker.info

        fiyat = info.get('currentPrice', 'N/A')
        fk_orani = info.get('trailingPE', 'N/A')
        temettu = info.get('dividendYield', 0) * 100 if info.get('dividendYield') else 0

        prompt = f"""
        Sen bir finansal analiz uzmanısın. Aşağıdaki verileri analiz et:

        Hisse: {hisse_kodu}
        Güncel Fiyat: {fiyat} TL
        F/K Oranı: {fk_orani}
        Temettü Verimi: %{temettu:.2f}

        Lütfen bu verileri yorumla. Hisse ucuz mu pahalı mı?
        Uzun vadeli biriktirmek mantıklı mı? Bir arkeoloji öğrencisinin
        anlayacağı dilden (kazı, katmanlar, stratigrafi ve antik değer gibi benzetmelerle) anlat.
        """

        with st.spinner('Veriler inceleniyor, katmanlar kazılıyor...'):
            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=prompt
            )

        st.write("### 📊 Teknik Veriler")
        col1, col2, col3 = st.columns(3)
        col1.metric("Fiyat", f"{fiyat} TL")
        col2.metric("F/K Oranı", fk_orani)
        col3.metric("Temettü %", f"{temettu:.2f}")

        st.write("### 🧠 Gemini Analizi")
        st.write(response.text)

    except Exception as e:
        st.error(f"Bir hata oluştu: {e}")

st.info("Not: Borsa İstanbul hisseleri için kodun sonuna '.IS' eklemeyi unutma (Örn: THYAO.IS)")
