// CE Hub settings. Edit this one file after creating your Supabase project.
// Supabase dashboard → Project Settings → API (or "API Keys"):
//   supabaseUrl     = the Project URL, e.g. https://abcdefghijkl.supabase.co
//   supabaseAnonKey = the "publishable" key (sb_publishable_…) or the legacy "anon public" key.
// Both are safe to publish — the database rules in supabase/schema.sql protect each user's data.
// NEVER put the "secret" / "service_role" key here.
window.CEHUB_CONFIG = {
  supabaseUrl: "https://YOUR-PROJECT-REF.supabase.co",
  supabaseAnonKey: "YOUR-PUBLISHABLE-KEY",
  contactEmail: "",      // shown for sponsorship and correction requests, e.g. "hello@eyelovetravel.com"
  defaultHome: null      // optional default for distances, e.g. {name:"Big Stone Gap, VA", lat:36.8682, lon:-82.776}
};
