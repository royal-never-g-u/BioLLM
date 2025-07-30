class Memory:
    def __init__(self):
        self.history = []
    def add(self, user_input, ai_output):
        self.history.append({"user": user_input, "ai": ai_output})
    def get_history(self):
        return self.history 