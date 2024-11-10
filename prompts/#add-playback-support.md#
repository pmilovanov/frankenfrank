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

I've written the following html/javascript viewer for yaml files like this:

```
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Chinese Dialogue Viewer</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/js-yaml/4.1.0/js-yaml.min.js"></script>
    <style>
        :root {
            --primary-color: #4CAF50;
            --secondary-color: #2196F3;
            --accent-color: #FF9800;  /* New color for Dialogues button */
            --bg-color: #f5f5f5;
            --panel-bg: white;
            --text-color: #333;
            --border-radius: 8px;
            --shadow: 0 2px 4px rgba(0,0,0,0.1);
            --side-panel-width: 300px;
            --panel-padding: 20px;
            --mobile-threshold: 768px;
            --mobile-header-height: 50px;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 0;
            background-color: var(--bg-color);
            color: var(--text-color);
        }

        .app-container {
            display: flex;
            min-height: 100vh;
            position: relative;
        }

        .side-panel {
            background: var(--panel-bg);
            padding: var(--panel-padding);
            width: var(--side-panel-width);
            box-shadow: var(--shadow);
            flex-shrink: 0;
            height: 100vh;
            position: sticky;
            top: 0;
            overflow-y: auto;
            display: flex;
            flex-direction: column;
        }

        .controls-wrapper {
            position: sticky;
            top: 0;
            background: var(--panel-bg);
            padding-bottom: 15px;
            z-index: 1;
        }

        .scrollable-content {
            flex: 1;
            overflow-y: auto;
        }

		.main-panel {
            flex-grow: 1;
            padding: var(--panel-padding);
            max-width: 800px;
            margin: 0 auto;
        }

        .controls {
            display: flex;
            gap: 8px;
            margin-bottom: 0;
        }

        .controls button {
            flex: 1;
            padding: 8px;
            font-size: 0.9em;
            background-color: var(--primary-color);
            color: white;
            border: none;
            border-radius: var(--border-radius);
            cursor: pointer;
            transition: background-color 0.2s ease;
        }

        .controls button:hover {
            background-color: #45a049;
        }

        .file-control {
            margin: 0 0 16px 0;
        }

        .file-control button {
            width: 100%;
            padding: 10px;
            background-color: var(--primary-color);
            color: white;
            border: none;
            border-radius: var(--border-radius);
            cursor: pointer;
        }

        .dialogue-list {
            list-style: none;
            padding: 0;
            margin: 0;
        }

        .dialogue-item {
            padding: 10px;
            margin: 4px 0;
            background: var(--bg-color);
            border-radius: var(--border-radius);
            cursor: pointer;
            transition: all 0.2s ease;
        }

        .dialogue-item:hover {
            background: #e8e8e8;
        }

        .dialogue-item.active {
            background: var(--primary-color);
            color: white;
        }

        .dialogue-line {
            margin-bottom: 20px;
            padding: 15px;
            background-color: white;
            border-left: 4px solid var(--primary-color);
            border-radius: var(--border-radius);
            position: relative;
            box-shadow: var(--shadow);
        }

        .speaker {
            position: absolute;
            top: -10px;
            left: -10px;
            background-color: var(--primary-color);
            color: white;
            padding: 4px 8px;
            border-radius: 12px;
            font-size: 0.9em;
            box-shadow: var(--shadow);
        }

        .chinese {
            font-size: 1.2em;
            margin-bottom: 5px;
            margin-top: 10px;
        }

        .pinyin {
            color: #666;
            margin-bottom: 5px;
        }

        .translation {
            color: #333;
            margin-bottom: 5px;
        }

        .commentary {
            color: #666;
            font-style: italic;
            padding-left: 10px;
            border-left: 2px solid #ddd;
            margin-top: 10px;
        }

        .dialogue-line[data-speaker="B"] {
            border-left-color: var(--secondary-color);
        }

        .dialogue-line[data-speaker="B"] .speaker {
            background-color: var(--secondary-color);
        }

        button.active:before {
            content: "✓";
            margin-right: 5px;
        }

        #fileInput {
            display: none;
        }

        .hidden {
            display: none;
        }

		 .mobile-controls {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            height: var(--mobile-header-height);
            background: var(--panel-bg);
            box-shadow: var(--shadow);
            z-index: 1000;
            padding: 8px;
        }

        .mobile-controls .controls {
            margin: 0;
            height: 100%;
            align-items: center;
        }

        .mobile-controls button {
            height: 34px;
        }

		.dialogues-btn {
            display: none;  /* Hidden by default, shown in mobile */
            background-color: var(--accent-color) !important;
        }

        .dialogues-btn:hover {
            background-color: #fb8c00 !important;
        }

        .dialogues-btn.active {
            background-color: #f57c00 !important;
        }

		.dialogue-title {
            font-size: 1.5em;
            font-weight: 600;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid var(--primary-color);
            color: var(--text-color);
        }

        @media (max-width: 768px) {
            .dialogue-title {
                margin-top: 10px;
            }
		
            .side-panel .controls {
                display: none;
            }

		    .mobile-controls {
                display: block;
                background-color: var(--panel-bg);
            }

            .dialogues-btn {
                display: block;  /* Show in mobile */
            }

            .app-container {
                flex-direction: column;
            }

            .side-panel {
                position: fixed;
                top: var(--mobile-header-height);
                left: 0;
                width: 100%;
                height: auto;
                max-height: calc(100vh - var(--mobile-header-height));
                z-index: 100;
                transform: translateY(-100%);
                transition: transform 0.3s ease;
                padding: 15px;
            }

            .side-panel.open {
                transform: translateY(0);
            }

            .main-panel {
                padding-top: calc(var(--mobile-header-height) + 20px);
                margin-top: 0;
            }

            .main-panel #dialogueContent {
                padding-top: 10px;
            }

            .dialogue-line:first-child {
                margin-top: 10px;
            }
        }
    </style>
</head>
<body>
  <div class="app-container">
        <div class="mobile-controls">
            <div class="controls">
                <button onclick="toggleElement('pinyin')" id="pinyinBtn">Pinyin</button>
                <button onclick="toggleElement('translation')" id="translationBtn">Translation</button>
                <button onclick="toggleElement('commentary')" id="commentaryBtn">Commentary</button>
                <button onclick="toggleMobilePanel()" class="dialogues-btn">Dialogues</button>
            </div>
        </div>

        <aside class="side-panel" id="sidePanel">
            <div class="controls-wrapper">
                <div class="controls">
                    <button onclick="toggleElement('pinyin')" id="pinyinBtn2">Pinyin</button>
                    <button onclick="toggleElement('translation')" id="translationBtn2">Translation</button>
                    <button onclick="toggleElement('commentary')" id="commentaryBtn2">Commentary</button>
                </div>
            </div>

            <div class="scrollable-content">
                <div class="file-control">
                    <input type="file" id="fileInput" accept=".yaml,.yml">
                    <button onclick="document.getElementById('fileInput').click()">Load Dialogues</button>
                </div>

                <ul class="dialogue-list" id="dialogueList">
                    <li class="dialogue-item">Select a dialogue...</li>
                </ul>
            </div>
        </aside>

        <main class="main-panel">
            <div id="dialogueContent"></div>
        </main>
  </div>
  
    <script>
        let dialogues = {};
        let displayState = {
            pinyin: false,
            translation: false,
            commentary: false
        };

        function toggleMobilePanel() {
            const panel = document.getElementById('sidePanel');
            panel.classList.toggle('open');
        }

        function toggleElement(elementClass) {
            displayState[elementClass] = !displayState[elementClass];
            
            // Toggle visibility of elements
            document.querySelectorAll(`.${elementClass}`).forEach(el => 
                el.classList.toggle('hidden', !displayState[elementClass]));
            
            // Toggle button active state for both desktop and mobile buttons
            document.getElementById(`${elementClass}Btn`).classList.toggle('active', displayState[elementClass]);
            document.getElementById(`${elementClass}Btn2`).classList.toggle('active', displayState[elementClass]);
        }

        async function loadDefaultDialogues() {
            try {
                const response = await fetch('dialogues.yaml');
                const text = await response.text();
                processYamlContent(text);
            } catch (error) {
                console.error('Error loading default dialogues:', error);
            }
        }

        function processYamlContent(content) {
            try {
                dialogues = jsyaml.load(content);
                updateDialogueList();
            } catch (error) {
                console.error('Error parsing YAML:', error);
                alert('Error parsing YAML file');
            }
        }

        function updateDialogueList() {
            const list = document.getElementById('dialogueList');
            list.innerHTML = '';
            
            let firstDialogueId = null;
            for (const dialogueId in dialogues) {
                if (!firstDialogueId) firstDialogueId = dialogueId;
                
                const item = document.createElement('li');
                item.className = 'dialogue-item';
                item.textContent = dialogueId;
                item.onclick = () => {
                    document.querySelectorAll('.dialogue-item').forEach(i => i.classList.remove('active'));
                    item.classList.add('active');
                    displayDialogue(dialogueId);
                    if (window.innerWidth <= 768) {
                        toggleMobilePanel();
                    }
                };
                list.appendChild(item);
            }

            // Auto-select first dialogue
            if (firstDialogueId) {
                const firstItem = list.firstElementChild;
                firstItem.classList.add('active');
                displayDialogue(firstDialogueId);
            }
        }

        function displayDialogue(dialogueId) {
            const dialogue = dialogues[dialogueId];
            if (!dialogue) return;

            const content = document.getElementById('dialogueContent');
            content.innerHTML = '';

            // Add title
            const titleDiv = document.createElement('div');
            titleDiv.className = 'dialogue-title';
            titleDiv.textContent = dialogueId;
            content.appendChild(titleDiv);

            dialogue.forEach(line => {
                const lineDiv = document.createElement('div');
                lineDiv.className = 'dialogue-line';
                lineDiv.setAttribute('data-speaker', line.s);

                const speaker = document.createElement('div');
                speaker.className = 'speaker';
                speaker.textContent = line.s;
                lineDiv.appendChild(speaker);

                const chinese = document.createElement('div');
                chinese.className = 'chinese';
                chinese.textContent = line.c;
                lineDiv.appendChild(chinese);

                const pinyin = document.createElement('div');
                pinyin.className = 'pinyin hidden';
                pinyin.textContent = line.p;
                lineDiv.appendChild(pinyin);

                const translation = document.createElement('div');
                translation.className = 'translation hidden';
                translation.textContent = line.t;
                lineDiv.appendChild(translation);

                if (line.d) {
                    const commentary = document.createElement('div');
                    commentary.className = 'commentary hidden';
                    commentary.textContent = line.d;
                    lineDiv.appendChild(commentary);
                }

                content.appendChild(lineDiv);
            });

            Object.entries(displayState).forEach(([key, value]) => {
                document.querySelectorAll(`.${key}`).forEach(el => 
                    el.classList.toggle('hidden', !value));
                document.getElementById(`${key}Btn`).classList.toggle('active', value);
                document.getElementById(`${key}Btn2`).classList.toggle('active', value);
            });
        }
	  
        document.getElementById('fileInput').addEventListener('change', (event) => {
            const file = event.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = (e) => processYamlContent(e.target.result);
                reader.readAsText(file);
            }
        });

        loadDefaultDialogues();
    </script>
</body>
</html>
```

Now I want to add an ability to play mp3 files of pronunciation of individual dialogue lines and the whole dialogue.

For that, in the yaml, I'm adding the attribute `a` for each line that contains the name of the mp3 file of the pronunciation of that line:

```
- s: A
  c: 就是那个很好看的。
  p: Jiù shì nà ge hěn hǎokàn de.
  t: The one that's really good.
  d: 就是 (jiùshì) means "exactly/precisely that one". 的 (de) at the end nominalizes
    the description
  a: 199aee6135081109689847f69eb730a417c226e9724201358d4182a392618b56.mp3
```

Let's add the following functionality:

- If an mp3 file is specified for a dialogue line in the yaml, in the UI, display the icon `assets/speaker32.png` for that line. It can be clicked on to play the pronunciation for that line.

- On top of the dialogue, display the icon `assets/play32.png`. It can be clicked on to play all lines sequentially. There's a 0.3 second pause between the lines.

- All audio files are found at the path `audio` relative to the page.