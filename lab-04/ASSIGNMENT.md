# Lab 4 — declare the place, do not click it

**Three sections. Due Wednesday 9 December, 23:59 Kyiv.** After that, 80% maximum.

This lab runs on a **real server**, at a real URL, with your state in a real backend. You are given
an account on the course server and nothing else. No application yet — that is the next lab. This
one is about the place the application will live, and about writing it down instead of clicking it.

Your stack answers at:

```
https://grizik.tech/<your-github-login>/
```

**You are already registered** if you have submitted at least one lab — your space was created from
your submission issues. If you have never submitted, send me your repository link in the chat and I
will add you. You will know it worked when the `prove who this run is` step goes green; a `403`
there means you are not on the roster yet, which is not something you can fix from your side.

---

## Before anything else — three one-time steps

| step | where | what to do |
|---|---|---|
| 1 | [app.terraform.io](https://app.terraform.io) | sign up (free), then **Account settings → Tokens → Create an API token**. A *user* token. An organization token cannot run a plan |
| 2 | your repository | variable `TF_CLOUD_ORGANIZATION` = your HCP organization · secret `TF_API_TOKEN` = that token |
| 3 | your HCP workspace | create `lab-04`, and set **Execution Mode: Local** |

Step 3 is not a formality. The course server is reachable only from inside *your pipeline run*, with
a certificate that run is issued for one hour. HCP's own runners have neither the route nor the
certificate, so a workspace left on Remote execution cannot work — and that is exactly what happens
with a private endpoint behind a VPC at work.

**The repository must be under your personal account.** The server identifies you from the GitHub
claim `repository_owner_id`; a repository owned by an organization presents the organization's id
and is refused.

### Your whole workflow file

You do not write the deployment plumbing. Copy this:

```yaml
name: lab 4
on:
  push:         { branches: [main], paths: ["lab-04/terraform/**"] }
  pull_request: { paths: ["lab-04/terraform/**"] }

permissions:
  contents: read
  id-token: write          # without this there is no token and no certificate

jobs:
  deploy:
    uses: kse-ci-cd-basics-course/catshop-grader/.github/workflows/lab-04-deploy.yml@v1
    with:
      hcp_org: ${{ vars.TF_CLOUD_ORGANIZATION }}
    secrets:
      TF_API_TOKEN: ${{ secrets.TF_API_TOKEN }}
```

Note the `paths:` filter. It covers the Terraform folder and nothing else: editing a README is not a
reason to touch infrastructure. Note also that it plans on a pull request and applies on `main` —
the shape lecture 6 argued for, and the reason you will see your plan before it happens.

There is **no secret for the server** anywhere in that file. Your pipeline proves who it is with a
token GitHub mints for the run, and gets back a certificate valid for one hour that can run exactly
one command in exactly one account. If you find yourself wanting an SSH key, you have taken a wrong
turn.

---

## Section 1 · The place, declared

A proxy, two copies of a web server behind it, and a volume. Public images only — you build nothing
and start nothing by hand.

**Write:** `lab-04/terraform/main.tf`, `lab-04/terraform/variables.tf`,
`lab-04/terraform/outputs.tf`, `lab-04/terraform/backend.tf`, `lab-04/terraform/nginx.conf.tftpl`

**Requirements:**

- `required_version` is set, and `required_providers` pins **`kreuzwerker/docker`** at a version —
  not at whatever the registry served today
- the provider's `host` comes from a **variable**. The workflow sets it for you as
  `TF_VAR_docker_host`; a default that only works on your own machine is a default that breaks in CI
- **four names are fixed**, because one grader reads thirty-two configurations: the variables
  `docker_host`, `port` and `bind_ip`, and the output `url`. Everything else is yours
- `backend.tf` declares `cloud {}` — **empty**. Organization and workspace come from the
  environment, which is what lets one configuration work for everyone. A `backend "local"` block, or
  no block at all, fails this section
- one `docker_network`, one `docker_volume`, **two** web containers from a **single** resource using
  `count`, and one proxy container in front of them
- the images are **`nginx:1.27-alpine`** with `keep_locally = true`. No `build` block in this lab
- `nginx.conf.tftpl` is rendered with `templatefile(...)` and the backend names come **from the
  resource**. If you typed `web-0` into that template by hand, raising `count` to three silently does
  nothing
- the proxy publishes on `var.port`, bound to **`var.bind_ip`**. Both are given to you. A container
  bound to `0.0.0.0` on a shared server is a second front door nobody is watching
- your two web containers must be **distinguishable**: `GET /whoami` through the proxy returns the
  hostname of whichever copy answered. nginx can do this on its own — `return 200 "$hostname\n";` —
  so no application code is needed
- `GET /health` through the proxy returns `200`
- `outputs.tf` exports `url`, and it is `var.public_url` when the workflow sets one, so the same
  configuration is true on your laptop and on the server
- `terraform init && terraform apply` is the whole command. No shell script, no `local-exec`, no
  `compose` file hiding underneath
- **a second `terraform plan` reports no changes.** This is graded on the exit code, not on the word
  "No changes." in a log

**In the pull request:** what `terraform apply` did in what order, and what in your file decided
that order · the line in `nginx.conf.tftpl` that makes the pool follow `count` · where your state
lives now, and what would have happened on the second run if it had lived on the runner.

## Section 2 · State is not reality

**Write:** `lab-04/DRIFT.md`

Stop one of the two web containers by hand. You have no shell on the server, so do it the way the
server allows — through the Docker API your pipeline already talks to, or with the two commands you
are given:

```
ssh studentNNN@grizik.tech catshop-ps
ssh studentNNN@grizik.tech "catshop-logs <container>"
```

Then look at what each side believes.

**Requirements:**

- with one copy stopped, the stack **still answers**. Requests through the proxy return `200`, not
  `502`, and not a hang
- `terraform plan` notices. It reports exactly **one** resource to put back, and the rest unchanged
- `DRIFT.md` records: the `plan` line as it printed, what `apply` then did, and the one sentence that
  explains why Terraform knew
- no state file is committed, and `git log` has never seen one. With `cloud {}` there should be
  nothing to commit — if there is, something is configured wrongly

> Your stack is removed automatically after 48 hours of nobody touching it. That is not a
> malfunction: it is the same drift you created on purpose, and re-running your pipeline is the
> repair. Say so in `DRIFT.md` if it happens to you.

**In the pull request:** what the state said and what the machine said · why the proxy did not need
to be told that a backend had gone · what would have happened if you had deleted the workspace's
state instead of a container.

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

## The server, and how to be a good neighbour

Thirty-two of you share one machine. It is not generous, and the limits are real rather than
advisory:

| | |
|---|---|
| memory | 320 MB, plus 128 MB of swap |
| CPU | half a core |
| processes | 150 |
| disk | 2 GB |
| deployments at once | **10 across the whole class** |

If all ten deployments are busy when your job starts, it **waits** — you will see a step called
*"Wait for a free deployment slot"* counting down. That is normal near a deadline. If it gives up,
the message says so in as many words: nothing was created, nothing was broken, re-run the job. A
failure that says *"this is not a problem with your code"* is not a problem with your code.

You cannot reach another student's account, containers, ports, home directory or processes. Please
do not spend the lab finding out — if you do find a way, tell me, and I will say so in the lecture
with your name on it.

---

## Handing it in

Pull request into your own `main`, template filled in, then a **submission issue** in
[catshop-submissions](https://github.com/kse-ci-cd-basics-course/catshop-submissions/issues/new/choose)
with the PR URL. The issue timestamp is your submission time.

A committed state file, a committed token, or configuration you cannot explain, scores zero.
