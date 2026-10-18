# Hume on Personal Identity: Mapping the *Treatise*

A map of how the scholarly literature on Hume's account of personal identity cites the *Treatise*. About 100 publications were processed for Norton and Selby-Bigge/Nidditch citations. The site shows which passages each publication cites, how publications compare with each other and with the literature as a whole, and which publications discuss a given part of the text.

This is the original 2020 version of the site, restored with its design unchanged. Live at https://treatise-mapping-project-ur.outsidethevillage.com.

## Layout

- `app/`: Flask app (routes, form, Jinja templates on Bootswatch "Flatly").
- `functions_and_classes/`: citation parsing, scoring and comparison code, plus the data loaders in `cloud_io.py`.
- `data/runtime/`: everything the site reads at runtime.
  - `publications/<id>.json`: one file per paper with its bibliography, citations and scores.
  - Comparison, reverse-lookup and literature-level CSVs.
  - The Treatise structure and the Norton↔SBN concordance.
- `notebooks/`: the original working notebooks (outputs stripped).

In 2020 the site read this data from Firestore and a Cloud Storage bucket. It now ships as plain files, and `cloud_io.py` keeps the original function names. The full paper texts and PDFs are not in this repository.

## Run locally

```bash
docker build --platform linux/amd64 -t treatise-ur .
docker run --rm -p 8080:8080 -e SECRET_KEY=dev treatise-ur
```

Then open http://localhost:8080. The image is pinned to Python 3.8 and the 2020 library versions so the site behaves as it originally did.

## Deploy (Cloud Run)

```bash
gcloud run deploy treatise-ur --source . --region us-central1 --allow-unauthenticated \
  --service-account treatise-ur-run@treatise-mapping-ur.iam.gserviceaccount.com \
  --set-env-vars SECRET_KEY=<random string>
```
