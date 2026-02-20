class DecisionMaker:

    def __init__(self):
        self.state = "SEARCH"

        # Basit P kazancı (demo için)
        self.Kp = 40

        # Sabit dönüş steering değeri
        self.turn_steering = 60

    def update(self, vision_data):

        # 1️⃣ Çizgi yoksa SEARCH
        if not vision_data["line_found"]:
            self.state = "SEARCH"

            return {
                "mode": "SEARCH",
                "steering": 0,
                "speed": 0
            }

        # 2️⃣ Turn varsa sağ/sol ayrımı
        if vision_data["turn_detected"]:

            if vision_data["turn_direction"] == "LEFT":
                self.state = "TURN_LEFT"

                return {
                    "mode": "TURN_LEFT",
                    "steering": -self.turn_steering,
                    "speed": 30
                }

            elif vision_data["turn_direction"] == "RIGHT":
                self.state = "TURN_RIGHT"

                return {
                    "mode": "TURN_RIGHT",
                    "steering": self.turn_steering,
                    "speed": 30
                }

        # 3️⃣ Normal takip modu
        self.state = "FOLLOW"

        error = vision_data["center_error"]

        steering = self.Kp * error

        return {
            "mode": "FOLLOW",
            "steering": steering,
            "speed": 50
        }