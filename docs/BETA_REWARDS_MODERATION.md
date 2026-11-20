# Beta policy v1 — implemented engineering policy, not original project subjects

## Executable daily mission
The only mission uses the supplied foundation Stream Sum Python specification
(`project_suites.SPEC`). Open `/progress`→editor and submit through the existing
trusted project pipeline. Eligibility requires an OWNED `success`,score>=80 record
for that exact project created within the current UTC day. Client scores, XP,
submission IDs, claimed dates or other users' results cannot establish eligibility.
Claim reward25XP once per user/UTC day. Unique durable claim+XP commit together;
PostgreSQL uses the same user lock as project awards. Replays409. No claim on GET.
Original nine subjects are not substituted by this mission. No judge execution
or mission completion is simulated while public judging is disabled. DB success
fixtures in local tests demonstrate award logic, not sandbox execution.

## Advanced measured badge/reputation catalog
`/progress` calculates current eligibility: bronze first passed project; silver five
passed projects; silver completed scored reviews for three DISTINCT other authors;
gold seven consecutive submission days UTC. Repeat reviews of one peer and self
reviews cannot inflate distinct-peer counts. These are current-record badges,
recalculated (not permanent historical certificates), and award no additional XP.
Owner UI and opted-in portfolio show qualifying badges. Existing manually awarded
badge records remain preserved, not rewritten.
Reputation is clamp0..100 of50 +min(30,2×passed projects)
+min(20,2×distinct reviewed authors) −min(50,5×distinct author messages removed by
staff). Open/duplicate/dismissed reports have no penalty. Repeat reads award nothing.
Analytics/portfolio use this policy. Historical stored User.reputation/badges fields
are retained for compatibility, not used as authority for this measured catalog.
This policy is transparent engagement feedback, not identity/skill certification.
Sybil/collusion prevention still needs operational/independent review.

## Basic room moderation and reporting
Members may report someone else's message with reason5..1000chars, one report per
reporter/message,30mutation requests/minute. Nonmembers receive404 without message
content disclosure. `/moderation` shows owned reports; administrators see bounded
paginated queue+message evidence. Only admins may dismiss/remove; reporter/author
admins cannot review their own conflicts. Resolve is single-winner; repeated409.
Remove transactionally marks the message independently of report lifetime, so
reporter deletion cannot restore content. It hides message from BOTH room detail
and history; evidence remains stored for
review/retention. Reasons remain reporter/admin only, never sent to message author.
Deleting an account follows FK cascades; no promise of backup erasure. No automated
classifier, platform-wide reporting, appeal workflow or staffed response SLA claimed.

Room messages poll every5seconds; staff/report queue every10seconds, only visible
tabs. Requests do not overlap slow responses; timers stop on unmount. No websocket
presence/audio/video/collaborative editor claim. Failed requests remain visible.
