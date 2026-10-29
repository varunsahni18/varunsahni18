# Website maintenance

GitHub Pages publishes the repository root from `main` using the existing custom domain. `.nojekyll` preserves generated pages without a Jekyll pass.

The authoring content, layouts, and styles are in this directory. From the repository root:

```sh
python3 -m pip install -r .github/portfolio/requirements.txt
python3 .github/portfolio/tools/build.py
python3 .github/portfolio/tools/package-dark.py --assets ./assets --output ./dist
python3 .github/portfolio/tools/preview.py --directory ./dist --port 8879
```

Review `dist/`, copy its contents to the repository root, then commit and push the release. Keep comparison pages out of production. The root README is the public GitHub profile and must contain personal profile content only.
