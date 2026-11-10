/**
 * CampusSwap research workspace — Google Apps Script.
 *
 * Creates, in a "CampusSwap — Research" Drive folder:
 *   - Screener form   (who to interview)
 *   - Survey form     (13 questions, anonymous)
 *   - "CampusSwap — Research data" spreadsheet with tabs:
 *       Links · Screener responses · Survey responses · Participants · Interview notes · Usability tests
 *
 * Both forms write into the same spreadsheet, so analysis scripts (research/analyze_survey.py) read one file.
 * Questions match docs/assets/campusswap-research-plan.pdf.
 *
 * Run: script.google.com → New project → paste this file → select createResearchWorkspace → Run → Allow.
 */

const GREEN = '#1E7B5C';

function createResearchWorkspace() {
  const folder = DriveApp.createFolder('CampusSwap — Research');
  const ss = SpreadsheetApp.create('CampusSwap — Research data');
  moveTo_(ss.getId(), folder);

  const screener = buildScreener_();
  const survey = buildSurvey_();
  moveTo_(screener.getId(), folder);
  moveTo_(survey.getId(), folder);

  linkResponses_(screener, ss.getId(), 'Screener responses');
  linkResponses_(survey, ss.getId(), 'Survey responses');

  const book = SpreadsheetApp.openById(ss.getId());
  addParticipants_(book);
  addInterviewNotes_(book);
  addUsabilityLog_(book);
  const links = [
    ['What', 'Link'],
    ['Screener form (share this)', screener.getPublishedUrl()],
    ['Survey form (share this)', survey.getPublishedUrl()],
    ['Screener form (edit)', screener.getEditUrl()],
    ['Survey form (edit)', survey.getEditUrl()],
    ['This spreadsheet', book.getUrl()],
    ['Drive folder', folder.getUrl()],
  ];
  const sheet = book.insertSheet('Links', 0);
  sheet.getRange(1, 1, links.length, 2).setValues(links);
  styleHeader_(sheet, 2);
  sheet.setColumnWidth(1, 240);
  sheet.setColumnWidth(2, 640);
  const blank = book.getSheetByName('Sheet1');
  if (blank) book.deleteSheet(blank);

  const out = {};
  links.slice(1).forEach(([k, v]) => (out[k] = v));
  Logger.log(JSON.stringify(out, null, 2));
  return out;
}

// ---------------------------------------------------------------- Screener

function buildScreener_() {
  const form = FormApp.create('CampusSwap — Join a 25-minute chat about swapping stuff in the dorms');
  form.setDescription(
    "Hi! I'm Ahmed, working on a UX course project about how students in the dorms buy, sell and give away " +
    'everyday items (kettles, lamps, books…). I\'m looking for 5–6 dorm residents for a 25-minute chat. ' +
    'No preparation needed. This form takes 1 minute.');
  form.setProgressBar(true);
  form.setConfirmationMessage("Thank you! If you're a match, I'll message you on Telegram to pick a time.");

  const lives = form.addMultipleChoiceItem().setTitle('Do you currently live in the campus dorms?').setRequired(true);
  lives.setChoices([lives.createChoice('Yes', FormApp.PageNavigationType.CONTINUE),
                    lives.createChoice('No', FormApp.PageNavigationType.SUBMIT)]);
  form.addPageBreakItem().setTitle('About you');

  form.addMultipleChoiceItem().setTitle('How long have you lived in the dorms?').setRequired(true)
    .setChoiceValues(['Less than 1 semester', '1–2 semesters', '3 or more semesters']);
  form.addCheckboxItem()
    .setTitle('In the last 12 months, which of these have you done with another student?').setRequired(true)
    .setChoiceValues(['Bought a used item', 'Sold an item', 'Gave an item away for free', 'Received an item for free',
                      'None of these']);
  form.addMultipleChoiceItem().setTitle('What year are you in?').setRequired(true)
    .setChoiceValues(['Bachelor 1', 'Bachelor 2', 'Bachelor 3', 'Bachelor 4', 'Master 1', 'Master 2'])
    .showOtherOption(true);
  form.addMultipleChoiceItem().setTitle('Are you a local or an international student?').setRequired(true)
    .setChoiceValues(['Local', 'International']);
  form.addMultipleChoiceItem().setTitle('Are you available for a 25-minute chat this week?').setRequired(true)
    .setChoiceValues(['Yes', 'No']);
  form.addTextItem().setTitle('Your first name').setRequired(true);
  form.addTextItem().setTitle('Your Telegram username, so I can schedule the chat').setRequired(true)
    .setHelpText('Used only to contact you about this study.');
  return form;
}

// ---------------------------------------------------------------- Survey

function buildSurvey_() {
  const form = FormApp.create('CampusSwap — How do students exchange stuff in the dorms? (5 min)');
  form.setDescription(
    'A short anonymous survey for a UX course project about buying, selling and giving away dorm items ' +
    '(kettles, lamps, books, furniture…). It takes about 5 minutes. Thank you!');
  form.setProgressBar(true);
  form.setConfirmationMessage('Thank you for helping! 🌱');

  // 1. screening with branching
  const q1 = form.addMultipleChoiceItem().setTitle('1. Do you currently live in the campus dorms?').setRequired(true);
  q1.setChoices([q1.createChoice('Yes', FormApp.PageNavigationType.CONTINUE),
                 q1.createChoice('No', FormApp.PageNavigationType.SUBMIT)]);
  form.addPageBreakItem().setTitle('Your experience');

  form.addMultipleChoiceItem().setTitle('2. What is your year of study?').setRequired(true)
    .setChoiceValues(['Bachelor 1', 'Bachelor 2', 'Bachelor 3', 'Bachelor 4', 'Master 1', 'Master 2'])
    .showOtherOption(true);
  form.addCheckboxItem().setTitle('3. In the last 12 months, which of these have you done with another student?')
    .setRequired(true)
    .setChoiceValues(['Bought', 'Sold', 'Gave away for free', 'Received for free', 'None of these']);
  form.addCheckboxItem().setTitle('4. Which types of items have you exchanged, or wanted to?').setRequired(true)
    .setChoiceValues(['Kitchen items', 'Lamps / electronics', 'Furniture / storage', 'Bedding', 'Textbooks',
                      'Sports gear', 'Clothes'])
    .showOtherOption(true);
  form.addCheckboxItem().setTitle('5. When do you most often need to get or get rid of items?').setRequired(true)
    .setChoiceValues(['Moving in', 'Moving out', 'Start of semester', 'Mid-semester', 'Anytime']);
  form.addCheckboxItem().setTitle('6. Which channels do you use to find or offer items?').setRequired(true)
    .setChoiceValues(['Telegram chats', 'Avito', 'VK or other social groups', 'Friends',
                      'Leaving items in common areas', 'None'])
    .showOtherOption(true);
  form.addScaleItem().setTitle('7. How satisfied are you with these channels?').setRequired(true)
    .setBounds(1, 5).setLabels('Very dissatisfied', 'Very satisfied');

  const q8 = form.addCheckboxItem().setTitle('8. What are the biggest problems you face? (pick up to 3)')
    .setRequired(true)
    .setChoiceValues(['Hard to find items', 'Posts get lost in chats', 'Slow or no replies', 'Unclear condition',
                      'Price haggling', 'No-shows', 'Arranging pickup', "Don't trust strangers"])
    .showOtherOption(true);
  q8.setValidation(FormApp.createCheckboxValidation().setHelpText('Pick up to 3.').requireSelectAtMost(3).build());

  form.addGridItem().setTitle('9. Rank what matters most when deciding to take an item (1 = most important)')
    .setHelpText('Use each rank once.').setRequired(true)
    .setRows(['Price', 'Photos', 'Condition description', 'Distance / building', 'Seller rating / profile',
              'Quick reply'])
    .setColumns(['1', '2', '3', '4', '5', '6'])
    .setValidation(FormApp.createGridValidation().setHelpText('Use each rank once.')
      .requireLimitOneResponsePerColumn().build());

  const q10 = form.addCheckboxItem().setTitle('10. What would make you trust another student for an exchange? (pick up to 2)')
    .setRequired(true)
    .setChoiceValues(['Verified university account', 'Ratings / reviews', 'Mutual contacts',
                      'Meeting in a public spot', 'Profile photo'])
    .showOtherOption(true);
  q10.setValidation(FormApp.createCheckboxValidation().setHelpText('Pick up to 2.').requireSelectAtMost(2).build());

  form.addMultipleChoiceItem()
    .setTitle('11. In the last year, have you thrown away an item that someone else could have used?')
    .setRequired(true).setChoiceValues(['Yes', 'No', 'Not sure']);
  form.addScaleItem()
    .setTitle('12. How likely would you be to use a campus-only app for buying, selling and giving away items?')
    .setRequired(true).setBounds(1, 5).setLabels('Very unlikely', 'Very likely');
  form.addParagraphTextItem().setTitle("13. Anything else you'd like to share about exchanging items on campus?");
  return form;
}

// ---------------------------------------------------------------- Working tabs

function addParticipants_(book) {
  const sheet = book.insertSheet('Participants');
  sheet.getRange(1, 1, 1, 10).setValues([['ID', 'First name', 'Telegram', 'Year', 'Local / Intl', 'Mostly gives / gets',
    'Interview date', 'Consent to record', 'Usability test date', 'Notes']]);
  const ids = [];
  for (let i = 1; i <= 8; i++) ids.push(['P' + i]);
  sheet.getRange(2, 1, ids.length, 1).setValues(ids);
  validateList_(sheet.getRange('E2:E50'), ['Local', 'International']);
  validateList_(sheet.getRange('F2:F50'), ['Mostly gives', 'Mostly gets', 'Both']);
  validateList_(sheet.getRange('H2:H50'), ['Yes', 'No']);
  styleHeader_(sheet, 10);
}

function addInterviewNotes_(book) {
  const sheet = book.insertSheet('Interview notes');
  sheet.getRange(1, 1, 1, 7).setValues([['Participant', 'Question #', 'Note (one idea per row)', 'Type',
    'Direct quote?', 'Theme (fill during synthesis)', 'Comment']]);
  validateList_(sheet.getRange('A2:A1000'), ['P1', 'P2', 'P3', 'P4', 'P5', 'P6', 'P7', 'P8']);
  validateList_(sheet.getRange('B2:B1000'), ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', 'Other']);
  validateList_(sheet.getRange('D2:D1000'), ['Highlight', 'Pain', 'Opportunity', 'Observation']);
  validateList_(sheet.getRange('E2:E1000'), ['Yes', 'No']);
  sheet.setColumnWidth(3, 480);
  styleHeader_(sheet, 7);
}

function addUsabilityLog_(book) {
  const sheet = book.insertSheet('Usability tests');
  sheet.getRange(1, 1, 1, 8).setValues([['Participant', 'Task', 'Completed', 'Time (s)', 'Errors',
    'Ease 1–7 (SEQ)', 'What happened', 'Quote']]);
  validateList_(sheet.getRange('A2:A200'), ['P1', 'P2', 'P3', 'P4', 'P5', 'P6', 'P7', 'P8']);
  validateList_(sheet.getRange('B2:B200'), ['T1 Find a free lamp', 'T2 Request + pick a time',
    'T3 Confirm handover + rate', 'T4 Post a kettle']);
  validateList_(sheet.getRange('C2:C200'), ['Yes', 'With help', 'No']);
  validateList_(sheet.getRange('F2:F200'), ['1', '2', '3', '4', '5', '6', '7']);
  sheet.setColumnWidth(7, 420);
  styleHeader_(sheet, 8);
}

// ---------------------------------------------------------------- Helpers

function linkResponses_(form, ssId, name) {
  const before = SpreadsheetApp.openById(ssId).getSheets().map((s) => s.getSheetId());
  form.setDestination(FormApp.DestinationType.SPREADSHEET, ssId);
  SpreadsheetApp.flush();
  const book = SpreadsheetApp.openById(ssId);
  const created = book.getSheets().find((s) => before.indexOf(s.getSheetId()) === -1);
  if (created) created.setName(name);
}

function moveTo_(fileId, folder) {
  DriveApp.getFileById(fileId).moveTo(folder);
}

function validateList_(range, values) {
  range.setDataValidation(SpreadsheetApp.newDataValidation().requireValueInList(values, true)
    .setAllowInvalid(false).build());
}

function styleHeader_(sheet, cols) {
  sheet.setFrozenRows(1);
  sheet.getRange(1, 1, 1, cols).setFontWeight('bold').setFontColor('#FFFFFF').setBackground(GREEN);
}
