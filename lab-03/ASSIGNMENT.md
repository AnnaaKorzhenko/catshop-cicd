# Lab 3 — a pipeline that does not repeat itself

Three sections. **Due Wednesday 2 December, 23:59 Kyiv.**
After the deadline the maximum for this lab is 80%.

**All three sections are open now.** Caching came from lecture 4, reusable workflows and the
concurrency identifier from lecture 5, the composite action from practice 3. Nothing here waits
for a session that has not happened.

Lab 2 left you a workflow that tests, builds and publishes. It is **one file that does everything
once**. This lab is about what happens when that is no longer true — a second pipeline, a second
repository, a QA suite somebody else owns — and about the two minutes you spend every run
downloading things you already had.

---

## What you are given

```
app.py                  the same Flask app, unchanged — do not edit it
requirements.txt        its three dependencies
partner/mappings/       the partner's stubbed responses, for the QA bonus
.env.example            copy to .env. Never commit .env
```

## What you write

```
lab-03/Dockerfile                        lab 2's, ordered for the layer cache
lab-03/requirements-dev.txt              whatever your suites need
lab-03/tests/test_*.py                   the unit suite — lab 2's, carried over
lab-03/qa/test_*.py                      section 3 — the AQA suite
lab-03/published.txt                     the digest your pipeline promoted
lab-03/CACHE.md                          section 2 — the two numbers and the two run URLs
lab-03/qa/REGRESSION.md                  bonus
lab-03/CONCURRENCY.md                    bonus

.github/workflows/lab-03-pipeline.yml    the caller — at the REPOSITORY ROOT
.github/workflows/_build-and-test.yml    called by it
.github/workflows/_qa.yml                called by it
.github/actions/<name>/action.yml        your composite action
```

Everything with `.github/` in front of it lives at the **repository root**, because that is the
only place GitHub reads workflows from. A reusable workflow is the same: it is only callable from
`.github/workflows/`, which is why `_build-and-test.yml` cannot live inside `lab-03/`.

Name the caller anything you like except `lab-03.yml` — that name is taken by the grader.

## The application

Unchanged, and still four endpoints:

| Endpoint | Depends on | Where it matters here |
|---|---|---|
| `GET /health` | nothing | the QA suite |
| `GET /ready` | the store it was configured with | the QA suite |
| `GET /visits` | our own state — a file, or Postgres | the QA suite |
| `GET /price/<sku>` | an API we do not own | the QA bonus |

> **One contract: the app serves on container port `8080`.** Anything that runs your image
> publishes it to host `8080` and probes `http://localhost:8080`.

## How you find out where you stand

**Push.** Each section is a named check. Click one and you get a table: every individual check,
pass or fail, with the reason. Push as often as you like — it costs nothing, and it is the same
result your mark comes from.

What follows says what each section has to **achieve**. It does not list the checks.

---

## Section 1 · one definition, called twice

Take the pipeline you wrote in lab 2 and split it so that **nothing is defined twice**.

- The test-and-build half becomes a **reusable workflow**: it takes arguments, and it hands
  something back — the thing the next job needs, which is the image reference.
- The QA half becomes a **second reusable workflow**, because somebody else is going to call it.
  In lab 5 that somebody is you, pointing this same file at three environments.
- Somewhere inside the reusable workflow there is a **composite action**: steps compose into a
  job, jobs compose into a workflow, and the difference between those two sentences is the
  section.

The caller is then short enough to read in one screen. If testing or building appears in more
than one file, you have made copies, not a pipeline.

One more thing, and it is the lesson from the moved tag: **everything you call, you call at a
version.** A branch is not a version.

**In the pull request:**

- **What the reusable workflow cannot do that the composite action can**, from having hit it —
  not from the table in the slides.
- The thing you passed **in** and the thing you got **back**, and what broke while you were
  getting the second one to work. Paste the error.
- One line: what would happen to your pipeline if the tag you call moved tonight.

## Section 2 · both caches, and the minutes

Lab 2 had you cache something as a bonus. Now it is the work.

There are **two** caches and they are not the same cache: the one that holds your dependencies,
and the one that holds your image layers. Add both. Then do the thing the section is actually
marked on — **measure it**:

1. Run the pipeline cold.
2. Run it again warm, changing nothing.
3. Write `lab-03/CACHE.md` with **both timings, the saving, and the URL of each of the two runs.**

The run URLs matter: the grader reads them back out of the API and compares the real durations
with what you wrote. Numbers typed from memory will not survive that.

Two things decide whether the cache works at all, and both of them are in your hands:

- **the key** — a key that never changes is a cache that is never refreshed, and a key with no
  fallback throws everything away the moment one dependency moves.
- **the Dockerfile's order** — the layer cache can only help you from the first line you changed
  onwards.

**In the pull request:**

- **The two numbers**, and one line on which of the two caches did the work.
- The key you tried **first** and why it was wrong.
- One thing you deliberately **did not** cache, and why. (There is at least one obvious candidate
  in this app, and caching it would be a mistake.)

## Section 3 · a suite that needs an address

A unit test runs before anything exists. **AQA runs after**, against the thing that now does.

Write `lab-03/qa/` — a suite that drives the running application **over HTTP**, from outside. It
may not import `app`, and it may not use Flask's test client: if it can do either, it is a unit
test wearing a QA hat and it will not notice a broken image.

Then wire it in:

- the QA workflow is given **the digest** your build produced, not a tag and never `latest`
- the suite reads its base address **from the environment**, because in lab 5 that address is
  going to be three different environments
- and something **depends on the QA job**. A QA job that nothing waits for is decoration: a red
  suite would change nothing about what reaches the registry. So have a **promotion** job — the one
  that records the digest you are standing behind — and make it reachable only through QA.

Publishing before QA and promoting after it is the honest order, and it is what the examples
repository does: the bytes go to the registry, the suite drives them, and only then does anything
say *this is the one*. `lab-03/published.txt` is that statement. Commit it yourself or have the job
write it — the grader reads the file, and reads the graph to see that QA stands in front of it.

The grader does what lab 5 will do for real: it pulls the digest in `published.txt`, starts it,
points **your** suite at it, and requires your suite to pass against bytes it did not build.

**In the pull request:**

- **The case that fails for the right reason.** Break the image on purpose, run the suite against
  it, paste the failure.
- What this suite **cannot** see from outside, that a unit test can.
- One line: what has to change to point it at a real deployment instead of a container on the
  runner.

---

## Bonus — adds marks, never costs them

Bonus checks run with `continue-on-error`, so a red bonus job cannot fail your pipeline.

**+ The suite grows up.** Five scenarios or more, and at least one of them expecting a
**failure** — a 404, a 502, a dependency that is not there. The stubbed partner in
`partner/mappings/` is how you make `/price` testable without the real partner. Then write
`lab-03/qa/REGRESSION.md`: **one incident in two lines, and the case that exists because of it.**
Run the suite over a **matrix**, and upload its report as an artifact — when the suite fails at
02:00 the log is gone and the report is not. Name the check a branch rule would require.

**+ Two pushes, one run.** Add a `concurrency:` group and then **demonstrate it**: push twice in
quick succession and watch the first run die. Write `lab-03/CONCURRENCY.md` with both run URLs,
what was cancelled, and **one line on why cancelling that one was safe** — because there is a job
in your pipeline where it would not have been, and saying which one is the whole bonus.

The group is an identifier. A constant serialises your entire repository; the ref is usually what
you meant. And `cancel-in-progress: true` with no condition will one day kill a publish halfway
through.

---

## Handing it in

1. Pull request from your `lab-03` branch into **`main` of your own repository**.
2. Fill in every heading in the template — the alternatives, the measurements and the AI
   disclosure are each worth marks, and no check can award them. One or two lines each.
3. Open a **submission issue** in
   [catshop-submissions](https://github.com/kse-ci-cd-basics-course/catshop-submissions/issues/new/choose)
   with the pull request URL. **That issue is what hands the lab in, and its timestamp is your
   submission time.** I do not watch your repository — a pull request nobody told me about is not
   a submission. I review the diff in your repository and reply there.

**Two things score zero regardless of green checks:** a committed `.env` — the checks read git
*history*, not just the working tree — and configuration you cannot explain.

`lab-01/` and `lab-02/` are frozen. Nothing in this lab edits either of them.
