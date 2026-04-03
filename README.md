# 📄 CV Builder

A Streamlit app that generates professional LaTeX CVs — with a live preview, PDF compilation, and one-click download.

**Made by Youseef & Abdelrahman**

---

## 🗂️ Project Structure

```
cv-builder/
├── app.py                  ← Main Streamlit app
├── models.py               ← Data models (CV, PersonalInfo, …)
├── cv_builder.py           ← LaTeX generation logic
├── requirements.txt        ← Python dependencies
├── packages.txt            ← System packages (pdflatex)
├── .streamlit/
│   └── config.toml         ← Streamlit theme & settings
└── README.md
```

---

## 🚀 Deploy on Streamlit Community Cloud (Free)

### Step 1 — Push to GitHub

1. Create a **new repo** on GitHub (public or private).
2. Upload all files:
   ```
   app.py
   models.py
   cv_builder.py
   requirements.txt
   packages.txt
   .streamlit/config.toml
   README.md
   ```
   You can drag & drop them all in the GitHub web UI, or use git:
   ```bash
   git init
   git add .
   git commit -m "initial commit"
   git remote add origin https://github.com/YOUR_USERNAME/cv-builder.git
   git push -u origin main
   ```

### Step 2 — Deploy on Streamlit Cloud

1. Go to **[share.streamlit.io](https://share.streamlit.io)** and sign in with GitHub.
2. Click **"New app"**.
3. Choose:
   - **Repository:** `YOUR_USERNAME/cv-builder`
   - **Branch:** `main`
   - **Main file path:** `app.py`
4. Click **"Deploy!"** — takes ~3 minutes on first build (installs texlive).
5. Your app is live at: `https://YOUR_USERNAME-cv-builder-app-XXXX.streamlit.app`

> **Note:** `packages.txt` tells Streamlit Cloud to install `pdflatex` automatically.  
> No extra configuration needed — PDF compilation works out of the box.

---

## 💻 Run Locally

### Prerequisites
- Python 3.9+
- pdflatex installed:
  - **Windows:** [MiKTeX](https://miktex.org/download)
  - **macOS:** `brew install --cask mactex`
  - **Ubuntu/Debian:** `sudo apt install texlive-latex-extra texlive-fonts-extra`

### Setup

```bash
# 1. Clone your repo
git clone https://github.com/YOUR_USERNAME/cv-builder.git
cd cv-builder

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the app
streamlit run app.py
```

App opens at `http://localhost:8501`

---

## ⚙️ How It Works

1. Fill in your CV data in the form (or load sample data to see a preview).
2. The **Live Preview** panel on the right updates as you type — showing a faithful HTML representation of your CV layout.
3. Click **Generate CV** — the app:
   - Builds a LaTeX document using `pylatex`
   - Compiles it with `pdflatex` (2 passes for correct layout)
   - Shows a PDF preview inline
   - Offers **Download PDF** and **Download .tex** buttons
4. If pdflatex is not available, download the `.tex` file and compile on [Overleaf](https://overleaf.com) (free, no install needed).

---

## 🧩 Sections Supported

| Section | Optional |
|---|---|
| Personal Information | Required |
| Career Objective | Required |
| Education | Required |
| Graduation Project | Optional |
| Work Experience | Optional |
| Courses | Optional |
| Projects | Optional |
| Volunteering | Optional |
| Technical Skills | Optional |
| Soft Skills | Optional |
| Certificates | Optional |
| Additional Experience | Optional |
| Languages | Optional |

---

## 🛠️ Tech Stack

- **Frontend:** Streamlit
- **PDF Generation:** pylatex + pdflatex (TeX Live)
- **Hosting:** Streamlit Community Cloud
