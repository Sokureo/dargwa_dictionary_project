class VirtualKeyboard {
    constructor(inputElement, configUrl = '/static/js/keyboard_config.json') {
        this.input = inputElement;
        this.config = null;
        this.currentLayout = 'cyrillic';
        this.shiftActive = false;
        this.keyboardContainer = null;
        this.lastCursorPosition = 0;
        this.configUrl = configUrl;
        this.isVisible = false;

        this.init();
    }

    async init() {
        await this.loadConfig();
        if (this.config) {
            this.createKeyboard();
            this.attachEvents();
        } else {
            console.error('Keyboard config not loaded');
        }
    }

    async loadConfig() {
        try {
            const response = await fetch(this.configUrl);
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }
            this.config = await response.json();
        } catch (error) {
            console.error('Failed to load keyboard config:', error);
        }
    }

    saveCursorPosition() {
        this.lastCursorPosition = this.input.selectionStart;
    }

    createKeyboard() {
        this.keyboardContainer = document.createElement('div');
        this.keyboardContainer.className = 'virtual-keyboard';
        this.keyboardContainer.style.cssText = `
            display: none;
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            background: #f0f0f0;
            border-top: 1px solid #ccc;
            padding: 10px;
            z-index: 10000;
            transform: translateY(100%);
            transition: transform 0.3s ease-in-out;
            box-shadow: 0 -2px 10px rgba(0,0,0,0.1);
        `;

        this.keyboardContainer.addEventListener('mousedown', (e) => {
            e.preventDefault();
        });

        const closeBtn = document.createElement('button');
        closeBtn.textContent = '✕';
        closeBtn.style.cssText = `
            position: absolute;
            right: 10px;
            top: 5px;
            background: none;
            border: none;
            font-size: 20px;
            cursor: pointer;
            z-index: 10001;
        `;
        closeBtn.onclick = () => this.hide();
        this.keyboardContainer.appendChild(closeBtn);

        const layoutSwitcher = document.createElement('div');
        layoutSwitcher.style.cssText = `
            text-align: center;
            margin-bottom: 10px;
        `;

        const cyrillicBtn = document.createElement('button');
        cyrillicBtn.textContent = 'Рус';
        cyrillicBtn.style.cssText = `
            padding: 5px 15px;
            margin: 0 5px;
            border: 1px solid #ccc;
            background: ${this.currentLayout === 'cyrillic' ? '#4dadb0' : 'white'};
            color: ${this.currentLayout === 'cyrillic' ? 'white' : '#333'};
            cursor: pointer;
            border-radius: 4px;
        `;
        cyrillicBtn.onclick = () => this.switchLayout('cyrillic');

        const latinBtn = document.createElement('button');
        latinBtn.textContent = 'En';
        latinBtn.style.cssText = `
            padding: 5px 15px;
            margin: 0 5px;
            border: 1px solid #ccc;
            background: ${this.currentLayout === 'latin' ? '#4dadb0' : 'white'};
            color: ${this.currentLayout === 'latin' ? 'white' : '#333'};
            cursor: pointer;
            border-radius: 4px;
        `;
        latinBtn.onclick = () => this.switchLayout('latin');

        layoutSwitcher.appendChild(cyrillicBtn);
        layoutSwitcher.appendChild(latinBtn);
        this.keyboardContainer.appendChild(layoutSwitcher);

        this.keysContainer = document.createElement('div');
        this.keysContainer.style.cssText = `
            display: flex;
            flex-direction: column;
            gap: 8px;
        `;
        this.keyboardContainer.appendChild(this.keysContainer);

        document.body.appendChild(this.keyboardContainer);

        this.layoutSwitcherBtns = { cyrillic: cyrillicBtn, latin: latinBtn };

        this.renderKeys();
    }

    switchLayout(layout) {
        this.currentLayout = layout;
        this.shiftActive = false;
        this.renderKeys();

        for (const [key, btn] of Object.entries(this.layoutSwitcherBtns)) {
            if (key === layout) {
                btn.style.background = '#4dadb0';
                btn.style.color = 'white';
            } else {
                btn.style.background = 'white';
                btn.style.color = '#333';
            }
        }
        this.input.focus();
        this.saveCursorPosition();
    }

    renderKeys() {
        if (!this.config || !this.keysContainer) return;

        this.keysContainer.innerHTML = '';
        const layout = this.config[this.currentLayout];
        if (!layout) return;

        const rows = this.shiftActive ? layout.shift : layout.rows;

        rows.forEach(row => {
            const rowDiv = document.createElement('div');
            rowDiv.style.cssText = `
                display: flex;
                justify-content: center;
                gap: 6px;
                flex-wrap: wrap;
            `;

            row.forEach(key => {
                const keyBtn = document.createElement('button');
                keyBtn.textContent = key;
                keyBtn.style.cssText = `
                    min-width: 40px;
                    height: 45px;
                    padding: 0 8px;
                    font-size: 16px;
                    border: 1px solid #ccc;
                    background: white;
                    border-radius: 6px;
                    cursor: pointer;
                    transition: all 0.2s;
                    font-family: 'Montserrat', sans-serif;
                `;

                keyBtn.onclick = () => {
                    this.insertChar(key);
                };

                rowDiv.appendChild(keyBtn);
            });

            this.keysContainer.appendChild(rowDiv);
        });

        const controlRow = document.createElement('div');
        controlRow.style.cssText = `
            display: flex;
            justify-content: center;
            gap: 6px;
            margin-top: 5px;
        `;

        const shiftBtn = document.createElement('button');
        shiftBtn.textContent = this.shiftActive ? '⇧' : 'Shift';
        shiftBtn.style.cssText = `
            min-width: 70px;
            height: 45px;
            padding: 0 12px;
            font-size: 14px;
            border: 1px solid #ccc;
            background: ${this.shiftActive ? '#4dadb0' : 'white'};
            color: ${this.shiftActive ? 'white' : '#333'};
            border-radius: 6px;
            cursor: pointer;
        `;
        shiftBtn.onclick = () => {
            this.shiftActive = !this.shiftActive;
            this.renderKeys();
            this.input.focus();
            this.saveCursorPosition();
        };
        controlRow.appendChild(shiftBtn);

        const spaceBtn = document.createElement('button');
        spaceBtn.textContent = 'Пробел';
        spaceBtn.style.cssText = `
            min-width: 150px;
            height: 45px;
            font-size: 14px;
            border: 1px solid #ccc;
            background: white;
            border-radius: 6px;
            cursor: pointer;
        `;
        spaceBtn.onclick = () => {
            this.insertChar(' ');
        };
        controlRow.appendChild(spaceBtn);

        const backspaceBtn = document.createElement('button');
        backspaceBtn.textContent = '⌫';
        backspaceBtn.style.cssText = `
            min-width: 70px;
            height: 45px;
            font-size: 18px;
            border: 1px solid #ccc;
            background: #ff6b6b;
            color: white;
            border-radius: 6px;
            cursor: pointer;
        `;
        backspaceBtn.onclick = () => {
            this.backspace();
        };
        controlRow.appendChild(backspaceBtn);

        this.keysContainer.appendChild(controlRow);
    }

    insertChar(char) {
        const cursorPos = this.lastCursorPosition;
        const value = this.input.value;

        this.input.value = value.substring(0, cursorPos) + char + value.substring(cursorPos);

        const newCursorPos = cursorPos + char.length;
        this.input.selectionStart = newCursorPos;
        this.input.selectionEnd = newCursorPos;
        this.lastCursorPosition = newCursorPos;

        this.input.dispatchEvent(new Event('input', { bubbles: true }));

        if (this.shiftActive && char !== ' ') {
            this.shiftActive = false;
            this.renderKeys();
        }

        this.input.focus();
    }

    backspace() {
        const cursorPos = this.lastCursorPosition;
        const value = this.input.value;

        if (cursorPos > 0) {
            this.input.value = value.substring(0, cursorPos - 1) + value.substring(cursorPos);
            const newCursorPos = cursorPos - 1;
            this.input.selectionStart = newCursorPos;
            this.input.selectionEnd = newCursorPos;
            this.lastCursorPosition = newCursorPos;
        }

        this.input.dispatchEvent(new Event('input', { bubbles: true }));
        this.input.focus();
    }

    show() {
        if (this.keyboardContainer && !this.isVisible) {
            this.saveCursorPosition();
            this.keyboardContainer.style.display = 'block';
            setTimeout(() => {
                this.keyboardContainer.style.transform = 'translateY(0)';
            }, 10);
            this.isVisible = true;
        }
    }

    hide() {
        if (this.keyboardContainer && this.isVisible) {
            this.keyboardContainer.style.transform = 'translateY(100%)';
            setTimeout(() => {
                if (!this.isVisible) return;
                this.keyboardContainer.style.display = 'none';
            }, 300);
            this.isVisible = false;
        }
    }

    attachEvents() {
        this.input.addEventListener('focus', () => {
            this.saveCursorPosition();
            this.show();
        });

        this.input.addEventListener('click', () => {
            this.saveCursorPosition();
        });

        this.input.addEventListener('keyup', () => {
            this.saveCursorPosition();
        });

        this.input.addEventListener('blur', () => {
            setTimeout(() => {
                const activeElement = document.activeElement;
                const isKeyboardButton = this.keyboardContainer && this.keyboardContainer.contains(activeElement);

                if (!isKeyboardButton) {
                    this.hide();
                }
            }, 150);
        });
    }
}

document.addEventListener('DOMContentLoaded', () => {
    const searchInput = document.querySelector('#id_search_word');
    if (searchInput) {
        window.virtualKeyboard = new VirtualKeyboard(searchInput);
    }
});
