# Eduardo Abi Jaber — academic website

English academic website prepared for **https://eduardo-abi-jaber.github.io**.

Six static pages: Home, Research, Publications, People, Teaching and Talks.
The site works without JavaScript except for the compact mobile navigation.

## Publish on GitHub Pages

1. Create a public repository named **eduardo-abi-jaber.github.io** under **eduardo-abi-jaber**. If it already exists, preserve and review its contents before changing it.
2. Add the contents of this folder to its `main` branch, including `.github/workflows/pages.yml`.
3. In the repository, open **Settings → Pages** and select **GitHub Actions** as the source.
4. Run **Publish website** from the Actions tab, or push a change to `main`.
5. Wait for the deployment to succeed. The site will then be available at the address above.

The repository has not been created or published by this package alone.

## Preview on your computer

Open `dist/index.html` directly, or run:

```sh
python3 build.py
python3 -m http.server 8000 --directory dist
```

Then open http://localhost:8000. Building requires only Python 3; no extra Python packages or JavaScript dependencies are needed.

## Add your portrait

1. Upload a portrait to `assets/portrait.jpg`. A vertical photo with a 4:5 ratio is ideal; the website crops it to fit.
2. In `site.json`, change `"portrait": ""` to `"portrait": "assets/portrait.jpg"`.
3. Commit the changes. GitHub Actions rebuilds and publishes the site.

The portrait remains a simple initials panel until you add a photo. There is no broken-image request or upload form.

## Update the content

- **People, teaching, talks, photo and account details:** edit `site.json`.
- **Publications:** edit `publications.json`. The entries are displayed in the order listed, newest first. The first three appear on the homepage.
- **Research and home introduction:** edit the corresponding text in `build.py`.
- **Colours, typography and layout:** edit `assets/style.css`.
- **Existing source links:** `source-links.json` contains the public links migrated from the original website. It is build input, not a separate page.

Every change pushed to `main` rebuilds the public site. For local changes, run `python3 build.py` to refresh `dist/`.

## Content notes

Content comes from the supplied CV and research statement, the user's corrections, and the Google website as retrieved on 26 September 2026. Paper links and publication details use the current Google webpage. Publication numbering is omitted because the source CV and Google page use different numbers for some papers.


The source page's ambiguous Toulouse date and placeholder Munich seminar URL have not been carried into the upcoming events list. Add these once confirmed. The Google source contains links reused across recurring conferences; check the event-year destination when updating future talks.

## Design and accessibility

White and cobalt palette, serif headings, mobile navigation, keyboard focus indicators and reduced-motion support. Fonts are loaded from Google Fonts with local system fallbacks. No analytics, cookies or tracking scripts are included.

Static links and markup were checked. An interactive browser preview was unavailable in the authoring session, so review the mobile menu and page layout in a browser before final public release.
