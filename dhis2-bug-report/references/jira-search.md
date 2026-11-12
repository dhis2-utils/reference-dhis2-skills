# Searching Jira for existing issues

The DHIS2 issue tracker is public, at `https://dhis2.atlassian.net` (project `DHIS2`). Anyone can read it without an account; filing needs one.

How to search, in order of preference:

- **A Jira integration in your environment** (an Atlassian MCP server or similar). Take the site or cloud id from the integration instead of hardcoding it, and check the access it grants: usually read-only, so you can search and read but not create.
- **No integration:** the issue navigator takes JQL in the URL, `https://dhis2.atlassian.net/issues/?jql=<url-encoded JQL>`. The REST search (`GET /rest/api/3/search/jql?jql=...&fields=summary,status,resolution,fixVersions,components`) may also answer without login; if it returns nothing or 401, give the user the navigator links instead of claiming the search was done.

Either way, produce the ticket as a file for the user to paste, and say plainly that you have not filed it.

Core issues live in project `DHIS2` ("DHIS 2 Software"). Apps are distinguished by component, named like `[App] Data visualizer`. To find the right component name, search for any issue you know is in that app and read its `components` field.

## Search strategy

Run three or four narrow searches rather than one long one. `text ~ "several words"` tokenises and matches loosely, so a long phrase returns a pile of unrelated old issues; the query `text ~ "reporting rate totals"` returns a 2019 issue about data item selection alongside the real match. Short, distinctive term pairs work better. For a true phrase match, nest the quotes: `text ~ "\"expected reports\""`.

Search the vocabulary a reporter would have used, which is often not yours. For a totals bug, try the symptom (`NaN`), the feature (`subtotal`), and the data type (`completeness`, `reporting rate`) as separate queries. Someone else's ticket may describe the same defect in words you would never pick.

```
project = DHIS2 AND component = "[App] Data visualizer" AND text ~ "NaN subtotal" ORDER BY updated DESC
project = DHIS2 AND text ~ "completeness totals" ORDER BY created DESC
```

Include closed issues. A resolved duplicate tells you the fix version, which changes the ticket entirely: if it is fixed in an app release newer than the one you tested, there is nothing to file. Ask for `status`, `resolution` and `fixVersions` in the fields list so you can see this without a second call.

## When to search

Search once after you have restated the bug, before spending effort on reproduction. Search again at the end, once you know the actual trigger, because by then you have better keywords than you started with. The second search is the one that catches issues filed against the underlying mechanism rather than the visible symptom.

## What to do with a hit

Read the candidate before calling it a duplicate. Same symptom is not the same bug: check that the trigger conditions and affected versions match.

Genuine duplicate, still open: tell the user the key and stop. Offer to add what you found as a comment if your reproduction adds something the existing issue lacks, such as another affected version or a narrower trigger.

Genuine duplicate, resolved in a version newer than the one tested: say so and stop. Suggest the user retest on the fixed version.

Related but not the same: finish the ticket and add a Related issues line naming the keys, so whoever triages can link them.

Nothing found: say the search was run and came back empty. That is worth one sentence in the ticket — it tells the triager the check was done and saves them repeating it.
