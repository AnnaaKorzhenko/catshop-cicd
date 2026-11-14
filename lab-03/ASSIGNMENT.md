# Lab 3 — a pipeline that does not repeat itself

**Two sections. Due Wednesday 2 December, 23:59 Kyiv.**
After the deadline the maximum for this lab is 80%.

You have a workflow that tests, builds and publishes: **one file that does everything once.** This
lab is about what happens when that is no longer true — a second pipeline, a second repository, a
QA suite somebody else owns — and about the two minutes you spend every run downloading things you
already had.

**Three bonus sections sit on top**, and the first of them is a whole stage of a real pipeline:
pull the image you published, stand it up, and drive it. They are worth going after.

---

## What you are given

```
app.py                  the same Flask app, unchanged — do not edit it
requirements.txt        its three dependencies
partner/mappings/       the partner's stubbed responses, behind a compose profile
.env.example            copy to .env. Never commit .env

qa/compose.qa.yaml      the stack an AQA run needs: the PULLED image, Postgres, and the
                        partner behind a profile. Note what it does not have: a `build:`
qa/test_smoke.py        five scenarios, written for you. They drive the app over HTTP
qa/README.md            how to run the stack and the suite, and what each reads from
                        the environment
```

The QA suite and its stack are **given on purpose**. Writing scenarios is not what this lab is
about; putting a stage in a pipeline is.

## What you write

```
lab-03/Dockerfile                        ordered for the layer cache
lab-03/requirements-dev.txt              pytest and requests
lab-03/tests/test_*.py                   the unit suite
lab-03/CACHE.md                          section 2 — the two numbers and the two run URLs

.github/workflows/lab-03-pipeline.yml    section 1, the caller — at the REPOSITORY ROOT
.github/workflows/_build-and-test.yml    called by it
.github/actions/<name>/action.yml        your composite action

lab-03/published.txt                     bonus 1 — the digest QA stood behind
.github/workflows/_qa.yml                bonus 1 — or the QA job, wherever you put it
lab-03/qa/test_<yours>.py                bonus 2 — your own scenarios, beside the given ones
lab-03/qa/REGRESSION.md                  bonus 2
lab-03/CONCURRENCY.md                    bonus 3
```

Everything with `.github/` in front of it lives at the **repository root**, because that is the only
place GitHub reads workflows from. A reusable workflow is the same: it is only callable from
`.github/workflows/`, which is why `_build-and-test.yml` cannot live inside `lab-03/`.

Name the caller anything you like except `lab-03.yml` — that name is taken by the grader.

## The application

Unchanged, and still four endpoints:

| Endpoint | Depends on | Where it matters here |
|---|---|---|
| `GET /health` | nothing | the QA bonus |
| `GET /ready` | the store it was configured with | the QA bonus |
| `GET /visits` | our own state — a file, or Postgres | the QA bonus |
| `GET /price/<sku>` | an API we do not own | the QA bonus, both ways round |

> **One contract: the app serves on container port `8080`.** Anything that runs your image
> publishes it to host `8080` and probes `http://localhost:8080`.

## How you find out where you stand

**Push.** Each section is a named check. Click one and you get a table: every individual check,
pass or fail, with the reason. Push as often as you like — it costs nothing, and it is the same
result your mark comes from.

What follows says what each section has to **achieve**. It does not list the checks.

---

## Section 1 · one definition, called twice

Split your pipeline so that **nothing is defined twice**.

- The test-and-build half becomes a **reusable workflow**: it takes arguments, and it hands
  something back — the thing the next job needs, which is the image reference.
- Somewhere inside it there is a **composite action**: steps compose into a job, jobs compose into
  a workflow, and the difference between those two sentences is the section.

The caller is then short enough to read in one screen. If testing or building appears in more than
one file, you have made copies, not a pipeline.

One more thing, and it is the lesson from the moved tag: **everything you call, you call at a
version.** A branch is not a version.

**In the pull request:**

- **What the reusable workflow cannot do that the composite action can**, from having hit it — not
  from the table in the slides.
- The thing you passed **in** and the thing you got **back**, and what broke while you were getting
  the second one to work. Paste the error.
- One line: what would happen to your pipeline if the tag you call moved tonight.

## Section 2 · both caches, and the minutes

There are **two** caches and they are not the same cache: the one that holds your dependencies, and
the one that holds your image layers. Add both. Then do the thing the section is actually marked on
— **measure it**:

1. Run the pipeline cold.
2. Run it again warm, changing nothing.
3. Write `lab-03/CACHE.md` with **both timings, the saving, and the URL of each of the two runs.**

The run URLs matter: the grader reads them back out of the API and compares the real durations with
what you wrote. Numbers typed from memory will not survive that.

Two things decide whether the cache works at all, and both are in your hands:

- **the key** — a key that never changes is a cache that is never refreshed, and a key with no
  fallback throws everything away the moment one dependency moves.
- **the Dockerfile's order** — the layer cache can only help you from the first line you changed
  onwards.

**In the pull request:**

- **The two numbers**, and one line on which of the two caches did the work.
- The key you tried **first** and why it was wrong.
- One thing you deliberately **did not** cache, and why. (There is at least one obvious candidate in
  this app, and caching it would be a mistake.)

---

## Bonus — adds marks, never costs them

Bonus checks run with `continue-on-error`, so a red bonus job cannot fail your pipeline.

### + Bonus 1 · the stage that drives what you published

**This is the big one, and it is optional. Skip it and lose nothing but the marks.**

A unit test runs before anything exists. **AQA runs after**, against the thing that now does. The
suite and the stack are already in `lab-03/qa/`. What is missing is the **job**: one that takes the
digest your build produced and does three things with it.

```yaml
- run: docker compose -f lab-03/qa/compose.qa.yaml up -d --wait
  env:
    QA_IMAGE: ${{ <the digest your build job output> }}

- run: python -m pytest lab-03/qa -q
  env:
    QA_BASE_URL: http://localhost:8080

- if: always()
  run: docker compose -f lab-03/qa/compose.qa.yaml down -v
```

Those three steps, in your pipeline, with the digest arriving from the job before them rather than
pasted in. **Write them as steps in the job** — do not hide them in a script. A stage you cannot
read in the workflow file is a stage nobody will debug at 02:00.

Then two things make it a stage rather than a demo:

- **the digest, not a tag.** `latest` is the one reference that can change between the build and the
  QA run, which would make the whole stage a lie.
- **something depends on it.** A QA job nothing waits for is decoration: a red suite would change
  nothing about what reaches the registry. So have a **promotion** — the thing that records the
  digest you are standing behind — and make it reachable only through QA. `lab-03/published.txt` is
  that record: one line, the digest, nothing else.

Publishing before QA and promoting after it is the honest order: the bytes go to the registry, the
suite drives them, and only then does anything say *this is the one*.

**In the pull request:** where the digest came from, and what the suite would and would not have
caught — one line each.

### + Bonus 2 · scenarios of your own

Five scenarios are given. Add **your own**, in your own file beside them, and at least one of them
expecting a **failure** — a 404, a 502, a dependency that is not there.

`QA_PROFILE=partner` starts the stubbed partner, and that variable reaches the suite, so one case
can assert both outcomes. The two profiles are the obvious two rows of a **matrix**. Upload the
report as an **artifact** — when it fails at 02:00 the log is gone and the report is not.

Then write `lab-03/qa/REGRESSION.md`: **one incident in two lines, and the case that exists because
of it.** Name the check a branch rule would require.

### + Bonus 3 · two pushes, one run

Add a `concurrency:` group and then **demonstrate it**: push twice in quick succession and watch the
first run die. Write `lab-03/CONCURRENCY.md` with both run URLs, what was cancelled, and **one line
on why cancelling that one was safe** — because there is a job in your pipeline where it would not
have been, and saying which one is the whole bonus.

The group is an identifier. A constant serialises your entire repository; the ref is usually what
you meant. And `cancel-in-progress: true` with no condition will one day kill a publish halfway
through.

---

## Handing it in

1. Pull request from your `lab-03` branch into **`main` of your own repository**.
2. Fill in every heading in the template — the alternatives, the measurements and the AI disclosure
   are each worth marks, and no check can award them. One or two lines each.
3. Open a **submission issue** in
   [catshop-submissions](https://github.com/kse-ci-cd-basics-course/catshop-submissions/issues/new/choose)
   with the pull request URL. **That issue is what hands the lab in, and its timestamp is your
   submission time.** I do not watch your repository — a pull request nobody told me about is not a
   submission. I review the diff in your repository and reply there.

**Two things score zero regardless of green checks:** a committed `.env` — the checks read git
*history*, not just the working tree — and configuration you cannot explain.
