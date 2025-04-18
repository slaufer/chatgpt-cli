from llmcli.message import Message

TEST_IMAGE = 'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABAQAAAAA3bvkkAAAACklEQVR4AWNgAAAAAgABc3UBGAAAAABJRU5ErkJggg=='

def get_assistant_args():
  return {
    'adapter': 'ollama',
    'adapter_options': {
      'model': 'gemma3',
      'temperature': 0.4,
    },
    'display_name': 'ollama / gemma3',
  }

def get_test_messages_system():
  return [Message(role='system', content='You are an assistant.')]

def get_test_messages_text():
  return [
    Message(role='assistant', content='Hello, world!', **get_assistant_args()),
    Message(role='user', content='How are you?'),
    Message(role='assistant', content='I am fine, thank you!', **get_assistant_args()),
  ]

def get_test_messages_file():
  return [
    Message(
      role='user',
      content='### File: test.txt (contents hidden)',
      file_path='test.txt',
      file_content='i\'m a file =3'
    ),
    Message(role='user', content='What is this file?'),
    Message(role='assistant', content='What a lovely file!', **get_assistant_args()),
  ]

def get_test_messages_image():
    return [
      Message(
        role='user',
        content='### File: test.txt (contents hidden)',
        image_path='test.png',
        image_content=TEST_IMAGE,
        image_type='image/png'
      ),
      Message(role='user', content='What is this image?'),
      Message(role='assistant', content='What a lovely image!', **get_assistant_args()),
    ]

def get_test_messages(system=True, text=True, file=False, image=False):
  messages = []
  
  if system:
    messages += get_test_messages_system()
  if text:
    messages += get_test_messages_text()
  if file:
    messages += get_test_messages_file()
  if image:
    messages += get_test_messages_image()

  return messages
