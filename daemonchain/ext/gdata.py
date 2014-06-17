import gdata.docs.client


def CreateClient(config):
  """Create a Documents List Client."""
  client = config.SERVICE(source=config.APP_NAME)
  client.http_client.debug = config.DEBUG
  try:
    client.ClientLogin(config.LOGIN, config.PASSWORD,config.APP_NAME)
  except gdata.client.BadAuthentication:
    exit('Invalid user credentials given.')
  except gdata.client.Error:
    exit('Login Error')
  return client