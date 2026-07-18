# Dashboard and Story Embed with UI (Flask)

A small Flask + Bootstrap app for embedding a Tableau Public **Dashboard**
and **Story** in a simple web UI.

## Project structure

```
tableau_flask_app/
├── app.py
├── requirements.txt
├── static/
│   └── css/
│       └── style.css
└── templates/
    ├── base.html
    ├── index.html
    ├── dashboard.html
    └── story.html
```

## Setup

1. Create a virtual environment (optional but recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate   # Windows: venv\Scripts\activate
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the app:
   ```bash
   python app.py
   ```
4. Open `http://127.0.0.1:5000` in your browser.

## Adding your Tableau Public embeds

1. In Tableau Desktop, publish your workbook: **File → Save to Tableau
   Public As...**, then sign in to your Tableau Public account.
2. On Tableau Public, open the workbook, go to **Settings**, and enable
   the sheets you want visible.
3. Open the dashboard, click **Share**, and copy the embed code.
4. Open `templates/dashboard.html` and replace the placeholder
   `<div class="tableauPlaceholder">...</div>` block with the copied
   embed code.
5. Repeat steps 3–4 for the story, using `templates/story.html`.

## Pages

- `/` – Landing page with links to the dashboard and story
- `/dashboard` – Embedded Tableau dashboard
- `/story` – Embedded Tableau story
