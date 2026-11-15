# Lab 2 — test, build, publish

**Three sections. Due Thursday 19 November, 23:59 Kyiv.** After that, 80% maximum.

## Given

```
app.py · requirements.txt     the Flask app — do not change it
partner/mappings/             the partner's stubbed responses, for the bonus
.env.example                  copy to .env. Never commit .env
```

## You write

```
lab-02/Dockerfile · requirements-dev.txt · tests/test_*.py · published.txt
lab-02/CACHE.md                          bonus
.github/workflows/publish-lab-02.yml     at the repository root
```

Workflows live at the repository root — nowhere else runs. The app serves on container port `8080`.

| Endpoint | Depends on | Section |
|---|---|---|
| `GET /health` | nothing | 1, 3 |
| `GET /ready` | the store it was configured with | 1 |
| `GET /visits` | our own state | 1, 3 |
| `GET /price/<sku>` | an API we do not own | bonus |

Push and read the checks; each section is one check with a table behind it.

---

## 1 · A suite that would notice

Write tests and make them pass. `pytest` exiting 0 is not the bar: **break the app on purpose and
your suite must go red.** `/price` needs a partner that is not there — that one is the bonus.

**Pull request:** the one-line mutation you made and the test output that caught it, and which test
caught it · one test you wrote first and deleted, with the reason · how long the suite takes, and
whether that is fast enough for every push.

## 2 · One workflow: test, build, publish

A push runs the suite, builds the image, publishes it to **GHCR**.

- a red suite must not be able to publish — structurally, not by ordering
- `latest` is rejected; tag something that names one build
- label the image with the commit it was built from, `org.opencontainers.image.revision`

You will meet a `403` on the first push to GHCR. The fix is one block in the workflow, not a
personal access token.

**Pull request:** the 403 and the exact change that fixed it, plus why the token was there but could
not do this · what happens on a fork's pull request, in two sentences · your tag scheme, and what
breaks if two pushes produce the same tag.

## 3 · An image somebody else can pull

One line in `lab-02/published.txt`, nothing else:

```
ghcr.io/<account>/<image>@sha256:<64 hex characters>
```

A tag is not accepted. The grader pulls exactly that, runs it, probes it, and checks the commit
label names a commit in your repository — so an image built on your laptop fails. The package must
be **public**; GHCR packages start private.

**Pull request:** where the digest came from, pasted from the step that produced it · tag versus
digest, with one scenario where the difference is the whole story · the package's visibility, where
you changed it and what it means.

---

## Bonus

Bonus sections report and cannot cost you marks.

**+ Cache something, and prove it.** Dependencies, Docker layers or both. Run cold, run warm, write
`lab-02/CACHE.md` with both timings and one sentence on what got faster. Key it on something that
changes — the grader asks the API for the entry your workflow created, by key then by id, and checks
it is not empty.

**+ The partner, stubbed.** Make `/price/MK-II` testable without the real partner —
`wiremock/wiremock:3.6.0` with the stubs in `partner/mappings/`, or fake the HTTP call. Say which
you chose and what it cannot catch.

**+ Docker Hub as well.** Publish the same image there, and say why this course grades on GHCR —
there are at least two reasons.

---

## Handing it in

Pull request into your own `main`, every template heading filled in — an empty required heading
fails the pull request — then a **submission issue** in
[catshop-submissions](https://github.com/kse-ci-cd-basics-course/catshop-submissions/issues/new/choose)
with the PR URL. The issue timestamp is your submission time.

A committed `.env` — the checks read git *history* — or configuration you cannot explain, scores
zero.
