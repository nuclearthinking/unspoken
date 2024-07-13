import torch

from unspoken.settings import settings


def get_device() -> torch.device:
    if torch.cuda.is_available():
        device = torch.device(f'{settings.device}:{settings.device_index}')
    else:
        device = torch.device('cpu')
    return device
