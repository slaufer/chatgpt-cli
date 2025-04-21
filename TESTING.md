### Running the tests

```
# do this once
git clone https://github.com/slaufer/chatgpt-cli
cd chatgpt-cli
python -m venv venv

# do this once per shell session
. venv/bin/activate

# do this to run the tests
pip install .[test] && pytest

# and run the linter
pylint llmcli
```

**NOTE:** Many of the tests are using UNIX-style file paths, and may or may not work in Windows.
