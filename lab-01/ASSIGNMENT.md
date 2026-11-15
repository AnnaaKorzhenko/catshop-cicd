# Lab 1 — containers and the image

**Three sections. Due Thursday 12 November, 23:59 Kyiv.** After that, 80% maximum.

## Given

```
app.py · requirements.txt     a small Flask app — do not change it
init-db/01-schema.sql         applied on the database's first boot
partner/mappings/             a third party's stubbed responses
.env.example                  copy to .env. Never commit .env
```

## You write

```
Dockerfile · .dockerignore · compose.yaml        all inside lab-01/
```

| Endpoint | Depends on | Section |
|---|---|---|
| `GET /health` | nothing | 1 |
| `GET /visits` | our own state — a file, then a database | 1, then 3 |
| `GET /price/<sku>` | an API we do not own | bonus |

Publish the app on host port `8080`. Push and read the checks; each section is one check with a
table behind it.

---

## 1 · An image that runs

`Dockerfile` and `.dockerignore`. Build, run, reach the app from your host. Build twice — the second
time after editing one line of `app.py` — and time both. Then reorder your instructions and do it
again.

**Pull request:** what `EXPOSE` actually does, with the output of trying to reach an unpublished
port · both sets of build timings and the reason for the difference · what `transferring context`
did when you added `.dockerignore`.

## 2 · An image worth shipping

The image works. It also carries things production has no use for, and the process inside it has
more power than it needs. Fix both without changing what the app does.

**Pull request:** both image sizes, and which change bought which saving · proof the thing you
removed is gone — ask both images for it · the error the less-privileged version hit · the two real
reasons chaining with `&&` matters, and why one enormous `RUN` is also wrong.

## 3 · A stack that keeps its data

`compose.yaml` with your app and PostgreSQL, counter moved out of the container's filesystem into
the database. Name the services `app` and `db`.

The checks run `docker compose up -d app` and nothing else. Three things must then be true: the app
answers, the rows survive the containers being destroyed and recreated, and nothing on your laptop
can connect to the database directly.

**Pull request:** the data-loss transcript — destroy and restore the stack once losing the rows and
once keeping them, paste both · the log from starting the stack with nothing coordinating app and
database, then what it waits for now · a named volume versus a bind mount, and when you reach for
each.

---

## Bonus

Bonus sections report and cannot cost you marks.

**+ The API you do not own.** Add `wiremock/wiremock:3.6.0` with the stubs in `partner/mappings/` so
`/price/MK-II` answers. Then produce the two failures the real partner would never give you on
request, and paste both.

**+ Close the doors.** Reach the database from four places, with the real error text for each: your
laptop, by service name on the default bridge, by container IP, and by service name on a network you
created. Restart the database between the third and the fourth. Then say why the attempt that worked
was still wrong. Finish by cutting the database and the partner off the internet with the app still
reaching both.

**+ Redis** as a fourth service, used for something real.

**+ Your own application** (+10). All three sections against a service you wrote, in any language.
`/health`, and configuration from the environment.

---

## Handing it in

Pull request into your own `main`, template filled in — alternatives, measurements and the AI
disclosure each carry marks — then a **submission issue** in
[catshop-submissions](https://github.com/kse-ci-cd-basics-course/catshop-submissions/issues/new/choose)
with the PR URL. The issue timestamp is your submission time.

A committed `.env`, or configuration you cannot explain, scores zero.
