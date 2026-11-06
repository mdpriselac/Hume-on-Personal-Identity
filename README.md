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

Then open http://localhost:8080. The app refuses to start without `SECRET_KEY`. The image is pinned to Python 3.8 and the 2020 library versions so the site behaves as it originally did.

## Deploy (Cloud Run)

```bash
gcloud run deploy treatise-ur --source . --region us-central1 --allow-unauthenticated \
  --service-account <run-service-account>@<your-project>.iam.gserviceaccount.com \
  --set-env-vars SECRET_KEY=<random string>
```

## How this was built

I wrote this project by hand between October 2019 and July 2020: the citation parsing, the scoring
and comparison code, the Flask app and the notebooks in `notebooks/`. Its development history
(from the first commit on 27 May 2020) lives in a separate working repository on my machine, so
this repository's history starts in 2026.

In October 2026 a Claude agent restored it from that repository (the commits carry a
`Co-Authored-By: Claude` trailer). It moved the data that used to be read from Firestore and Cloud
Storage into plain files, replaced the Tableau Public charts with Chart.js, upgraded the web
libraries for security, and packaged it for Cloud Run. The pages, templates and processing code
are otherwise as I left them in 2020.

The 2026 rebuild of the same project, with an LLM-assisted citation pipeline, is
[treatise-mapping-new](https://github.com/mdpriselac/treatise-mapping-new).
[2020 vs 2026](https://github.com/mdpriselac/treatise-mapping-new/blob/main/docs/2020-vs-2026.md)
compares the two, and the project page is
[outsidethevillage.com/hume](https://outsidethevillage.com/hume.html).
