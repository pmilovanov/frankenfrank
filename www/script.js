let dialogues = {};
let dialogueIndex = [];
let displayState = {
    pinyin: false,
    translation: false,
    commentary: false
};
let currentDialogue = null;
let currentDialogueFile = null;
let currentAudio = null;
let isPlaying = false;

function toggleMobilePanel() {
    const panel = document.getElementById('sidePanel');
    panel.classList.toggle('open');
}

function toggleElement(elementClass) {
    displayState[elementClass] = !displayState[elementClass];

    document.querySelectorAll(`.${elementClass}`).forEach(el =>
        el.classList.toggle('hidden', !displayState[elementClass]));

    document.getElementById(`${elementClass}Btn`).classList.toggle('active', displayState[elementClass]);
    document.getElementById(`${elementClass}Btn2`).classList.toggle('active', displayState[elementClass]);
}

async function loadIndex() {
    try {
        const response = await fetch('index.yaml');
        const text = await response.text();
        dialogueIndex = jsyaml.load(text);

        const select = document.getElementById('dialogueSelect');
        select.innerHTML = dialogueIndex.map(item =>
            `<option value="${item.path}">${item.title}</option>`
        ).join('');

        if (dialogueIndex.length > 0) {
            await loadDialogueFile(dialogueIndex[0].path);
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

// Add cleanup when changing dialogues
function processYamlContent(content) {
    stopAudio(); // Stop any playing audio when loading new content
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

    if (firstDialogueId) {
        const firstItem = list.firstElementChild;
        firstItem.classList.add('active');
        displayDialogue(firstDialogueId);
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
        await new Promise((resolve, reject) => {
            currentAudio.onended = resolve;
            currentAudio.onerror = reject;
        });
    } catch (error) {
        console.error('Error playing audio:', error);
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

async function playAllAudio(dialogueId) {
    if (isPlaying) {
        stopAudio();
        return;
    }

    isPlaying = true;
    const playAllBtn = document.querySelector('.play-all-btn img');
    playAllBtn.src = 'assets/stop32.png';

    const dialogue = dialogues[dialogueId];
    const lines = document.querySelectorAll('.dialogue-line');

    try {
        for (let i = 0; i < dialogue.length; i++) {
            const line = dialogue[i];
            if (!isPlaying) break;  // Check if we should stop

            if (line.a) {
                await playAudio(line.a, lines[i], true);
                if (isPlaying) {  // Only wait if we haven't stopped
                    await new Promise(resolve => setTimeout(resolve, 300));
                }
            }
        }
    } finally {
        // Reset play button icon
        const playAllBtn = document.querySelector('.play-all-btn img');
        if (playAllBtn) {
            playAllBtn.src = 'assets/play32.png';
        }
        isPlaying = false;
        currentAudio = null;
    }
}

function stopAudio() {
    if (currentAudio) {
        currentAudio.pause();
        currentAudio.currentTime = 0;
    }

    // Reset all playing states and icons
    document.querySelectorAll('.dialogue-line.playing').forEach(line => {
        line.classList.remove('playing');
        const btn = line.querySelector('.audio-btn');
        if (btn) {
            const img = btn.querySelector('img');
            img.src = 'assets/speaker32.png';
        }
    });

    // Reset play all button
    const playAllBtn = document.querySelector('.play-all-btn img');
    if (playAllBtn) {
        playAllBtn.src = 'assets/play32.png';
    }

    isPlaying = false;
    currentAudio = null;
}

function displayDialogue(dialogueId) {
    currentDialogue = dialogueId;
    const dialogue = dialogues[dialogueId];
    if (!dialogue) return;

    const content = document.getElementById('dialogueContent');
    content.innerHTML = '';

    const titleContainer = document.createElement('div');
    titleContainer.className = 'dialogue-title-container';

    const titleDiv = document.createElement('div');
    titleDiv.className = 'dialogue-title';
    titleDiv.textContent = dialogueId;

    const playAllBtn = document.createElement('button');
    playAllBtn.className = 'play-all-btn';
    playAllBtn.onclick = () => playAllAudio(dialogueId);

    const playAllImg = document.createElement('img');
    playAllImg.src = isPlaying ? 'assets/stop32.png' : 'assets/play32.png';
    playAllImg.alt = isPlaying ? 'Stop' : 'Play all';

    playAllBtn.appendChild(playAllImg);
    titleContainer.appendChild(titleDiv);
    titleContainer.appendChild(playAllBtn);
    content.appendChild(titleContainer);

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

        if (line.a) {
            const audioBtn = document.createElement('button');
            audioBtn.className = 'audio-btn';
            audioBtn.onclick = () => playAudio(line.a, lineDiv);

            const audioImg = document.createElement('img');
            audioImg.src = 'assets/speaker32.png';
            audioImg.alt = 'Play audio';

            audioBtn.appendChild(audioImg);
            chinese.appendChild(audioBtn);
        }

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

document.addEventListener('DOMContentLoaded', () => {
    // Add event listener for dropdown
    document.getElementById('dialogueSelect').addEventListener('change', (event) => {
        if (event.target.value) {
            loadDialogueFile(event.target.value);
        }
    });

    // Add event listener for file input
    document.getElementById('fileInput').addEventListener('change', (event) => {
        const file = event.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = (e) => processYamlContent(e.target.result);
            reader.readAsText(file);
        }
    });

    // Load index instead of default dialogues
    loadIndex();
});