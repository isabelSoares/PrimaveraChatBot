import pyaudio
from deepspeech import Model
import scipy.io.wavfile as wav
import wave


WAVE_OUTPUT_FILENAME = "test_audio.wav"

def record_audio(WAVE_OUTPUT_FILENAME):
	CHUNK = 1024
	FORMAT = pyaudio.paInt16
	CHANNELS = 1
	RATE = 16000
	RECORD_SECONDS = 5

	p = pyaudio.PyAudio()

	stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK)

	print("* recording")

	frames = [stream.read(CHUNK) for i in range(0, int(RATE / CHUNK * RECORD_SECONDS))]

	print("* done recording")

	stream.stop_stream()
	stream.close()
	p.terminate()

	wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
	wf.setnchannels(CHANNELS)
	wf.setsampwidth(p.get_sample_size(FORMAT))
	wf.setframerate(RATE)
	wf.writeframes(b''.join(frames))
	wf.close()


def deepspeech_predict(WAVE_OUTPUT_FILENAME):

	N_FEATURES = 25
	N_CONTEXT = 9
	BEAM_WIDTH = 500
	LM_ALPHA = 0.75
	LM_BETA = 1.85


	ds = Model('deepspeech-0.5.1-models/output_graph.pbmm', N_FEATURES, N_CONTEXT, 'deepspeech-0.5.1-models/alphabet.txt', BEAM_WIDTH)

	fs, audio = wav.read(WAVE_OUTPUT_FILENAME)
	return ds.stt(audio, fs)

if __name__ == '__main__':
	record_audio(WAVE_OUTPUT_FILENAME)
	predicted_text = deepspeech_predict(WAVE_OUTPUT_FILENAME)
	print(predicted_text)