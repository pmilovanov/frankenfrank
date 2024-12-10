A file with dialogues formerly looked like this:

```
{
  "1 - Что ты думаешь?": [
    {
      "s": "A",
      "c": "你觉得这个怎么样？",
      "p": "Nǐ juéde zhège zěnmeyàng?",
      "t": "Что ты об этом думаешь?",
      "d": "觉得 (juéde) \"думать/чувствовать\", часто используется, чтобы обозначить мнение"
    },
    {
      "s": "B",
      "c": "我觉得很好。",
      "p": "Wǒ juéde hěn hǎo.",
      "t": "Я думаю, что это хорошо."
    }
  ],
  "2 - You look very happy!": [
    {
      "s": "A",
      "c": "你今天看起来很高兴。",
      "p": "Nǐ jīntiān kàn qǐlái hěn gāoxìng.",
      "t": "Сегодня ты выглядишь очень счастливым.",
      "d": "看起来 (kàn qǐlái) значит \"выглядеть\", часто используется для описания внешнего вида"
    }
  ]
}
```

We are now changing the format to the one below:
- dialogues are now in a list, not in a dictionary
- each dialogue has a "title" field and a "lines" field
- title moved from the key of the dictionary to the "title" field of the dialogue
- the "lines" field contains the dialogue lines

```json
[
  {
    "lines": [
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
      }
      /* more dialogue lines here */
    ],
    "title": "В гостях у Ма"
  },
  /* more dialogues here */
]
```