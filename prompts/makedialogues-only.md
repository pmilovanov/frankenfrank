Make some short dialogues using ONLY the words from the list of words at the bottom. 

Output the dialogues using the following yaml format:

```
1 - What do you think?:
 - s: A
   c: 你觉得这个怎么样？
   p: Nǐ juéde zhège zěnmeyàng?
   t: What do you think of this?
   d: 觉得 (juéde) "to think/feel" is very commonly used for opinions

 - s: B
   c: 我觉得很好。
   p: Wǒ juéde hěn hǎo.
   t: I think it's very good.
   
 # dialog continues with more lines

2 - You look very happy!:
 - s: A
   c: 你今天看起来很高兴。
   p: Nǐ jīntiān kàn qǐlái hěn gāoxìng.
   t: You look very happy today.
   d: 看起来 (kàn qǐlái) means "looks like/appears to be"
   
  # dialog continues with more lines
```

Each dialogue line is as follows: 
```
- s: speaker id (e.g A, B)
  c: chinese text
  p: pinyin
  t: english translation
  d: commentary on anything that might be of particular interest to a learner. Be judicious on whether any is necessary for a given line.
```

- Remember to add comments if there are any interesting observations to be made about the words / expressions / forms being introduced

- Make each dialogue at least 4 and up to 9 lines long, 

We are going to start with a small set of words from the list below and start gradually adding more words as we make more dialogues. The goal for this is to create reading material for beginning chinese learners.

List of words:
-----
的,我,你,是,了,不,在,他,我们,好,有,这,就,会,吗,要,什么,说,她,想,一,很,知道,人,吧,那,来,都,个,能,去,没,和,他们,到,对,也,啊,还,把,让,做,给,一个,上,你们,过,没有,得,看,真,着,事,这个,怎么,现在,可以,点,呢,如果,只,别,哦,但,被,走,太,这样,里,跟,告诉,因为,自己,再,听,这里,快,谁,但是,多,用,时候,下,已经,谢谢,为什么,觉得,天,像,这么,它,从,先生,找,最,喜欢,可,为,大,可能,需要,是的,死,次,出,那么,干,那个,嘿,们,话,而,么,东西,应该,孩子,起来,所以,这些,才,两,错,还有,又,小,中,叫,嗯,该,等,问题,一起,拿,更,开始,帮,打,爱,带,时间,年,请,回,工作,然后,当,见,钱,噢,一样,事情,就是,吃,所有,开,一下,家,非常,看到,希望,那些,哪,当然,也许,行,朋友,妈妈,相信,前,嗨,认为,将,这儿,今天,明白,一直,看看,车,时,杀,地方,不过,呃,发生,几,回来,准备,找到,后,爸爸,一切,抱歉,比,感觉,些,只是,怎么样,出来,不要,对不起,问,离开,一点,一定,起,还是,发现,所,住,件,正,而且,并,必须,意思,放,不错,肯定,电话,为了,搞,棒,第一,妈,地,进,那样,大家,新,您,向,一些,三,那里,以为,高兴,嘛,老,位,过来,掉,先,等等,生活,之,买,种,医生,最后,之前,伙计,手,任何,很多,哪儿,这种,上帝,女人,名字,认识,坐,今晚,其他,喝,记得,家伙,与,或者,写,穿,弄,过去,哪里,啦,却,算,担心,继续,送,女孩,以,玩,亲爱,下来,成,条,够,父亲,以前,跑,月,早,美国,长,完全,宝贝,号,枪,狗,可是,世界,小时,重要,谈,别人,男人,头,机会,岁,出去,活,看见,者,打电话,喂,好像,得到,警察,完,张,儿子,之后,漂亮,分钟,接,场,再见,求,刚,如何,比赛,呀,情况,变,关系,真是,女士,本,马上,决定,见到,根本,关于,那儿,难,只要,里面,每,份,到底,了解,明天,站,结束,公司,成为,永远,帮助,来说,多少,哇,名,它们,总,确定,有人,清楚,晚上,安全,怎样,没什么,块,回家,留,周,愿意,计划,爸,俩,停,不能,他妈的,说话,另,心,花,她们,有些,门,感谢,谈谈,定,于,以后,管,照片,每个,欢迎,敢,兄弟,从来,总是,嘴,跳,拜托,女儿,抓,小姐,动,赢,消息,女,忙,或许,如此,队,无法,房子,拉,衣服,听说,救,参加,办法,睡,唯一,回去,人们,晚,该死,闭,选择,坏,原因,下去,受,连,好好,全,确实,挺,此,水,混蛋,杯,保证,学校,卖,信,接受,改变,舞,看来,高,麻烦,出现,打算,电影,试,身上,房间,美,不管,书,特别,注意,球,查,忘,甚至,保护,真正,结果,表现,拍,其实,小心,进来,路,呆,四,久,当时,或,懂,只有,怎么办,第,马,讲,绝对,长官,员,进去,至少,律师,喔,整个,听到,表演,
