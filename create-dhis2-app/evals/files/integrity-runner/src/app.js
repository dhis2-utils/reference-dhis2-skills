"use strict";

//JS
import { d2PostThenGet } from "./js/d2api.js";
import { loadLegacyHeaderBarIfNeeded } from "./js/check-header-bar.js";
loadLegacyHeaderBarIfNeeded();

//CSS
import "./css/style.css";

const statusEl = document.getElementById("status");
const resultsEl = document.getElementById("results");

function renderIssues(issues) {
    resultsEl.replaceChildren();
    const header = document.createElement("tr");
    for (const label of ["Name", "UID", "Comment"]) {
        const th = document.createElement("th");
        th.textContent = label;
        header.appendChild(th);
    }
    resultsEl.appendChild(header);
    for (const issue of issues) {
        const row = document.createElement("tr");
        for (const value of [issue.name, issue.id, issue.comment || ""]) {
            const td = document.createElement("td");
            td.textContent = value;
            row.appendChild(td);
        }
        resultsEl.appendChild(row);
    }
}

async function runCheck() {
    const check = document.getElementById("checkSelect").value;
    statusEl.textContent = "Running " + check + "...";
    resultsEl.replaceChildren();
    try {
        const data = await d2PostThenGet("/api/dataIntegrity/details?checks=" + check);
        const result = data[check];
        if (!result || result.issues.length === 0) {
            statusEl.textContent = "No issues found.";
            return;
        }
        statusEl.textContent = result.issues.length + " issue(s) found.";
        renderIssues(result.issues);
    } catch (error) {
        statusEl.textContent = "Error: " + error.message;
    }
}

document.getElementById("runButton").addEventListener("click", runCheck);
