import basic_app_frame_xethhung12 as project
from j_vault_http_client_xethhung12 import client
def main():
    client.load_to_env()
    project.hello("user")
