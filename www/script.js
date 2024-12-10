let dialogues = [];
let displayState = {
    characters: true,
    pinyin: false,
    translation: false,
    commentary: false
};
let currentDialogue = null;
let currentDialogueFile = null;
let currentAudio = null;
let isPlaying = false;
let isPlayingSlow = false;
let lineStates = new Map();

const LINE_STATES = [
    ['chinese'],
    ['chinese', 'pinyin'],
    ['chinese', 'pinyin', 'translation'],
    ['chinese', 'pinyin', 'translation', 'commentary']
];

function toggleMobilePanel() {
    const panel = document.getElementById('sidePanel');
    panel.classList.toggle('open');
}

function toggleElement(elementClass) {
    lineStates.clear();  // Clear individual line states when using global controls

    if (elementClass === 'characters') {
        displayState = {
            characters: true,
            pinyin: false,
            translation: false,
            commentary: false
        };
    } else if (elementClass === 'pinyin') {
        displayState = {
            characters: true,
            pinyin: true,
            translation: false,
            commentary: false
        };
    } else if (elementClass === 'translation') {
        displayState = {
            characters: true,
            pinyin: true,
            translation: true,
            commentary: false
        };
    } else if (elementClass === 'commentary') {
        displayState = {
            characters: true,
            pinyin: true,
            translation: true,
            commentary: true
        };
    }

    updateVisibility();
    updateButtonStates();
}

function updateVisibility() {
    document.querySelectorAll('.dialogue-line').forEach(line => {
        const lineIndex = Array.from(line.parentElement.children).indexOf(line);

        if (lineStates.has(lineIndex)) {
            return;
        }

        line.querySelector('.chinese').classList.remove('hidden');
        const pinyin = line.querySelector('.pinyin');
        const translation = line.querySelector('.translation');
        const commentary = line.querySelector('.commentary');

        pinyin?.classList.toggle('hidden', !displayState.pinyin);
        translation?.classList.toggle('hidden', !displayState.translation);
        commentary?.classList?.toggle('hidden', !displayState.commentary);
    });
}

function updateButtonStates() {
    Object.keys(displayState).forEach(key => {
        const btn = document.getElementById(`${key}Btn`);
        const btn2 = document.getElementById(`${key}Btn2`);

        if (btn) btn.classList.toggle('active', displayState[key]);
        if (btn2) btn2.classList.toggle('active', displayState[key]);
    });
}

async function loadIndex() {
    try {
        const response = await fetch('index.yaml');
        const text = await response.text();
        const indexData = jsyaml.load(text);

        const select = document.getElementById('dialogueSelect');
        select.innerHTML = indexData.map(item =>
            `<option value="${item.path}">${item.title}</option>`
        ).join('');

        if (indexData.length > 0) {
            await loadDialogueFile(indexData[0].path);
        }
    } catch (error) {
        console.error('Error loading index:', error);
        document.getElementById('dialogueSelect').innerHTML =
            '<option value="">Error loading dialogue files</option>';
    }
}

async function loadDialogueFile(path) {
    try {
        currentDialogueFile = path;
        const response = await fetch(path);
        const text = await response.text();
        processYamlContent(text);
    } catch (error) {
        console.error('Error loading dialogue file:', error);
        alert(`Error loading dialogue file: ${path}`);
    }
}

function processYamlContent(content) {
    stopAudio(); // Stop any playing audio when loading new content
    try {
        const parsed = jsyaml.load(content);
        if (!parsed || !Array.isArray(parsed)) {
            throw new Error('Invalid dialogue format: expected array of dialogues');
        }
        dialogues = parsed;
        updateDialogueList();
    } catch (error) {
        console.error('Error parsing YAML:', error);
        alert('Error parsing YAML file');
    }
}

function updateDialogueList() {
    const list = document.getElementById('dialogueList');
    list.innerHTML = '';

    dialogues.forEach((dialogue, index) => {
        const item = document.createElement('li');
        item.className = 'dialogue-item';
        item.textContent = dialogue.title || `Dialogue ${index + 1}`;
        item.onclick = () => {
            document.querySelectorAll('.dialogue-item').forEach(i => i.classList.remove('active'));
            item.classList.add('active');
            displayDialogue(index);
            if (window.innerWidth <= 768) {
                toggleMobilePanel();
            }
        };
        list.appendChild(item);
    });

    if (dialogues.length > 0) {
        const firstItem = list.firstElementChild;
        firstItem.classList.add('active');
        displayDialogue(0);
    }
}

async function playAudio(audioFile, lineElement = null, isPartOfSequence = false) {
    if (isPlaying && !isPartOfSequence) {
        stopAudio();
        return;
    }

    if (lineElement) {
        lineElement.classList.add('playing');
    }

    if (!isPartOfSequence) {
        isPlaying = true;
    }

    currentAudio = new Audio(`audio/${audioFile}`);

    try {
        await currentAudio.play();
        await new Promise((resolve) => {
            currentAudio.onended = resolve;
        });
    } finally {
        if (lineElement) {
            lineElement.classList.remove('playing');
        }
        if (!isPartOfSequence) {
            isPlaying = false;
            currentAudio = null;
        }
    }
}

function updatePlayButtons(playing = false, slow = false) {
    const playAllBtns = document.querySelectorAll('.play-all-btn');
    playAllBtns.forEach((btn, index) => {
        const img = btn.querySelector('img');
        if (playing && ((slow && index === 1) || (!slow && index === 0))) {
            img.src = 'assets/stop32.png';
            btn.title = 'Stop';
        } else {
            if (index === 0) {
                img.src = 'assets/play32.png';
                btn.title = 'Play dialogue';
            } else {
                img.src = 'assets/play-slow32.png';
                btn.title = 'Play dialogue slowly';
            }
        }
    });
}

async function playAllAudio(dialogueIndex, slow = false) {
    if (isPlaying) {
        stopAudio();
        return;
    }

    isPlaying = true;
    isPlayingSlow = slow;
    updatePlayButtons(true, slow);

    const dialogue = dialogues[dialogueIndex];
    const lines = document.querySelectorAll('.dialogue-line');

    try {
        for (let i = 0; i < dialogue.lines.length; i++) {
            if (!isPlaying) break;

            const line = dialogue.lines[i];
            if (line.a) {
                const audioFile = (slow && line.as) ? line.as : line.a;
                await playAudio(audioFile, lines[i], true);
                if (isPlaying) {
                    await new Promise(resolve => setTimeout(resolve, 300));
                }
            }
        }
    } finally {
        isPlaying = false;
        isPlayingSlow = false;
        currentAudio = null;
        updatePlayButtons();
    }
}

function stopAudio() {
    if (currentAudio) {
        currentAudio.pause();
        currentAudio.currentTime = 0;
    }

    document.querySelectorAll('.dialogue-line.playing').forEach(line => {
        line.classList.remove('playing');
    });

    isPlaying = false;
    isPlayingSlow = false;
    currentAudio = null;
    updatePlayButtons();
}

function createAudioButton(audioFile, lineDiv, isSlow = false) {
    const audioBtn = document.createElement('button');
    audioBtn.className = 'audio-btn';
    audioBtn.onclick = () => playAudio(audioFile, lineDiv, false);
    audioBtn.title = isSlow ? 'Play pronunciation slowly' : 'Play pronunciation';

    const audioImg = document.createElement('img');
    audioImg.src = isSlow ? 'assets/speaker-slow32.png' : 'assets/speaker32.png';
    audioImg.alt = isSlow ? 'Play audio slow' : 'Play audio';

    audioBtn.appendChild(audioImg);
    return audioBtn;
}

function createPlayAllButtons(dialogueIndex, hasSlowVersion) {
    const buttonsContainer = document.createElement('div');
    buttonsContainer.className = 'dialogue-buttons';

    const playAllBtn = document.createElement('button');
    playAllBtn.className = 'play-all-btn';
    playAllBtn.onclick = () => playAllAudio(dialogueIndex, false);
    playAllBtn.title = 'Play dialogue';

    const playAllImg = document.createElement('img');
    playAllImg.src = 'assets/play32.png';
    playAllImg.alt = 'Play all';

    playAllBtn.appendChild(playAllImg);
    buttonsContainer.appendChild(playAllBtn);

    if (hasSlowVersion) {
        const playAllSlowBtn = document.createElement('button');
        playAllSlowBtn.className = 'play-all-btn';
        playAllSlowBtn.onclick = () => playAllAudio(dialogueIndex, true);
        playAllSlowBtn.title = 'Play dialogue slowly';

        const playAllSlowImg = document.createElement('img');
        playAllSlowImg.src = 'assets/play-slow32.png';
        playAllSlowImg.alt = 'Play all slow';

        playAllSlowBtn.appendChild(playAllSlowImg);
        buttonsContainer.appendChild(playAllSlowBtn);
    }

    return buttonsContainer;
}

function cycleLine(lineDiv) {
    const lineIndex = Array.from(lineDiv.parentElement.children).indexOf(lineDiv);
    const currentState = lineStates.get(lineIndex) || 0;
    const nextState = (currentState + 1) % LINE_STATES.length;
    lineStates.set(lineIndex, nextState);

    const pinyin = lineDiv.querySelector('.pinyin');
    const translation = lineDiv.querySelector('.translation');
    const commentary = lineDiv.querySelector('.commentary');

    pinyin?.classList.toggle('hidden', !LINE_STATES[nextState].includes('pinyin'));
    translation?.classList.toggle('hidden', !LINE_STATES[nextState].includes('translation'));
    commentary?.classList?.toggle('hidden', !LINE_STATES[nextState].includes('commentary'));
}

function createDialogueLine(line, index) {
    const lineDiv = document.createElement('div');
    lineDiv.className = 'dialogue-line';
    lineDiv.setAttribute('data-speaker', line.s);

    lineDiv.addEventListener('click', (e) => {
        if (e.target.closest('.audio-btn') || e.target.closest('.audio-buttons')) {
            return;
        }
        cycleLine(lineDiv);
    });

    lineDiv.style.cursor = 'pointer';

    const speaker = document.createElement('div');
    speaker.className = 'speaker';
    speaker.textContent = line.s;
    lineDiv.appendChild(speaker);

    const chinese = document.createElement('div');
    chinese.className = 'chinese';
    const chineseText = document.createElement('span');
    chineseText.textContent = line.c;
    chinese.appendChild(chineseText);

    if (line.a) {
        const audioButtonsContainer = document.createElement('div');
        audioButtonsContainer.className = 'audio-buttons';
        audioButtonsContainer.appendChild(createAudioButton(line.a, lineDiv));

        if (line.as) {
            audioButtonsContainer.appendChild(createAudioButton(line.as, lineDiv, true));
        }

        chinese.appendChild(audioButtonsContainer);
    }

    lineDiv.appendChild(chinese);

    if (line.p) {
        const pinyin = document.createElement('div');
        pinyin.className = 'pinyin hidden';
        pinyin.textContent = line.p;
        lineDiv.appendChild(pinyin);
    }

    if (line.t) {
        const translation = document.createElement('div');
        translation.className = 'translation hidden';
        translation.textContent = line.t;
        lineDiv.appendChild(translation);
    }

    if (line.d) {
        const commentary = document.createElement('div');
        commentary.className = 'commentary hidden';
        commentary.textContent = line.d;
        lineDiv.appendChild(commentary);
    }

    return lineDiv;
}

function displayDialogue(index) {
    currentDialogue = index;
    const dialogue = dialogues[index];
    if (!dialogue) return;

    lineStates.clear();

    const content = document.getElementById('dialogueContent');
    content.innerHTML = '';

    const titleContainer = document.createElement('div');
    titleContainer.className = 'dialogue-title-container';

    const titleDiv = document.createElement('div');
    titleDiv.className = 'dialogue-title';
    titleDiv.textContent = dialogue.title || `Dialogue ${index + 1}`;

    const hasSlowVersion = dialogue.lines.some(line => line.as);
    const buttonsContainer = createPlayAllButtons(index, hasSlowVersion);

    titleContainer.appendChild(titleDiv);
    titleContainer.appendChild(buttonsContainer);
    content.appendChild(titleContainer);

    dialogue.lines.forEach((line, i) => {
        content.appendChild(createDialogueLine(line, i));
    });

    updateVisibility();
    updateButtonStates();
}

document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('dialogueSelect').addEventListener('change', (event) => {
        if (event.target.value) {
            loadDialogueFile(event.target.value);
        }
    });

    document.getElementById('fileInput').addEventListener('change', (event) => {
        const file = event.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = (e) => processYamlContent(e.target.result);
            reader.readAsText(file);
        }
    });

    loadIndex();
});