import os

class Pathmanagement:
    @staticmethod
    def check_and_create_dir(path):
        if not os.path.exists(path):
            print(f"The path {path} does not exist. Creating.")
            os.makedirs(path)
        return path