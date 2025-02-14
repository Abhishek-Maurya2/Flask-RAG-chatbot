class SystemPromptManager:
    __default_prompt = (
        "You are Luna, an AI assistant built by Abhishek. "
        "You have realtime access to the internet and can help with a variety of tasks. "
        "Use will only use one tool at a time"
    )

    def __init__(self, prompt: str = None):
        self._prompt = prompt.strip() if prompt and prompt.strip() else self.__default_prompt

    @property
    def prompt(self) -> str:
        return self._prompt

    @prompt.setter
    def prompt(self, value: str) -> None:
        self._prompt = value.strip() if value and value.strip() else self.__default_prompt


sys_prompt_manager = SystemPromptManager()

def set_sys_prompt(value: str) -> None:
    sys_prompt_manager.prompt = value

def get_sys_prompt() -> str:
    return sys_prompt_manager.prompt
