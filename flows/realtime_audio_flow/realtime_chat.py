from promptflow.core import tool
from promptflow.connections import AzureOpenAIConnection
import asyncio
import os
import sys
import numpy as np
import soundfile as sf
from azure.core.credentials import AzureKeyCredential
from scipy.signal import resample
from azure.core.exceptions import ServiceRequestError
    

from rtclient import (
    InputAudioTranscription,
    RTAudioContent,
    RTClient,
    RTFunctionCallItem,
    RTInputAudioItem,
    RTMessageItem,
    RTResponse,
    ServerVAD,
)

str_buffer = []
file_list = []

def resample_audio(audio_data, original_sample_rate, target_sample_rate):
    print('resampling audio')
    number_of_samples = round(len(audio_data) * float(target_sample_rate) / original_sample_rate)
    resampled_audio = resample(audio_data, number_of_samples)
    return resampled_audio.astype(np.int16)


async def send_audio(client: RTClient, audio_file_path: str):
    print(f"Sending audio from {audio_file_path}")
    sample_rate = 24000
    duration_ms = 100
    samples_per_chunk = sample_rate * (duration_ms / 1000)
    bytes_per_sample = 2
    bytes_per_chunk = int(samples_per_chunk * bytes_per_sample)

    extra_params = (
        {
            "samplerate": sample_rate,
            "channels": 1,
            "subtype": "PCM_16",
        }
        if audio_file_path.endswith(".raw")
        else {}
    )

    audio_data, original_sample_rate = sf.read(audio_file_path, dtype="int16", **extra_params)

    if original_sample_rate != sample_rate:
        audio_data = resample_audio(audio_data, original_sample_rate, sample_rate)

    audio_bytes = audio_data.tobytes()

    for i in range(0, len(audio_bytes), bytes_per_chunk):
        chunk = audio_bytes[i : i + bytes_per_chunk]
        await client.send_audio(chunk)


async def receive_message_item(item: RTMessageItem, out_dir: str):
    global str_buffer, file_list
    print(f"Received message item {item.id}")
    prefix = f"[response={item.response_id}][item={item.id}]"
    async for contentPart in item:
        if contentPart.type == "audio":

            async def collect_audio(audioContentPart: RTAudioContent):
                audio_data = bytearray()
                async for chunk in audioContentPart.audio_chunks():
                    audio_data.extend(chunk)
                return audio_data

            async def collect_transcript(audioContentPart: RTAudioContent):
                audio_transcript: str = ""
                async for chunk in audioContentPart.transcript_chunks():
                    audio_transcript += chunk
                return audio_transcript

            audio_task = asyncio.create_task(collect_audio(contentPart))
            transcript_task = asyncio.create_task(collect_transcript(contentPart))
            audio_data, audio_transcript = await asyncio.gather(audio_task, transcript_task)
            print(prefix, f"Audio received with length: {len(audio_data)}")
            print(prefix, f"Audio Transcript: {audio_transcript}")
            str_buffer.append(audio_transcript)
            audio_filename = os.path.join(out_dir, f"{item.id}_{contentPart.content_index}.wav")
            file_list.append(audio_filename)                              
            with open(audio_filename, "wb") as out:
                audio_array = np.frombuffer(audio_data, dtype=np.int16)
                sf.write(out, audio_array, samplerate=24000)
            


async def receive_response(client: RTClient, response: RTResponse, out_dir: str):
    print(f"Received response {response.id}")
    prefix = f"[response={response.id}]"
    async for item in response:
        print(prefix, f"Received item {item.id}")
        if item.type == "message":
            asyncio.create_task(receive_message_item(item, out_dir))

    print(prefix, f"Response completed ({response.status})")
    if response.status == "completed":
        await client.close()


async def receive_input_item(item: RTInputAudioItem):
    print(f"Received input item {item.id}")
    prefix = f"[input_item={item.id}]"
    #await item
    print(prefix, f"Transcript: {item.transcript}")
    print(prefix, f"Audio Start [ms]: {item.audio_start_ms}")
    print(prefix, f"Audio End [ms]: {item.audio_end_ms}")


async def receive_events(client: RTClient, out_dir: str):
    print("Receiving Events")
    async for event in client.events():
        print(f"Received event {event.type}")
        if event.type == "input_audio":
            asyncio.create_task(receive_input_item(event))
        elif event.type == "response":
            asyncio.create_task(receive_response(client, event, out_dir))


async def receive_messages(client: RTClient, out_dir: str):
    print("Receiving Messages")
    await asyncio.gather(
        receive_events(client, out_dir),
    )

# The inputs section will change based on the arguments of the tool function, after you save the code
# Adding type to arguments and return value will help the system show the types properly
# Please update the function name/signature per need
@tool
async def my_python_tool(audio_input_path: str, system_msg: str, aoai_connection:AzureOpenAIConnection, deployment: str) -> str:
    endpoint = aoai_connection.api_base
    key = aoai_connection.api_key
    deployment = deployment
    out_dir = "./output"
    audio_file_path = audio_input_path

    async def connect_with_retry(url, key_credential, azure_deployment, retries=5, initial_delay=2):
        delay = initial_delay
        for attempt in range(retries):
            try:
                client = RTClient(url=url, key_credential=key_credential, azure_deployment=azure_deployment)
                await client.__aenter__()
                return client
            except Exception as e:
                if attempt < retries - 1:
                    await asyncio.sleep(delay)
                    delay *= 2  # Exponential backoff
                else:
                    raise e


    client = await connect_with_retry(url=endpoint, key_credential=AzureKeyCredential(key), azure_deployment=deployment)
    try:
        print("Configuring Session...", end="", flush=True)
        await client.configure(
            instructions=system_msg,
            turn_detection=ServerVAD(threshold=0.5, prefix_padding_ms=300, silence_duration_ms=200),
            input_audio_transcription=InputAudioTranscription(model="whisper-1"),
        )
        print("Done")
        
        print("Sending Audio")
        send_audio_task = send_audio(client, audio_file_path)
        receive_messages_task = receive_messages(client, out_dir)

        # Await both tasks and capture the result of receive_messages
        _, received_messages_output = await asyncio.gather(send_audio_task, receive_messages_task)
        # Return an object with the output from receive_messages
        print("Received Messages")
        return {
            "audio_transcript": str_buffer,
            "file_outputs": file_list
        }
    finally:
        await client.__aexit__(None, None, None)