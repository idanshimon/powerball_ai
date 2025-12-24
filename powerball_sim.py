import pymunk
import pygame
import random
import math
import imageio
import os
import sys

# --- Configuration ---
WIDTH, HEIGHT = 600, 600
FPS = 50
STEPS_PER_FRAME = 5  # Physics steps per render frame for stability
TOTAL_WHITE_BALLS = 69
TOTAL_RED_BALLS = 26
BALL_RADIUS = 12
BALL_MASS = 1
GRAVITY = 900.0
PADDLE_SPEED = 8.0  # Radians per second
MIX_TIME = 3.0      # Seconds to mix before drawing
DRAW_INTERVAL = 0.5 # Seconds between draws
OUTPUT_GIF = "powerball_simulation.gif"

# Colors
WHITE = (255, 255, 255)
RED = (200, 0, 0)
BLACK = (20, 20, 20)
GRAY = (100, 100, 100)
GOLD = (255, 215, 0)
GREEN = (0, 200, 0)

class PowerballSim:
    def __init__(self):
        pygame.init()
        self.surface = pygame.Surface((WIDTH, HEIGHT))
        self.frames = []
        self.font = pygame.font.SysFont("Arial", 16, bold=True)
        self.large_font = pygame.font.SysFont("Arial", 32, bold=True)
        
    def setup_physics(self, ball_count, is_red_draw=False):
        self.space = pymunk.Space()
        self.space.gravity = (0.0, GRAVITY)
        self.balls = []
        self.drawn_balls = []
        self.is_red_draw = is_red_draw
        
        # --- Create Chamber (Circle) ---
        center = (WIDTH // 2, HEIGHT // 2)
        radius = 250
        num_segments = 60
        segment_length = (2 * math.pi * radius) / num_segments
        
        # Create static walls (leave a gap at the bottom for the "exit")
        # Actually, for Halogen II, balls usually drop or are picked. 
        # We'll simulate a "trap" at the bottom.
        
        for i in range(num_segments):
            angle = (i / num_segments) * 2 * math.pi
            next_angle = ((i + 1) / num_segments) * 2 * math.pi
            
            p1 = (center[0] + radius * math.cos(angle), center[1] + radius * math.sin(angle))
            p2 = (center[0] + radius * math.cos(next_angle), center[1] + radius * math.sin(next_angle))
            
            wall = pymunk.Segment(self.space.static_body, p1, p2, 5)
            wall.elasticity = 0.6
            wall.friction = 0.5
            self.space.add(wall)

        # --- Create Paddle (Agitator) ---
        self.paddle_body = pymunk.Body(body_type=pymunk.Body.KINEMATIC)
        self.paddle_body.position = center
        self.paddle_body.angular_velocity = PADDLE_SPEED
        
        # Cross shape paddle
        paddle_len = 180
        s1 = pymunk.Segment(self.paddle_body, (-paddle_len, 0), (paddle_len, 0), 8)
        s2 = pymunk.Segment(self.paddle_body, (0, -paddle_len), (0, paddle_len), 8)
        s1.elasticity = 0.8
        s2.elasticity = 0.8
        s1.friction = 0.8
        s2.friction = 0.8
        
        self.space.add(self.paddle_body, s1, s2)
        
        # --- Create Balls ---
        # Grid layout for initialization to prevent overlap
        cols = 8
        start_x = center[0] - 100
        start_y = center[1] - 100
        
        numbers = list(range(1, ball_count + 1))
        random.shuffle(numbers) # Randomize initial positions
        
        for i, number in enumerate(numbers):
            row = i // cols
            col = i % cols
            pos = (start_x + col * (BALL_RADIUS * 2 + 2), start_y + row * (BALL_RADIUS * 2 + 2))
            
            mass = BALL_MASS
            moment = pymunk.moment_for_circle(mass, 0, BALL_RADIUS)
            body = pymunk.Body(mass, moment)
            body.position = pos
            
            shape = pymunk.Circle(body, BALL_RADIUS)
            shape.elasticity = 0.9
            shape.friction = 0.4
            
            self.space.add(body, shape)
            self.balls.append({"body": body, "shape": shape, "number": number, "active": True})

    def draw(self, message=""):
        self.surface.fill(BLACK)
        
        # Draw Chamber
        pygame.draw.circle(self.surface, GRAY, (WIDTH // 2, HEIGHT // 2), 255, 5)
        
        # Draw Paddle
        p_pos = self.paddle_body.position
        angle = self.paddle_body.angle
        # We need to calculate endpoints based on rotation
        paddle_len = 180
        
        # Arm 1
        p1_x = p_pos.x + paddle_len * math.cos(angle)
        p1_y = p_pos.y + paddle_len * math.sin(angle)
        p2_x = p_pos.x - paddle_len * math.cos(angle)
        p2_y = p_pos.y - paddle_len * math.sin(angle)
        pygame.draw.line(self.surface, GOLD, (p1_x, p1_y), (p2_x, p2_y), 8)
        
        # Arm 2
        p3_x = p_pos.x + paddle_len * math.cos(angle + math.pi/2)
        p3_y = p_pos.y + paddle_len * math.sin(angle + math.pi/2)
        p4_x = p_pos.x - paddle_len * math.cos(angle + math.pi/2)
        p4_y = p_pos.y - paddle_len * math.sin(angle + math.pi/2)
        pygame.draw.line(self.surface, GOLD, (p3_x, p3_y), (p4_x, p4_y), 8)

        # Draw Balls
        for ball in self.balls:
            if not ball["active"]: continue
            
            pos = ball["body"].position
            color = RED if self.is_red_draw else WHITE
            
            pygame.draw.circle(self.surface, color, (int(pos.x), int(pos.y)), BALL_RADIUS)
            
            # Draw Number
            text = self.font.render(str(ball["number"]), True, BLACK)
            text_rect = text.get_rect(center=(int(pos.x), int(pos.y)))
            self.surface.blit(text, text_rect)

        # Draw UI
        if message:
            msg_surf = self.large_font.render(message, True, GREEN)
            self.surface.blit(msg_surf, (20, 20))
            
        # Draw "Drawn Balls" list
        y_offset = 60
        title = self.font.render("Drawn Numbers:", True, WHITE)
        self.surface.blit(title, (20, y_offset))
        
        for i, num in enumerate(self.drawn_balls):
            num_text = self.large_font.render(str(num), True, GOLD)
            self.surface.blit(num_text, (20 + i * 50, y_offset + 30))

        # Capture frame
        # Convert Pygame surface to numpy array for imageio
        view = pygame.surfarray.array3d(self.surface)
        view = view.transpose([1, 0, 2]) # Pygame is (w, h, c), imageio needs (h, w, c)
        self.frames.append(view)

    def select_ball(self):
        # In a real machine, a ball drops. Here, we'll pick a random ball 
        # that is currently in the "lower half" of the drum (simulating gravity feed)
        # This adds a physics bias - balls flying high won't be picked.
        
        candidates = []
        center_y = HEIGHT // 2
        
        for ball in self.balls:
            if ball["active"] and ball["body"].position.y > center_y:
                candidates.append(ball)
        
        if candidates:
            # Pick one from the bottom candidates
            selected = random.choice(candidates)
            selected["active"] = False
            # Remove from physics space
            self.space.remove(selected["body"], selected["shape"])
            return selected["number"]
        return None

    def run_simulation(self):
        print("Starting Powerball Simulation...")
        
        # --- PHASE 1: White Balls ---
        print("Simulating White Balls...")
        self.setup_physics(TOTAL_WHITE_BALLS, is_red_draw=False)
        
        # Mixing Phase
        for _ in range(int(MIX_TIME * FPS)):
            for _ in range(STEPS_PER_FRAME):
                self.space.step(1.0 / (FPS * STEPS_PER_FRAME))
            self.draw("Mixing White Balls...")
            
        # Drawing Phase (5 balls)
        for i in range(5):
            # Mix a bit between draws
            for _ in range(int(DRAW_INTERVAL * FPS)):
                for _ in range(STEPS_PER_FRAME):
                    self.space.step(1.0 / (FPS * STEPS_PER_FRAME))
                self.draw(f"Drawing Ball {i+1}...")
            
            number = self.select_ball()
            if number:
                self.drawn_balls.append(number)
                print(f"White Ball {i+1}: {number}")
                
        white_balls_result = list(self.drawn_balls)
        
        # Transition Phase
        for _ in range(int(1.0 * FPS)):
            self.draw("Switching to Red Ball...")

        # --- PHASE 2: Red Ball ---
        print("Simulating Red Ball...")
        # Keep the white balls in the display list but reset physics for red
        saved_white_balls = list(self.drawn_balls)
        self.setup_physics(TOTAL_RED_BALLS, is_red_draw=True)
        self.drawn_balls = saved_white_balls # Restore list for UI
        
        # Mixing Phase
        for _ in range(int(MIX_TIME * FPS)):
            for _ in range(STEPS_PER_FRAME):
                self.space.step(1.0 / (FPS * STEPS_PER_FRAME))
            self.draw("Mixing Red Ball...")
            
        # Drawing Phase (1 ball)
        for _ in range(int(DRAW_INTERVAL * FPS)):
            for _ in range(STEPS_PER_FRAME):
                self.space.step(1.0 / (FPS * STEPS_PER_FRAME))
            self.draw("Drawing Powerball...")
            
        number = self.select_ball()
        if number:
            self.drawn_balls.append(number)
            print(f"Red Ball: {number}")

        # Final Freeze
        for _ in range(int(2.0 * FPS)):
            self.draw("Simulation Complete!")

        # Save GIF
        print(f"Saving simulation to {OUTPUT_GIF}...")
        imageio.mimsave(OUTPUT_GIF, self.frames, fps=FPS)
        print("Done!")
        
        return self.drawn_balls

if __name__ == "__main__":
    sim = PowerballSim()
    results = sim.run_simulation()
    print("\n" + "="*30)
    print("FINAL PREDICTION")
    print("="*30)
    print(f"White Balls: {results[:5]}")
    print(f"Powerball:   {results[5]}")
    print("="*30)
