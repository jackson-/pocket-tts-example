# Pocket Voice Agent

A real-time, conversational voice agent that runs locally on your Mac. It uses **Google Gemini 2.0 Flash** for its "brain" and **Kyutai Pocket TTS** for high-quality, low-latency speech synthesis, with support for **voice cloning**.

## Features

*   **Real-time Conversation:** Speaks back to you naturally with minimal latency using streaming responses.
*   **Voice Cloning:** Can clone your voice (or any voice) from a simple 10-second recording.
*   **Conversational Memory:** Remembers the context of your chat.
*   **Custom Persona:** Currently configured as a loving, attentive partner, but easily customizable.
*   **Local TTS:** Uses `pocket-tts`, a 100M parameter model that runs efficiently on your CPU.

## Prerequisites

*   **Python 3.10 or 3.11** (Required by `pocket-tts`)
*   **PortAudio** (Required for microphone access)
*   **Hugging Face Account** (Required for the voice cloning model)
*   **Google Gemini API Key**

## Setup

1.  **Install System Dependencies:**
    ```bash
    brew install portaudio
    ```

2.  **Clone the Repository:**
    ```bash
    git clone <your-repo-url>
    cd voice-chat
    ```

3.  **Create and Activate Virtual Environment:**
    ```bash
    # Must use Python 3.11
    python3.11 -m venv venv
    source venv/bin/activate
    ```

4.  **Install Python Packages:**
    ```bash
    pip install -r requirements.txt
    ```

5.  **Environment Variables:**
    Create a `.env` file in the root directory:
    ```bash
    cp .env.example .env
    ```
    Edit `.env` and add your Google Gemini API Key:
    ```
    GEMINI_API_KEY=your_api_key_here
    ```

6.  **Hugging Face Authentication (Crucial for Voice Cloning):**
    *   Go to [https://huggingface.co/kyutai/pocket-tts](https://huggingface.co/kyutai/pocket-tts) and accept the license terms.
    *   Create a **Classic Read Token** (or a Fine-grained token with "Gated Repositories" permission) at [https://huggingface.co/settings/tokens](https://huggingface.co/settings/tokens).
    *   Log in via the terminal:
        ```bash
        hf auth login
        ```
    *   Paste your token when prompted.

## Usage

### 1. Clone Your Voice (Optional)
If you want the agent to sound like you (or anyone else), record a sample:

```bash
python record_voice.py
```
*   Follow the prompts to record for 10 seconds.
*   This creates `my_voice.wav`.
*   If this file exists, the agent will use it automatically. If not, it defaults to a built-in voice.

### 2. Run the Agent

```bash
python agent.py
```
*   Wait for initialization (it may take a moment to download the model weights the first time).
*   Start talking when you see "Listening...".
*   Say "goodbye", "quit", or "exit" to end the session.

## Troubleshooting

*   **"FutureWarning: All support for google.generativeai..."**: This is a known warning from the Google SDK. It does not affect functionality.
*   **"ValueError: We could not download the weights..."**: This means you haven't accepted the terms on Hugging Face or your token doesn't have permissions for "Gated Repositories". See Step 6 in Setup.
*   **Microphone Issues:** Ensure your terminal has permission to access the microphone in macOS System Settings > Privacy & Security > Microphone.

## Customization

*   **Change Persona:** Edit the `system_instruction` variable in `agent.py`.
*   **Adjust Latency/Patience:** Modify `pause_threshold` and `phrase_time_limit` in `agent.py` to make the agent wait longer (or shorter) for you to finish speaking.
