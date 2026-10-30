# Website maintenance

GitHub Pages publishes the repository root from `main` using the existing custom domain. `.nojekyll` preserves generated pages without a Jekyll pass.

The authoring content, layouts, and styles are in this directory. From the repository root:

```sh
python3 -m pip install -r .github/portfolio/requirements.txt
python3 .github/portfolio/tools/build.py
python3 .github/portfolio/tools/package-dark.py --assets ./assets --output ./dist
python3 .github/portfolio/tools/preview.py --directory ./dist --port 8879
```

Review `dist/`, copy its contents to the repository root, then commit and push the release. Keep the authoring `/compare/` design directions out of production. New York is the default theme for every page, including direct visits without a theme query. The public `/themes/` page compares the four color themes; `/new-york/` opens the New York edition. Theme choices travel in the URL so links can be shared and the selection follows internal navigation. The root README is the public GitHub profile and must contain personal profile content only.

## Résumé URL

The public résumé is linked at `/resume.pdf`. Packaging copies the document from `assets/documents/Varun_Sahni_resume.pdf` to that short path, and preserves the original path for existing inbound links. Update the original asset and rebuild to keep both copies identical.

The root README is Varun’s public GitHub profile. Keep build and maintenance notes in this folder.
