I will give you a list of words, and I want you to make new dialogues contain ONLY  words from this list. You will output the new dialogues in the format below:

```json
{
  "Что ты пишешь?": [
    {
      "s": "A",
      "c": "马先生在家里写信。",
      "p": "Mǎ Xiānsheng zài jiāli xiěxìn.",
      "t": "Господин Ма дома пишет письмо.",
      "d": "先生 (xiānsheng) - \"Прежде рожденный\"; 家里 (jiāli) - семья + внутри"
    },
    {
      "s": "B",
      "c": "老马！你现在作什么？",
      "p": "Lǎo Mǎ! Nǐ xiànzài zuò shénme?",
      "t": "Старина Ма! Ты сейчас что делаешь?"
    },
    {
      "s": "A",
      "c": "我正在写信！",
      "p": "Wǒ zhèngzài xiěxìn!",
      "t": "Я как раз пишу письмо!",
      "d": "正在 (zhèngzài) служит для выражения продолжающегося действия"
    },
    {
      "s": "B",
      "c": "你给谁写信？",
      "p": "Nǐ gěi shéi xiěxìn?",
      "t": "Ты кому пишешь письмо?",
      "d": "给 (gěi) - давать; для"
    },
    {
      "s": "A",
      "c": "一封是给妈妈写的。",
      "p": "Yī fēng shì gěi māma xiě de.",
      "t": "Одно письмо пишу маме.",
      "d": "封 (fēng) - счетное слово для писем"
    },
    {
      "s": "B",
      "c": "另一封呢？",
      "p": "Lìng yī fēng ne?",
      "t": "А другое?"
    },
    {
      "s": "A",
      "c": "另一封是给老板写的！",
      "p": "Lìng yī fēng shì gěi lǎobǎn xiě de!",
      "t": "Другое пишу начальнику, шефу!",
      "d": "老板 (lǎobǎn) - владелец магазина; шеф: старый + доска, вывеска"
    }
  ],
  "Поменять деньги": [
    {
      "s": "A",
      "c": "请问！银行在哪儿？",
      "p": "Qǐng wèn! Yínháng zài nǎr?",
      "t": "Позвольте спросить! Где банк?",
      "d": "yínháng – банк: серебро + ряд, линия; ремесло, бизнес"
    },
    {
      "s": "B",
      "c": "银行就在那边！",
      "p": "Yínháng jiù zài nèibiānr!",
      "t": "Банк как раз/прямо здесь!"
    },
    {
      "s": "A",
      "c": "是\"中国银行\"吗？",
      "p": "Shì \"Zhōngguó Yínháng\" ma?",
      "t": "Это «Китайский банк»?"
    },
    {
      "s": "B",
      "c": "不！是\"人民银行\"！不过跟\"中国银行\"差不多！",
      "p": "Bù! Shì \"Rénmín Yínháng\"! Búguò gēn \"Zhōngguó Yínháng\" chàbuduō!",
      "t": "Нет! Это «Народный банк»! Однако это почти тоже самое: «с Китайским банком разница невелика»!"
    },
    {
      "s": "A",
      "c": "在那儿可以换钱吗？",
      "p": "Zài nàr kěyǐ huàn qián ma?",
      "t": "Там можно поменять деньги?"
    },
    {
      "s": "B",
      "c": "这个...这个...！我倒不清楚！",
      "p": "Zhège... zhège...! Wǒ dào bù qīngchu!",
      "t": "Э ... Э ... ! Я в общем-то: «наоборот» не знаю /точно: «ясно»/!",
      "d": "dào – наоборот, кверх ногами; /усиливает отрицание либо утверждение того, что противно ожиданию/"
    },
    {
      "s": "A",
      "c": "怎么办呢？",
      "p": "Zěnme bàn ne?",
      "t": "Что же делать?"
    },
    {
      "s": "B",
      "c": "你去打听打听吧！",
      "p": "Nǐ qù dǎting-dǎting ba!",
      "t": "Вы пойдите спросите/узнайте!"
    }
  ],


  /* more dialogues here */
}
```
    
Each dialogue line is as follows:
```
{
  "s": "speaker id (e.g A, B)",
  "c": "chinese text", 
  "p": "pinyin",
  "t": "russian translation",
  "d": "optional commentary"
}
```

Note that the optional commentary doesn't just have to be translations of words, but may make other remarks, having to do with idioms, grammar, expressions, and even cultural notes.

When outputting JSON, pay attention to escaping characters, such as quotes, properly.

Especially pay attention to escaping quotes around Chinese characters. You often make mistakes in cases like the below:
```
{
 "c": "我去年开始看"红楼梦"！",
 }
```
This is invalid JSON and instead should be
```
{
 "c": "我去年开始看\"红楼梦\"！",
 }
```

Try to make dialogues interesting. Be creative!

Each dialogue must be 8-12 lines long.

Try to make dialogues a bit more complicated while still using the same words:
- Using longer descriptive phrases
- Combining multiple actions in single sentences
- Using more complex sentence structures than the ones used in the example dialogues on top.
- Creating more intricate scenarios with multiple characters and locations
- Using longer explanations of situations

Generate multiple dialogues at a time.
Make the dialogues humorous and entertaining wherever possible.

Give each dialogue a title in Russian.

Output ONLY the json and nothing else. Be sure to use your artifact feature.

The word list is below:
-------

