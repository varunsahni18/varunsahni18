# Varun Sahni

Personal website: https://www.varunsahni.in

The selected immersive dark design is published as static HTML through GitHub Pages, from `main` at the repository root. `.nojekyll` keeps the generated article and project pages unchanged. The original domain and media paths are preserved.

## Editing and rebuilding

The authoring sources are retained in `.github/portfolio/`. They contain the curated public content, original article Markdown, layout generators, CSS, and JavaScript. No private ResumePrep documents are included.

```sh
python3 -m pip install -r .github/portfolio/requirements.txt
python3 .github/portfolio/tools/build.py
python3 .github/portfolio/tools/package-dark.py --assets ./assets --output ./dist
python3 .github/portfolio/tools/preview.py --directory ./dist --port 8879
```

Review `dist/`, then copy its contents to the repository root before committing a release. Do not deploy the editorial/minimal comparison directories or the authoring build output.

CabinAI's web demo skips the first 40 seconds of setup. Its original full recording is retained and linked from the project page. Other recordings use the original H.264/AAC media.

The tennis distinction and academic records remain on the detailed pages. The homepage highlights the five professional awards.
