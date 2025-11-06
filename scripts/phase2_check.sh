#!/usr/bin/env bash
set -u
BASE=${BASE:-http://localhost:8000}
TOKEN=${TOKEN:-dev123}
hdr=(-H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json")
pass(){ echo "✅ $*"; }
fail(){ echo "❌ $*"; FAILED=1; }
FAILED=0
TMP=$(mktemp -d); trap 'rm -rf "$TMP"' EXIT
echo "=== Phase-2 validation ==="

# health
code=$(curl -s -o /dev/null -w "%{http_code}" "$BASE/health" "${hdr[@]:0:1}")
[[ "$code" == "200" ]] && pass "health ok" || fail "health $code"

# upsert
u=$(curl -s -X POST "$BASE/profile:upsert" "${hdr[@]}" -d '{
  "name":"Vaishnavi","email":"vaishnavi@example.com","domain":"career",
  "data":{"goal":"Backend internship","hours_per_week":10,"style":"hands-on"}
}')
echo "$u" > "$TMP/u.json"
uid=$(jq -r '.user_id // empty' "$TMP/u.json")
[[ -n "$uid" ]] && pass "profile ok id=$uid" || fail "profile failed"

# generate
g=$(curl -s -X POST "$BASE/roadmap:generate" "${hdr[@]}" -d "{ \"user_id\": $uid, \"domain\": \"career\" }")
echo "$g" > "$TMP/g.json"
rid=$(jq -r '.roadmap_id // empty' "$TMP/g.json")
ver=$(jq -r '.version // empty' "$TMP/g.json")
[[ -n "$rid" ]] && pass "generate ok id=$rid v=$ver" || fail "generate failed"

# revise twice
rev1=$(curl -s -X POST "$BASE/roadmap:revise" "${hdr[@]}" -d "{ \"roadmap_id\": $rid, \"feedback\": {\"signal_type\":\"missing_topic\",\"notes\":\"Include basic system design.\"}}")
rid1=$(jq -r '.roadmap_id // empty' <<<"$rev1")
ver1=$(jq -r '.version // empty' <<<"$rev1")
rev2=$(curl -s -X POST "$BASE/roadmap:revise" "${hdr[@]}" -d "{ \"roadmap_id\": $rid1, \"feedback\": {\"signal_type\":\"missing_topic\",\"notes\":\"Add DB indexing basics.\"}}")
rid2=$(jq -r '.roadmap_id // empty' <<<"$rev2")
ver2=$(jq -r '.version // empty' <<<"$rev2")
[[ "$ver1" -gt "$ver" && "$ver2" -gt "$ver1" ]] && pass "versions increase $ver->$ver1->$ver2" || fail "versions not increasing"

# design check
d=$(curl -s "$BASE/roadmap/$rid2" "${hdr[@]:0:1}")
ok=$(jq -r '[.plan.milestones[]?.title|ascii_downcase|contains("design")]|any' <<<"$d")
[[ "$ok" == "true" ]] && pass "design milestone present" || fail "no design milestone"

[[ "$FAILED" -eq 0 ]] && pass "Phase-2 ✅ PASSED" || fail "Phase-2 ❌ FAILED"
