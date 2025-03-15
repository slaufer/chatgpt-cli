# LLM CLI (Formerly chatgpt-cli)

I get asked about my LLM CLI sometimes, so I'm posting it here. Enjoy!

## Installation:

Run `pip install git+https://github.com/slaufer/chatgpt-cli`

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
  
  MODEL ARGUMENTS:
  --list-models                List available models for automatic API selection.
  -m, --model <model_name>     Specify the model to use. (default: gpt-4o)
  --api                        Specify the API to use. Required for unrecognized models. (options: openai, anthropic)
  --temperature <value>        The sampling temperature to use, between 0 and 1.
  --max-tokens <number>        The maximum number of tokens to generate in the completion.
  --top-p <value>              The top-p sampling value to use, between 0 and 1.
  --frequency-penalty <value>  The frequency penalty to use, between -2.0 and 2.0. (OpenAI models only)
  --presence-penalty <value>   The presence penalty to use, between -2.0 and 2.0. (OpenAI models only)
        
  OTHER ARGUMENTS:
  -n, --non-interactive        Disable interactive mode, get a completion and exit. Use message arguments to specify the conversation.
  -l, --log-file <filename>    Log output to a specified file.
  -j, --log-file-json <file>   Output a JSON-formatted log to a specified file.
  -g, --immediate              Get an assistant response immediately, before entering interactive mode.
  -x, --separator <separator>  Specify the separator to use between messages.
  -o, --no-intro               Don't print the system prompt, or messages specified on the command line.
  -h, --help                   Print this help message and exit.

Message arguments are added to the conversation in the order in which they are specified on the command line. If no system prompt is specified, a default prompt will be added.

By default, the program begins in interactive mode. Interactive mode uses a multi-line editor. Press Alt+Enter to submit; Ctrl+F to add file; Ctrl+I to add image; Ctrl+S to get completion without message; Ctrl+C or Ctrl+D to exit.

Make sure you set the appropriate API key environment variable. For OpenAI models, set OPENAI_API_KEY. For Anthropic models, set ANTHROPIC_API_KEY.

TIP: Try `llmcli -c mylog.json -j mylog.json` to persist conversations between sessions.

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
 
Hi!

 #============================================================================#

Assistant:

Hello! How can I assist you today?

 #============================================================================#

User:
 
/home/slaufer/test.png
IMAGE: test.png (contents hidden)

 #============================================================================#

User:
 
What is in this image?

 #============================================================================#

Assistant:

The image shows a kitten sitting in a woven basket.
```

## TODO

- Separate options for model adapters
- Replace interactive mode hotkeys with a single menu
- Image support for Ollama (how?)
