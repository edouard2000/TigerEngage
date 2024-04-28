document.addEventListener('DOMContentLoaded', function() {
    const mic_btn = document.querySelector('#mic');
    const submit_btn = document.querySelector('#submitTranscript');
    const transcriptArea = document.querySelector('#transcriptArea');
    const playback = document.querySelector(".playback");
    const recordingDot = document.querySelector('.recording-dot');
    const audioStartAlert = document.getElementById('recordingAlert');
    const audioStopAlert = document.getElementById('recordingStopAlert');
    let isRecording = false;  
    let recorder = null;
    let chunks = [];
    let can_record = false;
    let recognition; 

    if ('webkitSpeechRecognition' in window) {
        recognition = new webkitSpeechRecognition();
        recognition.continuous = true;
        recognition.interimResults = false; 
        recognition.lang = 'en-US';

        recognition.onresult = function(event) {
            const transcript = Array.from(event.results)
                                    .map(result => result[0])
                                    .map(result => result.transcript)
                                    .join('');
            transcriptArea.value += transcript; 
        };

        recognition.onerror = function(event) {
            console.error('Speech recognition error:', event.error);
        };
    } else {
        console.log('Speech recognition not supported in this browser.');
    }

    function SetupAudio() {
        navigator.mediaDevices.getUserMedia({ audio: true })
            .then(SetupStream)
            .catch(err => {
                console.error('Failed to get audio stream from microphone:', err);
                alert('Could not access the microphone.');
            });
    }

    SetupAudio();

    function SetupStream(stream) {
        recorder = new MediaRecorder(stream);

        recorder.ondataavailable = e => chunks.push(e.data);

        recorder.onstop = e => {
            const blob = new Blob(chunks, {type: 'audio/ogg; codecs=opus'});
            chunks = [];
            const audioURL = window.URL.createObjectURL(blob);
            playback.src = audioURL;
        };

        can_record = true;
    }

    mic_btn.addEventListener('click', function() {
        if (!isRecording) {
            audioStartAlert.play();
            mic_btn.textContent = 'Stop';
            recordingDot.style.display = 'inline-block';
            if (can_record) {
                recorder.start();
                recognition.start(); 
            }
            isRecording = true;
        } else {
            audioStopAlert.play();
            mic_btn.textContent = 'Record';
            recordingDot.style.display = 'none';
            if (can_record) {
                recorder.stop();
                recognition.stop();
            }
            isRecording = false;
        }
    });

    submit_btn.addEventListener('click', function() {
        const transcript = transcriptArea.value;
        if (transcript) {
            fetch('/process_transcript', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ transcript: transcript })
            })
            .then(response => response.blob())
            .then(blob => {
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.style.display = 'none';
                a.href = url;
                a.download = 'notes.pdf';
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);
            })
            .catch(error => console.error('Error:', error));
        }
    });
});
