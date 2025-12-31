// Lyrics Synchronization System
// Синхронизация текста песен с YouTube видео

class LyricsSync {
    constructor(videoId, lyricsData, containerId = 'song-lyrics') {
        this.videoId = videoId;
        this.lyricsData = lyricsData;
        this.containerId = containerId;
        this.player = null;
        this.currentWordIndex = -1;
        this.words = [];
        this.isPlaying = false;
        this.updateInterval = null;
        this.currentDataIndex = 0; // Индекс для последовательного поиска в данных
        
        this.init();
    }

    init() {
        // Подготавливаем текст сразу
        this.prepareLyrics();
        
        // Загружаем YouTube IFrame API
        if (!window.YT) {
            console.log('Loading YouTube IFrame API...');
            // Сохраняем существующий обработчик, если есть
            const existingHandler = window.onYouTubeIframeAPIReady;
            
            window.onYouTubeIframeAPIReady = () => {
                console.log('YouTube IFrame API ready');
                if (existingHandler) existingHandler();
                this.createPlayer();
            };
            
            const tag = document.createElement('script');
            tag.src = 'https://www.youtube.com/iframe_api';
            const firstScriptTag = document.getElementsByTagName('script')[0];
            firstScriptTag.parentNode.insertBefore(tag, firstScriptTag);
        } else {
            // API уже загружен
            console.log('YouTube IFrame API already loaded');
            this.createPlayer();
        }
    }

    createPlayer() {
        try {
            const playerElement = document.getElementById('youtube-player');
            if (!playerElement) {
                console.error('YouTube player container not found');
                return;
            }

            this.player = new YT.Player('youtube-player', {
                videoId: this.videoId,
                width: '100%',
                height: '100%',
                playerVars: {
                    'rel': 0,
                    'modestbranding': 1,
                    'playsinline': 1,
                    'enablejsapi': 1
                },
                events: {
                    'onReady': () => this.onPlayerReady(),
                    'onStateChange': (event) => this.onPlayerStateChange(event),
                    'onError': (event) => {
                        console.error('YouTube player error:', event.data);
                    }
                }
            });
        } catch (error) {
            console.error('Error creating YouTube player:', error);
        }
    }

    onPlayerReady() {
        console.log('YouTube player ready');
        console.log('Player object:', this.player);
        // Можно добавить автозапуск или другие действия
    }

    onPlayerStateChange(event) {
        if (event.data === YT.PlayerState.PLAYING) {
            this.isPlaying = true;
            this.startSync();
        } else if (event.data === YT.PlayerState.PAUSED) {
            this.isPlaying = false;
            this.stopSync();
        } else if (event.data === YT.PlayerState.ENDED) {
            this.isPlaying = false;
            this.stopSync();
            this.resetHighlight();
        }
    }

    prepareLyrics() {
        const container = document.getElementById(this.containerId);
        if (!container) return;

        // Создаем индекс слов из данных таймингов для быстрого поиска
        this.wordIndex = 0;
        
        // Разбиваем текст на слова с data-атрибутами
        const verses = container.querySelectorAll('.verse, .chorus');
        
        verses.forEach((verse, verseIndex) => {
            const lines = verse.querySelectorAll('p');
            lines.forEach((line, lineIndex) => {
                const text = line.textContent.trim();
                const words = text.split(/\s+/);
                
                line.innerHTML = words.map((word, wordIndex) => {
                    const wordData = this.findWordTiming(word);
                    const wordId = `word-${this.wordIndex++}`;
                    
                    const start = wordData ? wordData.start : 0;
                    const end = wordData ? wordData.end : 0;
                    
                    // Сохраняем в массив для синхронизации
                    this.words.push({
                        id: wordId,
                        start: start,
                        end: end,
                        element: null
                    });
                    
                    return `<span class="word" data-word-id="${wordId}" data-start="${start}" data-end="${end}">${word}</span>`;
                }).join(' ');
            });
        });

        // Сохраняем ссылки на элементы после рендеринга
        setTimeout(() => {
            this.words.forEach(wordData => {
                const element = document.querySelector(`[data-word-id="${wordData.id}"]`);
                if (element) {
                    wordData.element = element;
                }
            });
            console.log(`Prepared ${this.words.length} words for synchronization`);
            console.log('Words with timings:', this.words.slice(0, 5).map(w => ({
                text: w.element?.textContent,
                start: w.start,
                end: w.end
            })));
        }, 100);
    }

    findWordTiming(word) {
        if (!this.lyricsData || !this.lyricsData.words || this.lyricsData.words.length === 0) {
            return null;
        }

        // Нормализуем слово (убираем пунктуацию, приводим к нижнему регистру)
        const wordNormalized = word.toLowerCase().replace(/[.,!?;:'"]/g, '').trim();
        
        // Ищем совпадение в данных таймингов
        // Используем индекс для последовательного поиска
        for (let i = this.currentDataIndex || 0; i < this.lyricsData.words.length; i++) {
            const dataWord = this.lyricsData.words[i];
            const dataWordNormalized = dataWord.text.toLowerCase().replace(/[.,!?;:'"]/g, '').trim();
            
            if (dataWordNormalized === wordNormalized) {
                this.currentDataIndex = i + 1; // Следующий поиск начнется отсюда
                return {
                    start: dataWord.start,
                    end: dataWord.end
                };
            }
        }

        // Если не нашли точное совпадение, возвращаем null
        // Система будет использовать приблизительные значения из data-атрибутов
        return null;
    }

    startSync() {
        if (this.updateInterval) return;
        
        console.log('Starting lyrics sync...');
        this.updateInterval = setInterval(() => {
            if (this.player && this.isPlaying) {
                try {
                    const currentTime = this.player.getCurrentTime();
                    if (currentTime && currentTime > 0) {
                        this.updateHighlight(currentTime);
                    }
                } catch (error) {
                    console.error('Error getting current time:', error);
                }
            }
        }, 100); // Обновляем каждые 100мс
    }

    stopSync() {
        if (this.updateInterval) {
            clearInterval(this.updateInterval);
            this.updateInterval = null;
        }
    }

    updateHighlight(currentTime) {
        // Находим текущее слово
        let newWordIndex = -1;
        
        // Ищем слово, которое должно быть активным в данный момент
        for (let i = 0; i < this.words.length; i++) {
            const word = this.words[i];
            // Если время попадает в диапазон слова
            if (currentTime >= word.start && currentTime < word.end) {
                newWordIndex = i;
                break;
            }
        }

        // Если не нашли точное совпадение, ищем последнее слово, которое уже началось
        if (newWordIndex === -1) {
            for (let i = this.words.length - 1; i >= 0; i--) {
                if (currentTime >= this.words[i].start) {
                    newWordIndex = i;
                    break;
                }
            }
        }

        // Обновляем подсветку только если изменилось слово
        if (newWordIndex !== this.currentWordIndex) {
            if (newWordIndex >= 0) {
                console.log(`Highlighting word ${newWordIndex}: "${this.words[newWordIndex].element?.textContent}" at time ${currentTime.toFixed(2)}s`);
            }
            this.highlightWord(newWordIndex);
            this.currentWordIndex = newWordIndex;
        }
    }

    highlightWord(wordIndex) {
        // Убираем подсветку со всех слов
        document.querySelectorAll('.word').forEach(word => {
            word.classList.remove('word-active', 'word-past');
        });

        // Подсвечиваем текущее слово
        if (wordIndex >= 0 && wordIndex < this.words.length) {
            const currentWord = this.words[wordIndex];
            if (currentWord.element) {
                currentWord.element.classList.add('word-active');
                
                // Прокручиваем к активному слову
                this.scrollToWord(currentWord.element);
                
                // Помечаем предыдущие слова
                for (let i = 0; i < wordIndex; i++) {
                    if (this.words[i].element) {
                        this.words[i].element.classList.add('word-past');
                    }
                }
            }
        }
    }

    scrollToWord(element) {
        if (!element) return;
        
        const container = document.getElementById(this.containerId);
        if (!container) return;

        const containerRect = container.getBoundingClientRect();
        const elementRect = element.getBoundingClientRect();
        
        // Если слово вне видимой области, прокручиваем
        if (elementRect.top < containerRect.top || elementRect.bottom > containerRect.bottom) {
            element.scrollIntoView({
                behavior: 'smooth',
                block: 'center'
            });
        }
    }

    resetHighlight() {
        document.querySelectorAll('.word').forEach(word => {
            word.classList.remove('word-active', 'word-past');
        });
        this.currentWordIndex = -1;
    }

    // Публичные методы для управления
    play() {
        if (this.player) {
            this.player.playVideo();
        }
    }

    pause() {
        if (this.player) {
            this.player.pauseVideo();
        }
    }

    seekTo(time) {
        if (this.player) {
            this.player.seekTo(time, true);
        }
    }
}

// Экспорт для использования в других скриптах
window.LyricsSync = LyricsSync;

