// Global Variables
let previousResponseId = null;
let isProcessing = false;
let uploadedFiles = []; // 업로드된 파일들을 저장하는 배열
let currentImageHTML = ''; // 현재 생성된 이미지 HTML 저장
let updateTextScheduled = false; // DOM 업데이트 스케줄링 플래그

// 텍스트 업데이트를 최적화하는 함수
function scheduleTextUpdate(textContainer, accumulatedText) {
    if (updateTextScheduled) return;
    
    updateTextScheduled = true;
    requestAnimationFrame(() => {
        const displayText = accumulatedText.replace(/\n/g, '<br>');
        textContainer.innerHTML = displayText;
        updateTextScheduled = false;
    });
}

// 상태 메시지 변환 함수
function getStatusMessage(status) {
    return status;
}

// sandbox:// 링크를 프록시 링크로 변환하는 함수
function convertSandboxLinks(text, annotations = []) {
    if (!annotations || annotations.length === 0) return text;
    
    // 파일명과 annotation 매핑 생성
    const fileMap = {};
    annotations.forEach(annotation => {
        if (annotation.type === 'container_file_citation' && annotation.filename) {
            fileMap[annotation.filename] = {
                container_id: annotation.container_id,
                file_id: annotation.file_id,
                filename: annotation.filename
            };
        }
    });
    
    // sandbox:/mnt/data/filename 패턴을 찾아서 프록시 링크로 변환
    return text.replace(/sandbox:\/mnt\/data\/([^)\s]+)/g, (match, filename) => {
        const fileInfo = fileMap[filename];
        if (fileInfo) {
            // filename을 쿼리 파라미터로 포함하여 원래 파일명으로 다운로드되도록 함
            return `/files/${fileInfo.container_id}/${fileInfo.file_id}?filename=${encodeURIComponent(fileInfo.filename)}`;
        }
        return match; // 매칭되는 파일이 없으면 원래 링크 유지
    });
}

function addMessage(content, isUser = false, files = []) {
    const messagesDiv = document.getElementById('messages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${isUser ? 'user-message' : 'assistant-message'}`;

    let messageContent = '';

    // 어시스턴트가 생성한 이미지인 경우 (content가 이미지 URL이고 files가 'image'인 경우)
    if (!isUser && files === 'image' && content) {
        messageContent = `<img src="${content}" class="generated-image" alt="Generated Image" style="max-width: 100%; height: auto; border-radius: 8px;">`;
    } else {
        // 텍스트 내용 처리
        if (content) {
            if (typeof marked !== 'undefined' && !isUser) {
                messageContent += marked.parse(content);
            } else {
                messageContent += content.replace(/\n/g, '<br>');
            }
        }

        // 사용자 메시지의 경우 파일들도 함께 표시
        if (isUser && files && Array.isArray(files) && files.length > 0) {
            if (content) messageContent += '<br><br>';
            messageContent += '<div class="user-files">';

            for (const fileObj of files) {
                if (fileObj.type === 'image') {
                    // 이미지 파일인 경우 썸네일 표시
                    const reader = new FileReader();
                    reader.onload = function(e) {
                        const img = messageDiv.querySelector(`[data-file-id="${fileObj.id}"]`);
                        if (img) {
                            img.src = e.target.result;
                        }
                    };
                    reader.readAsDataURL(fileObj.file);

                    messageContent += `<img data-file-id="${fileObj.id}" src="" style="max-width: 100px; max-height: 100px; margin: 2px; border-radius: 4px;" title="${fileObj.name}">`;
                } else {
                    messageContent += `<span class="file-badge">📄 ${fileObj.name}</span>`;
                }
            }
            messageContent += '</div>';
        }
    }

    messageDiv.innerHTML = messageContent;
    messagesDiv.appendChild(messageDiv);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
}

function setProcessing(processing) {
    isProcessing = processing;
    const sendButton = document.getElementById('sendButton');
    const messageInput = document.getElementById('messageInput');
    const attachButton = document.getElementById('attachButton');

    sendButton.disabled = processing;
    messageInput.disabled = processing;
    attachButton.disabled = processing;

    if (processing) {
        // 어시스턴트 메시지 박스를 먼저 생성하고 그 안에 스피너와 상태 메시지 표시
        const messagesDiv = document.getElementById('messages');
        const assistantDiv = document.createElement('div');
        assistantDiv.className = 'message assistant-message';
        assistantDiv.id = 'current-assistant-message';
        assistantDiv.innerHTML = '<div class="thinking-message"><div class="spinner"></div><span id="current-status">Processing request...</span></div>';
        messagesDiv.appendChild(assistantDiv);
        messagesDiv.scrollTop = messagesDiv.scrollHeight;
    }
}

// 파일 메뉴 토글
function toggleFileMenu() {
    const fileMenu = document.getElementById('fileMenu');
    fileMenu.style.display = fileMenu.style.display === 'none' ? 'block' : 'none';
}

// 외부 클릭시 파일 메뉴 닫기
document.addEventListener('click', function(event) {
    const fileMenu = document.getElementById('fileMenu');
    const attachButton = document.getElementById('attachButton');

    if (!fileMenu.contains(event.target) && !attachButton.contains(event.target)) {
        fileMenu.style.display = 'none';
    }
});

// 파일 업로드 트리거
function triggerImageUpload() {
    document.getElementById('imageInput').click();
    document.getElementById('fileMenu').style.display = 'none';
}

function triggerPdfUpload() {
    document.getElementById('pdfInput').click();
    document.getElementById('fileMenu').style.display = 'none';
}

// 파일 업로드 처리
function handleFileUpload(input, type) {
    const files = Array.from(input.files);

    // 지원되는 이미지 포맷 정의
    const supportedImageFormats = ['.jfif', '.pjp', '.jpg', '.pjpeg', '.jpeg', '.gif', '.png'];
    const supportedPdfFormats = ['.pdf'];

    files.forEach(file => {
        const fileName = file.name.toLowerCase();
        const fileExtension = '.' + fileName.split('.').pop();

        // 파일 포맷 검증
        if (type === 'image') {
            if (!supportedImageFormats.includes(fileExtension)) {
                alert(`Unsupported image format: ${file.name}\nSupported formats: ${supportedImageFormats.join(', ')}`);
                return;
            }
        } else if (type === 'pdf') {
            if (!supportedPdfFormats.includes(fileExtension)) {
                alert(`Unsupported file format: ${file.name}\nSupported formats: ${supportedPdfFormats.join(', ')}`);
                return;
            }
        }

        const fileObj = {
            id: Date.now() + Math.random(),
            file: file,
            type: type,
            name: file.name,
            size: formatFileSize(file.size)
        };

        uploadedFiles.push(fileObj);

        if (type === 'image') {
            createImagePreview(fileObj);
        } else {
            createFilePreview(fileObj);
        }
    });

    updateFilePreviewVisibility();
    input.value = ''; // 입력 초기화
}

// 클립보드 이미지 붙여넣기
function handlePaste(event) {
    const items = (event.clipboardData || event.originalEvent.clipboardData).items;

    for (let item of items) {
        if (item.type.indexOf('image') !== -1) {
            const file = item.getAsFile();
            if (file) {
                const fileObj = {
                    id: Date.now() + Math.random(),
                    file: file,
                    type: 'image',
                    name: `Clipboard_Image_${new Date().getTime()}.png`,
                    size: formatFileSize(file.size)
                };

                uploadedFiles.push(fileObj);
                createImagePreview(fileObj);
                updateFilePreviewVisibility();
            }
        }
    }
}

// 이미지 미리보기 생성
function createImagePreview(fileObj) {
    const reader = new FileReader();
    reader.onload = function(e) {
        const previewItem = createPreviewItem(fileObj, e.target.result);
        document.getElementById('filePreview').appendChild(previewItem);
    };
    reader.readAsDataURL(fileObj.file);
}

// 파일 미리보기 생성 (PDF 등)
function createFilePreview(fileObj) {
    const previewItem = createPreviewItem(fileObj, null);
    document.getElementById('filePreview').appendChild(previewItem);
}

// 미리보기 아이템 생성
function createPreviewItem(fileObj, imageSrc) {
    const div = document.createElement('div');
    div.className = 'file-preview-item';
    div.setAttribute('data-file-id', fileObj.id);

    let iconOrImage;
    if (imageSrc) {
        iconOrImage = `<img src="${imageSrc}" alt="${fileObj.name}">`;
    } else {
        iconOrImage = `<div class="file-icon">📄</div>`;
    }

    div.innerHTML = `
        ${iconOrImage}
        <div class="file-info">
            <div class="file-name">${fileObj.name}</div>
            <div class="file-size">${fileObj.size}</div>
        </div>
        <button class="remove-btn" onclick="removeFile('${fileObj.id}')">×</button>
    `;

    return div;
}

// 파일 제거
function removeFile(fileId) {
    uploadedFiles = uploadedFiles.filter(file => file.id != fileId);
    const previewItem = document.querySelector(`[data-file-id="${fileId}"]`);
    if (previewItem) {
        previewItem.remove();
    }
    updateFilePreviewVisibility();
}

// 파일 미리보기 영역 표시/숨김
function updateFilePreviewVisibility() {
    const filePreview = document.getElementById('filePreview');
    filePreview.style.display = uploadedFiles.length > 0 ? 'flex' : 'none';
}

// 파일 크기 포맷팅
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

async function fileToBase64(file) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = () => resolve(reader.result);
        reader.onerror = reject;
        reader.readAsDataURL(file);
    });
}

async function fileToBase64Only(file) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = () => {
            // data:mime;base64, 부분을 제거하고 base64 문자열만 반환
            const base64 = reader.result.split(',')[1];
            resolve(base64);
        };
        reader.onerror = reject;
        reader.readAsDataURL(file);
    });
}

function handleKeyDown(event) {
    if (event.key === 'Enter') {
        if (event.shiftKey) {
            // Shift+Enter: allow line break (default behavior)
            autoResizeTextarea(event.target);
            return true;
        } else {
            // Enter only: send message
            event.preventDefault();
            if (!isProcessing) {
                sendMessage();
            }
            return false;
        }
    }
}

function autoResizeTextarea(textarea) {
    // Automatically adjust textarea height
    textarea.style.height = 'auto';
    textarea.style.height = Math.min(textarea.scrollHeight, 150) + 'px';
}

async function sendMessage() {
    if (isProcessing) return;

    // 첫 메시지 전송 시 중앙 타이틀 사라지게 하기
    const centerTitle = document.getElementById('centerTitle');
    if (centerTitle && !centerTitle.classList.contains('fade-out')) {
        centerTitle.classList.add('fade-out');
        setTimeout(() => {
            centerTitle.style.display = 'none';
        }, 500); // 애니메이션 시간과 동일
    }

    // 기존 오류 메시지 제거
    const existingErrorMessages = document.querySelectorAll('.error-message');
    existingErrorMessages.forEach(errorMsg => errorMsg.remove());

    const messageInput = document.getElementById('messageInput');
    const messageText = messageInput.value.trim();

    if (!messageText && uploadedFiles.length === 0) {
        alert('Please enter a message or select a file.');
        return;
    }

    try {
        // 사용자 메시지를 먼저 화면에 표시
        addMessage(messageText, true, uploadedFiles);

        // 처리 중 상태로 설정 (어시스턴트 메시지 박스와 스피너 생성)
        setProcessing(true);

        // 입력 메시지 구성 (파일 초기화 전에 먼저 처리)
        const inputContent = [];

        // 업로드된 파일들 처리
        for (const fileObj of uploadedFiles) {
            if (fileObj.type === 'image') {
                const imageBase64 = await fileToBase64(fileObj.file);
                inputContent.push({
                    type: "input_image",
                    image_url: imageBase64
                });
            } else if (fileObj.type === 'pdf') {
                const pdfBase64Only = await fileToBase64Only(fileObj.file);
                inputContent.push({
                    type: "input_file",
                    filename: fileObj.name,
                    file_data: `data:application/pdf;base64,${pdfBase64Only}`
                });
            }
        }

        // 텍스트 메시지 처리
        if (messageText) {
            inputContent.push({
                type: "input_text",
                text: messageText
            });
        }

        // 입력 필드와 파일 목록 초기화 (메시지 구성 후)
        messageInput.value = '';
        uploadedFiles = [];
        document.getElementById('filePreview').innerHTML = '';
        updateFilePreviewVisibility();

        // textarea 높이도 리셋
        messageInput.style.height = 'auto';

        const inputMessage = [{
            role: "user",
            content: inputContent
        }];

        // 현재 URL의 쿼리 파라미터 가져오기
        const urlParams = new URLSearchParams(window.location.search);
        const queryString = urlParams.toString();
        
        // API 호출 (스트리밍만 사용)
        const apiUrl = queryString ? `/api?${queryString}` : '/api';
        const response = await fetch(apiUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                input_message: inputMessage,
                previous_response_id: previousResponseId
            })
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        // 스트리밍 응답 처리
        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let assistantMessageDiv = null;
        let accumulatedText = '';
        let buffer = '';
        let currentAnnotations = []; // annotations 저장
        currentImageHTML = ''; // 새 응답 시작시 이미지 HTML 초기화

        while (true) {
            const { done, value } = await reader.read();
            if (done) break;

            const chunk = decoder.decode(value, { stream: true });
            buffer += chunk;
            
            const lines = buffer.split('\n');
            buffer = lines.pop(); // 마지막 불완전한 라인은 버퍼에 보관

            for (const line of lines) {
                if (line.startsWith('data: ') && line.trim() !== 'data: ') {
                    try {
                        const jsonStr = line.slice(6).trim();
                        if (jsonStr && jsonStr !== '') {
                            const data = JSON.parse(jsonStr);

                            if (data.type === 'status') {
                                // 상태 메시지 업데이트
                                const statusElement = document.getElementById('current-status');
                                if (statusElement) {
                                    statusElement.textContent = getStatusMessage(data.status);
                                }
                            } else if (data.type === 'text_delta') {
                                if (!assistantMessageDiv) {
                                    // 기존 어시스턴트 메시지 박스 찾기 (스피너가 있는)
                                    assistantMessageDiv = document.getElementById('current-assistant-message');
                                    if (!assistantMessageDiv) {
                                        const messagesDiv = document.getElementById('messages');
                                        assistantMessageDiv = document.createElement('div');
                                        assistantMessageDiv.className = 'message assistant-message';
                                        assistantMessageDiv.id = 'current-assistant-message';
                                        messagesDiv.appendChild(assistantMessageDiv);
                                    }
                                }

                                accumulatedText += data.delta;
                                
                                // 기존 스피너 영역 찾기 또는 생성
                                let thinkingElement = assistantMessageDiv.querySelector('.thinking-message');
                                if (!thinkingElement) {
                                    thinkingElement = document.createElement('div');
                                    thinkingElement.className = 'thinking-message';
                                    thinkingElement.innerHTML = '<div class="spinner"></div><span id="current-status">Processing...</span>';
                                    assistantMessageDiv.appendChild(thinkingElement);
                                }
                                
                                // 텍스트 내용 영역 찾기 또는 생성
                                let contentElement = assistantMessageDiv.querySelector('.message-content');
                                if (!contentElement) {
                                    contentElement = document.createElement('div');
                                    contentElement.className = 'message-content';
                                    assistantMessageDiv.appendChild(contentElement);
                                    
                                    // 이미지 영역과 텍스트 영역을 분리
                                    const imageContainer = document.createElement('div');
                                    imageContainer.className = 'image-container';
                                    contentElement.appendChild(imageContainer);
                                    
                                    const textContainer = document.createElement('div');
                                    textContainer.className = 'text-container';
                                    contentElement.appendChild(textContainer);
                                }
                                
                                // 기존 이미지 유지하고 텍스트만 업데이트
                                const imageContainer = contentElement.querySelector('.image-container');
                                const textContainer = contentElement.querySelector('.text-container');
                                
                                if (imageContainer && currentImageHTML && !imageContainer.innerHTML) {
                                    imageContainer.innerHTML = currentImageHTML;
                                }
                                
                                // 텍스트는 최적화된 방식으로 업데이트
                                if (textContainer) {
                                    scheduleTextUpdate(textContainer, accumulatedText);
                                }

                                document.getElementById('messages').scrollTop = document.getElementById('messages').scrollHeight;

                            } else if (data.type === 'image_generated') {
                                if (!assistantMessageDiv) {
                                    // 기존 어시스턴트 메시지 박스 찾기 (스피너가 있는)
                                    assistantMessageDiv = document.getElementById('current-assistant-message');
                                    if (!assistantMessageDiv) {
                                        const messagesDiv = document.getElementById('messages');
                                        assistantMessageDiv = document.createElement('div');
                                        assistantMessageDiv.className = 'message assistant-message';
                                        assistantMessageDiv.id = 'current-assistant-message';
                                        messagesDiv.appendChild(assistantMessageDiv);
                                    }
                                }

                                // 기존 스피너 영역 찾기 또는 생성
                                let thinkingElement = assistantMessageDiv.querySelector('.thinking-message');
                                if (!thinkingElement) {
                                    thinkingElement = document.createElement('div');
                                    thinkingElement.className = 'thinking-message';
                                    thinkingElement.innerHTML = '<div class="spinner"></div><span id="current-status">Processing...</span>';
                                    assistantMessageDiv.appendChild(thinkingElement);
                                }
                                
                                // 텍스트 내용 영역 찾기 또는 생성
                                let contentElement = assistantMessageDiv.querySelector('.message-content');
                                if (!contentElement) {
                                    contentElement = document.createElement('div');
                                    contentElement.className = 'message-content';
                                    assistantMessageDiv.appendChild(contentElement);
                                    
                                    // 이미지 영역과 텍스트 영역을 분리
                                    const imageContainer = document.createElement('div');
                                    imageContainer.className = 'image-container';
                                    contentElement.appendChild(imageContainer);
                                    
                                    const textContainer = document.createElement('div');
                                    textContainer.className = 'text-container';
                                    contentElement.appendChild(textContainer);
                                }
                                
                                // 이미지 HTML을 현재 이미지 변수에 저장
                                const imageHTML = `<img src="${data.image_data}" style="max-width: 100%; height: auto; border-radius: 8px; margin-bottom: 10px;">`;
                                currentImageHTML = imageHTML;
                                
                                // 이미지 컨테이너에 이미지 추가
                                const imageContainer = contentElement.querySelector('.image-container');
                                const textContainer = contentElement.querySelector('.text-container');
                                
                                if (imageContainer) {
                                    imageContainer.innerHTML = currentImageHTML;
                                }
                                
                                // 기존 텍스트가 있으면 유지
                                if (textContainer && accumulatedText) {
                                    const displayText = accumulatedText.replace(/\n/g, '<br>');
                                    textContainer.innerHTML = displayText;
                                }
                                document.getElementById('messages').scrollTop = document.getElementById('messages').scrollHeight;
                            } else if (data.type === 'done') {
                                // annotations 저장
                                if (data.annotations) {
                                    currentAnnotations = data.annotations;
                                }
                                
                                // 응답 완료 시 스피너와 상태 메시지 제거
                                if (assistantMessageDiv) {
                                    const thinkingElement = assistantMessageDiv.querySelector('.thinking-message');
                                    if (thinkingElement) {
                                        thinkingElement.remove();
                                    }
                                    
                                    // 응답 완료 시 최종 Markdown 파싱 및 sandbox 링크 변환 적용
                                    const contentElement = assistantMessageDiv.querySelector('.message-content');
                                    const textContainer = contentElement ? contentElement.querySelector('.text-container') : null;
                                    
                                    if (textContainer && accumulatedText) {
                                        // sandbox 링크를 프록시 링크로 변환
                                        const convertedText = convertSandboxLinks(accumulatedText, currentAnnotations);
                                        
                                        let finalTextContent = '';
                                        if (typeof marked !== 'undefined') {
                                            finalTextContent = marked.parse(convertedText);
                                        } else {
                                            finalTextContent = convertedText.replace(/\n/g, '<br>');
                                        }
                                        textContainer.innerHTML = finalTextContent;
                                    }
                                    
                                    assistantMessageDiv.id = ''; // ID 제거
                                }

                                if (data.response_id) {
                                    previousResponseId = data.response_id;
                                }
                                console.log('Stream completed');
                            } else if (data.type === 'error') {
                                // 서버에서 에러가 발생한 경우 처리
                                console.error('Server error:', data.message);
                                
                                // 스피너가 있는 어시스턴트 메시지 박스 제거
                                const currentAssistantMessage = document.getElementById('current-assistant-message');
                                if (currentAssistantMessage) {
                                    currentAssistantMessage.remove();
                                }
                                
                                // 오류 메시지를 빨간색으로 중앙 정렬해서 표시
                                const messagesDiv = document.getElementById('messages');
                                const errorDiv = document.createElement('div');
                                errorDiv.className = 'error-message';
                                errorDiv.textContent = `Server error: ${data.message}`;
                                messagesDiv.appendChild(errorDiv);
                                messagesDiv.scrollTop = messagesDiv.scrollHeight;
                                
                                // 처리 완료로 설정
                                setProcessing(false);
                            }
                        }
                    } catch (e) {
                        console.error('JSON parsing error for line:', line);
                        console.error('Error details:', e);
                        // JSON 파싱 에러는 무시하고 계속 진행
                    }
                }
            }
        }

    } catch (error) {
        console.error('Error:', error);

        // 스피너가 있는 어시스턴트 메시지 박스 제거
        const currentAssistantMessage = document.getElementById('current-assistant-message');
        if (currentAssistantMessage) {
            currentAssistantMessage.remove();
        }

        // 오류 메시지를 빨간색으로 중앙 정렬해서 표시
        const messagesDiv = document.getElementById('messages');
        const errorDiv = document.createElement('div');
        errorDiv.className = 'error-message';
        errorDiv.textContent = `An error occurred: ${error.message}`;
        messagesDiv.appendChild(errorDiv);
        messagesDiv.scrollTop = messagesDiv.scrollHeight;
    } finally {
        setProcessing(false);
    }
}