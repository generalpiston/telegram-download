import asyncio
import configparser
import os
import time
from telethon import TelegramClient

CONFIG_INI = 'telegram-download.ini'

class TelegramDownload(object):
  def __init__(self, api_id, api_hash, output, entity='me', delete_on_download=False):
    self.api_id = api_id
    self.api_hash = api_hash
    self.entity = entity
    self.output = output
    self.delete_on_download = delete_on_download
    self.client = TelegramClient('download', self.api_id, self.api_hash)
    self.client.flood_sleep_threshold = 10
    self.client.start()

  def find_photos(self):
    print('Finding photos for {}'.format(self.entity))

    messages = []

    for message in self.client.iter_messages(self.entity):
      if hasattr(message, 'media') and hasattr(message.media, 'photo'):
        messages.append(message)

    return messages

  def download_photos(self, messages=[], batch_size=25, wait=3):
    print('Downloading photos to {}'.format(self.output))

    if not os.path.isdir(self.output):
      os.mkdir(self.output)

    loop = asyncio.get_event_loop()

    for i in range(0,int(len(messages)/batch_size)):
      tasks = []

      for message in messages[i*batch_size:(i+1)*batch_size]:
        tasks.append(message.download_media(self.output))

      loop.run_until_complete(asyncio.gather(*tasks))

      time.sleep(3)

  def execute(self):
    messages = self.find_photos()
    self.download_photos(list(messages))
    if self.delete_on_download:
      self.delete_photos(messages)

  def delete_photos(self, messages):
    print('Deleting photos')

    loop = asyncio.get_event_loop()
    tasks = []

    for message in messages:
      tasks.append(message.delete())

    loop.run_until_complete(asyncio.gather(*tasks))


def write_config(path=CONFIG_INI):
  config = configparser.ConfigParser()

  print("Generate the answers to the following questions here: http://my.telegram.org/.")
  config['DEFAULT']['api_id'] = input("API ID: ")
  config['DEFAULT']['api_hash'] = input("API Hash: ")
  config['DEFAULT']['output'] = input("Output Location: ")

  with open(path, 'w') as f:
    config.write(f)

def read_config(path=CONFIG_INI):
  config = configparser.ConfigParser()
  config.read(path)
  return config['DEFAULT']

def ensure_config(path=CONFIG_INI):
  if not os.path.isfile(path):
    write_config(path)

  return read_config()

def main():
  config = ensure_config()
  delete_on_download = input("Delete Photos On Download? (Y|N) (Default: N): ") == 'Y'
  entity = input("Channel? (Default: Saved Messages): ") or "me"

  client = TelegramDownload(config['api_id'], config['api_hash'], config['output'], entity, delete_on_download)
  client.execute()

main()