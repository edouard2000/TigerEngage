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
    let recognition = null; 

    mic_btn.addEventListener('click', function() {
        if (!isRecording) {
            // Request access to the microphone
            navigator.mediaDevices.getUserMedia({ audio: true })
                .then(setupStream)
                .catch(err => {
                    console.error('Failed to get audio stream from microphone:', err);
                    alert('Could not access the microphone.');
                });
            isRecording = true;
        } else {
            stopRecording();
        }
    });

    function setupStream(stream) {
        recorder = new MediaRecorder(stream);
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

        recorder.ondataavailable = e => chunks.push(e.data);

        recorder.onstop = e => {
            const blob = new Blob(chunks, {type: 'audio/ogg; codecs=opus'});
            const audioURL = window.URL.createObjectURL(blob);
            playback.src = audioURL;
            stopRecognition(); // Stop speech recognition
        };

        recorder.start();
        recognition.start();
        mic_btn.textContent = 'Stop Recording';
        recordingDot.style.display = 'inline-block';
    }

    function stopRecording() {
        if (recorder.state !== 'inactive') {
            recorder.stop();
            recorder.stream.getTracks().forEach(track => track.stop()); // Release the media stream
        }
        mic_btn.textContent = 'Start Recording';
        recordingDot.style.display = 'none';
        isRecording = false;
    }

    function stopRecognition() {
        if (recognition) {
            recognition.stop();
        }
    }

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