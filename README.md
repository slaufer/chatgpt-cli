# LLM CLI (Formerly chatgpt-cli)

I get asked about my LLM CLI sometimes, so I'm posting it here. Enjoy!

## Installation:

### Install with pipx
Run `pipx install git+https://github.com/slaufer/chatgpt-cli`

## Usage:

If you installed using pip, just run `llmcli`. Here's the help message:

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

  By default, the program begins in interactive mode. Interactive mode uses a multi-line editor. Press Alt+Enter to submit; Ctrl+F to add file; Ctrl+I to add image; Ctrl+S to get completion without message; Ctrl+C or Ctrl+D to exit.

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

Here's an example:


```
slaufer@localhost:~$ llmcli
Press Alt+Enter to submit; Ctrl+F to add file; Ctrl+I to add image; Ctrl+S to get completion without message; Ctrl+C or Ctrl+D to exit.
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

## TODO
- Image support for Ollama
