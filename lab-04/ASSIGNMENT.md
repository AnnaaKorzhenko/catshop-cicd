# Lab 4 — declare the place, do not click it

**Three sections. Due Wednesday 9 December, 23:59 Kyiv.** After that, 80% maximum.

Given: `app.py`, `requirements.txt`, `.env.example`, `.gitignore`. Do not change `app.py`.

It serves five endpoints. Two of them are new and exist only because there is now more than one
copy of it running:

| | |
|---|---|
| `/health` | is the process alive |
| `/ready` | can it serve right now |
| `/visits` | the counter — file-backed, or Postgres when `DATABASE_URL` is set |
| `/whoami` | **which copy answered**, and whether anything is proxying for it |
| `/version` | **which commit** this image was built from |

Push and read the checks. Each section is one check with a table behind it.

---

## Section 1 · The stack, declared

A load balancer, two copies of the application behind it, and one database behind them. You do not
start any of it by hand. You write it down and run two commands.

**Write:** `lab-04/terraform/main.tf`, `lab-04/terraform/variables.tf`,
`lab-04/terraform/outputs.tf`, `lab-04/terraform/nginx.conf.tftpl`, `lab-04/Dockerfile`

**Requirements:**

- `required_version` is set, and `required_providers` pins **`kreuzwerker/docker`** at a version —
  not at whatever the registry served today
- the provider's `host` comes from a **variable**. A default that only works on your own machine is
  a default that breaks in CI
- **three names are fixed**, because one grader reads forty-two configurations: the variables
  `docker_host` and `port`, and the output `url`. Everything else is yours
- one `docker_network`, one Postgres container, **two** application containers from a **single**
  resource using `count`, and one nginx container in front of them
- the application image is built by Terraform — a `docker_image` with a `build` block whose context
  is this folder. No registry login, no `docker build` in a workflow step
- `nginx.conf.tftpl` is rendered with `templatefile(...)`, and the backend names come **from the
  resource**. If you typed `catshop-app-0` into that template by hand, raising `count` to three
  silently does nothing
- the database password is a **`random_password`**, never a literal in the file
- the application reads `DATABASE_URL`, so both copies count into the *same* Postgres — two replicas
  with two separate counters is two applications, not one
- `outputs.tf` exports the URL the stack answers on, and the port comes from a variable
- `terraform init && terraform apply` is the whole command. No shell script, no `local-exec`, no
  `compose` file hiding underneath
- `terraform destroy` leaves nothing behind — no container, no network, no volume

**In the pull request:** what `terraform apply` did in what order, and what in your file decided
that order · the line in `nginx.conf.tftpl` that makes the pool follow `count` · where the database
password ended up, and who can read it there.

## Section 2 · State is not reality

**Write:** `lab-04/DRIFT.md`

Stop one of the two application containers by hand — `docker stop`, not Terraform. Then look at
what each side believes.

**Requirements:**

- with one copy stopped, the stack **still answers**. Requests through the load balancer return
  `200`, not `502`, and not a hang
- `terraform plan` notices. It reports exactly **one** resource to put back, and the rest unchanged
- `DRIFT.md` records: the `plan` line as it printed, what `apply` then did, and the one sentence
  that explains why Terraform knew
- no state file is committed. `*.tfstate` is ignored, and `git log` has never seen one

**In the pull request:** what the state said and what the machine said · why the load balancer did
not need to be told that a backend had gone · what would have happened if you had deleted
`terraform.tfstate` instead of a container.

## Section 3 · The same shape, rented

The same three things, written for a cloud you are **not** going to run. This section never leaves
`plan` and never needs an account.

**Write:** `lab-04/cloud/main.tf`, `lab-04/cloud/variables.tf`, `lab-04/COST.md`

**Requirements:**

- one cloud, chosen by you, declared properly: a **load balancer**, **two** instances, and a
  **managed database** — so pick one that has one: AWS, Google, Azure, DigitalOcean, Scaleway
- `terraform init -backend=false && terraform validate` passes with **no credentials anywhere**
- every data source is **parameterised**. A lookup that goes and asks the cloud something — an AMI
  by name, a zone listing — turns this into a configuration nobody can check
- a health check is declared, and its path is `/health`
- there is **no NAT gateway** in the file. It is the ~$32-a-month line nobody chose
- a `backend` block is written and committed, even though nothing here uses it
- `COST.md` prices your file: every resource, what it costs a month at rest, what the whole thing
  costs if nobody ever sends it a request, and which single line is the most expensive

**In the pull request:** the resource you expected to be free and was not · what your file would
actually create, in order · one thing `validate` cannot tell you.

---

## Bonus · reports, cannot cost you marks

### + It is on the internet

Put it somewhere real, with Terraform, on your own account. Any provider with a Terraform provider
counts — Hetzner, DigitalOcean, Scaleway, Fly, AWS, Google. A single instance is fine. This is
**not** section 1 again on a bigger machine; it is the smallest thing that is genuinely reachable.

**Write:** `lab-04/deploy/` — your configuration, `url.txt`, and `outputs.json`

**Requirements:**

- `url.txt` is one line: an `https://` URL, nothing else
- the certificate is real. The grader does not pass `-k`
- `GET /health` answers `200`
- `GET /version` returns **the commit being graded**. Build the sha into the image
  (`--build-arg GIT_SHA=...`) and deploy it — a version read from a variable at run time proves
  nothing about which code is running
- `outputs.json` is `terraform output -json`, committed, and the URL in it is the URL you published.
  Terraform made this, not a console
- `/whoami` shows a forwarded header. Whatever is in front of you — a cloud load balancer, a PaaS
  router, a reverse proxy — your application never sees the client's address directly

**In the pull request:** which provider and why · what it costs you a month · **the output of
`terraform destroy`**, and the empty resource listing after it.

> Leaving it running costs you money, not marks. Destroy it when you are done.

---

## Handing it in

Pull request into your own `main`, template filled in, then a **submission issue** in
[catshop-submissions](https://github.com/kse-ci-cd-basics-course/catshop-submissions/issues/new/choose)
with the PR URL. The issue timestamp is your submission time.

A committed `.env`, a committed `*.tfstate`, or configuration you cannot explain, scores zero.
