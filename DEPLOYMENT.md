# Deployment

Site: https://lawupdates.github.io/survivor-justice-news/

GitHub Pages source: GitHub Actions.

Publishing workflow: `.github/workflows/pages.yml` runs on every push to `main`.

To inspect deployment errors: https://github.com/Lawupdates/survivor-justice-news/actions/workflows/pages.yml

News collector: `.github/workflows/news-update.yml` runs every four hours once GitHub Actions is permitted and schedules operate.
