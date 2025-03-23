# LLM CLI (Formerly chatgpt-cli)

LLM CLI is a command-line tool to chat with LLMs via the OpenAI, Anthropic, and Ollama APIs.

- [Installation](#installation)
  - [Install with pipx (recommended)](#install-with-pipx)
  - [Setting up PATH](#setting-up-path)
- [Usage](#usage)
  - [Help message](#help-message)
  - [Example usage](#example-usage)
- [TODO](#todo)

## <a name="installation"></a> Installation:

### <a name="install-with-pipx"></a> Install with pipx (recommended)
The easiest way to install is using pipx:

`pipx install git+https://github.com/slaufer/chatgpt-cli`

### <a name="setting-up-path"></a> Setting up PATH

If the `llmcli` command is not found after install, you may need to add its location to your PATH variable.

In Linux and MacOS, add this to your ~/.bashrc or ~/.zshrc file, and restart your terminal:
```bash
export PATH="$HOME/.local/bin:$PATH"
```

In Windows, Use System Properties -> Environment Variables to edit your PATH, and add:
```
%USERPROFILE%\AppData\Roaming\Python\Scripts
```


## <a name="usage"></a> Usage:

If you installed using pipx, just run `llmcli`.

### <a name="help-message"></a> Help message

```
LLM CLI

This command line interface allows you to interact with OpenAI and Anthropic's chat completion APIs in various ways, including sending system prompts, assistant responses, user prompts, and loading previous conversations. It supports both interactive and non-interactive modes.

Usage:
  llmcli [options]

Options:
  MESSAGE ARGUMENTS:
  -s, --system <message>       Add a system prompt message. If not specified, a default system prompt is used.
  -a, --assistant <message>    Add an assistant response message.
  -u, --user <message>         Add a user prompt message.
  -f, --file <filename>        Add a user prompt message from a file.
  -i, --image <filename>       Add a user prompt message from an image. If --max-tokens is not specified, a default value may be applied.
  -c, --conversation <file>    Load a previous conversation from a file. (see -j / --log-file-json)
  -d, --no-system-prompt       Don't add a default system prompt if none is present.

  Message arguments are added to the conversation in the order in which they are specified on the command line.

  API ARGUMENTS:
  -p, --api                    Identifier of the API adapter to use. (See ADAPTERS below.) (default: openai)
  -o, --api-options            API options, in the format <key1>=<value1>;<key2>=<value2>;... (See ADAPTERS below.)

  OTHER ARGUMENTS:
  -n, --non-interactive        Disable interactive mode, get a completion and exit. Use message arguments to specify the conversation.
  -l, --log-file <filename>    Log output to a specified file.
  -j, --log-file-json <file>   Output a JSON-formatted log to a specified file.
  -g, --immediate              Get an assistant response immediately, before entering interactive mode.
  -x, --separator <separator>  Specify the separator to use between messages.
  -q, --no-intro               Don't print the system prompt, or messages specified on the command line.
  -h, --help                   Print this help message and exit.

  By default, the program begins in interactive mode. Interactive mode uses a multi-line editor. Press Alt+Enter to submit; Ctrl+M to show the menu; Ctrl+C or Ctrl+D to exit.

  TIP: Try `llmcli -c mylog.json -j mylog.json` to persist conversations between sessions.

  ADAPTERS:
    OpenAI (openai)
      OPTIONS:
      - model                  Model ID used to generate the response. (default: gpt-4o)
      - api_key                Your OpenAI API key (default: XXXX)
      - max_tokens             The maximum number of tokens that can be generated in the chat completion.
      - temperature            What sampling temperature to use, between 0 and 2.
      - top_p                  An alternative to sampling with temperature, called nucleus sampling.
      - frequency_penalty      Number between -2.0 and 2.0. Positive values penalize new tokens based on their existing frequency in the text so far.
      - presence_penalty       Number between -2.0 and 2.0. Positive values penalize new tokens based on whether they appear in the text so far.

      By default, uses the OpenAI API key from the environment variable OPENAI_API_KEY.

    Anthropic (anthropic)
      OPTIONS:
      - model                  Model ID used to generate the response. (default: claude-3-7-sonnet-latest)
      - api_key                Your Anthropic API key (default: XXXX)
      - max_tokens             The maximum number of tokens that can be generated in the chat completion (default: 1000)
      - temperature            What sampling temperature to use, between 0 and 2.
      - top_p                  An alternative to sampling with temperature, called nucleus sampling.

      By default, uses the Anthropic API key from the environment variable ANTHROPIC_API_KEY.

    Ollama (ollama)
      OPTIONS:
      - model                  Model ID used to generate the response. (default: llama3.1:8b)

      By default, uses an Ollama instance running on localhost. For remote instances, set the OLLAMA_HOST environment variable.
```

### <a name="example-usage"></a> Example usage:

```
slaufer@localhost:~$ llmcli
Press Alt+Enter to submit; Ctrl+M to show the menu; Ctrl+C or Ctrl+D to exit.
 #============================================================================#

System:

Carefully heed the user's instructions.
Respond using Markdown.
Respond briefly and concisely unless you are instructed to do otherwise.
Do not include any extraneous or tangential details unless you are instructed to do otherwise.

 #============================================================================#

User:

hey chatgpt!

 #============================================================================#

Assistant:

Hello! How can I assist you today?

 #============================================================================#

User:

 
[0] Add a file
[1] Add an image
[2] Change API
[3] Change API options
[4] Change JSON log file
[5] Exit menu
[6] Quit
 
Enter selection: 1
Enter image path: ~/test.png
IMAGE: ../../test.png (contents hidden)

 #============================================================================#

User:

what is this image?

 #============================================================================#

Assistant:

This image shows a kitten sitting inside a woven basket.

```

## <a name="todo"></a> TODO
- Image support for Ollama
- Additional model parameters for Ollama
