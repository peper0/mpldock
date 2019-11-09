import json
import logging
import os
from dataclasses import dataclass
from typing import Dict

import appdirs

from .common import DumpStateFunction, DumpedState, RestoreStateFunction

APPNAME = 'mpldock'

encoders = dict(
    json=json.dumps,
)

decoders = dict(
    json=json.loads,
)


@dataclass
class Client:
    dump_state: DumpStateFunction
    restore_state: RestoreStateFunction


class StateManager:
    def __init__(self, id, factory_default_path):
        self._factory_default_path = factory_default_path
        self._id = id

        self._clients_by_name: Dict[str, Client] = {}
        self._restored_clients_state: Dict[str, DumpedState] = {}

    def add_client(self, name, dump_state: DumpStateFunction, restore_state: RestoreStateFunction):
        self._clients_by_name[name] = Client(dump_state=dump_state, restore_state=restore_state)

    def get_client_state(self, name):
        return self._restored_clients_state.get(name)

    def _dump_state(self):
        clients = {}
        for name, client in self._clients_by_name.items():
            try:
                clients[name] = client.dump_state()
            except Exception:
                logging.exception("Exception during dumping state of '{name}'")
        return dict(clients=clients)

    def save_to_file(self, path: str):
        *_, ext = path.rpartition('.')
        encode = encoders.get(ext)
        if not encode:
            raise Exception(f"unknown format: {ext}")
        encoded = encode(self._dump_state())
        # we encode before opening a file to be safe if exception is raised during encoding
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w') as f:
            f.write(encoded)

    def _restore_state(self, state: DumpedState):
        clients_state = state['clients']
        self._restored_clients_state = clients_state
        for name, client in self._clients_by_name.items():
            client_state = clients_state.get(name)
            if client_state is not None:
                try:
                    client.restore_state(client_state)
                except Exception:
                    logging.exception("Exception during restoring state of '{name}'")

    def restore_from_file(self, path):
        *_, ext = path.rpartition('.')
        decode = decoders.get(ext)
        if not decode:
            raise Exception(f"unknown format: {ext}")
        with open(path, 'r') as f:
            state = decode(f.read())
        self._restore_state(state)

    def _system_state_path(self, id):
        return os.path.join(appdirs.user_data_dir(APPNAME, False), f"{id}.state.json")

    def restore_from_system(self, id):
        path = self._system_state_path(id)
        if os.path.exists(path):
            try:
                self.restore_from_file(path)
                return True
            except Exception:
                logging.exception(f"Exception during loading state from file '{path}'")
        return False

    def save_to_system(self, id):
        path = self._system_state_path(id)
        self.save_to_file(path)

    def save_as_last(self):
        if self._id:
            self.save_to_system(self._id)

    def restore_last(self):
        if self._id:
            self.restore_from_system(self._id)

    def has_factory_default(self):
        return self._factory_default_path is not None

    def has_last(self):
        return self._id is not None

    def save_as_default(self):
        if self._factory_default_path:
            self.save_to_file(self._factory_default_path)
