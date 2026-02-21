class DecisionMaker:

    def __init__(self):
        self.state = "SEARCH"

        # --- DEĞİŞTİRİLDİ ---
        self.Kp = 35
        self.max_steering = 60
        self.deadband = 0.05
        self.turn_steering = 60

    def update(self, vision_data):

        if not vision_data["line_found"]:
            self.state = "SEARCH"
            return {
                "mode": "SEARCH",
                "steering": 0,
                "speed": 0,
                "debug": "Line not found"
            }

        if vision_data["turn_detected"]:

            if vision_data["turn_direction"] == "LEFT":
                self.state = "TURN_LEFT"
                return {
                    "mode": "TURN_LEFT",
                    "steering": -self.turn_steering,
                    "speed": 30,
                    "debug": "Sharp LEFT turn detected"
                }

            elif vision_data["turn_direction"] == "RIGHT":
                self.state = "TURN_RIGHT"
                return {
                    "mode": "TURN_RIGHT",
                    "steering": self.turn_steering,
                    "speed": 30,
                    "debug": "Sharp RIGHT turn detected"
                }

        self.state = "FOLLOW"

        error = vision_data["center_error"]

        # --- DEĞİŞTİRİLDİ: Deadband ---
        if abs(error) < self.deadband:
            steering = 0
            debug_msg = "Centered → Going straight"
        else:
            steering = self.Kp * error

            # --- DEĞİŞTİRİLDİ: Clamp ---
            steering = max(min(steering, self.max_steering), -self.max_steering)

            if error > 0:
                debug_msg = f"Line slightly RIGHT → correcting LEFT ({round(steering,2)})"
            else:
                debug_msg = f"Line slightly LEFT → correcting RIGHT ({round(steering,2)})"

        return {
            "mode": "FOLLOW",
            "steering": steering,
            "speed": 50,
            "debug": debug_msg
        }