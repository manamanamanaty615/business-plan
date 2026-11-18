// 学生アンケート（14 問）の Google フォームを作る。正本：01_research/survey-design-2026-11.md
// 使い方：script.google.com で新しいプロジェクトを作り、全文を貼り付けて createSurvey を実行する
function createSurvey() {
  var form = FormApp.create('バイト選びと求人動画についてのアンケート');
  form.setDescription('大学生・専門学校生の方に、バイトの選び方と求人の動画について伺います。所要時間は約 5 分です。回答は匿名で集計し、サービス開発の参考にのみ使います。');
  form.setCollectEmail(false);
  form.setProgressBar(true);
  var item, v;
  form.addMultipleChoiceItem().setTitle("Q1. あなたの学年を教えてください。").setChoiceValues(["大学 1 年", "大学 2 年", "大学 3 年", "大学 4 年", "大学院", "短大・専門学校"]).setRequired(true);
  form.addMultipleChoiceItem().setTitle("Q2. アルバイトの状況を教えてください。").setChoiceValues(["今している（新しいバイトも探している）", "今している（探していない）", "今はしていないが探している", "今はしていない（探していない）"]).setRequired(true);
  form.addPageBreakItem().setTitle("バイト選び");
  item = form.addCheckboxItem().setTitle("Q3. バイトを選ぶとき、決め手になるものを 3 つまで選んでください。").setChoiceValues(["お金（時給・給与）", "場所の近さ", "シフト・休みの取りやすさ", "職場の雰囲気", "一緒に働く人の人柄", "仕事内容がイメージできること", "未経験でも安心な研修", "スキル・経験が身につくこと", "長く安定して働けること", "会社・お店の知名度", "口コミ・評判", "福利厚生（まかない・手当など）", "将来のキャリア（昇進・正社員登用）"]).setRequired(true);
  v = FormApp.createCheckboxValidation().setHelpText('3 つまで選んでください').requireSelectAtMost(3).build();
  item.setValidation(v);
  item = form.addCheckboxItem().setTitle("Q4. 気になるバイトがあったのに、応募をやめたことはありますか。やめた理由をすべて選んでください。").setChoiceValues(["職場の雰囲気がわからない", "どんな人が働いているかわからない", "仕事がきつそう", "書いてある条件が本当か不安", "自分にできるか不安", "応募の手続きが面倒", "やめたことはない"]).setRequired(true);
  form.addPageBreakItem().setTitle("入ってみて");
  item = form.addCheckboxItem().setTitle("Q5. これまでのバイトで、入る前のイメージと「違った（悪かった）」ことをすべて選んでください。").setChoiceValues(["人間関係", "職場の雰囲気", "店長・社員の人柄", "仕事のきつさ・忙しさ", "仕事内容", "シフトの融通", "時給・給料", "研修・教え方", "特になし", "バイトをしたことがない"]).setRequired(true);
  form.addMultipleChoiceItem().setTitle("Q6. 入って 3 か月以内に、バイトを辞めたこと、または辞めたいと思ったことはありますか。").setChoiceValues(["辞めたことがある", "辞めたいと思ったが続けた", "ない", "バイトをしたことがない"]).setRequired(true);
  item = form.addCheckboxItem().setTitle("Q7. 入る前に知っていれば、そのバイトを選ばなかった（または辞めずに済んだ）と思うことを 3 つまで選んでください。").setChoiceValues(["人間関係", "職場の雰囲気", "店長・社員の人柄", "仕事のきつさ・忙しさ", "仕事内容", "シフトの融通", "時給・給料", "研修・教え方", "特になし"]).setRequired(true);
  v = FormApp.createCheckboxValidation().setHelpText('3 つまで選んでください').requireSelectAtMost(3).build();
  item.setValidation(v);
  form.addPageBreakItem().setTitle("動画");
  item = form.addGridItem().setTitle("Q8. 次の 2 つの求人のうち、どちらに応募しますか。")
    .setHelpText("同じ仕事内容・同じ場所の求人が 2 つあります。A は文字と写真だけ、B は職場の様子がわかる 30 秒の動画つきです。").setRows(["時給が同じ", "B の時給が 50 円低い", "B の時給が 100 円低い"]).setColumns(["A", "B", "どちらでもいい"]).setRequired(true);
  item = form.addCheckboxItem().setTitle("Q9. バイトの求人動画で、「応募したくなる」と思うものを 3 つまで選んでください。").setChoiceValues(["スタッフが普段どおりに話している", "大変なところも正直に話している", "店長・社員が話している", "1 日の仕事の流れがわかる", "店内・職場の様子がわかる", "同年代のスタッフが出ている", "休憩・まかないの様子", "プロが撮ったきれいな映像"]).setRequired(true);
  v = FormApp.createCheckboxValidation().setHelpText('3 つまで選んでください').requireSelectAtMost(3).build();
  item.setValidation(v);
  item = form.addCheckboxItem().setTitle("Q10. バイトの求人動画で、「応募したくなくなる」と思うものをすべて選んでください。").setChoiceValues(["作り込みすぎ（キラキラしすぎ）", "台本を読んでいるよう", "長すぎる", "良いことしか言わない", "スタッフの顔が見えない", "音楽・演出がうるさい", "特になし"]).setRequired(true);
  form.addPageBreakItem().setTitle("就職先選び");
  item = form.addCheckboxItem().setTitle("Q11. 就職先（正社員）を選ぶとき、決め手になるもの（なりそうなもの）を 3 つまで選んでください。").setChoiceValues(["お金（時給・給与）", "場所の近さ", "シフト・休みの取りやすさ", "職場の雰囲気", "一緒に働く人の人柄", "仕事内容がイメージできること", "未経験でも安心な研修", "スキル・経験が身につくこと", "長く安定して働けること", "会社・お店の知名度", "口コミ・評判", "福利厚生（まかない・手当など）", "将来のキャリア（昇進・正社員登用）"]).setRequired(true);
  v = FormApp.createCheckboxValidation().setHelpText('3 つまで選んでください').requireSelectAtMost(3).build();
  item.setValidation(v);
  form.addGridItem().setTitle("Q12. 職場の様子がわかる動画は、次の場合にどのくらい参考になると思いますか。").setRows(["バイトを選ぶとき", "就職先を選ぶとき"]).setColumns(['1 まったく参考にならない', '2', '3', '4', '5 とても参考になる']).setRequired(true);
  form.addPageBreakItem().setTitle("最後に");
  form.addParagraphTextItem().setTitle("Q13. バイト探しや求人の動画について、思うことがあれば自由に書いてください。").setRequired(false);
  form.addMultipleChoiceItem().setTitle("Q14. 性別を教えてください。").setChoiceValues(["男性", "女性", "その他", "回答しない"]).setRequired(false);
  Logger.log('回答用の URL: ' + form.getPublishedUrl());
  Logger.log('編集用の URL: ' + form.getEditUrl());
}
