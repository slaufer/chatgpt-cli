# llm-cli
I get asked about my LLM CLI sometimes, so I'm posting it here. Enjoy!

You might need to run `pip3 install prompt_toolkit openai anthropic` to make this script work.

```
LLM CLI

This command line interface allows you to interact with OpenAI and Anthropic's chat completion APIs in various ways, including sending system prompts, assistant responses, user prompts, and loading previous conversations. It supports both interactive and non-interactive modes.

Usage:
  {exec_path} [options]

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
  --list-models                List available models.
  -m, --model <model_name>     Specify the model to use. (default: gpt-4o)
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

By default, the program begins in interactive mode. Interactive mode uses a multi-line editor, press Alt+Enter to submit, and Ctrl+C or Ctrl+D to exit.

Make sure you set the appropriate API key environment variable. For OpenAI models, set OPENAI_API_KEY. For Anthropic models, set ANTHROPIC_API_KEY.

TIP: Try `{exec_path} -c mylog.json -j mylog.json` to persist conversations between sessions.
```
