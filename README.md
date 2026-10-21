# CE Hub 2027: setup guide

This package is the public version of your CE Hub. When it's live, visitors can browse every listing without an account, and anyone who signs in with their email gets their favorites, licenses and transcript saved privately.

Plan on about 45 minutes. You'll set up three services, all free to start:

| Service | What it does | Cost to start |
|---|---|---|
| GitHub | Stores the site files | Free |
| Supabase | Handles sign-in and the private user database | Free tier |
| IONOS Deploy Now | Publishes the site on eyelovetravel.com | Free starter tier (3 projects); confirm at checkout |

Menus move around over time. If a button below has a slightly different name, look for the closest match.

---

## Step 0: Decide where the hub lives

Open **www.eyelovetravel.com** in your browser.

- **A. Nothing there yet, or just a parked or "coming soon" page:** the hub goes at **www.eyelovetravel.com/cehub**, exactly as you asked. Follow the **A** notes below.
- **B. A real website is already live there:** don't replace it. Put the hub on the subdomain **cehub.eyelovetravel.com**, then link to it from your main site's menu. Follow the **B** notes below.

The reason: Deploy Now publishes to a whole domain or subdomain, not a single folder of a site that's hosted elsewhere.

---

## Step 1: GitHub (10 min)

1. Go to **github.com** and choose **Sign up**. Use your email and verify it.
2. Click **+** (top right), then **New repository**.
   - Repository name: `cehub`
   - Visibility: **Private** is fine.
   - Leave "Add a README" unchecked.
   - Click **Create repository**.
3. On the new empty repo page, click the link **uploading an existing file**.
4. **Unzip** `cehub-site-claude.zip` on your computer. Drag everything *inside* the unzipped folder into the browser window: the `cehub` folder, the `supabase` folder, `index.html` and `README.md`. Don't drag the zip file itself.
5. Click **Commit changes**.

## Step 2: Supabase (10 min)

1. Go to **supabase.com**, choose **Start your project**, then **Continue with GitHub**. This is the easiest way, since it reuses your new GitHub login.
2. Click **New project**.
   - Name: `cehub`
   - Database password: click **Generate** and save it in your password manager.
   - Region: **East US**
   - Plan: **Free**
   - Click **Create new project** and wait about two minutes while it sets up.
3. Left menu: **SQL Editor**, then **New query**. Open `supabase/schema.sql` from the zip, copy all of it, paste it in, and click **Run**. You should see "Success. No rows returned."
4. Left menu: **Authentication**, then **URL Configuration**.
   - **Site URL:** `https://www.eyelovetravel.com/cehub/` (B: `https://cehub.eyelovetravel.com/`)
   - **Redirect URLs:** add the same address with `**` on the end, for example `https://www.eyelovetravel.com/cehub/**`. Click **Save**.
5. Left menu: **Authentication**, then **Sign In / Providers**. Make sure **Email** is enabled. It is by default.
6. Left menu: **Project Settings**, then **API Keys** (or **API**). Copy two things:
   - the **Project URL** (looks like `https://abcdefghijkl.supabase.co`)
   - the **Publishable key** (starts with `sb_publishable_`; older projects call it the **anon public** key)

   **Never copy the "secret" or "service_role" key anywhere.**
7. Back in GitHub, open your `cehub` repo, then the `cehub` folder, then `config.js`, then click the **pencil (Edit)** icon. Paste the URL and key between the quotes. Optionally add your contact email for sponsorship and correction requests. Click **Commit changes**.

## Step 3: IONOS Deploy Now (10–15 min)

1. Go to **ionos.com/hosting/deploy-now**, choose **Get started**, and log in with your IONOS account (the one that holds eyelovetravel.com). Pick the **free starter** option.
2. Choose **Connect GitHub**. Authorize the **IONOS Deploy Now** app and give it access to the `cehub` repository.
3. Select the `cehub` repo. When it asks about the project:
   - Type or framework: **Static site / no framework** (plain HTML)
   - Build command: leave it empty
   - Publish (dist) directory:
     - **A:** `./`, the repository root
     - **B:** `cehub`
4. Click **Deploy**. Deploy Now adds a small settings file and a workflow to your repo, then publishes. After a few minutes you'll get a preview address ending in `.ionos.space`.
   - **A:** open `<preview address>/cehub/`
   - **B:** open the preview address itself

   You should see the calendar.
5. In the Deploy Now project, open **Domains** (or **Add domain**):
   - **A:** choose `eyelovetravel.com` with `www`. If IONOS warns that the domain is in use by another product, stop. That means a site exists, and you should use option B.
   - **B:** create and choose the subdomain `cehub.eyelovetravel.com`.

   Because the domain is in the same IONOS account, Deploy Now sets up DNS and the SSL certificate for you. It can take up to an hour.
6. **B only:** in your main site's editor, add a menu item or button named "CE Hub" that links to `https://cehub.eyelovetravel.com/`.

## Step 4: Test it (5 min)

1. Open your live address. It loads with no account.
2. Star a meeting. It shows in the Favorites sidebar.
3. Click **Sign in**, enter your email, and open the link in the email **on the same device**. Your star should still be there, now saved to your account.
4. Go to **My licenses & CE**. Add Virginia with your renewal date, then upload your OE TRACKER transcript PDF and check the column matching.
5. In Supabase, open **Table Editor**, then **user_data**. You should see one row: yours.

If the sign-in link opens a page with an error, the address in Step 2.4 doesn't match your live address exactly. Fix it there.

---

## Before you promote it

- **Sign-in emails:** Supabase's built-in email sender only sends a few emails per hour, which is fine for testing but not a launch. In Supabase, go to **Authentication**, then **Emails**, then **SMTP Settings**. Enter the SMTP settings of an email account, for example an IONOS mailbox such as `hello@eyelovetravel.com`, or a sending service.
- **Inactivity pause:** free Supabase projects pause after about a week with no visitors. Steady traffic avoids this. Upgrading to the paid plan removes it when the hub catches on.
- **Privacy and Terms:** `cehub/privacy.html` and `cehub/terms.html` are drafts. Fill in the bracketed items (legal business name, contact email, address) and have an attorney review them.
- **Weekly updates:** the listings live in `cehub/data/events.json`. Until the weekly task can write to GitHub, the claude.ai version keeps updating, and Claude can copy the changes over on request. The permanent fix is to connect GitHub to Claude so the Monday task commits the update itself. Ask Claude to set that up once this is live.
- **Sponsored listings:** set `"sponsored": true` and `"sponsorLabel": "Sponsored"` on a listing in `events.json`. It moves to the top of its month and into the Featured section, always labeled. Collect payment with a Stripe payment link to start.

## What's in this package

```
index.html              → sends visitors from the domain root to /cehub/ (option A)
cehub/index.html        → the hub
cehub/config.js         → the only file you edit (Supabase URL and key, contact email)
cehub/data/*.json       → listings, state CE rules, update log
cehub/vendor/           → PDF reader (pdf.js) used for transcript uploads
cehub/privacy.html, terms.html → draft legal pages
supabase/schema.sql     → database setup (run once in Supabase)
```
