# Nursing Govt Exam & Job Tracker

An auto-updating dashboard that checks for nursing-related government exam
and job notifications (AIIMS NORCET, ESIC, RRB, state nursing boards, etc.)
every 30 minutes and shows them on a simple web page.

No paid services, no API keys.

---

## How it works

1. `scripts/scrape.py` checks a list of sources (AIIMS, ESIC, and major
   job-alert aggregator sites) for links containing nursing-related keywords
   (nurse, nursing officer, NORCET, ANM, GNM, etc.)
2. New items get added to `data/notices.json`
3. `docs/index.html` is a dashboard that reads that JSON and displays it,
   with filters by category and a "New" flag for anything found in the
   last 24 hours
4. `.github/workflows/update.yml` runs the scraper automatically every
   30 minutes via GitHub Actions, commits the updated data, and GitHub Pages
   serves the dashboard from the `docs/` folder

---

## One-time setup (about 10 minutes)

### 1. Create a GitHub account
If you don't have one: go to github.com → Sign up (free).

### 2. Create a new repository
- Click the "+" in the top right → "New repository"
- Name it something like `nursing-exam-tracker`
- Set it to **Public** (required for free GitHub Pages)
- Click "Create repository"

### 3. Upload these files
On the new repo page, click "uploading an existing file" and drag in this
entire folder structure (keeping the folder names: `.github/workflows/`,
`scripts/`, `data/`, `docs/`).

Alternatively, if you're comfortable with git:
```bash
git init
git add .
git commit -m "Initial setup"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/nursing-exam-tracker.git
git push -u origin main
```

### 4. Enable GitHub Pages
- Go to your repo → Settings → Pages
- Under "Build and deployment" → Source: select "Deploy from a branch"
- Branch: `main`, Folder: `/docs`
- Click Save

Your dashboard will be live at:
`https://YOUR_USERNAME.github.io/nursing-exam-tracker/`
(takes 1-2 minutes to go live after first save)

### 5. Enable Actions (if needed)
- Go to repo → Actions tab
- If prompted, click "I understand my workflows, enable them"
- The workflow runs automatically every 30 minutes from then on
- To test immediately: go to Actions → "Update Nursing Exam Tracker" →
  "Run workflow" button

---

## Customizing

- **Add more sources**: edit the `SOURCES` list in `scripts/scrape.py`
- **Add/remove keywords**: edit `NURSING_KEYWORDS` in the same file
- **Change check frequency**: edit the `cron` line in
  `.github/workflows/update.yml` (e.g. `*/60 * * * *` for hourly).
  Note: GitHub's minimum practical interval is 5 minutes, but scheduled
  workflows can be delayed during high-load periods — 30 min is a
  reliable real-world interval.

---

## Notes

- Some sites occasionally block scrapers or change their HTML structure.
  If a source stops returning results, the scraper just skips it (logs a
  warning) — it won't break the whole run.
- This is a best-effort tracker built on public aggregator sites, not an
  official government feed. Always confirm details on the official
  recruiting body's website before applying.
