I have some dialogues in the following yaml format:

```
dialogue_id:
# list of lines of the dialogue
- s: speaker (identifies who the line belongs to)
  c: chinese text
  p: pinyin
  t: english translation
  d: commentary on anything that might be of particular interest to a learner
```

example:

```
dialogue_6:
 - s: A
   c: 你最近在做什么？
   p: Nǐ zuìjìn zài zuò shénme?
   t: What have you been doing lately?
   d: 最近 (zuìjìn) is a very common time word meaning "recently, lately". The 在 indicates ongoing action.
 
 - s: B
   c: 我在学习。你呢？
   p: Wǒ zài xuéxí. Nǐ ne?
   t: I'm studying. How about you?
   d: 呢 (ne) is a common particle used to ask "how about you/what about...?"

dialogue_7:
 - s: A
   c: 你看见我的书了吗？
   p: Nǐ kànjiàn wǒ de shū le ma?
   t: Have you seen my book?
   d: 看见 (kànjiàn) specifically means "to see" as in "to spot/notice", different from just 看 (kàn)
```

Let's write a simple html/javascript page to display these. 
---

1. The page loads dialogues from a path defaulting to a `dialogues.yaml` file in the same parent path as the page. The URL of this file can be specified by pressing a button.

2. I can select a dialogue from the list of dialogues in the file.

3. The dialogue is then displayed on the page.

4. There are controls on the page that let me toggle between these modes: displaying chinese text only, chinese+pinyin, chinese+pinyin+translation, chinese+pinyin+translation+commentary.

5. Make the page pretty using some css.

