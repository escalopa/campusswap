# Research toolkit

| File | What it does |
|---|---|
| `forms/create_research_workspace.gs` | Google Apps Script that creates the screener form, the survey form and the **CampusSwap — Research data** spreadsheet (both forms answer into it, plus tabs for participants, interview notes and usability tests). |
| `analyze_survey.py` | Turns the CSV export of the spreadsheet tabs into a Markdown summary and charts for the research report. |

## Workflow

1. **Create the forms (once):** script.google.com → New project → paste `forms/create_research_workspace.gs` → run `createResearchWorkspace` → allow access. The links appear in the spreadsheet's **Links** tab.
2. **Recruit:** post the screener link in dorm and course chats, then pick 5–6 people:
   ```bash
   python research/analyze_survey.py screener "Screener responses.csv"
   ```
3. **Interview:** one row per idea in the **Interview notes** tab (participant, question #, note, type).
4. **Survey:** share the survey link; aim for 30+ answers. Then:
   ```bash
   pip install matplotlib
   python research/analyze_survey.py survey "Survey responses.csv" --out research/results
   ```
   `research/results/summary.md` has every question with counts and %, and `q*.png` charts go into the report and the deck.
5. **Usability tests:** one row per participant and task in the **Usability tests** tab.

Raw responses contain names and Telegram usernames: keep the CSV exports out of git (`research/*.csv` is ignored).
