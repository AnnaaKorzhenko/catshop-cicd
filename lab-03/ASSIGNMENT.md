# Lab 3 — a pipeline that does not repeat itself

**Two sections. Due Wednesday 2 December, 23:59 Kyiv.** After that, 80% maximum.

## Given

```
app.py · requirements.txt · .env.example · partner/mappings/
qa/compose.qa.yaml   the stack an AQA run needs. It pulls an image; it has no build:
qa/test_smoke.py     five scenarios, over HTTP
qa/README.md         how to run them
```

## You write

```
lab-03/Dockerfile · requirements-dev.txt · tests/test_*.py
lab-03/CACHE.md
.github/workflows/<caller>.yml · _build-and-test.yml
.github/actions/<name>/action.yml

bonus:  _qa.yml · published.txt · qa/test_<yours>.py · qa/REGRESSION.md · CONCURRENCY.md
```

Workflows live at the repository root — nowhere else runs. Not `lab-03.yml`; that is the grader.
The app serves on container port `8080`.

Push and read the checks. Each section is one check with a table behind it.

---

## 1 · One definition, called twice

- test-and-build becomes a **reusable workflow**: typed inputs, and the image reference handed back
- a **composite action** inside it
- testing and building appear in **one** file, not several
- everything you call, you call at a version

**Pull request:** what the reusable workflow cannot do that the composite action can · what you
passed in, what came back, and the error you hit getting it · what happens if the tag you call
moves tonight.

## 2 · Both caches, and the minutes

Two caches: dependencies, and image layers. Add both. Then run cold, run warm, and write
`lab-03/CACHE.md` with both timings, the saving, and both run URLs.

The grader reads those runs back out of the API and compares durations.

**Pull request:** the two numbers and which cache did the work · the key you tried first and why it
was wrong · one thing you did not cache, and why.

---

## Bonus

Bonus sections report and cannot cost you marks.

**+ The AQA stage.** A job that takes the digest your build produced, stands up `qa/compose.qa.yaml`,
runs `qa/`, and tears it down. The digest, never a tag. Something must **depend** on it: make the
promotion — `lab-03/published.txt`, one line — reachable only through QA. Steps in the job, not a
script.

**+ Your own scenarios.** Three or more in your own file beside the given five, one expecting a
failure. `QA_PROFILE=partner` is the second row of a matrix. Upload the report. Then
`qa/REGRESSION.md`: one incident, and the case that exists because of it.

**+ Concurrency.** A group, demonstrated: push twice, watch the first run die. `CONCURRENCY.md` —
both run URLs, what was cancelled, why that one was safe to cancel.

---

## Handing it in

Pull request into your own `main`, template filled in, then a **submission issue** in
[catshop-submissions](https://github.com/kse-ci-cd-basics-course/catshop-submissions/issues/new/choose)
with the PR URL. The issue timestamp is your submission time.

A committed `.env`, or configuration you cannot explain, scores zero.
