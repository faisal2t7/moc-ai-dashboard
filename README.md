# Military MOC AI Dashboard

📊 An intelligent dashboard built with Streamlit to manage and track Military MOC (Modules of Competency) performance, training hours, and promotion readiness.

## 🚀 Features

- 🔐 Secure login (admin/mocpass)
- 📥 Voice or image input processing
- 🧠 AI self-learning memory (`ai_memory.csv`)
- 📊 Charts and statistics by staff, MOC, and level
- 📋 Promotion recommendations based on real performance
- 📤 Email alerts using Hotmail (SMTP)
- 🧾 PDF and image chart exports

## 🛠 Requirements

- Python 3.10 or higher
- Streamlit, Pandas, Scikit-learn, FPDF, Dotenv

Install all dependencies:
```bash
pip install -r requirements.txt
```

## 📂 Secrets Configuration (DO NOT COMMIT `.env`)

In Streamlit Cloud, add the following secrets:

```
EMAIL_USER=hope444455444455@hotmail.com
EMAIL_PASS=afad-5566
```

## ✅ How to Run Locally

1. Clone or download this repo
2. Make sure `.env` file exists in the root folder
3. Run the app:
```bash
streamlit run moc_dashboard_app.py
```

## 📬 Email Alerts

Alerts will be sent to the configured Hotmail when staff are eligible for promotion.

---

Built with ❤️ by [Faisal's AI Assistant]