# Voice Flow
Voice Flow is designed for conversational application development using audio inputs and outputs, leveraging the capabilities of the GPT-4o-Realtime-Preview model for voice-to-voice interactions. With Voice Flow, you can easily create a voicebot that handles audio input and generates both audio and text outputs.
realtime client: [https://github.com/Azure-Samples/aoai-realtime-audio-sdk](https://github.com/Azure-Samples/aoai-realtime-audio-sdk)

## Prerequisites
```bash
pip install -r requirements.txt
pip install rtclient-0.5.1-py3-none-any.whl
```

## Create connection for LLM tool to use
Ensure you have a deployment of the 'gpt-4o-realtime-preview' model and create a connection to it in promptflow.

Please refer to connections [document](https://promptflow.azurewebsites.net/community/local/manage-connections.html) and [example](https://github.com/microsoft/promptflow/tree/main/examples/connections) for more details.

## Run the voice flow
This flow uses the `audio_input_file` parameter to generate a text description of the audio file passed as well as a reference to the audio file that was generated from the model.
Outputs
- `audio_transcript` - The text description of the audio file passed.
- `file_outputs` - The path to the audio file generated from the model.
  
![alt text](<assets/Screenshot 2024-10-29 091525.png>)

Example Input: 
<audio controls src="assets/example_in.wav" title=""></audio>
[input](assets/example_in.wav)

Example Output:

- Audio transcript: 
`
I hear a person speaking English with an American accent in a clear tone. They said the following: "A fault observed in layers of sedimentary rock most likely resulted from the converging of crustal plates."
`

- Audio output:
- <audio controls src="assets/example_out.wav" title="Title"></audio>
  [output](assets/example_out.wav)

### Batch Execution
Use the `input/realtime_batchrun.jsonl` file to run the flow in batch mode.
Batch execution:
![alt text](<assets/Screenshot 2024-10-29 091145.png>)

Example Batch execution results:
![alt text](<assets/Screenshot 2024-10-29 091540.png>)


