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


# Remove single global manager and add a mapping for user-specific managers
user_prompt_managers = {}

def get_sys_prompt(user_id: str) -> str:
    if user_id not in user_prompt_managers:
        user_prompt_managers[user_id] = SystemPromptManager()
    return user_prompt_managers[user_id].prompt

def set_sys_prompt(user_id: str, value: str) -> None:
    if user_id not in user_prompt_managers:
        user_prompt_managers[user_id] = SystemPromptManager(value)
    else:
        user_prompt_managers[user_id].prompt = value
